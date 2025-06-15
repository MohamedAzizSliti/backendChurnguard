# backend/infrastructure/services/sample_data_initializer.py

from domain.entities.client import Client, Contact
from domain.entities.interaction import Interaction
from domain.entities.recommendation import Recommendation
from domain.entities.factor import Factor
from domain.entities.user import User, UserRole
from domain.entities.note import Note
from infrastructure.repositories.client_repository import ClientRepository
from infrastructure.repositories.interaction_repository import InteractionRepository
from infrastructure.repositories.recommendation_repository import RecommendationRepository
from infrastructure.repositories.factor_repository import FactorRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.note_repository import NoteRepository
from datetime import datetime, timedelta
import uuid
import random
from typing import List, Dict, Any, Optional
from passlib.context import CryptContext
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def initialize_sample_data(
    client_repo: ClientRepository,
    interaction_repo: InteractionRepository,
    recommendation_repo: RecommendationRepository,
    factor_repo: FactorRepository,
    note_repo: Optional[NoteRepository] = None
):
    """Initialize database with comprehensive sample data if empty"""
    try:
        # Check if there are already clients
        existing_clients = await client_repo.get_all()
        if existing_clients:
            logger.info("Sample data already exists, skipping initialization")
            return

        logger.info("Initializing comprehensive sample data...")

        # Enhanced sample clients with more variety and realistic data
        sample_clients = [
            {
                "name": "Jean Dupont",
                "segment": "Premium",
                "since": "3 ans",
                "churn_risk": "91",  # Fixed: should be string
                "contacts": Contact(
                    primary="+33 6 12 34 56 78",
                    secondary="+33 1 23 45 67 89",
                    preferred_time="Après-midi (14h-18h)",
                    last_call="10/05/2023 - Service Support Technique"
                ),
                "monthly_revenue": "120.50",  # Fixed: should be string
                "churn_trend": "+12%",
                "churn_trend_days": 30
            },
            {
                "name": "Marie Laurent",
                "segment": "Standard",
                "since": "1 an",
                "churn_risk": "78",
                "contacts": Contact(
                    primary="+33 6 98 76 54 32",
                    secondary="",
                    preferred_time="Matin (9h-12h)",
                    last_call="05/05/2023 - Service Commercial"
                ),
                "monthly_revenue": "75.00",
                "churn_trend": "+8%",
                "churn_trend_days": 30
            },
            {
                "name": "Pierre Martin",
                "segment": "Premium",
                "since": "5 ans",
                "churn_risk": "45",
                "contacts": Contact(
                    primary="+33 6 11 22 33 44",
                    secondary="+33 1 11 22 33 44",
                    preferred_time="Soir (18h-20h)",
                    last_call="15/04/2023 - Service Facturation"
                ),
                "monthly_revenue": "150.75",
                "churn_trend": "-5%",
                "churn_trend_days": 30
            },
            {
                "name": "Sophie Bernard",
                "segment": "Standard",
                "since": "2 ans",
                "churn_risk": "62",
                "contacts": Contact(
                    primary="+33 6 55 66 77 88",
                    secondary="",
                    preferred_time="Après-midi (14h-18h)",
                    last_call="20/04/2023 - Service Support Technique"
                ),
                "monthly_revenue": "85.25",
                "churn_trend": "+3%",
                "churn_trend_days": 30
            },
            # Additional diverse clients
            {
                "name": "Antoine Moreau",
                "segment": "Enterprise",
                "since": "7 ans",
                "churn_risk": "25",
                "contacts": Contact(
                    primary="+33 6 77 88 99 00",
                    secondary="+33 1 77 88 99 00",
                    preferred_time="Matin (8h-12h)",
                    last_call="01/06/2023 - Service Commercial"
                ),
                "monthly_revenue": "350.00",
                "churn_trend": "-8%",
                "churn_trend_days": 30
            },
            {
                "name": "Isabelle Rousseau",
                "segment": "Basic",
                "since": "6 mois",
                "churn_risk": "85",
                "contacts": Contact(
                    primary="+33 6 33 44 55 66",
                    secondary="",
                    preferred_time="Soir (17h-19h)",
                    last_call="25/05/2023 - Service Support Technique"
                ),
                "monthly_revenue": "45.00",
                "churn_trend": "+15%",
                "churn_trend_days": 30
            }
        ]

        # Create sample data for each client
        created_clients = []

        for client_data in sample_clients:
            # Parse "X ans" or "X mois" into a real date
            since_parts = client_data["since"].split()
            if len(since_parts) >= 2:
                value = int(since_parts[0])
                unit = since_parts[1]
                if "an" in unit:
                    days_ago = value * 365
                elif "mois" in unit:
                    days_ago = value * 30
                else:
                    days_ago = 365  # default to 1 year
            else:
                days_ago = 365

            since_date = (datetime.now().date() - timedelta(days=days_ago))
            since_str = since_date.isoformat()

            # Build the Client entity
            client = Client(
                id=str(uuid.uuid4()),
                name=client_data["name"],
                segment=client_data["segment"],
                since=since_str,
                churn_risk=client_data["churn_risk"],
                contacts=client_data["contacts"],
                monthly_revenue=client_data["monthly_revenue"],
                churn_trend=client_data["churn_trend"],
                churn_trend_days=client_data["churn_trend_days"],
                created_at=datetime.now()
            )

            # Use the repository's create method instead of create_from_dict
            created_client = await client_repo.create(client)
            created_clients.append(created_client)

        # Add factors for each client with varied data
        factor_templates = [
            {"name": "Problèmes techniques récurrents", "percentage_range": (40, 60)},
            {"name": "Augmentation tarifaire récente", "percentage_range": (25, 45)},
            {"name": "Sous-utilisation des services", "percentage_range": (15, 35)},
            {"name": "Concurrence agressive", "percentage_range": (20, 40)},
            {"name": "Insatisfaction service client", "percentage_range": (30, 50)},
            {"name": "Problèmes de facturation", "percentage_range": (10, 30)}
        ]

        for client in created_clients:
            # Select 2-4 random factors per client
            selected_factors = random.sample(factor_templates, random.randint(2, 4))

            for factor_template in selected_factors:
                factor = Factor(
                    id=str(uuid.uuid4()),
                    client_id=client.id,
                    name=factor_template["name"],
                    percentage=random.randint(*factor_template["percentage_range"]),
                    created_at=datetime.now()
                )
                await factor_repo.create(factor)

        # Add interactions for each client
        interaction_types = [
            "Appel support technique",
            "Intervention technique",
            "Appel service commercial",
            "Email de réclamation",
            "Chat en ligne",
            "Visite en magasin"
        ]

        interaction_details = {
            "Appel support technique": [
                "Problème de connexion signalé",
                "Problème de débit signalé",
                "Panne équipement",
                "Configuration réseau"
            ],
            "Intervention technique": [
                "Remplacement du routeur",
                "Installation nouvelle ligne",
                "Réparation câblage",
                "Mise à jour équipement"
            ],
            "Appel service commercial": [
                "Demande d'information tarifs",
                "Négociation contrat",
                "Demande de résiliation",
                "Upgrade service"
            ]
        }

        for client in created_clients:
            # Generate 2-5 interactions per client over the last 6 months
            num_interactions = random.randint(2, 5)

            for _ in range(num_interactions):
                interaction_type = random.choice(interaction_types)
                details_list = interaction_details.get(interaction_type, ["Interaction générale"])

                # Generate random date within last 6 months
                days_ago = random.randint(1, 180)
                interaction_date = (datetime.now().date() - timedelta(days=days_ago)).isoformat()

                interaction = Interaction(
                    id=str(uuid.uuid4()),
                    client_id=client.id,
                    type=interaction_type,
                    date=interaction_date,
                    details=random.choice(details_list),
                    created_at=datetime.now()
                )
                await interaction_repo.create(interaction)

        # Add recommendations for each client
        recommendation_templates = [
            {"title": "Prioritaire: Résolution technique", "impact_range": (-40, -25), "details": "Intervention sur site pour optimiser la connexion"},
            {"title": "Offre fidélité", "impact_range": (-25, -10), "details": "Remise de 15% pendant 6 mois"},
            {"title": "Upgrade technologique", "impact_range": (-35, -20), "details": "Passage à la fibre optique premium"},
            {"title": "Formation utilisateur", "impact_range": (-15, -5), "details": "Session de formation pour optimiser l'utilisation"},
            {"title": "Support prioritaire", "impact_range": (-20, -10), "details": "Accès au support technique prioritaire"},
            {"title": "Révision tarifaire", "impact_range": (-30, -15), "details": "Négociation d'un tarif préférentiel"}
        ]

        for client in created_clients:
            # Generate 1-3 recommendations per client
            num_recommendations = random.randint(1, 3)
            selected_recommendations = random.sample(recommendation_templates, num_recommendations)

            for rec_template in selected_recommendations:
                recommendation = Recommendation(
                    id=str(uuid.uuid4()),
                    client_id=client.id,
                    title=rec_template["title"],
                    impact=random.randint(*rec_template["impact_range"]),
                    details=rec_template["details"],
                    created_at=datetime.now()
                )
                await recommendation_repo.create(recommendation)

        # Add sample notes if note repository is provided
        if note_repo:
            sample_notes = [
                {
                    "title": "Alerte: Clients à risque élevé",
                    "description": "3 clients ont un risque de churn supérieur à 80%. Action immédiate requise.",
                    "recipients": ["marketing_agent", "admin"]
                },
                {
                    "title": "Rapport mensuel disponible",
                    "description": "Le rapport d'analyse des tendances de churn est maintenant disponible.",
                    "recipients": ["admin", "marketing_agent", "technical_agent"]
                },
                {
                    "title": "Nouvelle fonctionnalité déployée",
                    "description": "Le système de recommandations automatiques est maintenant actif.",
                    "recipients": ["technical_agent"]
                }
            ]

            for note_data in sample_notes:
                note = Note(
                    id=str(uuid.uuid4()),
                    title=note_data["title"],
                    description=note_data["description"],
                    sender_id="system",
                    recipients=note_data["recipients"],
                    is_read=False,
                    timestamp=datetime.now()
                )
                await note_repo.create(note)

        logger.info("Sample data initialization complete.")

    except Exception as e:
        logger.error(f"Error initializing sample data: {str(e)}")
        raise

