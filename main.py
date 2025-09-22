from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.api.routes import cases, states, commissions
from app.core.config import settings
from app.services.jagriti_service import JagritiService

jagriti_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global jagriti_service
    jagriti_service = JagritiService()
    await jagriti_service.initialize()
    app.state.jagriti_service = jagriti_service
    yield
    # Shutdown
    await jagriti_service.cleanup()

app = FastAPI(
    title="Jagriti Case Search API",
    description="API for searching District Consumer Court cases via Jagriti portal",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cases.router, prefix="/cases", tags=["cases"])
app.include_router(states.router, prefix="/states", tags=["states"])
app.include_router(commissions.router, prefix="/commissions", tags=["commissions"])

@app.get("/")
async def root():
    return {
        "message": "Jagriti Case Search API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "states": "/states",
            "commissions": "/commissions/{state_id}",
            "search_endpoints": [
                "/cases/by-case-number",
                "/cases/by-complainant", 
                "/cases/by-respondent",
                "/cases/by-complainant-advocate",
                "/cases/by-respondent-advocate",
                "/cases/by-industry-type",
                "/cases/by-judge"
            ]
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )