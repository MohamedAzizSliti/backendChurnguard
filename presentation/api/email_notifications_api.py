from fastapi import APIRouter, Depends, Path, Query, HTTPException, UploadFile, File
from application.services.email_notification_service import EmailNotificationApplicationService
from application.dtos.auth_dtos import UserProfileDTO
from application.dtos.email_notification_dtos import (
    EmailNotificationDTO, 
    EmailNotificationCreateDTO, 
    EmailNotificationUpdateDTO,
    EmailSendRequestDTO,
    EmailSendResponseDTO
)
from domain.entities.email_notification import NotificationStatus
from infrastructure.repositories.email_notification_repository import EmailNotificationRepository
from presentation.api.auth_api import get_current_user
from typing import List, Optional
from infrastructure.services.supabase_initializer import get_supabase_client

router = APIRouter()

# Supabase client
supabase_client = get_supabase_client()

# Repository
email_notification_repository = EmailNotificationRepository(supabase_client)

# Service
email_notification_service = EmailNotificationApplicationService(email_notification_repository)

@router.get("/", response_model=List[EmailNotificationDTO])
async def get_all_email_notifications(
    status: Optional[NotificationStatus] = Query(None, description="Filter by status"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get all email notifications, optionally filtered by status"""
    if status:
        return await email_notification_service.get_notifications_by_status(status)
    return await email_notification_service.get_all_email_notifications()

@router.post("/upload-csv")
async def upload_csv_email_notifications(
    file: UploadFile = File(...),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Upload and process a CSV file with email notifications
    
    Expected CSV headers: email,name,issue,status (status is optional, defaults to 'pending')
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Process the CSV file
        result = await email_notification_service.process_csv_file(csv_content)
        
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
        import traceback
        import logging

        # Log the full error for debugging
        logging.error(f"Error processing CSV file: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")

        # Return a more detailed error message
        error_detail = {
            "error": "Error processing file",
            "message": str(e),
            "type": type(e).__name__
        }

        # Check for common database errors
        if "relation" in str(e).lower() and "does not exist" in str(e).lower():
            error_detail["suggestion"] = "The email_notifications table may not exist. Please check your database setup."
        elif "connection" in str(e).lower():
            error_detail["suggestion"] = "Database connection error. Please check your database configuration."

        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/{notification_id}", response_model=EmailNotificationDTO)
async def get_email_notification(
    notification_id: int = Path(..., title="The ID of the email notification to get"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get email notification by ID"""
    notification = await email_notification_service.get_email_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Email notification not found")
    return notification

@router.post("/", response_model=EmailNotificationDTO)
async def create_email_notification(
    notification: EmailNotificationCreateDTO,
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Create a new email notification"""
    return await email_notification_service.create_email_notification(notification)

@router.put("/{notification_id}", response_model=EmailNotificationDTO)
async def update_email_notification(
    notification: EmailNotificationUpdateDTO,
    notification_id: int = Path(..., title="The ID of the email notification to update"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Update an email notification by ID"""
    updated_notification = await email_notification_service.update_email_notification(notification_id, notification)
    if not updated_notification:
        raise HTTPException(status_code=404, detail="Email notification not found")
    return updated_notification

@router.post("/send", response_model=EmailSendResponseDTO)
async def send_email_notifications(
    send_request: EmailSendRequestDTO = EmailSendRequestDTO(),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Send email notifications
    
    - If notification_ids is provided, send only those specific notifications
    - If notification_ids is None, send all pending notifications
    - Use force_resend=True to resend already sent notifications
    """
    return await email_notification_service.send_emails(send_request)

@router.post("/send/pending", response_model=EmailSendResponseDTO)
async def send_pending_email_notifications(
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Send all pending email notifications"""
    send_request = EmailSendRequestDTO(notification_ids=None, force_resend=False)
    return await email_notification_service.send_emails(send_request)

@router.delete("/{notification_id}")
async def delete_email_notification(
    notification_id: int = Path(..., title="The ID of the email notification to delete"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Delete an email notification by ID"""
    success = await email_notification_service.delete_email_notification(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Email notification not found")
    return {"message": "Email notification deleted successfully"} 