async def initialize_sample_users(user_repo: UserRepository):
    """Initialize sample users with different roles"""
    try:
        # Check if users already exist
        existing_user = await user_repo.get_by_email("admin@example.com")
        if existing_user:
            logger.info("Sample users already exist, skipping initialization")
            return
    except Exception:
        # User doesn't exist, continue with initialization
        pass

    logger.info("Initializing sample users...")

    # Create sample users with different roles and stronger passwords
    sample_users = [
        {
            "email": "admin@example.com",
            "password": pwd_context.hash("AdminPass123!"),
            "full_name": "Administrateur Système",
            "role": UserRole.ADMIN,
            "cin": "ADMIN12345",
            "code": "ADM001"
        },
        {
            "email": "marketing@example.com",
            "password": pwd_context.hash("MarketingPass123!"),
            "full_name": "Agent Marketing",
            "role": UserRole.MARKETING_AGENT,
            "cin": "MKT12345",
            "code": "MKT001"
        },
        {
            "email": "technical@example.com",
            "password": pwd_context.hash("TechnicalPass123!"),
            "full_name": "Agent Technique",
            "role": UserRole.TECHNICAL_AGENT,
            "cin": "TECH12345",
            "code": "TECH001"
        },
        {
            "email": "support@example.com",
            "password": pwd_context.hash("SupportPass123!"),
            "full_name": "Agent Support Client",
            "role": UserRole.TECHNICAL_AGENT,
            "cin": "SUP12345",
            "code": "SUP001"
        },
        {
            "email": "manager@example.com",
            "password": pwd_context.hash("ManagerPass123!"),
            "full_name": "Responsable Commercial",
            "role": UserRole.MARKETING_AGENT,
            "cin": "MGR12345",
            "code": "MGR001"
        }
    ]

    for user_data in sample_users:
        try:
            user = User(
                id="",  # Will be generated by repository
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                password=user_data["password"],
                cin=user_data["cin"],
                code=user_data["code"],
                created_at=datetime.now()
            )
            await user_repo.create(user)
            logger.info(f"Created user: {user_data['email']} ({user_data['role'].value})")
        except Exception as e:
            logger.error(f"Failed to create user {user_data['email']}: {str(e)}")

    logger.info("Sample users initialization complete.")


