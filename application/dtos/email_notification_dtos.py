from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from domain.entities.email_notification import NotificationStatus

class EmailNotificationDTO(BaseModel):
    id: Optional[int] = None
    email: str
    name: str
    issue: str
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None

class EmailNotificationCreateDTO(BaseModel):
    email: str
    name: str
    issue: str
    status: NotificationStatus = NotificationStatus.PENDING

class EmailNotificationUpdateDTO(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    issue: Optional[str] = None
    status: Optional[NotificationStatus] = None

class EmailSendRequestDTO(BaseModel):
    notification_ids: Optional[list[int]] = None  # If None, send all pending
    force_resend: bool = False  # If True, resend even if already sent

class EmailSendResponseDTO(BaseModel):
    success: bool
    message: str
    sent_count: int
    failed_count: int
    errors: Optional[list[str]] = None 