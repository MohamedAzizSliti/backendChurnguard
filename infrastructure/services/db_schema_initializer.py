import os
import asyncpg
import logging

async def create_tables():
    db_url = os.getenv("SUPABASE_DB_URL")  # You need to set this in your .env
    if not db_url:
        logging.warning("SUPABASE_DB_URL not set. Database tables will not be created.")
        return

    try:
        conn = await asyncpg.connect(dsn=db_url)
        
        # Create clients table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name text NOT NULL,
            segment text NOT NULL,
            since text NOT NULL,
            churn_risk text NOT NULL,
            contacts jsonb NOT NULL,
            monthly_revenue text,
            churn_trend text,
            churn_trend_days integer,
            created_at timestamptz DEFAULT NOW(),
            updated_at timestamptz
        );
        """)
        
        # Add the notes table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            title text NOT NULL,
            description text NOT NULL,
            sender_id uuid NOT NULL,
            recipients text[] NOT NULL,
            is_read boolean DEFAULT FALSE,
            timestamp timestamptz NOT NULL
        );
        """)
        
        # Create users table if it doesn't exist
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            email text UNIQUE NOT NULL,
            full_name text NOT NULL,
            role text NOT NULL,
            password text NOT NULL,
            cin text UNIQUE NOT NULL,
            code text UNIQUE NOT NULL,
            created_at timestamptz NOT NULL,
            updated_at timestamptz
        );
        """)

        # Create email_notifications table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS email_notifications (
            id SERIAL PRIMARY KEY,
            email text NOT NULL,
            name text NOT NULL,
            issue text NOT NULL,
            status text NOT NULL DEFAULT 'pending',
            created_at timestamptz DEFAULT NOW(),
            updated_at timestamptz DEFAULT NOW(),
            sent_at timestamptz
        );
        """)

        # Create customer_issues table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS customer_issues (
            id SERIAL PRIMARY KEY,
            customer_id float,
            code_contrat float,
            client_type float,
            client_region float,
            client_categorie float,
            incident_title text,
            churn_risk float,
            status text DEFAULT 'not sent',
            created_at timestamptz DEFAULT NOW(),
            updated_at timestamptz DEFAULT NOW()
        );
        """)

        # Create customer_incident_predictions table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS customer_incident_predictions (
            id SERIAL PRIMARY KEY,
            customer_id text,
            client_region text,
            client_type text,
            client_category text,
            q1_prediction float,
            q2_prediction float,
            q3_prediction float,
            q4_prediction float,
            most_likely_incident text,
            recommendation text,
            created_at timestamptz DEFAULT NOW(),
            updated_at timestamptz DEFAULT NOW()
        );
        """)

        # Create interactions table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            clientId uuid NOT NULL,
            type text NOT NULL,
            date text NOT NULL,
            details text NOT NULL,
            created_at timestamptz DEFAULT NOW()
        );
        """)

        # Create recommendations table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            clientId uuid NOT NULL,
            title text NOT NULL,
            impact integer NOT NULL,
            details text NOT NULL,
            created_at timestamptz DEFAULT NOW()
        );
        """)

        # Create factors table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS factors (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            clientId uuid NOT NULL,
            name text NOT NULL,
            percentage integer NOT NULL,
            created_at timestamptz DEFAULT NOW()
        );
        """)

        await conn.close()
        logging.info("Database tables created successfully.")
    except Exception as e:
        logging.error(f"Error creating database tables: {str(e)}")
        logging.info("Application will continue without database connection. Some features may not work correctly.")