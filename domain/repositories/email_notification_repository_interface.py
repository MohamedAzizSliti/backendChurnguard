from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from domain.entities.email_notification import EmailNotification, NotificationStatus

class EmailNotificationRepositoryInterface(ABC):
    @abstractmethod
    async def get_all(self) -> List[EmailNotification]:
        pass
    
    @abstractmethod
    async def get_by_id(self, notification_id: int) -> Optional[EmailNotification]:
        pass
    
    @abstractmethod
    async def get_by_status(self, status: NotificationStatus) -> List[EmailNotification]:
        pass
    
    @abstractmethod
    async def create(self, email_notification: EmailNotification) -> EmailNotification:
        pass
    
    @abstractmethod
    async def batch_create(self, email_notifications: List[EmailNotification]) -> List[EmailNotification]:
        pass
    
    @abstractmethod
    async def update(self, notification_id: int, email_notification: EmailNotification) -> Optional[EmailNotification]:
        pass
    
    @abstractmethod
    async def update_status(self, notification_id: int, status: NotificationStatus, sent_at: Optional[datetime] = None) -> bool:
        pass
    
    @abstractmethod
    async def delete(self, notification_id: int) -> bool:
        pass 