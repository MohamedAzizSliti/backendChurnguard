from fastapi import APIRouter, Depends
from application.services.report_service import ReportApplicationService
from application.dtos.auth_dtos import UserProfileDTO
from application.dtos.report_dtos import ChurnTrendsDTO, ChurnBySegmentDTO, ChurnFactorsDTO, RetentionActionsDTO
from presentation.api.auth_api import get_current_user

router = APIRouter()

# Services
report_service = ReportApplicationService()

@router.get("/churn-trends", response_model=ChurnTrendsDTO)
async def get_churn_trends(current_user: UserProfileDTO = Depends(get_current_user)):
    """Get churn trend data for reports"""
    return await report_service.get_churn_trends()

@router.get("/churn-by-segment", response_model=ChurnBySegmentDTO)
async def get_churn_by_segment(current_user: UserProfileDTO = Depends(get_current_user)):
    """Get churn data by segment for reports"""
    return await report_service.get_churn_by_segment()

@router.get("/churn-factors", response_model=ChurnFactorsDTO)
async def get_churn_factors(current_user: UserProfileDTO = Depends(get_current_user)):
    """Get churn factors data for reports"""
    return await report_service.get_churn_factors()

@router.get("/retention-actions", response_model=RetentionActionsDTO)
async def get_retention_actions(current_user: UserProfileDTO = Depends(get_current_user)):
    """Get retention actions data for reports"""
    return await report_service.get_retention_actions()
