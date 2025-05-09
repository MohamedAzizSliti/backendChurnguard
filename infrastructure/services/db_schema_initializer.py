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
        
        # Example for clients table, repeat for others as needed
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            email text,
            full_name text,
            created_at timestamptz,
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
        
        # Repeat for other tables: interactions, recommendations, factors
        await conn.close()
        logging.info("Database tables created successfully.")
    except Exception as e:
        logging.error(f"Error creating database tables: {str(e)}")
        logging.info("Application will continue without database connection. Some features may not work correctly.")