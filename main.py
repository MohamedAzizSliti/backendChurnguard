from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import os
import logging
import traceback
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables from .env file
load_dotenv()

# Import API modules
from presentation.api.auth_api import router as auth_router
from presentation.api.client_api import router as client_router
from presentation.api.report_api import router as report_router
from presentation.api.note_api import router as note_router
from presentation.api.customer_issues_api import router as customer_issues_router
from presentation.api.email_notifications_api import router as email_notifications_router
from presentation.api.customer_incident_predictions_api import router as customer_incident_predictions_router

# Import Supabase initializer
from infrastructure.services.supabase_initializer import get_supabase_client

# Import database schema initializer
from infrastructure.services.db_schema_initializer import create_tables

# Initialize FastAPI app
app = FastAPI(
    title="ChurnGuard API", 
    description="API for ChurnGuard application",
    version="1.0.0"
)

# Error handling middleware
@app.middleware("http")
async def db_exception_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # Log the exception
        logging.error(f"Request failed: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Return a generic error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An error occurred processing your request. Please check the logs for more details."},
        )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {str(exc)}")
    logging.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Initialize Supabase
try:
    supabase = get_supabase_client()
except ValueError as e:
    logging.error(f"Failed to initialize Supabase: {str(e)}")
    supabase = None

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(client_router, prefix="/clients", tags=["Clients"])
app.include_router(report_router, prefix="/reports", tags=["Reports"])
app.include_router(note_router, prefix="/notes", tags=["Notes"])
app.include_router(customer_issues_router, prefix="/customer-issues", tags=["Customer Issues"])
app.include_router(email_notifications_router, prefix="/email-notifications", tags=["Email Notifications"])
app.include_router(customer_incident_predictions_router, prefix="/customer-incident-predictions", tags=["Customer Incident Predictions"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Initialize sample data on startup
@app.on_event("startup")
async def startup_db_client():
    try:
        # First create database tables if they don't exist
        await create_tables()
        
        # Initialize Supabase connection
        try:
            supabase_client = get_supabase_client()
        except ValueError as e:
            logging.error(f"Supabase client initialization failed: {str(e)}")
            logging.warning("Application will run with limited functionality.")
            return
            
        # Then initialize repositories and sample data
        from infrastructure.repositories.client_repository import ClientRepository
        from infrastructure.repositories.interaction_repository import InteractionRepository
        from infrastructure.repositories.recommendation_repository import RecommendationRepository
        from infrastructure.repositories.factor_repository import FactorRepository
        from infrastructure.repositories.user_repository import UserRepository
        from infrastructure.services.sample_data_initializer import initialize_sample_data, initialize_sample_users
        
        client_repo = ClientRepository(supabase)
        interaction_repo = InteractionRepository(supabase)
        recommendation_repo = RecommendationRepository(supabase)
        factor_repo = FactorRepository(supabase)
        user_repo = UserRepository(supabase)
        
        try:
            # Initialize sample clients, interactions, etc.
            await initialize_sample_data(
                client_repo, 
                interaction_repo, 
                recommendation_repo, 
                factor_repo
            )
            
            # Initialize sample users
            await initialize_sample_users(user_repo)
        except Exception as e:
            logging.error(f"Error initializing sample data: {str(e)}")
            logging.warning("Application will continue without sample data.")
    except Exception as e:
        logging.error(f"Startup process failed: {str(e)}")
        logging.warning("Application started with errors. Some features may not work correctly.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
