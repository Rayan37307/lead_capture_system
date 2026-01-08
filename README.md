# AI Lead Capture & Automation System

A Python-based system for capturing and automating leads from multiple channels (Website, WhatsApp, Instagram, Facebook Messenger).

## Features

- AI-powered lead capture bot
- Multi-channel support (Website, WhatsApp, Instagram, Facebook Messenger)
- Lead storage in MongoDB with optional Google Sheets sync
- Instant notifications via email and WhatsApp
- Custom Python workflow engine (replacing n8n)
- 30-day performance tracking
- **Multi-Tenant Architecture:** Supports data isolation for multiple clients using JWT authentication.

## Tech Stack

- **Backend**: Python (FastAPI)
- **AI**: OpenAI / OpenRouter / Gemini (pluggable provider)
- **Database**: MongoDB
- **Messaging**: WhatsApp Cloud API, Instagram Messaging API, Facebook Messenger API
- **Email**: SMTP (Gmail / Resend / SendGrid)
- **Queue/Task**: BackgroundTasks
- **Auth**: JWT based (OAuth2)
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
- `API_KEY`: API key for legacy integrations (consider deprecating for JWT)
- `SECRET_KEY`: **CRITICAL** Secret key for JWT token signing. Must be a strong, random string.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Minutes until JWT access token expires (e.g., 30)

## API Endpoints

All API endpoints (except chat interactions from unauthenticated webhooks) now require JWT authentication. See `API_DOCUMENTATION.md` for full details on authentication flow.

### Authentication
- `POST /auth/register` - Register a new user with a tenant ID
- `POST /auth/token` - Get JWT access token

### Webhooks (tenant_id in path)
- `POST /webhook/whatsapp/{tenant_id}` - WhatsApp messages
- `GET /webhook/whatsapp/{tenant_id}` - WhatsApp webhook verification
- `POST /webhook/instagram/{tenant_id}` - Instagram messages
- `GET /webhook/instagram/{tenant_id}` - Instagram webhook verification
- `POST /messenger/{tenant_id}` - Facebook Messenger messages
- `GET /messenger/{tenant_id}` - Facebook Messenger webhook verification

### Chat
- `POST /chat/respond` - Get AI response for chat messages (requires `tenant_id` in payload)

### Leads (JWT Protected)
- `POST /lead/` - Create a new lead (requires `tenant_id` in payload)
- `GET /lead/{lead_id}` - Get a specific lead
- `GET /lead/` - Get all leads
- `GET /lead/source/{source}` - Get leads by source
- `GET /lead/intent/{intent}` - Get leads by intent

### Analytics (JWT Protected)
- `GET /analytics/summary` - Get analytics summary
- `GET /analytics/detailed` - Get detailed analytics

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

- JWT-based authentication
- Webhook signature verification (still relevant for external services)
- Environment-based secrets
- **Multi-tenancy:** Data isolation per tenant.

## Deployment and Integration

This guide will walk you through deploying the lead capture system on your own server and integrating the chat widget into your website.

### 1. Server Setup & Deployment

The entire application is packaged using Docker, so you don't need to install Python or MongoDB manually. All you need is a server with Docker installed.

**Step 1: Install Docker**
Ensure your server has both Docker and Docker Compose installed. You can find official installation instructions here:
- [Install Docker Engine](https://docs.docker.com/engine/install/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

**Step 2: Configure Your Environment**
The project requires API keys and settings to function.
1.  In the project's root directory, copy the example configuration file:
    `cp .env.example .env`
2.  Open the `.env` file with a text editor and fill in your actual credentials for OpenAI, Twilio, Google Sheets, `SECRET_KEY` and any other required settings.

**Step 3: Launch the Application**
From the root project directory, run the following command:
`docker-compose up -d`

That's it! Docker will now download the necessary images and start the application and database in the background. The API will be available at `http://your-server-ip:8000`.

### 2. Website Integration

Follow these steps to add the chat widget to your website.

**Step 1: Obtain `tenant_id`**
You will need your unique `tenant_id` to configure the chat widget. If you are using the admin panel (to be developed), you can find it there. Otherwise, you may generate one manually (e.g., using `from bson import ObjectId; print(str(ObjectId()))` in Python).

**Step 2: Configure the Widget**
1.  Create the `ChatWidget.js` and `ChatWidget.css` files (as provided by your agent) in your React project, for example, in `src/components/`.
2.  Open the `ChatWidget.js` file and near the top, find the line `const BACKEND_URL = 'http://localhost:8000';`.
3.  Change `http://localhost:8000` to the public URL of your deployed backend server (e.g., `'http://YOUR_SERVER_IP:8000'`).
4.  Also in `ChatWidget.js`, you'll need to define your `tenant_id` to be used in chat requests: `const TENANT_ID = "YOUR_TENANT_ID";`.

**Step 3: Embed the Component**
Import and render the `ChatWidget` component in your main React application file (e.g., `App.js`) where you want the chat widget to appear.

```javascript
// App.js or your main layout file
import ChatWidget from './components/ChatWidget'; // Adjust path if needed
import './components/ChatWidget.css'; // Adjust path if needed

function App() {
  return (
    <div className="App">
      {/* Your other app content */}
      <ChatWidget />
    </div>
  );
}
export default App;
```
For more detailed integration examples, refer to `API_DOCUMENTATION.md`.