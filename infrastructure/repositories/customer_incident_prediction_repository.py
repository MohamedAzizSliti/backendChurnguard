from domain.repositories.customer_incident_prediction_repository_interface import CustomerIncidentPredictionRepositoryInterface
from domain.entities.customer_incident_prediction import CustomerIncidentPrediction, IncidentType
from supabase import Client as SupabaseClient
from typing import List, Optional
from datetime import datetime

class CustomerIncidentPredictionRepository(CustomerIncidentPredictionRepositoryInterface):
    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase
        self.table = "customer_incident_predictions"
    
    async def get_all(self) -> List[CustomerIncidentPrediction]:
        response = self.supabase.table(self.table).select("*").order("created_at", desc=True).execute()
        data = response.data or []
        return [CustomerIncidentPrediction.from_dict(item) for item in data]
    
    async def get_by_id(self, prediction_id: int) -> Optional[CustomerIncidentPrediction]:
        response = self.supabase.table(self.table).select("*").eq("id", prediction_id).execute()
        data = response.data
        if not data:
            return None
        return CustomerIncidentPrediction.from_dict(data[0])
    
    async def get_by_customer_id(self, customer_id: str) -> Optional[CustomerIncidentPrediction]:
        response = self.supabase.table(self.table).select("*").eq("customer_id", customer_id).execute()
        data = response.data
        if not data:
            return None
        return CustomerIncidentPrediction.from_dict(data[0])
    
    async def get_by_region(self, client_region: str) -> List[CustomerIncidentPrediction]:
        response = self.supabase.table(self.table).select("*").eq("client_region", client_region).order("created_at", desc=True).execute()
        data = response.data or []
        return [CustomerIncidentPrediction.from_dict(item) for item in data]
    
    async def get_by_incident_type(self, incident_type: IncidentType) -> List[CustomerIncidentPrediction]:
        response = self.supabase.table(self.table).select("*").eq("most_likely_incident", incident_type.value).order("created_at", desc=True).execute()
        data = response.data or []
        return [CustomerIncidentPrediction.from_dict(item) for item in data]
    
    async def get_by_risk_level(self, min_avg_risk: float) -> List[CustomerIncidentPrediction]:
        # Note: This is a simplified version. For complex calculations, you might want to use a database view or raw SQL
        all_predictions = await self.get_all()
        return [pred for pred in all_predictions if pred.get_average_risk_percentage() >= min_avg_risk]
    
    async def create(self, prediction: CustomerIncidentPrediction) -> CustomerIncidentPrediction:
        prediction_dict = prediction.to_dict()
        # Remove id since it's auto-generated
        if 'id' in prediction_dict:
            del prediction_dict['id']
        # Remove timestamps as they're handled by the database
        if 'created_at' in prediction_dict:
            del prediction_dict['created_at']
        if 'updated_at' in prediction_dict:
            del prediction_dict['updated_at']
        
        response = self.supabase.table(self.table).insert(prediction_dict).execute()
        return CustomerIncidentPrediction.from_dict(response.data[0])
    
    async def batch_create(self, predictions: List[CustomerIncidentPrediction]) -> List[CustomerIncidentPrediction]:
        """Insert multiple customer incident predictions in batch"""
        predictions_data = []
        for prediction in predictions:
            prediction_dict = prediction.to_dict()
            # Remove id since it's auto-generated
            if 'id' in prediction_dict:
                del prediction_dict['id']
            # Remove timestamps as they're handled by the database
            if 'created_at' in prediction_dict:
                del prediction_dict['created_at']
            if 'updated_at' in prediction_dict:
                del prediction_dict['updated_at']
            predictions_data.append(prediction_dict)
        
        try:
            response = self.supabase.table(self.table).insert(predictions_data).execute()
            return [CustomerIncidentPrediction.from_dict(item) for item in response.data]
        except Exception as e:
            # Handle Supabase errors more specifically
            error_msg = str(e)
            if "409" in error_msg or "duplicate key" in error_msg.lower() or "unique constraint" in error_msg.lower():
                raise ValueError("Duplicate customer_id found. Each customer_id must be unique in the database.")
            else:
                raise e
    
    async def update(self, prediction_id: int, prediction: CustomerIncidentPrediction) -> Optional[CustomerIncidentPrediction]:
        prediction_dict = prediction.to_dict()
        # Remove id and timestamps from update data
        if 'id' in prediction_dict:
            del prediction_dict['id']
        if 'created_at' in prediction_dict:
            del prediction_dict['created_at']
        if 'updated_at' in prediction_dict:
            del prediction_dict['updated_at']
        
        response = self.supabase.table(self.table).update(prediction_dict).eq("id", prediction_id).execute()
        data = response.data
        if not data:
            return None
        return CustomerIncidentPrediction.from_dict(data[0])
    
    async def delete(self, prediction_id: int) -> bool:
        self.supabase.table(self.table).delete().eq("id", prediction_id).execute()
        return True 