def generate_french_phone_number() -> str:
    """Generate a realistic French phone number"""
    prefixes = ["06", "07"]  # Mobile prefixes
    prefix = random.choice(prefixes)
    number = f"+33 {prefix[1]} " + " ".join([f"{random.randint(10, 99)}" for _ in range(4)])
    return number


def generate_realistic_client_data(segment: str, base_churn_risk: int) -> Dict[str, Any]:
    """Generate realistic client data based on segment"""

    # French names pool
    first_names = [
        "Jean", "Marie", "Pierre", "Sophie", "Antoine", "Isabelle", "Michel", "Catherine",
        "Philippe", "Nathalie", "Alain", "Sylvie", "François", "Martine", "Daniel", "Christine",
        "Laurent", "Monique", "Bernard", "Nicole", "Thierry", "Françoise", "Patrick", "Brigitte"
    ]

    last_names = [
        "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand",
        "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David",
        "Bertrand", "Roux", "Vincent", "Fournier", "Morel", "Girard", "Andre", "Lefevre"
    ]

    # Generate name
    name = f"{random.choice(first_names)} {random.choice(last_names)}"

    # Segment-based parameters
    segment_config = {
        "Basic": {
            "revenue_range": (25, 60),
            "churn_risk_modifier": 15,
            "preferred_times": ["Soir (18h-20h)", "Week-end"],
            "since_range": (3, 18)  # months
        },
        "Standard": {
            "revenue_range": (60, 120),
            "churn_risk_modifier": 5,
            "preferred_times": ["Matin (9h-12h)", "Après-midi (14h-18h)"],
            "since_range": (6, 36)  # months
        },
        "Premium": {
            "revenue_range": (120, 250),
            "churn_risk_modifier": -10,
            "preferred_times": ["Matin (8h-12h)", "Après-midi (14h-17h)"],
            "since_range": (12, 84)  # months
        },
        "Enterprise": {
            "revenue_range": (250, 500),
            "churn_risk_modifier": -20,
            "preferred_times": ["Matin (8h-12h)", "Après-midi (13h-17h)"],
            "since_range": (24, 120)  # months
        }
    }

    config = segment_config.get(segment, segment_config["Standard"])

    # Calculate values
    monthly_revenue = round(random.uniform(*config["revenue_range"]), 2)
    churn_risk = max(5, min(95, base_churn_risk + config["churn_risk_modifier"] + random.randint(-10, 10)))

    # Generate since date
    months_ago = random.randint(*config["since_range"])
    if months_ago >= 12:
        years = months_ago // 12
        remaining_months = months_ago % 12
        if remaining_months == 0:
            since = f"{years} an{'s' if years > 1 else ''}"
        else:
            since = f"{years} an{'s' if years > 1 else ''} et {remaining_months} mois"
    else:
        since = f"{months_ago} mois"

    # Generate churn trend
    if churn_risk > 70:
        trend_direction = "+"
        trend_value = random.randint(8, 20)
    elif churn_risk < 40:
        trend_direction = "-"
        trend_value = random.randint(3, 12)
    else:
        trend_direction = random.choice(["+", "-"])
        trend_value = random.randint(2, 8)

    churn_trend = f"{trend_direction}{trend_value}%"

    # Generate contact info
    primary_phone = generate_french_phone_number()
    secondary_phone = generate_french_phone_number() if random.random() > 0.4 else ""
    preferred_time = random.choice(config["preferred_times"])

    # Generate last call info
    call_types = [
        "Service Support Technique",
        "Service Commercial",
        "Service Facturation",
        "Service Client",
        "Support Premium"
    ]

    days_ago = random.randint(1, 60)
    last_call_date = (datetime.now().date() - timedelta(days=days_ago)).strftime("%d/%m/%Y")
    last_call = f"{last_call_date} - {random.choice(call_types)}"

    return {
        "name": name,
        "segment": segment,
        "since": since,
        "churn_risk": str(churn_risk),
        "contacts": Contact(
            primary=primary_phone,
            secondary=secondary_phone,
            preferred_time=preferred_time,
            last_call=last_call
        ),
        "monthly_revenue": str(monthly_revenue),
        "churn_trend": churn_trend,
        "churn_trend_days": 30
    }


