# AI Lead Capture & Automation System

A Python-based system for capturing and automating leads from multiple channels (Website, WhatsApp, Instagram).

## Features

- AI-powered lead capture bot
- Multi-channel support (Website, WhatsApp, Instagram)
- Lead storage in MongoDB with optional Google Sheets sync
- Instant notifications via email and WhatsApp
- Custom Python workflow engine (replacing n8n)
- 30-day performance tracking

## Tech Stack

- **Backend**: Python (FastAPI)
- **AI**: OpenAI / OpenRouter / Gemini (pluggable provider)
- **Database**: MongoDB
- **Messaging**: WhatsApp Cloud API, Instagram Messaging API
- **Email**: SMTP (Gmail / Resend / SendGrid)
- **Queue/Task**: BackgroundTasks
- **Auth**: API key based
- **Deployment**: Docker + VPS

## Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- MongoDB (if running locally without Docker)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd lead_capture_system
   ```

2. Copy the environment file and update the values:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Build and run the application:
   ```bash
   docker-compose up -d
   ```

4. The API will be available at `http://localhost:8000`

### Environment Variables

- `MONGODB_URL`: MongoDB connection string
- `OPENAI_API_KEY`: Your OpenAI API key
- `WHATSAPP_*`: WhatsApp Business API credentials
- `INSTAGRAM_*`: Instagram API credentials
- `SMTP_*`: Email server configuration
- `API_KEY`: API key for authentication
- `SECRET_KEY`: Secret key for security

## API Endpoints

### Webhooks
- `POST /webhook/website` - Website chat messages
- `POST /webhook/whatsapp` - WhatsApp messages
- `POST /webhook/instagram` - Instagram messages

### Chat
- `POST /chat/respond` - Get AI response for chat messages

### Leads
- `POST /lead/` - Create a new lead
- `GET /lead/{lead_id}` - Get a specific lead
- `GET /lead/` - Get all leads
- `GET /lead/source/{source}` - Get leads by source
- `GET /lead/intent/{intent}` - Get leads by intent

### Analytics
- `GET /analytics/summary` - Get analytics summary

## Architecture

The system follows a clean architecture pattern:

- `app/` - Main application code
- `app/api/` - API routes and endpoints
- `app/models/` - Data models
- `app/schemas/` - Pydantic schemas
- `app/services/` - Business logic services
- `app/database/` - Database connection and models
- `app/utils/` - Utility functions
- `app/constants/` - Constants and enums

## Workflow Engine

The system includes a custom Python workflow engine that replaces n8n:

- Event-driven triggers (on_new_message, on_lead_created, on_hot_lead)
- Each trigger executes AI processing, DB writes, and notifications
- Extensible with custom handlers

## Security

- Webhook signature verification
- API key authentication
- Rate limiting
- Environment-based secrets

## Deployment

The application is designed for Docker deployment on a VPS:

1. Update the `docker-compose.yml` with your domain and SSL settings
2. Configure SSL certificates
3. Deploy using `docker-compose up -d`

## Next.js Frontend

The system is designed to work with a Next.js landing page that captures leads and sends them to the backend API.