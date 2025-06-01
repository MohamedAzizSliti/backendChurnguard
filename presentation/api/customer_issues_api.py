from fastapi import APIRouter, Depends, Path, Query, HTTPException, UploadFile, File
from application.services.customer_issue_service import CustomerIssueApplicationService
from application.dtos.auth_dtos import UserProfileDTO
from application.dtos.customer_issue_dtos import CustomerIssueDTO, CustomerIssueCreateDTO, CustomerIssueUpdateDTO
from infrastructure.repositories.customer_issue_repository import CustomerIssueRepository
from presentation.api.auth_api import get_current_user
from typing import List
from infrastructure.services.supabase_initializer import get_supabase_client

router = APIRouter()

# Supabase client
supabase_client = get_supabase_client()

# Repository
customer_issue_repository = CustomerIssueRepository(supabase_client)

# Service
customer_issue_service = CustomerIssueApplicationService(customer_issue_repository)

@router.get("/", response_model=List[CustomerIssueDTO])
async def get_all_customer_issues(current_user: UserProfileDTO = Depends(get_current_user)):
    """Get all customer issues with all columns"""
    return await customer_issue_service.get_all_customer_issues()

@router.post("/upload-csv")
async def upload_csv_customer_issues(
    file: UploadFile = File(...),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Upload and process a CSV file with customer issues
    
    Expected CSV headers: customer_id,code_contrat,client_type,client_region,client_categorie,incident_title,churn_risk
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Process the CSV file
        result = await customer_issue_service.process_csv_file(csv_content)
        
        if result["success"]:
            return {
                "message": result["message"],
                "processed_count": result["processed_count"],
                "total_rows": result["total_rows"],
                "errors": result["errors"] if result["errors"] else None
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": result["message"],
                    "errors": result["errors"]
                }
            )
            
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be a valid UTF-8 encoded CSV file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/customer/{customer_id}", response_model=List[CustomerIssueDTO])
async def get_customer_issues_by_customer_id(
    customer_id: float = Path(..., title="The customer ID to get issues for"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get all customer issues for a specific customer ID"""
    return await customer_issue_service.get_customer_issues_by_customer_id(customer_id)

@router.post("/", response_model=CustomerIssueDTO)
async def create_customer_issue(
    customer_issue: CustomerIssueCreateDTO,
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Create a new customer issue"""
    return await customer_issue_service.create_customer_issue(customer_issue)

@router.put("/customer/{customer_id}/incident/{incident_title}")
async def update_customer_issue(
    customer_issue: CustomerIssueUpdateDTO,
    customer_id: float = Path(..., title="The customer ID"),
    incident_title: str = Path(..., title="The incident title"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Update a customer issue by customer ID and incident title"""
    success = await customer_issue_service.update_customer_issue(customer_id, incident_title, customer_issue)
    if not success:
        raise HTTPException(status_code=404, detail="Customer issue not found")
    return {"message": "Customer issue updated successfully"}

@router.delete("/customer/{customer_id}/incident/{incident_title}")
async def delete_customer_issue(
    customer_id: float = Path(..., title="The customer ID"),
    incident_title: str = Path(..., title="The incident title"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Delete a customer issue by customer ID and incident title"""
    success = await customer_issue_service.delete_customer_issue(customer_id, incident_title)
    if not success:
        raise HTTPException(status_code=404, detail="Customer issue not found")
    return {"message": "Customer issue deleted successfully"} 