async def generate_additional_sample_clients(
    client_repo: ClientRepository,
    count: int = 20
) -> List[Client]:
    """Generate additional diverse sample clients"""

    segments = ["Basic", "Standard", "Premium", "Enterprise"]
    segment_weights = [0.3, 0.4, 0.25, 0.05]  # Distribution weights

    base_churn_risks = {
        "Basic": 75,
        "Standard": 55,
        "Premium": 35,
        "Enterprise": 20
    }

    created_clients = []

    for _ in range(count):
        # Select segment based on weights
        segment = random.choices(segments, weights=segment_weights)[0]
        base_risk = base_churn_risks[segment]

        # Generate client data
        client_data = generate_realistic_client_data(segment, base_risk)

        # Parse since date
        since_parts = client_data["since"].split()
        days_ago = 365  # default

        if "an" in client_data["since"]:
            years = int(since_parts[0])
            days_ago = years * 365
            if "mois" in client_data["since"]:
                # Handle "X ans et Y mois" format
                mois_index = client_data["since"].find("mois")
                if mois_index > 0:
                    mois_part = client_data["since"][client_data["since"].rfind("et")+2:mois_index].strip()
                    try:
                        months = int(mois_part.split()[0])
                        days_ago += months * 30
                    except:
                        pass
        elif "mois" in client_data["since"]:
            months = int(since_parts[0])
            days_ago = months * 30

        since_date = (datetime.now().date() - timedelta(days=days_ago))
        since_str = since_date.isoformat()

        # Create client
        client = Client(
            id=str(uuid.uuid4()),
            name=client_data["name"],
            segment=client_data["segment"],
            since=since_str,
            churn_risk=client_data["churn_risk"],
            contacts=client_data["contacts"],
            monthly_revenue=client_data["monthly_revenue"],
            churn_trend=client_data["churn_trend"],
            churn_trend_days=client_data["churn_trend_days"],
            created_at=datetime.now()
        )

        created_client = await client_repo.create(client)
        created_clients.append(created_client)

    logger.info(f"Generated {count} additional sample clients")
    return created_clients


