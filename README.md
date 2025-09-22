# Jagriti Case Search API

A FastAPI-based backend service that provides programmatic access to District Consumer Court (DCDRC) case data from the Jagriti portal (https://e-jagriti.gov.in/advance-case-search).

## Features

- **Multiple Search Types**: Search cases by case number, complainant, respondent, advocates, industry type, and judge
- **State & Commission Management**: Get lists of available states and commissions with internal IDs
- **Real-time Data**: Makes actual requests to Jagriti portal (no mock data)
- **Robust Error Handling**: Comprehensive error handling with retries and graceful fallbacks
- **Clean Architecture**: Well-structured codebase with separation of concerns
- **Production Ready**: Built with FastAPI, async/await, proper logging, and documentation

## API Endpoints

### Case Search Endpoints
- `POST /cases/by-case-number` - Search by case number
- `POST /cases/by-complainant` - Search by complainant name
- `POST /cases/by-respondent` - Search by respondent name  
- `POST /cases/by-complainant-advocate` - Search by complainant's advocate
- `POST /cases/by-respondent-advocate` - Search by respondent's advocate
- `POST /cases/by-industry-type` - Search by industry type
- `POST /cases/by-judge` - Search by judge name

All search endpoints also support GET method with query parameters.

### Supporting Endpoints
- `GET /states` - Get list of all states with internal IDs
- `GET /commissions/{state_id}` - Get commissions for a specific state

### Utility Endpoints
- `GET /` - API information and available endpoints
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Request Format

### POST Request Body
```json
{
  "state": "KARNATAKA",
  "commission": "Bangalore 1st & Rural Additional", 
  "search_value": "Reddy"
}
```

### GET Request Parameters
```
?state=KARNATAKA&commission=Bangalore%201st%20%26%20Rural%20Additional&search_value=Reddy
```

## Response Format

### Case Search Response
```json
{
  "cases": [
    {
      "case_number": "123/2025",
      "case_stage": "Hearing",
      "filing_date": "2025-02-01",
      "complainant": "John Doe",
      "complainant_advocate": "Adv. Reddy",
      "respondent": "XYZ Ltd.",
      "respondent_advocate": "Adv. Mehta", 
      "document_link": "https://e-jagriti.gov.in/.../case123"
    }
  ],
  "total_count": 1,
  "search_parameters": {
    "state": "KARNATAKA",
    "commission": "Bangalore 1st & Rural Additional",
    "search_value": "Reddy"
  }
}
```

### States Response
```json
{
  "states": [
    {
      "id": "KA",
      "name": "KARNATAKA"
    }
  ]
}
```

### Commissions Response
```json
{
  "commissions": [
    {
"id": "<portal-internal-id>", 
"name": "<commission-name-from-portal>",
      "state_id": "KA"
    }
  ],
  "state_id": "KA"
}
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd jagriti-case-search-api
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy .env file and modify if needed
cp .env.example .env
```

5. **Run the application**
```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

6. **Access the API**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Usage Examples

### Using cURL

**Get all states:**
```bash
curl -X GET "http://localhost:8000/states"
```

**Get commissions for Karnataka:**
```bash
curl -X GET "http://localhost:8000/commissions/KA"
```

**Search cases by complainant (POST):**
```bash
curl -X POST "http://localhost:8000/cases/by-complainant" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "KARNATAKA",
    "commission": "Bangalore 1st & Rural Additional",
    "search_value": "Reddy"
  }'
```

**Search cases by complainant (GET):**
```bash
curl -X GET "http://localhost:8000/cases/by-complainant?state=KARNATAKA&commission=Bangalore%201st%20%26%20Rural%20Additional&search_value=Reddy"
```

### Using Python requests

```python
import requests

# Search cases
response = requests.post(
    "http://localhost:8000/cases/by-complainant",
    json={
        "state": "KARNATAKA", 
        "commission": "Bangalore 1st & Rural Additional",
        "search_value": "Reddy"
    }
)

cases = response.json()
print(f"Found {cases['total_count']} cases")
for case in cases['cases']:
    print(f"Case: {case['case_number']} - {case['complainant']}")
```

## Architecture

### Project Structure
```
├── main.py                    # FastAPI application entry point
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py         # Configuration and settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py        # Pydantic models for requests/responses
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── cases.py      # Case search endpoints
│   │       ├── states.py     # States endpoints
│   │       └── commissions.py # Commissions endpoints
│   └── services/
│       ├── __init__.py
│       └── jagriti_service.py # Core service for Jagriti interaction
├── requirements.txt
├── .env.example
└── README.md
```

### Key Components

1. **JagritiService**: Core service that handles:
   - HTTP requests to Jagriti portal
   - HTML/JSON response parsing
   - State and commission ID mapping
   - Caching for performance
   - Error handling and retries

2. **API Routes**: RESTful endpoints organized by functionality:
   - Cases: All search operations
   - States: State management
   - Commissions: Commission management

3. **Models**: Pydantic schemas for:
   - Request validation
   - Response serialization
   - Type safety

4. **Configuration**: Centralized settings management

## Key Features

### Robust HTTP Client
- Connection pooling with aiohttp
- Automatic retries with exponential backoff
- Rate limiting protection
- Timeout handling
- Custom User-Agent rotation

### Smart Data Parsing
- Handles both JSON and HTML responses
- Flexible table parsing for different layouts
- Date normalization across formats
- Document link extraction
- Text cleaning and normalization

### Efficient Caching
- In-memory caching of states and commissions
- Reduces API calls to Jagriti portal
- Automatic cache invalidation
- Lazy loading of commission data

### Error Handling
- Graceful degradation on failures
- Detailed error messages
- No mock fallbacks (live data only)
- Request validation
- HTTP status code mapping

## Configuration

The application uses environment variables for configuration. Key settings:

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Jagriti Portal
JAGRITI_BASE_URL=https://e-jagriti.gov.in
JAGRITI_SEARCH_URL=https://e-jagriti.gov.in/advance-case-search

# Request Handling
REQUEST_TIMEOUT=30
MAX_RETRIES=3
DELAY_BETWEEN_REQUESTS=1.0
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

An example file is provided at `env.example`.

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Captcha Handling

The API detects when the Jagriti portal presents a captcha challenge and responds with HTTP 503 and a descriptive message. Automated captcha solving is not enabled by default. If you encounter repeated 503 responses, slow down requests or refresh cookies via a manual visit to the portal.

### Production Considerations
- Use gunicorn with uvicorn workers for production
- Set up reverse proxy (nginx)
- Configure logging and monitoring
- Set appropriate resource limits
- Use production database for caching
- Implement rate limiting

## Limitations & Considerations

1. **Jagriti Portal Dependency**: This API depends on the structure and availability of the Jagriti portal
2. **Rate Limiting**: Built-in delays to respect the source website
3. **Captcha Handling**: May require additional logic for captcha challenges
4. **Data Accuracy**: Results are as accurate as the source data
5. **Performance**: Response times depend on Jagriti portal performance

## Testing

Run tests with:
```bash
pytest

# With coverage
pytest --cov=app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the documentation at `/docs`
2. Review existing GitHub issues
3. Create a new issue with detailed information

## Changelog

### v1.0.0
- Initial release
- All core search endpoints
- State and commission management
- Comprehensive error handling
- Production-ready architecture