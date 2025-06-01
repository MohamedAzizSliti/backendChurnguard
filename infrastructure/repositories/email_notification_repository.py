from domain.repositories.email_notification_repository_interface import EmailNotificationRepositoryInterface
from domain.entities.email_notification import EmailNotification, NotificationStatus
from supabase import Client as SupabaseClient
from typing import List, Optional
from datetime import datetime

class EmailNotificationRepository(EmailNotificationRepositoryInterface):
    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase
        self.table = "email_notifications"
    
    async def get_all(self) -> List[EmailNotification]:
        response = self.supabase.table(self.table).select("*").order("created_at", desc=True).execute()
        data = response.data or []
        return [EmailNotification.from_dict(item) for item in data]
    
    async def get_by_id(self, notification_id: int) -> Optional[EmailNotification]:
        response = self.supabase.table(self.table).select("*").eq("id", notification_id).execute()
        data = response.data
        if not data:
            return None
        return EmailNotification.from_dict(data[0])
    
    async def get_by_status(self, status: NotificationStatus) -> List[EmailNotification]:
        response = self.supabase.table(self.table).select("*").eq("status", status.value).order("created_at", desc=True).execute()
        data = response.data or []
        return [EmailNotification.from_dict(item) for item in data]
    
    async def create(self, email_notification: EmailNotification) -> EmailNotification:
        notification_dict = email_notification.to_dict()
        # Remove id since it's auto-generated
        if 'id' in notification_dict:
            del notification_dict['id']
        # Remove timestamps as they're handled by the database
        if 'created_at' in notification_dict:
            del notification_dict['created_at']
        if 'updated_at' in notification_dict:
            del notification_dict['updated_at']
        
        response = self.supabase.table(self.table).insert(notification_dict).execute()
        return EmailNotification.from_dict(response.data[0])
    
    async def batch_create(self, email_notifications: List[EmailNotification]) -> List[EmailNotification]:
        """Insert multiple email notifications in batch"""
        notifications_data = []
        for notification in email_notifications:
            notification_dict = notification.to_dict()
            # Remove id since it's auto-generated
            if 'id' in notification_dict:
                del notification_dict['id']
            # Remove timestamps as they're handled by the database
            if 'created_at' in notification_dict:
                del notification_dict['created_at']
            if 'updated_at' in notification_dict:
                del notification_dict['updated_at']
            notifications_data.append(notification_dict)
        
        response = self.supabase.table(self.table).insert(notifications_data).execute()
        return [EmailNotification.from_dict(item) for item in response.data]
    
    async def update(self, notification_id: int, email_notification: EmailNotification) -> Optional[EmailNotification]:
        notification_dict = email_notification.to_dict()
        # Remove id and timestamps from update data
        if 'id' in notification_dict:
            del notification_dict['id']
        if 'created_at' in notification_dict:
            del notification_dict['created_at']
        if 'updated_at' in notification_dict:
            del notification_dict['updated_at']
        
        response = self.supabase.table(self.table).update(notification_dict).eq("id", notification_id).execute()
        data = response.data
        if not data:
            return None
        return EmailNotification.from_dict(data[0])
    
    async def update_status(self, notification_id: int, status: NotificationStatus, sent_at: Optional[datetime] = None) -> bool:
        update_data = {"status": status.value}
        if sent_at:
            update_data["sent_at"] = sent_at.isoformat()
        
        response = self.supabase.table(self.table).update(update_data).eq("id", notification_id).execute()
        return len(response.data) > 0
    
    async def delete(self, notification_id: int) -> bool:
        self.supabase.table(self.table).delete().eq("id", notification_id).execute()
        return True 