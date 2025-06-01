from domain.repositories.customer_incident_prediction_repository_interface import CustomerIncidentPredictionRepositoryInterface
from domain.entities.customer_incident_prediction import CustomerIncidentPrediction, IncidentType
from application.dtos.customer_incident_prediction_dtos import (
    CustomerIncidentPredictionDTO, 
    CustomerIncidentPredictionCreateDTO, 
    CustomerIncidentPredictionUpdateDTO,
    CustomerRiskAnalysisDTO
)
from typing import List, Optional
from decimal import Decimal
import logging
import csv
import io

class CustomerIncidentPredictionApplicationService:
    def __init__(self, prediction_repository: CustomerIncidentPredictionRepositoryInterface):
        self.prediction_repository = prediction_repository
    
    async def get_all_predictions(self) -> List[CustomerIncidentPredictionDTO]:
        predictions = await self.prediction_repository.get_all()
        return [self._to_dto(prediction) for prediction in predictions]
    
    async def get_prediction_by_id(self, prediction_id: int) -> Optional[CustomerIncidentPredictionDTO]:
        prediction = await self.prediction_repository.get_by_id(prediction_id)
        if not prediction:
            return None
        return self._to_dto(prediction)
    
    async def get_prediction_by_customer_id(self, customer_id: str) -> Optional[CustomerIncidentPredictionDTO]:
        prediction = await self.prediction_repository.get_by_customer_id(customer_id)
        if not prediction:
            return None
        return self._to_dto(prediction)
    
    async def get_predictions_by_region(self, client_region: str) -> List[CustomerIncidentPredictionDTO]:
        predictions = await self.prediction_repository.get_by_region(client_region)
        return [self._to_dto(prediction) for prediction in predictions]
    
    async def get_predictions_by_incident_type(self, incident_type: IncidentType) -> List[CustomerIncidentPredictionDTO]:
        predictions = await self.prediction_repository.get_by_incident_type(incident_type)
        return [self._to_dto(prediction) for prediction in predictions]
    
    async def get_high_risk_predictions(self, min_risk: float = 60.0) -> List[CustomerIncidentPredictionDTO]:
        predictions = await self.prediction_repository.get_by_risk_level(min_risk)
        return [self._to_dto(prediction) for prediction in predictions]
    
    async def create_prediction(self, create_dto: CustomerIncidentPredictionCreateDTO) -> CustomerIncidentPredictionDTO:
        prediction = CustomerIncidentPrediction(
            customer_id=create_dto.customer_id,
            client_region=create_dto.client_region,
            client_type=create_dto.client_type,
            client_category=Decimal(str(create_dto.client_category)) if create_dto.client_category is not None else None,
            q1_prediction=Decimal(str(create_dto.q1_prediction)),
            q2_prediction=Decimal(str(create_dto.q2_prediction)),
            q3_prediction=Decimal(str(create_dto.q3_prediction)),
            q4_prediction=Decimal(str(create_dto.q4_prediction)),
            most_likely_incident=create_dto.most_likely_incident,
            recommendation=create_dto.recommendation
        )
        created_prediction = await self.prediction_repository.create(prediction)
        return self._to_dto(created_prediction)
    
    async def check_existing_customer_ids(self, customer_ids: List[str]) -> List[str]:
        """Check which customer IDs already exist in the database"""
        existing_ids = []
        for customer_id in customer_ids:
            existing_prediction = await self.prediction_repository.get_by_customer_id(customer_id)
            if existing_prediction:
                existing_ids.append(customer_id)
        return existing_ids

    async def process_csv_file(self, csv_content: str) -> dict:
        """Process CSV file content and insert customer incident predictions
        
        Expected CSV headers: customer_id,client_region,client_type,client_category,q1_prediction,q2_prediction,q3_prediction,q4_prediction,most_likely_incident,recommendation
        """
        try:
            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            predictions = []
            errors = []
            processed_count = 0
            customer_ids_in_csv = set()  # Track customer_ids in CSV to detect duplicates
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is headers
                try:
                    # Validate required fields
                    customer_id = row.get('customer_id', '').strip()
                    client_region = row.get('client_region', '').strip()
                    client_type = row.get('client_type', '').strip()
                    most_likely_incident = row.get('most_likely_incident', '').strip()
                    recommendation = row.get('recommendation', '').strip()
                    
                    if not customer_id:
                        errors.append(f"Row {row_num}: customer_id is required")
                        continue
                    if not client_region:
                        errors.append(f"Row {row_num}: client_region is required")
                        continue
                    if not client_type:
                        errors.append(f"Row {row_num}: client_type is required")
                        continue
                    if not most_likely_incident:
                        errors.append(f"Row {row_num}: most_likely_incident is required")
                        continue
                    if not recommendation:
                        errors.append(f"Row {row_num}: recommendation is required")
                        continue
                    
                    # Check for duplicate customer_id within the CSV
                    if customer_id in customer_ids_in_csv:
                        errors.append(f"Row {row_num}: Duplicate customer_id '{customer_id}' found in CSV")
                        continue
                    customer_ids_in_csv.add(customer_id)
                    
                    # Parse optional client_category
                    client_category = None
                    if row.get('client_category', '').strip():
                        try:
                            client_category = Decimal(str(row.get('client_category')))
                        except (ValueError, TypeError):
                            errors.append(f"Row {row_num}: Invalid client_category value")
                            continue
                    
                    # Parse prediction values
                    try:
                        q1_prediction = Decimal(str(row.get('q1_prediction', '0.0')))
                        q2_prediction = Decimal(str(row.get('q2_prediction', '0.0')))
                        q3_prediction = Decimal(str(row.get('q3_prediction', '0.0')))
                        q4_prediction = Decimal(str(row.get('q4_prediction', '0.0')))
                    except (ValueError, TypeError):
                        errors.append(f"Row {row_num}: Invalid prediction values")
                        continue
                    
                    # Validate incident type
                    try:
                        incident_type = IncidentType(most_likely_incident)
                    except ValueError:
                        valid_types = [e.value for e in IncidentType]
                        errors.append(f"Row {row_num}: Invalid incident type '{most_likely_incident}'. Valid types: {valid_types}")
                        continue
                    
                    # Create prediction object
                    prediction = CustomerIncidentPrediction(
                        customer_id=customer_id,
                        client_region=client_region,
                        client_type=client_type,
                        client_category=client_category,
                        q1_prediction=q1_prediction,
                        q2_prediction=q2_prediction,
                        q3_prediction=q3_prediction,
                        q4_prediction=q4_prediction,
                        most_likely_incident=incident_type,
                        recommendation=recommendation
                    )
                    predictions.append(prediction)
                    processed_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    continue
            
            # Batch insert valid records
            if predictions:
                try:
                    existing_customer_ids = await self.check_existing_customer_ids([prediction.customer_id for prediction in predictions])
                    if existing_customer_ids:
                        return {
                            "success": False,
                            "message": f"The following customer_ids already exist in the database: {', '.join(existing_customer_ids)}",
                            "processed_count": 0,
                            "errors": errors,
                            "total_rows": processed_count + len(errors)
                        }
                    created_predictions = await self.prediction_repository.batch_create(predictions)
                    return {
                        "success": True,
                        "message": f"Successfully processed {len(created_predictions)} customer incident predictions",
                        "processed_count": len(created_predictions),
                        "errors": errors,
                        "total_rows": processed_count + len(errors)
                    }
                except ValueError as e:
                    # Handle unique constraint violations specifically
                    if "duplicate" in str(e).lower():
                        return {
                            "success": False,
                            "message": "Some customer_ids already exist in the database. Each customer_id must be unique.",
                            "processed_count": 0,
                            "errors": errors + [f"Database error: {str(e)}"],
                            "total_rows": processed_count + len(errors),
                            "suggestion": "Please check your CSV for duplicate customer_ids or remove existing records from the database before uploading."
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Database error occurred: {str(e)}",
                            "processed_count": 0,
                            "errors": errors + [f"Database error: {str(e)}"],
                            "total_rows": processed_count + len(errors)
                        }
                except Exception as e:
                    # Handle other database errors
                    error_msg = str(e)
                    return {
                        "success": False,
                        "message": f"Database error occurred: {error_msg}",
                        "processed_count": 0,
                        "errors": errors + [f"Database error: {error_msg}"],
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
    
    async def update_prediction(self, prediction_id: int, update_dto: CustomerIncidentPredictionUpdateDTO) -> Optional[CustomerIncidentPredictionDTO]:
        existing_prediction = await self.prediction_repository.get_by_id(prediction_id)
        if not existing_prediction:
            return None
        
        # Update only provided fields
        if update_dto.customer_id is not None:
            existing_prediction.customer_id = update_dto.customer_id
        if update_dto.client_region is not None:
            existing_prediction.client_region = update_dto.client_region
        if update_dto.client_type is not None:
            existing_prediction.client_type = update_dto.client_type
        if update_dto.client_category is not None:
            existing_prediction.client_category = Decimal(str(update_dto.client_category))
        if update_dto.q1_prediction is not None:
            existing_prediction.q1_prediction = Decimal(str(update_dto.q1_prediction))
        if update_dto.q2_prediction is not None:
            existing_prediction.q2_prediction = Decimal(str(update_dto.q2_prediction))
        if update_dto.q3_prediction is not None:
            existing_prediction.q3_prediction = Decimal(str(update_dto.q3_prediction))
        if update_dto.q4_prediction is not None:
            existing_prediction.q4_prediction = Decimal(str(update_dto.q4_prediction))
        if update_dto.most_likely_incident is not None:
            existing_prediction.most_likely_incident = update_dto.most_likely_incident
        if update_dto.recommendation is not None:
            existing_prediction.recommendation = update_dto.recommendation
        
        updated_prediction = await self.prediction_repository.update(prediction_id, existing_prediction)
        if not updated_prediction:
            return None
        return self._to_dto(updated_prediction)
    
    async def delete_prediction(self, prediction_id: int) -> bool:
        return await self.prediction_repository.delete(prediction_id)
    
    def _to_dto(self, prediction: CustomerIncidentPrediction) -> CustomerIncidentPredictionDTO:
        return CustomerIncidentPredictionDTO(
            id=prediction.id,
            customer_id=prediction.customer_id,
            client_region=prediction.client_region,
            client_type=prediction.client_type,
            client_category=float(prediction.client_category) if prediction.client_category is not None else None,
            q1_prediction=float(prediction.q1_prediction),
            q2_prediction=float(prediction.q2_prediction),
            q3_prediction=float(prediction.q3_prediction),
            q4_prediction=float(prediction.q4_prediction),
            most_likely_incident=prediction.most_likely_incident,
            recommendation=prediction.recommendation,
            created_at=prediction.created_at,
            updated_at=prediction.updated_at,
            avg_risk_percentage=prediction.get_average_risk_percentage(),
            risk_level=prediction.get_risk_level()
        ) 