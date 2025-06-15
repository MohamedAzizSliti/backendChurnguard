# ChurnGuard API

A FastAPI backend application for managing customer churn, with user role management and a comprehensive notes system.

## Features

- **Authentication & Authorization**

  - JWT-based authentication
  - Role-based access control
  - Secure password hashing with bcrypt

- **User Role Management**

  - Three distinct roles: Admin, Marketing Agent, Technical Agent
  - Role-specific permissions and access controls

- **Notes System**

  - Role-based messaging system
  - Admins can send notes to any role
  - Marketing and Technical agents can only send notes to Admins
  - Read status tracking for notes

- **Client Management**

  - Track client details and churn risk
  - Record client interactions and contact history
  - Manage client-specific churn factors

- **Reports & Analytics**
  - Churn trends visualization
  - Segment-based churn analysis
  - Churn factor identification
  - Retention action recommendations

## Prerequisites

- Python 3.8+
- Supabase account for database storage
- PostgreSQL knowledge for advanced database management

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
   SUPABASE_DB_URL=postgresql://postgres:your-db-password@db.your-project-ref.supabase.co:5432/postgres
   ```

   You can find these values in your Supabase dashboard:

   - SUPABASE_URL: Project URL (Settings > API)
   - SUPABASE_KEY: Project API key (Settings > API > Project API keys > anon/public)
   - SUPABASE_DB_URL: Database connection string (Settings > Database > Connection string > URI)

## Database Setup

If the automatic database setup fails, you can manually create the required tables:

1. Open your Supabase dashboard
2. Go to the "SQL Editor" section
3. Create a new query
4. Paste the following SQL commands:

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text UNIQUE NOT NULL,
    full_name text NOT NULL,
    role text NOT NULL,
    password text NOT NULL,
    created_at timestamptz NOT NULL,
    updated_at timestamptz
);

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title text NOT NULL,
    description text NOT NULL,
    sender_id uuid NOT NULL,
    recipients text[] NOT NULL,
    is_read boolean DEFAULT FALSE,
    timestamp timestamptz NOT NULL
);

-- Create clients table
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

-- Create email_notifications table
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

-- Create customer_issues table
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

-- Create customer_incident_predictions table
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

-- Create interactions table
CREATE TABLE IF NOT EXISTS interactions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    clientId uuid NOT NULL,
    type text NOT NULL,
    date text NOT NULL,
    details text NOT NULL,
    created_at timestamptz DEFAULT NOW()
);

-- Create recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    clientId uuid NOT NULL,
    title text NOT NULL,
    impact integer NOT NULL,
    details text NOT NULL,
    created_at timestamptz DEFAULT NOW()
);

-- Create factors table
CREATE TABLE IF NOT EXISTS factors (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    clientId uuid NOT NULL,
    name text NOT NULL,
    percentage integer NOT NULL,
    created_at timestamptz DEFAULT NOW()
);

-- Create sample users with different roles
INSERT INTO users (email, full_name, role, password, created_at)
VALUES
    ('admin@example.com', 'Admin User', 'admin', '$2b$12$1mE7KFkbqcCwZKOV8Q4jYuVRYGyrn8jmKzWtAxW.f2ksH0tuo/aSG', NOW()),
    ('marketing@example.com', 'Marketing Agent', 'marketing_agent', '$2b$12$M3L44ZLkDlQZWNY9eQVkDeHaZZg.vNyTSgO1wy8nNdYjnOXk0p2m6', NOW()),
    ('technical@example.com', 'Technical Agent', 'technical_agent', '$2b$12$D.71gTCuj0uMmGNVvdz5te96TPAX.Bm62YZq0K1QCWsVpuTUEQBdS', NOW());
```

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

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user profile

### Notes System

- `POST /notes/` - Create a new note
  ```json
  {
    "title": "Note Title",
    "description": "Note content/message",
    "recipients": ["admin", "marketing_agent", "technical_agent"]
  }
  ```
