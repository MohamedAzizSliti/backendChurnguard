from domain.repositories.email_notification_repository_interface import EmailNotificationRepositoryInterface
from domain.entities.email_notification import EmailNotification, NotificationStatus
from application.dtos.email_notification_dtos import (
    EmailNotificationDTO, 
    EmailNotificationCreateDTO, 
    EmailNotificationUpdateDTO,
    EmailSendRequestDTO,
    EmailSendResponseDTO
)
from infrastructure.services.email_service import EmailService
from typing import List, Optional
from datetime import datetime
import logging
import csv
import io

class EmailNotificationApplicationService:
    def __init__(self, email_notification_repository: EmailNotificationRepositoryInterface):
        self.email_notification_repository = email_notification_repository
        self.email_service = EmailService()
    
    async def get_all_email_notifications(self) -> List[EmailNotificationDTO]:
        notifications = await self.email_notification_repository.get_all()
        return [self._to_dto(notification) for notification in notifications]
    
    async def get_email_notification_by_id(self, notification_id: int) -> Optional[EmailNotificationDTO]:
        notification = await self.email_notification_repository.get_by_id(notification_id)
        if not notification:
            return None
        return self._to_dto(notification)
    
    async def get_notifications_by_status(self, status: NotificationStatus) -> List[EmailNotificationDTO]:
        notifications = await self.email_notification_repository.get_by_status(status)
        return [self._to_dto(notification) for notification in notifications]
    
    async def create_email_notification(self, create_dto: EmailNotificationCreateDTO) -> EmailNotificationDTO:
        notification = EmailNotification(
            email=create_dto.email,
            name=create_dto.name,
            issue=create_dto.issue,
            status=create_dto.status
        )
        created_notification = await self.email_notification_repository.create(notification)
        return self._to_dto(created_notification)
    
    async def process_csv_file(self, csv_content: str) -> dict:
        """Process CSV file content and insert email notifications"""
        try:
            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            email_notifications = []
            errors = []
            processed_count = 0
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is headers
                try:
                    # Validate required fields
                    email = row.get('email', '').strip()
                    name = row.get('name', '').strip()
                    issue = row.get('issue', '').strip()
                    
                    if not email:
                        errors.append(f"Row {row_num}: Email is required")
                        continue
                    if not name:
                        errors.append(f"Row {row_num}: Name is required")
                        continue
                    if not issue:
                        errors.append(f"Row {row_num}: Issue is required")
                        continue
                    
                    # Parse status (optional, defaults to pending)
                    status_str = row.get('status', 'pending').strip().lower()
                    try:
                        status = NotificationStatus(status_str)
                    except ValueError:
                        status = NotificationStatus.PENDING
                        errors.append(f"Row {row_num}: Invalid status '{status_str}', defaulting to 'pending'")
                    
                    # Create notification object
                    notification = EmailNotification(
                        email=email,
                        name=name,
                        issue=issue,
                        status=status
                    )
                    email_notifications.append(notification)
                    processed_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    continue
            
            # Batch insert valid records
            if email_notifications:
                created_notifications = await self.email_notification_repository.batch_create(email_notifications)
                return {
                    "success": True,
                    "message": f"Successfully processed {len(created_notifications)} email notifications",
                    "processed_count": len(created_notifications),
                    "errors": errors,
                    "total_rows": processed_count + len(errors)
                }
            else:
                return {
                    "success": False,
                    "message": "No valid records found in CSV",
                    "processed_count": 0,
                    "errors": errors,
                    "total_rows": len(errors)
                }
                
        except Exception as e:
            import traceback
            logging.error(f"Error processing CSV file: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")

            error_message = f"Error processing CSV file: {str(e)}"

            # Check for common database errors
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                error_message += " - The email_notifications table may not exist. Please check your database setup."
            elif "connection" in str(e).lower():
                error_message += " - Database connection error. Please check your database configuration."

            return {
                "success": False,
                "message": error_message,
                "processed_count": 0,
                "errors": [str(e)],
                "total_rows": 0
            }
    
    async def update_email_notification(self, notification_id: int, update_dto: EmailNotificationUpdateDTO) -> Optional[EmailNotificationDTO]:
        existing_notification = await self.email_notification_repository.get_by_id(notification_id)
        if not existing_notification:
            return None
        
        # Update only provided fields
        if update_dto.email is not None:
            existing_notification.email = update_dto.email
        if update_dto.name is not None:
            existing_notification.name = update_dto.name
        if update_dto.issue is not None:
            existing_notification.issue = update_dto.issue
        if update_dto.status is not None:
            existing_notification.status = update_dto.status
        
        updated_notification = await self.email_notification_repository.update(notification_id, existing_notification)
        if not updated_notification:
            return None
        return self._to_dto(updated_notification)
    
    async def send_emails(self, send_request: EmailSendRequestDTO) -> EmailSendResponseDTO:
        """Send email notifications"""
        try:
            # Get notifications to send
            if send_request.notification_ids:
                # Send specific notifications
                notifications_to_send = []
                for notification_id in send_request.notification_ids:
                    notification = await self.email_notification_repository.get_by_id(notification_id)
                    if notification:
                        # Check if we should send (pending or force resend)
                        if notification.status == NotificationStatus.PENDING or send_request.force_resend:
                            notifications_to_send.append(notification)
            else:
                # Send all pending notifications
                notifications_to_send = await self.email_notification_repository.get_by_status(NotificationStatus.PENDING)
            
            if not notifications_to_send:
                return EmailSendResponseDTO(
                    success=True,
                    message="No notifications to send",
                    sent_count=0,
                    failed_count=0
                )
            
            sent_count = 0
            failed_count = 0
            errors = []
            
            for notification in notifications_to_send:
                try:
                    # Update status to sending
                    await self.email_notification_repository.update_status(
                        notification.id, 
                        NotificationStatus.SENDING
                    )
                    
                    # Send email
                    success, error_msg = await self.email_service.send_email(
                        notification.email,
                        notification.name,
                        notification.issue
                    )
                    
                    if success:
                        # Update status to sent
                        await self.email_notification_repository.update_status(
                            notification.id,
                            NotificationStatus.SENT,
                            datetime.now()
                        )
                        sent_count += 1
                    else:
                        # Update status to failed
                        await self.email_notification_repository.update_status(
                            notification.id,
                            NotificationStatus.FAILED
                        )
                        failed_count += 1
                        if error_msg:
                            errors.append(f"ID {notification.id}: {error_msg}")
                        
                except Exception as e:
                    # Update status to failed
                    await self.email_notification_repository.update_status(
                        notification.id,
                        NotificationStatus.FAILED
                    )
                    failed_count += 1
                    errors.append(f"ID {notification.id}: {str(e)}")
            
            success = failed_count == 0
            message = f"Sent {sent_count} emails successfully"
            if failed_count > 0:
                message += f", {failed_count} failed"
            
            return EmailSendResponseDTO(
                success=success,
                message=message,
                sent_count=sent_count,
                failed_count=failed_count,
                errors=errors if errors else None
            )
            
        except Exception as e:
            logging.error(f"Error in send_emails: {str(e)}")
            return EmailSendResponseDTO(
                success=False,
                message=f"Error sending emails: {str(e)}",
                sent_count=0,
                failed_count=0,
                errors=[str(e)]
            )
    
    async def delete_email_notification(self, notification_id: int) -> bool:
        return await self.email_notification_repository.delete(notification_id)
    
    def _to_dto(self, notification: EmailNotification) -> EmailNotificationDTO:
        return EmailNotificationDTO(
            id=notification.id,
            email=notification.email,
            name=notification.name,
            issue=notification.issue,
            status=notification.status,
            created_at=notification.created_at,
            updated_at=notification.updated_at,
            sent_at=notification.sent_at
        ) 