async def initialize_comprehensive_sample_data(
    client_repo: ClientRepository,
    interaction_repo: InteractionRepository,
    recommendation_repo: RecommendationRepository,
    factor_repo: FactorRepository,
    user_repo: UserRepository,
    note_repo: Optional[NoteRepository] = None,
    include_additional_clients: bool = True,
    additional_client_count: int = 15
):
    """Initialize comprehensive sample data including users and extended client data"""
    try:
        logger.info("Starting comprehensive sample data initialization...")

        # Initialize users first
        await initialize_sample_users(user_repo)

        # Initialize core sample data
        await initialize_sample_data(
            client_repo=client_repo,
            interaction_repo=interaction_repo,
            recommendation_repo=recommendation_repo,
            factor_repo=factor_repo,
            note_repo=note_repo
        )

        # Add additional diverse clients if requested
        if include_additional_clients:
            additional_clients = await generate_additional_sample_clients(
                client_repo=client_repo,
                count=additional_client_count
            )

            # Add factors, interactions, and recommendations for additional clients
            await _add_sample_data_for_clients(
                clients=additional_clients,
                factor_repo=factor_repo,
                interaction_repo=interaction_repo,
                recommendation_repo=recommendation_repo
            )

        logger.info("Comprehensive sample data initialization completed successfully!")

    except Exception as e:
        logger.error(f"Error during comprehensive sample data initialization: {str(e)}")
        raise


