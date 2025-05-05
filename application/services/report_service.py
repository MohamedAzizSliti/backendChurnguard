from application.dtos.report_dtos import (
    ChurnTrendsDTO, 
    ChurnBySegmentDTO, 
    ChurnSegmentDTO,
    ChurnFactorsDTO,
    ChurnFactorDTO,
    RetentionActionsDTO,
    RetentionActionDTO
)
from fastapi import HTTPException, status

class ReportApplicationService:
    async def get_churn_trends(self) -> ChurnTrendsDTO:
        """Get churn trend data for reports"""
        try:
            # In a real app, you would query a repository for this data
            # For now, return mock data
            return ChurnTrendsDTO(
                months=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                churn_rates=[4.2, 4.3, 4.5, 4.7, 4.6, 4.5, 4.4, 4.3, 4.2, 4.1, 4.0, 3.9]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch churn trends: {str(e)}"
            )
    
    async def get_churn_by_segment(self) -> ChurnBySegmentDTO:
        """Get churn data by segment for reports"""
        try:
            # In a real app, you would query a repository for this data
            # For now, return mock data
            return ChurnBySegmentDTO(
                segments=[
                    ChurnSegmentDTO(name="Premium", percentage=35, color="#f97316"),
                    ChurnSegmentDTO(name="Standard", percentage=45, color="#fb923c"),
                    ChurnSegmentDTO(name="Basic", percentage=20, color="#fdba74")
                ]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch churn by segment: {str(e)}"
            )
    
    async def get_churn_factors(self) -> ChurnFactorsDTO:
        """Get churn factors data for reports"""
        try:
            # In a real app, you would query a repository for this data
            # For now, return mock data
            return ChurnFactorsDTO(
                factors=[
                    ChurnFactorDTO(name="Problèmes techniques", percentage=42),
                    ChurnFactorDTO(name="Augmentation tarifaire", percentage=28),
                    ChurnFactorDTO(name="Sous-utilisation", percentage=18),
                    ChurnFactorDTO(name="Offres concurrentes", percentage=12)
                ]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch churn factors: {str(e)}"
            )
    
    async def get_retention_actions(self) -> RetentionActionsDTO:
        """Get retention actions data for reports"""
        try:
            # In a real app, you would query a repository for this data
            # For now, return mock data
            return RetentionActionsDTO(
                actions=[
                    RetentionActionDTO(name="Résolution technique", effectiveness=78, cost=120, roi=320),
                    RetentionActionDTO(name="Offre fidélité", effectiveness=65, cost=85, roi=240),
                    RetentionActionDTO(name="Upgrade technologique", effectiveness=58, cost=150, roi=180),
                    RetentionActionDTO(name="Formation client", effectiveness=45, cost=60, roi=210),
                    RetentionActionDTO(name="Remise commerciale", effectiveness=40, cost=100, roi=150)
                ]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch retention actions: {str(e)}"
            )
