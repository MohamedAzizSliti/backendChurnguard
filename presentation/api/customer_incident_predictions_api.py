from fastapi import APIRouter, Depends, Path, Query, HTTPException, UploadFile, File
from application.services.customer_incident_prediction_service import CustomerIncidentPredictionApplicationService
from application.dtos.auth_dtos import UserProfileDTO
from application.dtos.customer_incident_prediction_dtos import (
    CustomerIncidentPredictionDTO, 
    CustomerIncidentPredictionCreateDTO, 
    CustomerIncidentPredictionUpdateDTO
)
from domain.entities.customer_incident_prediction import IncidentType
from infrastructure.repositories.customer_incident_prediction_repository import CustomerIncidentPredictionRepository
from presentation.api.auth_api import get_current_user
from typing import List, Optional
from infrastructure.services.supabase_initializer import get_supabase_client

router = APIRouter()

# Supabase client
supabase_client = get_supabase_client()

# Repository
prediction_repository = CustomerIncidentPredictionRepository(supabase_client)

# Service
prediction_service = CustomerIncidentPredictionApplicationService(prediction_repository)

@router.get("/", response_model=List[CustomerIncidentPredictionDTO])
async def get_all_customer_incident_predictions(
    region: Optional[str] = Query(None, description="Filter by client region"),
    incident_type: Optional[IncidentType] = Query(None, description="Filter by incident type"),
    min_risk: Optional[float] = Query(None, description="Filter by minimum average risk percentage"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get all customer incident predictions with optional filters"""
    if region:
        return await prediction_service.get_predictions_by_region(region)
    elif incident_type:
        return await prediction_service.get_predictions_by_incident_type(incident_type)
    elif min_risk is not None:
        return await prediction_service.get_high_risk_predictions(min_risk)
    else:
        return await prediction_service.get_all_predictions()

@router.post("/upload-csv")
async def upload_csv_customer_incident_predictions(
    file: UploadFile = File(...),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Upload and process a CSV file with customer incident predictions
    
    Expected CSV headers: customer_id,client_region,client_type,client_category,q1_prediction,q2_prediction,q3_prediction,q4_prediction,most_likely_incident,recommendation
    
    Valid incident types: internet_problem, wifi_issue, hardware_config, slow_connection, disconnection, other_incident
    
    Note: Each customer_id must be unique. If a customer_id already exists in the database, the upload will fail.
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Process the CSV file
        result = await prediction_service.process_csv_file(csv_content)
        
        if result["success"]:
            return {
                "message": result["message"],
                "processed_count": result["processed_count"],
                "total_rows": result["total_rows"],
                "errors": result["errors"] if result["errors"] else None
            }
        else:
            # Provide detailed error information
            error_detail = {
                "message": result["message"],
                "processed_count": result["processed_count"],
                "total_rows": result["total_rows"],
                "errors": result["errors"]
            }
            
            # Add suggestion if available
            if "suggestion" in result:
                error_detail["suggestion"] = result["suggestion"]
            
            raise HTTPException(
                status_code=400, 
                detail=error_detail
            )
            
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be a valid UTF-8 encoded CSV file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/customer/{customer_id}", response_model=CustomerIncidentPredictionDTO)
async def get_prediction_by_customer_id(
    customer_id: str = Path(..., title="The customer ID to get prediction for"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get customer incident prediction by customer ID"""
    prediction = await prediction_service.get_prediction_by_customer_id(customer_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Customer incident prediction not found")
    return prediction

@router.get("/high-risk", response_model=List[CustomerIncidentPredictionDTO])
async def get_high_risk_predictions(
    min_risk: float = Query(60.0, description="Minimum average risk percentage (default: 60.0)"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get high-risk customer predictions"""
    return await prediction_service.get_high_risk_predictions(min_risk)

@router.get("/region/{region}", response_model=List[CustomerIncidentPredictionDTO])
async def get_predictions_by_region(
    region: str = Path(..., title="The client region to filter by"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get customer incident predictions by region"""
    return await prediction_service.get_predictions_by_region(region)

@router.get("/incident-type/{incident_type}", response_model=List[CustomerIncidentPredictionDTO])
async def get_predictions_by_incident_type(
    incident_type: IncidentType = Path(..., title="The incident type to filter by"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get customer incident predictions by incident type"""
    return await prediction_service.get_predictions_by_incident_type(incident_type)

@router.get("/{prediction_id}", response_model=CustomerIncidentPredictionDTO)
async def get_customer_incident_prediction(
    prediction_id: int = Path(..., title="The ID of the prediction to get"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get customer incident prediction by ID"""
    prediction = await prediction_service.get_prediction_by_id(prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Customer incident prediction not found")
    return prediction

@router.post("/", response_model=CustomerIncidentPredictionDTO)
async def create_customer_incident_prediction(
    prediction: CustomerIncidentPredictionCreateDTO,
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Create a new customer incident prediction"""
    try:
        return await prediction_service.create_prediction(prediction)
    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Customer ID already exists. Each customer_id must be unique.")
        raise HTTPException(status_code=500, detail=f"Error creating prediction: {str(e)}")

@router.put("/{prediction_id}", response_model=CustomerIncidentPredictionDTO)
async def update_customer_incident_prediction(
    prediction: CustomerIncidentPredictionUpdateDTO,
    prediction_id: int = Path(..., title="The ID of the prediction to update"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Update a customer incident prediction by ID"""
    updated_prediction = await prediction_service.update_prediction(prediction_id, prediction)
    if not updated_prediction:
        raise HTTPException(status_code=404, detail="Customer incident prediction not found")
    return updated_prediction

@router.delete("/{prediction_id}")
async def delete_customer_incident_prediction(
    prediction_id: int = Path(..., title="The ID of the prediction to delete"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Delete a customer incident prediction by ID"""
    success = await prediction_service.delete_prediction(prediction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer incident prediction not found")
    return {"message": "Customer incident prediction deleted successfully"} 