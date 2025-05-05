# File: application/services/client_service.py

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status

from domain.entities.client import Client, Contact
from domain.repositories.client_repository_interface import ClientRepositoryInterface
from domain.repositories.interaction_repository_interface import InteractionRepositoryInterface
from domain.repositories.recommendation_repository_interface import RecommendationRepositoryInterface
from domain.repositories.factor_repository_interface import FactorRepositoryInterface

from application.dtos.client_dtos import (
    ClientDTO,
    ClientDetailDTO,
    ClientCreateDTO,
    ContactDTO,
)


class ClientApplicationService:
    def __init__(
        self,
        client_repository: ClientRepositoryInterface,
        interaction_repository: InteractionRepositoryInterface,
        recommendation_repository: RecommendationRepositoryInterface,
        factor_repository: FactorRepositoryInterface,
    ):
        self.client_repository = client_repository
        self.interaction_repository = interaction_repository
        self.recommendation_repository = recommendation_repository
        self.factor_repository = factor_repository

    async def get_all_clients(self) -> List[ClientDTO]:
        """Get all clients (list view)"""
        try:
            clients = await self.client_repository.get_all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch clients: {str(e)}",
            )

        result: List[ClientDTO] = []
        for client in clients:
            # Map domain Contact → ContactDTO
            contact_dto: Optional[ContactDTO] = None
            if client.contacts:
                cd = client.contacts
                contact_dto = ContactDTO(
                    primary=cd.primary,
                    secondary=cd.secondary,
                    preferred_time=cd.preferred_time,
                    last_call=cd.last_call,
                )

            result.append(
                ClientDTO(
                    id=client.id,
                    name=client.name,
                    segment=client.segment,
                    since=client.since,
                    churn_risk=client.churn_risk,
                    contacts=contact_dto,
                )
            )
        return result

    async def get_client_by_id(self, client_id: str) -> ClientDTO:
        """Get a single client by ID (list‐style DTO)"""
        try:
            client = await self.client_repository.get_by_id(client_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch client: {str(e)}",
            )

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found",
            )

        contact_dto: Optional[ContactDTO] = None
        if client.contacts:
            cd = client.contacts
            contact_dto = ContactDTO(
                primary=cd.primary,
                secondary=cd.secondary,
                preferred_time=cd.preferred_time,
                last_call=cd.last_call,
            )

        return ClientDTO(
            id=client.id,
            name=client.name,
            segment=client.segment,
            since=client.since,
            churn_risk=client.churn_risk,
            contacts=contact_dto,
        )

    async def get_client_detail(self, client_id: str) -> ClientDetailDTO:
        """Get detailed client information by ID"""
        # Fetch base client
        try:
            client = await self.client_repository.get_by_id(client_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch client detail: {str(e)}",
            )

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found",
            )

        # Map Contact
        contact_dto: Optional[ContactDTO] = None
        if client.contacts:
            cd = client.contacts
            contact_dto = ContactDTO(
                primary=cd.primary,
                secondary=cd.secondary,
                preferred_time=cd.preferred_time,
                last_call=cd.last_call,
            )

        # Fetch and map related lists
        interactions = await self.interaction_repository.get_by_client_id(client_id)
        interactions_data = [i.to_dict() for i in interactions]

        recommendations = await self.recommendation_repository.get_by_client_id(client_id)
        recommendations_data = [r.to_dict() for r in recommendations]

        factors = await self.factor_repository.get_by_client_id(client_id)
        factors_data = [f.to_dict() for f in factors]

        return ClientDetailDTO(
            id=client.id,
            name=client.name,
            segment=client.segment,
            since=client.since,
            churn_risk=client.churn_risk,
            contacts=contact_dto,
            monthly_revenue=client.monthly_revenue,
            churn_trend=client.churn_trend,
            churn_trend_days=client.churn_trend_days,
            interactions=interactions_data,
            recommendations=recommendations_data,
            factors=factors_data,
        )

    async def create_client(self, client_data: ClientCreateDTO) -> ClientDTO:
        """Create a new client"""
        # Build domain Contact entity
        contact_entity = Contact(
            primary=client_data.contacts.primary,
            secondary=client_data.contacts.secondary,
            preferred_time=client_data.contacts.preferred_time,
            last_call=client_data.contacts.last_call,
        )

        # Build domain Client entity
        client_entity = Client(
            id="",  # repository will generate
            name=client_data.name,
            segment=client_data.segment,
            since=client_data.since,
            churn_risk=client_data.churn_risk,
            contacts=contact_entity,
            monthly_revenue=client_data.monthly_revenue,
            churn_trend=client_data.churn_trend,
            churn_trend_days=client_data.churn_trend_days,
            created_at=datetime.now(),
        )

        # Persist
        try:
            created_client = await self.client_repository.create(client_entity)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create client: {str(e)}",
            )

        # Map created Contact → ContactDTO
        response_contact: Optional[ContactDTO] = None
        if created_client.contacts:
            cd = created_client.contacts
            response_contact = ContactDTO(
                primary=cd.primary,
                secondary=cd.secondary,
                preferred_time=cd.preferred_time,
                last_call=cd.last_call,
            )

        return ClientDTO(
            id=created_client.id,
            name=created_client.name,
            segment=created_client.segment,
            since=created_client.since,
            churn_risk=created_client.churn_risk,
            contacts=response_contact,
        )

    async def update_client(self, client_id: str, client_data: ClientCreateDTO) -> ClientDTO:
        """Update an existing client"""
        try:
            existing = await self.client_repository.get_by_id(client_id)
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Client {client_id} not found"
                )

            # map DTO → domain entity
            contact = Contact(
                primary=client_data.contacts.primary,
                secondary=client_data.contacts.secondary,
                preferred_time=client_data.contacts.preferred_time,
                last_call=client_data.contacts.last_call
            )
            updated_entity = Client(
                id=client_id,
                name=client_data.name,
                segment=client_data.segment,
                since=client_data.since,
                churn_risk=client_data.churn_risk,
                contacts=contact,
                monthly_revenue=existing.monthly_revenue,
                churn_trend=existing.churn_trend,
                churn_trend_days=existing.churn_trend_days,
                created_at=existing.created_at,
                updated_at=datetime.now()
            )

            saved = await self.client_repository.update(client_id, updated_entity)
            return ClientDTO(
                id=saved.id,
                name=saved.name,
                segment=saved.segment,
                since=saved.since,
                churn_risk=saved.churn_risk,
                contacts=saved.contacts
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update client: {str(e)}"
            )