async def _add_sample_data_for_clients(
    clients: List[Client],
    factor_repo: FactorRepository,
    interaction_repo: InteractionRepository,
    recommendation_repo: RecommendationRepository
):
    """Add factors, interactions, and recommendations for a list of clients"""

    # Factor templates
    factor_templates = [
        {"name": "Problèmes techniques récurrents", "percentage_range": (40, 60)},
        {"name": "Augmentation tarifaire récente", "percentage_range": (25, 45)},
        {"name": "Sous-utilisation des services", "percentage_range": (15, 35)},
        {"name": "Concurrence agressive", "percentage_range": (20, 40)},
        {"name": "Insatisfaction service client", "percentage_range": (30, 50)},
        {"name": "Problèmes de facturation", "percentage_range": (10, 30)},
        {"name": "Changement de besoins", "percentage_range": (20, 35)},
        {"name": "Problèmes de communication", "percentage_range": (15, 30)}
    ]

    # Interaction types and details
    interaction_types = [
        "Appel support technique",
        "Intervention technique",
        "Appel service commercial",
        "Email de réclamation",
        "Chat en ligne",
        "Visite en magasin",
        "Appel de suivi",
        "Demande d'information"
    ]

    interaction_details = {
        "Appel support technique": [
            "Problème de connexion signalé",
            "Problème de débit signalé",
            "Panne équipement",
            "Configuration réseau",
            "Problème d'authentification",
            "Dysfonctionnement service"
        ],
        "Intervention technique": [
            "Remplacement du routeur",
            "Installation nouvelle ligne",
            "Réparation câblage",
            "Mise à jour équipement",
            "Diagnostic sur site",
            "Configuration avancée"
        ],
        "Appel service commercial": [
            "Demande d'information tarifs",
            "Négociation contrat",
            "Demande de résiliation",
            "Upgrade service",
            "Demande de remise",
            "Changement d'offre"
        ]
    }

    # Recommendation templates
    recommendation_templates = [
        {"title": "Prioritaire: Résolution technique", "impact_range": (-40, -25), "details": "Intervention sur site pour optimiser la connexion"},
        {"title": "Offre fidélité", "impact_range": (-25, -10), "details": "Remise de 15% pendant 6 mois"},
        {"title": "Upgrade technologique", "impact_range": (-35, -20), "details": "Passage à la fibre optique premium"},
        {"title": "Formation utilisateur", "impact_range": (-15, -5), "details": "Session de formation pour optimiser l'utilisation"},
        {"title": "Support prioritaire", "impact_range": (-20, -10), "details": "Accès au support technique prioritaire"},
        {"title": "Révision tarifaire", "impact_range": (-30, -15), "details": "Négociation d'un tarif préférentiel"},
        {"title": "Service personnalisé", "impact_range": (-25, -12), "details": "Attribution d'un conseiller dédié"},
        {"title": "Compensation geste commercial", "impact_range": (-20, -8), "details": "Avoir sur prochaine facture"}
    ]

    for client in clients:
        # Add factors (2-4 per client)
        selected_factors = random.sample(factor_templates, random.randint(2, 4))
        for factor_template in selected_factors:
            factor = Factor(
                id=str(uuid.uuid4()),
                client_id=client.id,
                name=factor_template["name"],
                percentage=random.randint(*factor_template["percentage_range"]),
                created_at=datetime.now()
            )
            await factor_repo.create(factor)

        # Add interactions (2-6 per client)
        num_interactions = random.randint(2, 6)
        for _ in range(num_interactions):
            interaction_type = random.choice(interaction_types)
            details_list = interaction_details.get(interaction_type, ["Interaction générale"])

            # Generate random date within last 6 months
            days_ago = random.randint(1, 180)
            interaction_date = (datetime.now().date() - timedelta(days=days_ago)).isoformat()

            interaction = Interaction(
                id=str(uuid.uuid4()),
                client_id=client.id,
                type=interaction_type,
                date=interaction_date,
                details=random.choice(details_list),
                created_at=datetime.now()
            )
            await interaction_repo.create(interaction)

        # Add recommendations (1-3 per client)
        num_recommendations = random.randint(1, 3)
        selected_recommendations = random.sample(recommendation_templates, num_recommendations)
        for rec_template in selected_recommendations:
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                client_id=client.id,
                title=rec_template["title"],
                impact=random.randint(*rec_template["impact_range"]),
                details=rec_template["details"],
                created_at=datetime.now()
            )
            await recommendation_repo.create(recommendation)

    logger.info(f"Added sample data for {len(clients)} clients")
