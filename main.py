from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import API modules
from presentation.api.auth_api import router as auth_router
from presentation.api.client_api import router as client_router
from presentation.api.report_api import router as report_router

# Import Supabase initializer
from infrastructure.services.supabase_initializer import get_supabase_client

# Import database schema initializer
from infrastructure.services.db_schema_initializer import create_tables

# Initialize FastAPI app
app = FastAPI(title="ChurnGuard API", description="API for ChurnGuard application")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase
supabase = get_supabase_client()

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(client_router, prefix="/clients", tags=["Clients"])
app.include_router(report_router, prefix="/reports", tags=["Reports"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Initialize sample data on startup
@app.on_event("startup")
async def startup_db_client():
    from infrastructure.repositories.client_repository import ClientRepository
    from infrastructure.repositories.interaction_repository import InteractionRepository
    from infrastructure.repositories.recommendation_repository import RecommendationRepository
    from infrastructure.repositories.factor_repository import FactorRepository
    from infrastructure.services.sample_data_initializer import initialize_sample_data
    
    client_repo = ClientRepository(supabase)
    interaction_repo = InteractionRepository(supabase)
    recommendation_repo = RecommendationRepository(supabase)
    factor_repo = FactorRepository(supabase)
    
    await initialize_sample_data(
        client_repo, 
        interaction_repo, 
        recommendation_repo, 
        factor_repo
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
