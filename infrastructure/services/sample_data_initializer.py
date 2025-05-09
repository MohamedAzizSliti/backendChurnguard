# backend/infrastructure/services/sample_data_initializer.py

from domain.entities.client import Client, Contact
from domain.entities.interaction import Interaction
from domain.entities.recommendation import Recommendation
from domain.entities.factor import Factor
from domain.entities.user import User, UserRole
from infrastructure.repositories.client_repository import ClientRepository
from infrastructure.repositories.interaction_repository import InteractionRepository
from infrastructure.repositories.recommendation_repository import RecommendationRepository
from infrastructure.repositories.factor_repository import FactorRepository
from infrastructure.repositories.user_repository import UserRepository
from datetime import datetime, timedelta
import uuid
from passlib.context import CryptContext

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def initialize_sample_data(
    client_repo: ClientRepository,
    interaction_repo: InteractionRepository,
    recommendation_repo: RecommendationRepository,
    factor_repo: FactorRepository
):
    """Initialize database with sample data if empty"""
    # Check if there are already clients
    existing_clients = await client_repo.get_all()
    if existing_clients:
        return

    print("Initializing sample data...")

    # Sample clients with human-readable 'since'
    sample_clients = [
        {
            "name": "Jean Dupont",
            "segment": "Premium",
            "since": "3 ans",
            "churn_risk": 91,
            "contacts": Contact(
                primary="+33 6 12 34 56 78",
                secondary="+33 1 23 45 67 89",
                preferred_time="Après-midi (14h-18h)",
                last_call="10/05/2023 - Service Support Technique"
            ),
            "monthly_revenue": 120,
            "churn_trend": "+12%",
            "churn_trend_days": 30
        },
        {
            "name": "Marie Laurent",
            "segment": "Standard",
            "since": "1 an",
            "churn_risk": 78,
            "contacts": Contact(
                primary="+33 6 98 76 54 32",
                secondary="",
                preferred_time="Matin (9h-12h)",
                last_call="05/05/2023 - Service Commercial"
            ),
            "monthly_revenue": 75,
            "churn_trend": "+8%",
            "churn_trend_days": 30
        },
        {
            "name": "Pierre Martin",
            "segment": "Premium",
            "since": "5 ans",
            "churn_risk": 45,
            "contacts": Contact(
                primary="+33 6 11 22 33 44",
                secondary="+33 1 11 22 33 44",
                preferred_time="Soir (18h-20h)",
                last_call="15/04/2023 - Service Facturation"
            ),
            "monthly_revenue": 150,
            "churn_trend": "-5%",
            "churn_trend_days": 30
        },
        {
            "name": "Sophie Bernard",
            "segment": "Standard",
            "since": "2 ans",
            "churn_risk": 62,
            "contacts": Contact(
                primary="+33 6 55 66 77 88",
                secondary="",
                preferred_time="Après-midi (14h-18h)",
                last_call="20/04/2023 - Service Support Technique"
            ),
            "monthly_revenue": 85,
            "churn_trend": "+3%",
            "churn_trend_days": 30
        }
    ]

    for client_data in sample_clients:
        # Parse "X ans" into a real date X years ago
        years = int(client_data["since"].split()[0])
        since_date = (datetime.utcnow().date() - timedelta(days=365 * years))
        since_str = since_date.isoformat()

        # Build the Client entity
        client = Client(
            id=str(uuid.uuid4()),
            name=client_data["name"],
            segment=client_data["segment"],
            since=since_str,                  # ISO string date
            churn_risk=client_data["churn_risk"],
            contacts=client_data["contacts"],
            monthly_revenue=client_data["monthly_revenue"],
            churn_trend=client_data["churn_trend"],
            churn_trend_days=client_data["churn_trend_days"],
            created_at=datetime.utcnow().isoformat()
        )

        # Convert to JSON-serializable dict
        client_dict = {**client.__dict__}
        client_dict["contacts"] = {
            "primary": client.contacts.primary,
            "secondary": client.contacts.secondary,
            "preferred_time": client.contacts.preferred_time,
            "last_call": client.contacts.last_call
        }

        # Insert client
        created_client = await client_repo.create_from_dict(client_dict)

        # Add factors
        factors = [
            Factor(
                id=str(uuid.uuid4()),
                client_id=created_client.id,
                name="Problèmes techniques récurrents",
                percentage=48,
                created_at=datetime.utcnow().isoformat()
            ),
            Factor(
                id=str(uuid.uuid4()),
                client_id=created_client.id,
                name="Augmentation tarifaire récente",
                percentage=35,
                created_at=datetime.utcnow().isoformat()
            ),
            Factor(
                id=str(uuid.uuid4()),
                client_id=created_client.id,
                name="Sous-utilisation des services",
                percentage=24,
                created_at=datetime.utcnow().isoformat()
            )
        ]
        for factor in factors:
            await factor_repo.create_from_dict(factor.__dict__)

        # Add interactions
        interactions = [
            {
                "id": str(uuid.uuid4()),
                "client_id": created_client.id,
                "type": "Appel support technique",
                "date": "2023-04-25",
                "details": "Problème de connexion signalé",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "client_id": created_client.id,
                "type": "Intervention technique",
                "date": "2023-04-28",
                "details": "Remplacement du routeur",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "client_id": created_client.id,
                "type": "Appel support technique",
                "date": "2023-05-10",
                "details": "Problème de débit signalé",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        for inter in interactions:
            await interaction_repo.create_from_dict(inter)

        # Add recommendations
        recommendations = [
            {
                "id": str(uuid.uuid4()),
                "client_id": created_client.id,
                "title": "Prioritaire: Résolution technique",
                "impact": -32,
                "details": "Intervention sur site pour optimiser la connexion",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "client_id": created_client.id,
                "title": "Offre fidélité",
                "impact": -18,
                "details": "Remise de 15% pendant 6 mois",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "client_id": created_client.id,
                "title": "Upgrade technologique",
                "impact": -24,
                "details": "Passage à la fibre optique premium",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        for rec in recommendations:
            await recommendation_repo.create_from_dict(rec)

    print("Sample data initialization complete.")

async def initialize_sample_users(user_repo: UserRepository):
    """Initialize sample users with different roles"""
    # Check if users already exist
    try:
        existing_user = await user_repo.get_by_email("admin@example.com")
        if existing_user:
            return
    except:
        pass
    
    print("Initializing sample users...")
    
    # Create sample users with different roles
    sample_users = [
        {
            "email": "admin@example.com",
            "password": pwd_context.hash("adminpass"),
            "full_name": "Admin User",
            "role": UserRole.ADMIN,
            "cin": "ADMIN123",
            "code": "ADM001"
        },
        {
            "email": "marketing@example.com",
            "password": pwd_context.hash("marketingpass"),
            "full_name": "Marketing Agent",
            "role": UserRole.MARKETING_AGENT,
            "cin": "MKT123",
            "code": "MKT001"
        },
        {
            "email": "technical@example.com",
            "password": pwd_context.hash("technicalpass"),
            "full_name": "Technical Agent",
            "role": UserRole.TECHNICAL_AGENT,
            "cin": "TECH123",
            "code": "TECH001"
        }
    ]
    
    for user_data in sample_users:
        user = User(
            id=None,  # Will be generated
            email=user_data["email"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            password=user_data["password"],
            cin=user_data["cin"],
            code=user_data["code"],
            created_at=datetime.now()
        )
        await user_repo.create(user)
    
    print("Sample users initialization complete.")
