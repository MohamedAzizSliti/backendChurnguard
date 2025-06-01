from domain.repositories.customer_issue_repository_interface import CustomerIssueRepositoryInterface
from domain.entities.customer_issue import CustomerIssue
from application.dtos.customer_issue_dtos import CustomerIssueDTO, CustomerIssueCreateDTO, CustomerIssueUpdateDTO
from typing import List, Optional
import csv
import io

class CustomerIssueApplicationService:
    def __init__(self, customer_issue_repository: CustomerIssueRepositoryInterface):
        self.customer_issue_repository = customer_issue_repository
    
    async def get_all_customer_issues(self) -> List[CustomerIssueDTO]:
        customer_issues = await self.customer_issue_repository.get_all()
        return [self._to_dto(issue) for issue in customer_issues]
    
    async def get_customer_issues_by_customer_id(self, customer_id: float) -> List[CustomerIssueDTO]:
        customer_issues = await self.customer_issue_repository.get_by_customer_id(customer_id)
        return [self._to_dto(issue) for issue in customer_issues]
    
    async def create_customer_issue(self, create_dto: CustomerIssueCreateDTO) -> CustomerIssueDTO:
        customer_issue = CustomerIssue(
            customer_id=create_dto.customer_id,
            code_contrat=create_dto.code_contrat,
            client_type=create_dto.client_type,
            client_region=create_dto.client_region,
            client_categorie=create_dto.client_categorie,
            incident_title=create_dto.incident_title,
            churn_risk=create_dto.churn_risk,
            status=create_dto.status
        )
        created_issue = await self.customer_issue_repository.create(customer_issue)
        return self._to_dto(created_issue)
    
    async def process_csv_file(self, csv_content: str) -> dict:
        """Process CSV file content and insert customer issues"""
        try:
            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            customer_issues = []
            errors = []
            processed_count = 0
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is headers
                try:
                    # Validate and convert data types
                    customer_issue = CustomerIssue(
                        customer_id=float(row['customer_id']) if row.get('customer_id') and row['customer_id'].strip() else None,
                        code_contrat=float(row['code_contrat']) if row.get('code_contrat') and row['code_contrat'].strip() else None,
                        client_type=float(row['client_type']) if row.get('client_type') and row['client_type'].strip() else None,
                        client_region=float(row['client_region']) if row.get('client_region') and row['client_region'].strip() else None,
                        client_categorie=float(row['client_categorie']) if row.get('client_categorie') and row['client_categorie'].strip() else None,
                        incident_title=row.get('incident_title', '').strip() if row.get('incident_title') else None,
                        churn_risk=float(row['churn_risk']) if row.get('churn_risk') and row['churn_risk'].strip() else None,
                        status="not sent"  # Default status for CSV imports
                    )
                    customer_issues.append(customer_issue)
                    processed_count += 1
                    
                except (ValueError, KeyError) as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    continue
            
            # Batch insert valid records
            if customer_issues:
                created_issues = await self.customer_issue_repository.batch_create(customer_issues)
                return {
                    "success": True,
                    "message": f"Successfully processed {len(created_issues)} customer issues",
                    "processed_count": len(created_issues),
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
            return {
                "success": False,
                "message": f"Error processing CSV file: {str(e)}",
                "processed_count": 0,
                "errors": [str(e)],
                "total_rows": 0
            }
    
    async def update_customer_issue(self, customer_id: float, incident_title: str, update_dto: CustomerIssueUpdateDTO) -> bool:
        customer_issue = CustomerIssue(
            customer_id=update_dto.customer_id if update_dto.customer_id is not None else customer_id,
            code_contrat=update_dto.code_contrat,
            client_type=update_dto.client_type,
            client_region=update_dto.client_region,
            client_categorie=update_dto.client_categorie,
            incident_title=update_dto.incident_title if update_dto.incident_title is not None else incident_title,
            churn_risk=update_dto.churn_risk,
            status=update_dto.status if update_dto.status is not None else "not sent"
        )
        return await self.customer_issue_repository.update_by_customer_id_and_title(customer_id, incident_title, customer_issue)
    
    async def delete_customer_issue(self, customer_id: float, incident_title: str) -> bool:
        return await self.customer_issue_repository.delete_by_customer_id_and_title(customer_id, incident_title)
    
    def _to_dto(self, customer_issue: CustomerIssue) -> CustomerIssueDTO:
        return CustomerIssueDTO(
            customer_id=customer_issue.customer_id,
            code_contrat=customer_issue.code_contrat,
            client_type=customer_issue.client_type,
            client_region=customer_issue.client_region,
            client_categorie=customer_issue.client_categorie,
            incident_title=customer_issue.incident_title,
            churn_risk=customer_issue.churn_risk,
            status=customer_issue.status
        ) 