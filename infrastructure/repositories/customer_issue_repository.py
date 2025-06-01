from domain.repositories.customer_issue_repository_interface import CustomerIssueRepositoryInterface
from domain.entities.customer_issue import CustomerIssue
from supabase import Client as SupabaseClient
from typing import List, Optional
from datetime import datetime

class CustomerIssueRepository(CustomerIssueRepositoryInterface):
    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase
        self.table = "customer_issues"
    
    async def get_all(self) -> List[CustomerIssue]:
        response = self.supabase.table(self.table).select("*").execute()
        data = response.data or []
        return [CustomerIssue.from_dict(item) for item in data]
    
    async def get_by_customer_id(self, customer_id: float) -> List[CustomerIssue]:
        response = self.supabase.table(self.table).select("*").eq("customer_id", customer_id).execute()
        data = response.data or []
        return [CustomerIssue.from_dict(item) for item in data]
    
    async def create(self, customer_issue: CustomerIssue) -> CustomerIssue:
        issue_dict = customer_issue.to_dict()
        response = self.supabase.table(self.table).insert(issue_dict).execute()
        return CustomerIssue.from_dict(response.data[0])
    
    async def batch_create(self, customer_issues: List[CustomerIssue]) -> List[CustomerIssue]:
        """Insert multiple customer issues in batch"""
        issues_data = [issue.to_dict() for issue in customer_issues]
        response = self.supabase.table(self.table).insert(issues_data).execute()
        return [CustomerIssue.from_dict(item) for item in response.data]
    
    async def update_by_customer_id_and_title(self, customer_id: float, incident_title: str, customer_issue: CustomerIssue) -> bool:
        issue_dict = customer_issue.to_dict()
        response = self.supabase.table(self.table).update(issue_dict).eq("customer_id", customer_id).eq("incident_title", incident_title).execute()
        return len(response.data) > 0
    
    async def delete_by_customer_id_and_title(self, customer_id: float, incident_title: str) -> bool:
        response = self.supabase.table(self.table).delete().eq("customer_id", customer_id).eq("incident_title", incident_title).execute()
        return True 