from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.customer_issue import CustomerIssue

class CustomerIssueRepositoryInterface(ABC):
    @abstractmethod
    async def get_all(self) -> List[CustomerIssue]:
        pass
    
    @abstractmethod
    async def create(self, customer_issue: CustomerIssue) -> CustomerIssue:
        pass
    
    @abstractmethod
    async def batch_create(self, customer_issues: List[CustomerIssue]) -> List[CustomerIssue]:
        pass
    
    @abstractmethod
    async def get_by_customer_id(self, customer_id: float) -> List[CustomerIssue]:
        pass
    
    @abstractmethod
    async def update_by_customer_id_and_title(self, customer_id: float, incident_title: str, customer_issue: CustomerIssue) -> bool:
        pass
    
    @abstractmethod
    async def delete_by_customer_id_and_title(self, customer_id: float, incident_title: str) -> bool:
        pass 