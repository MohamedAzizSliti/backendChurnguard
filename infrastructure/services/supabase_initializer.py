# Supabase initializer for the project
from supabase import create_client, Client
import os
import logging

def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        error_msg = "SUPABASE_URL and SUPABASE_KEY must be set in environment variables."
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        client = create_client(url, key)
        logging.info("Supabase client initialized successfully")
        return client
    except Exception as e:
        error_msg = f"Failed to initialize Supabase client: {str(e)}"
        logging.error(error_msg)
        raise ValueError(error_msg)