- `GET /notes/inbox` - Get notes received by the current user's role
- `GET /notes/sent` - Get notes sent by the current user
- `GET /notes/{note_id}` - Get details of a specific note
- `POST /notes/{note_id}/read` - Mark a note as read

### Clients

- `GET /clients/` - Get all clients
- `POST /clients/` - Create a new client
- `GET /clients/{client_id}` - Get client by ID
- `PUT /clients/{client_id}` - Update a client
- `GET /clients/{client_id}/detail` - Get detailed client information

### Reports

- `GET /reports/churn-trends` - Get churn trend data
- `GET /reports/churn-by-segment` - Get churn data by segment
- `GET /reports/churn-factors` - Get churn factors data
- `GET /reports/retention-actions` - Get retention actions data

## Notes System Details

The notes system allows communication between different roles with specific permissions:

### Permissions

- **Admin Role**:

  - Can send notes to any role (Admin, Marketing Agent, Technical Agent)
  - Can read notes sent to the Admin role

- **Marketing Agent Role**:

  - Can only send notes to Admins
  - Can read notes sent to the Marketing Agent role

- **Technical Agent Role**:
  - Can only send notes to Admins
  - Can read notes sent to the Technical Agent role

### How Notes Work

1. **Role-Based Delivery**:

   - Notes are sent to roles (Admin, Marketing Agent, Technical Agent)
   - All users with that role will see the note
   - Good for announcements or messages meant for entire departments

2. **Read Status**:
   - Notes can be marked as read
   - Read status is tracked per note, not per user

### Example Workflows

1. **Admin to Marketing Team**:

   - Admin creates a note with recipients = ["marketing_agent"]
   - All Marketing Agents will see this note in their inbox

2. **Technical Agent to Admin**:

   - Technical Agent creates a note with recipients = ["admin"]
   - All Admins will see this note in their inbox

3. **Restricted Communication**:
   - If a Marketing Agent tries to send a note to Technical Agents, they will receive a 403 Forbidden error
   - Communication between non-admin roles must go through Admins

## Making Notes Real-Time (Future Enhancement)

To make the notes system real-time, the following enhancements could be implemented:

### 1. WebSocket Integration

- Add WebSocket endpoints for real-time notifications
- Create a connection manager to handle client connections
- Send instant notifications when new notes are created

### 2. Client-Side Implementation

- Connect to WebSocket endpoint with authentication token
- Listen for new note notifications
- Update UI immediately when new notes arrive

### 3. Notification Features

- Real-time unread count updates
- Desktop notifications for new notes
- Sound alerts for important messages

## Project Structure

- `main.py`: Application entry point
- `domain/`: Domain entities and repository interfaces
- `application/`: Application services and DTOs
- `infrastructure/`: Implementation of repositories and services
- `presentation/`: API endpoints and controllers

## Architecture

The application follows a clean architecture pattern:

1. **Domain Layer** (Innermost)

   - Contains business entities, value objects, and repository interfaces
   - No dependencies on outer layers

2. **Application Layer**

   - Contains application services and DTOs
   - Orchestrates domain objects to perform use cases
   - Depends only on the domain layer

3. **Infrastructure Layer**

   - Implements repository interfaces from the domain layer
   - Contains database access code, external service integrations
   - Depends on domain and application layers

4. **Presentation Layer** (Outermost)
   - Contains API endpoints, controllers, and request/response models
   - Depends on all inner layers

This architecture allows for separation of concerns and makes the codebase more maintainable and testable.

## Error Handling

The application includes robust error handling:

- Detailed error messages with appropriate HTTP status codes
- Exception middleware for catching unhandled exceptions
- Graceful handling of database connection issues
- Comprehensive logging for debugging

## Future Enhancements

- WebSocket integration for real-time notes
- Mobile application support
- Enhanced analytics and reporting
- AI-powered churn prediction
- Multi-language support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
