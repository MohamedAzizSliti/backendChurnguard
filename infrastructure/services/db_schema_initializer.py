import os
import asyncpg

async def create_tables():
    db_url = os.getenv("SUPABASE_DB_URL")  # You need to set this in your .env
    if not db_url:
        raise ValueError("SUPABASE_DB_URL must be set in environment variables.")

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
    # Repeat for other tables: users, interactions, recommendations, factors
    await conn.close()