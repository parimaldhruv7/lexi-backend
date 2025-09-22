import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, parse_qs, urlparse
from bs4 import BeautifulSoup
import logging
from datetime import datetime

from app.core.config import settings
from app.models.schemas import Case, State, Commission, SearchType

logger = logging.getLogger(__name__)

class JagritiService:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.states_cache: Dict[str, State] = {}
        self.commissions_cache: Dict[str, List[Commission]] = {}
        
        # Field mappings for different search types
        self.search_field_mapping = {
            SearchType.CASE_NUMBER: "case_no",
            SearchType.COMPLAINANT: "complainant_name", 
            SearchType.RESPONDENT: "respondent_name",
            SearchType.COMPLAINANT_ADVOCATE: "complainant_advocate",
            SearchType.RESPONDENT_ADVOCATE: "respondent_advocate",
            SearchType.INDUSTRY_TYPE: "industry_type",
            SearchType.JUDGE: "judge_name"
        }
    
    async def initialize(self):
        """Initialize the service with HTTP session and cached data"""
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': settings.USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        # Load states data
        await self._load_states()
    
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make HTTP request with retry logic"""
        for attempt in range(settings.MAX_RETRIES):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return response
                    elif response.status == 429:  # Rate limited
                        await asyncio.sleep(settings.DELAY_BETWEEN_REQUESTS * (attempt + 1))
                        continue
                    else:
                        response.raise_for_status()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == settings.MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(settings.DELAY_BETWEEN_REQUESTS * (attempt + 1))
        
        raise Exception("Max retries exceeded")
    
    async def _load_states(self):
        """Load and cache states from Jagriti portal. No mock fallback."""
        try:
            # Get the main search page to extract states and commissions
            response = await self._make_request('GET', settings.JAGRITI_SEARCH_URL)
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            # Captcha detection
            if self._detect_captcha(html):
                raise RuntimeError("Captcha encountered while loading states")
            
            # Extract states from dropdown/form
            states_select = soup.find('select', {'name': 'state'}) or soup.find('select', {'id': 'state'})
            if states_select:
                for option in states_select.find_all('option'):
                    if option.get('value') and option.text.strip():
                        state_id = option['value']
                        state_name = option.text.strip().upper()
                        self.states_cache[state_name] = State(id=state_id, name=state_name)
            
            if not self.states_cache:
                raise RuntimeError("Failed to load states from Jagriti portal")
            
            logger.info(f"Loaded {len(self.states_cache)} states from portal")
            
        except Exception as e:
            logger.error(f"Error loading states: {e}")
            # Do not fallback to mock data per requirements
            raise
    
    def _load_default_states_mapping(self):
        """Deprecated: no mock fallback allowed by requirements."""
        raise RuntimeError("Default state mapping is disabled (no mock data allowed)")
    
    async def get_states(self) -> List[State]:
        """Get list of all available states"""
        return list(self.states_cache.values())
    
    async def get_commissions(self, state_id: str) -> List[Commission]:
        """Get commissions for a specific state"""
        if state_id in self.commissions_cache:
            return self.commissions_cache[state_id]
        
        try:
            # Load the search page with the state parameter so the portal populates commissions
            params = {'state': state_id, 'court': 'DCDRC'}
            response = await self._make_request('GET', settings.JAGRITI_SEARCH_URL, params=params)
            html = await response.text()
            if self._detect_captcha(html):
                raise RuntimeError("Captcha encountered while loading commissions")
            soup = BeautifulSoup(html, 'html.parser')
            
            commissions = []
            # Extract commissions from dropdown/form
            commission_select = (
                soup.find('select', {'name': 'commission'}) or 
                soup.find('select', {'id': 'commission'}) or
                soup.find('select', {'name': 'dcdrc'})
            )
            if commission_select:
                for option in commission_select.find_all('option'):
                    if option.get('value') and option.text.strip():
                        commission_id = option['value']
                        commission_name = option.text.strip()
                        commissions.append(Commission(
                            id=commission_id,
                            name=commission_name,
                            state_id=state_id
                        ))
            
            if not commissions:
                raise RuntimeError(f"Failed to load commissions for state {state_id}")
            
            self.commissions_cache[state_id] = commissions
            return commissions
            
        except Exception as e:
            logger.error(f"Error getting commissions for state {state_id}: {e}")
            raise
    
    def _get_default_commissions(self, state_id: str) -> List[Commission]:
        """Deprecated: no mock fallback allowed by requirements."""
        raise RuntimeError("Default commissions mapping is disabled (no mock data allowed)")
    
    def _find_state_id(self, state_name: str) -> Optional[str]:
        """Find internal state ID from state name"""
        state_name_upper = state_name.upper()
        if state_name_upper in self.states_cache:
            return self.states_cache[state_name_upper].id
        # strict: no fuzzy fallback to avoid wrong IDs
        return None
    
    def _find_commission_id(self, state_id: str, commission_name: str) -> Optional[str]:
        """Find internal commission ID from commission name"""
        if state_id not in self.commissions_cache:
            return None
        
        # strict: exact match first (case-insensitive), no partials to reduce ambiguity
        target = commission_name.strip().lower()
        for commission in self.commissions_cache[state_id]:
            if commission.name.strip().lower() == target:
                return commission.id
        return None
    
    async def search_cases(
        self, 
        search_type: SearchType, 
        state: str, 
        commission: str, 
        search_value: str
    ) -> List[Case]:
        """Search for cases based on the given parameters"""
        try:
            # Map state and commission names to internal IDs
            state_id = self._find_state_id(state)
            if not state_id:
                raise ValueError(f"State '{state}' not found")
            
            # Load commissions for this state if not cached
            if state_id not in self.commissions_cache:
                await self.get_commissions(state_id)
            
            commission_id = self._find_commission_id(state_id, commission)
            if not commission_id:
                raise ValueError(f"Commission '{commission}' not found for state '{state}'")
            
            # Prepare search parameters and submit form
            search_field = self.search_field_mapping[search_type]
            html = await self._submit_search_form(
                state_id=state_id,
                commission_id=commission_id,
                search_field=search_field,
                search_value=search_value
            )
            if self._detect_captcha(html):
                raise RuntimeError("Captcha encountered during search")
            return self._parse_html_response(html)
                
        except Exception as e:
            logger.error(f"Error searching cases: {e}")
            raise
    
    def _parse_json_response(self, json_data: dict) -> List[Case]:
        """Parse JSON response from Jagriti API"""
        cases = []
        
        if 'cases' in json_data:
            for case_data in json_data['cases']:
                try:
                    case = Case(
                        case_number=case_data.get('case_number', ''),
                        case_stage=case_data.get('case_stage', ''),
                        filing_date=case_data.get('filing_date', ''),
                        complainant=case_data.get('complainant', ''),
                        complainant_advocate=case_data.get('complainant_advocate', ''),
                        respondent=case_data.get('respondent', ''),
                        respondent_advocate=case_data.get('respondent_advocate', ''),
                        document_link=case_data.get('document_link', '')
                    )
                    cases.append(case)
                except Exception as e:
                    logger.warning(f"Error parsing case data: {e}")
                    continue
        
        return cases

    async def _submit_search_form(
        self,
        state_id: str,
        commission_id: str,
        search_field: str,
        search_value: str
    ) -> str:
        """Simulate the portal search by submitting the advanced search form and return HTML."""
        # Load page to capture cookies and hidden inputs
        get_resp = await self._make_request('GET', settings.JAGRITI_SEARCH_URL)
        page_html = await get_resp.text()
        soup = BeautifulSoup(page_html, 'html.parser')
        form = soup.find('form')
        action = settings.JAGRITI_SEARCH_URL
        method = 'POST'
        if form:
            action_attr = form.get('action')
            if action_attr:
                action = urljoin(settings.JAGRITI_BASE_URL, action_attr)
            method = (form.get('method') or 'POST').upper()
        # Collect hidden inputs
        form_data: Dict[str, str] = {}
        if form:
            for inp in form.find_all('input'):
                name = inp.get('name')
                if not name:
                    continue
                value = inp.get('value') or ''
                input_type = (inp.get('type') or '').lower()
                if input_type in ('hidden', 'text') and name not in form_data:
                    form_data[name] = value
        # Assign required fields (best-effort names based on portal)
        form_data.update({
            'state': state_id,
            'commission': commission_id,
            'court_type': 'DCDRC',
            'order_type': 'daily_order',
            'date_filter': 'filing_date',
            search_field: search_value,
        })
        # Submit
        if method == 'GET':
            resp = await self._make_request('GET', action, params=form_data)
        else:
            resp = await self._make_request('POST', action, data=form_data)
        return await resp.text()

    def _detect_captcha(self, html: str) -> bool:
        """Heuristically detect captcha challenge in HTML."""
        if not html:
            return False
        lower = html.lower()
        markers = [
            'captcha',
            'g-recaptcha',
            'cf-challenge',
            'please verify you are a human',
        ]
        return any(m in lower for m in markers)
    
    def _parse_html_response(self, html: str) -> List[Case]:
        """Parse HTML response from Jagriti portal"""
        cases = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the table containing case results
        results_table = soup.find('table', {'class': 'results'}) or soup.find('table', {'id': 'case-results'})
        
        if not results_table:
            # Try to find any table with case data
            tables = soup.find_all('table')
            for table in tables:
                if self._contains_case_data(table):
                    results_table = table
                    break
        
        if results_table:
            rows = results_table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                try:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 7:  # Ensure we have enough columns
                        case = Case(
                            case_number=self._extract_text(cells[0]),
                            case_stage=self._extract_text(cells[1]),
                            filing_date=self._normalize_date(self._extract_text(cells[2])),
                            complainant=self._extract_text(cells[3]),
                            complainant_advocate=self._extract_text(cells[4]),
                            respondent=self._extract_text(cells[5]),
                            respondent_advocate=self._extract_text(cells[6]),
                            document_link=self._extract_document_link(cells[0] if len(cells) > 7 else cells[0])
                        )
                        cases.append(case)
                except Exception as e:
                    logger.warning(f"Error parsing table row: {e}")
                    continue
        
        return cases
    
    def _contains_case_data(self, table) -> bool:
        """Check if table contains case data"""
        headers = table.find('tr')
        if headers:
            header_text = ' '.join([th.get_text().lower() for th in headers.find_all(['th', 'td'])])
            return any(keyword in header_text for keyword in ['case', 'complainant', 'respondent', 'filing'])
        return False
    
    def _extract_text(self, cell) -> str:
        """Extract text from table cell"""
        if not cell:
            return ""
        
        # Remove extra whitespace and newlines
        text = ' '.join(cell.get_text().split())
        return text.strip()
    
    def _extract_document_link(self, cell) -> str:
        """Extract document link from table cell"""
        if not cell:
            return ""
        
        # Look for links in the cell
        link = cell.find('a')
        if link and link.get('href'):
            href = link['href']
            if href.startswith('/'):
                return urljoin(settings.JAGRITI_BASE_URL, href)
            elif href.startswith('http'):
                return href
        
        return ""
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format"""
        if not date_str:
            return ""
        
        # Try to parse various date formats
        date_formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d.%m.%Y']
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str.strip(), fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If parsing fails, return original string
        return date_str.strip()