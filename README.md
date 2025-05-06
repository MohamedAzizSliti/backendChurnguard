# ChurnGuard API

A FastAPI backend application for managing customer churn, with user role management and a notes system.

## Features

- User authentication with JWT
- Role-based access control (Admin, Marketing Agent, Technical Agent)
- Client management
- Notes system for communication between different user roles
- Churn prediction and management

## Prerequisites

- Python 3.8+
- Supabase account for database

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `example.env`:
   ```bash
   cp example.env .env
   ```

4. Configure your Supabase credentials in the `.env` file:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-key
   SUPABASE_DB_URL=postgresql://postgres:your-db-password@your-db-host:5432/postgres
   ```

   You can find these values in your Supabase dashboard:
   - SUPABASE_URL: Project URL (Settings > API)
   - SUPABASE_KEY: Project API key (Settings > API > Project API keys > anon/public)
   - SUPABASE_DB_URL: Database connection string (Settings > Database > Connection string > URI)

## Running the application

Start the server:
```bash
python main.py
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Default Users

When the application starts for the first time, it creates the following default users:

1. Admin:
   - Email: admin@example.com
   - Password: adminpass
   - Role: Admin

2. Marketing Agent:
   - Email: marketing@example.com
   - Password: marketingpass
   - Role: Marketing Agent

3. Technical Agent:
   - Email: technical@example.com
   - Password: technicalpass
   - Role: Technical Agent

## Project Structure

- `main.py`: Application entry point
- `domain/`: Domain entities and repository interfaces
- `application/`: Application services and DTOs
- `infrastructure/`: Implementation of repositories and services
- `presentation/`: API endpoints and controllers

## Notes System

The notes system allows communication between different roles:
- Admins can send notes to any role
- Marketing and Technical agents can only send notes to Admins 