# Lead Capture System API Documentation

## Overview

The Lead Capture System is a Python-based system built with FastAPI that enables capturing and automating leads from multiple channels (Website, WhatsApp, Instagram). It features an AI-powered assistant that can engage with users, track conversations, and classify leads by intent (hot, warm, cold). It now supports multi-tenancy, allowing for secure data isolation between different clients, leveraging **SQLite** as its database technology.

## Base URL

The API is accessible at: `http://localhost:8000` (or your deployed domain)

All API endpoints are prefixed with `/api/v1`

## Authentication

Most endpoints (Lead Management, Analytics) require **JWT Bearer Token** authentication.

1.  **Register a User:** First, register a new user with their associated `tenant_id`.
    *   **Endpoint:** `POST /api/v1/auth/register`
    *   **Example Request:**
        ```bash
        curl -X POST http://localhost:8000/api/v1/auth/register \
          -H "Content-Type: application/json" \
          -d '{"email": "user@example.com", "password": "securepassword", "tenant_id": "YOUR_TENANT_ID"}'
        ```

2.  **Log In and Get Token:** Use the registered credentials to obtain a JWT access token. **Note: `tenant_id` is now required for login.**
    *   **Endpoint:** `POST /api/v1/auth/token`
    *   **Example Request:**
        ```bash
        curl -X POST http://localhost:8000/api/v1/auth/token \
          -H "Content-Type: application/x-www-form-urlencoded" \
          -d "username=user@example.com&password=securepassword&tenant_id=YOUR_TENANT_ID"
        ```

Once you have the `access_token`, include it in the `Authorization` header for protected endpoints:

```
Authorization: Bearer YOUR_JWT_ACCESS_TOKEN
```

### Unauthenticated Endpoints (Tenant ID in Payload/Path)

Some public-facing endpoints (Chat, Webhooks) do not require JWT authentication but still operate within the context of a `tenant_id`, which must be provided in the request payload or as a path parameter.

## API Endpoints

### Authentication Endpoints

#### POST `/api/v1/auth/register`
Register a new user associated with a tenant.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "tenant_id": "YOUR_TENANT_ID_HERE"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword", "tenant_id": "YOUR_TENANT_ID_HERE"}'
```

#### POST `/api/v1/auth/token`
Obtain a JWT access token for an existing user.

**Request Body (x-www-form-urlencoded):**
```
username=user@example.com&password=securepassword&tenant_id=YOUR_TENANT_ID
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword&tenant_id=YOUR_TENANT_ID"
```

### Chat Endpoints

#### POST `/api/v1/chat/respond`

Generate an AI response for a chat message. Requires `tenant_id` in the request body.

**Request Body:**
```json
{
  "message": "User's message",
  "user_id": "Unique identifier for the user (e.g., phone number, web session ID)",
  "source": "website|whatsapp|instagram",
  "tenant_id": "YOUR_TENANT_ID"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/respond \
  -H "Content-Type: application/json" \
  -d '{"message": "I am interested in your product", "user_id": "web_user_12345", "source": "website", "tenant_id": "YOUR_TENANT_ID_HERE"}'
```

### Lead Management Endpoints

All Lead Management endpoints require JWT authentication.

#### POST `/api/v1/lead/`

Create a new lead. The `tenant_id` in the payload must match the authenticated user's `tenant_id`.

**Request Body:**
```json
{
  "name": "Lead's name",
  "email": "lead@example.com",
  "phone": "+1234567890",
  "source": "website|whatsapp|instagram",
  "intent": "HOT|WARM|COLD",
  "tenant_id": "YOUR_TENANT_ID"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/lead/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"name": "Test Lead", "email": "test@example.com", "phone": "+1234567890", "source": "website", "intent": "WARM", "tenant_id": "YOUR_TENANT_ID_HERE"}'
```

#### GET `/api/v1/lead/{lead_id}`

Get a lead by ID. Requires JWT authentication. Only retrieves leads belonging to the authenticated user\'s `tenant_id`.

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/v1/lead/YOUR_LEAD_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### GET `/api/v1/lead/`

Get all leads for the authenticated user\'s `tenant_id`. Requires JWT authentication.

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/v1/lead/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### GET `/api/v1/lead/source/{source}`

Get leads by source for the authenticated user\'s `tenant_id`. Requires JWT authentication.

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/v1/lead/source/website \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### GET `/api/v1/lead/intent/{intent}`

Get leads by intent for the authenticated user\'s `tenant_id`. Requires JWT authentication.

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/v1/lead/intent/HOT \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Webhook Endpoints

Webhook endpoints now include a `tenant_id` path parameter to associate incoming events with a specific tenant.

#### POST `/api/v1/webhook/whatsapp/{tenant_id}`

Handle incoming WhatsApp messages via webhook for a specific tenant.

**Example Request:**
```bash
# The payload is defined by WhatsApp Cloud API
curl -X POST http://localhost:8000/api/v1/webhook/whatsapp/YOUR_TENANT_ID \
  -H "Content-Type: application/json" \
  -d '{"object":"whatsapp_business_account","entry":[...] }'
```

#### GET `/api/v1/webhook/whatsapp/{tenant_id}`

Verify WhatsApp webhook for a specific tenant.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/webhook/whatsapp/YOUR_TENANT_ID?hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=CHALLENGE_STRING"
```

#### POST `/api/v1/webhook/instagram/{tenant_id}`

Handle incoming Instagram messages via webhook for a specific tenant.

**Example Request:**
```bash
# The payload is defined by Instagram Messaging API
curl -X POST http://localhost:8000/api/v1/webhook/instagram/YOUR_TENANT_ID \
  -H "Content-Type: application/json" \
  -d '{"object":"instagram","entry":[...] }'
```

#### GET `/api/v1/webhook/instagram/{tenant_id}`

Verify Instagram webhook for a specific tenant.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/webhook/instagram/YOUR_TENANT_ID?hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=CHALLENGE_STRING"
```

#### POST `/api/v1/messenger/{tenant_id}`

Handle incoming Facebook Messenger messages via webhook for a specific tenant.

**Example Request:**
```bash
# The payload is defined by Facebook Messenger API
curl -X POST http://localhost:8000/api/v1/messenger/YOUR_TENANT_ID \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature: sha1=signature_hash" \
  -d '{"object":"page","entry":[...] }'
```

#### GET `/api/v1/messenger/{tenant_id}`

Verify Facebook Messenger webhook for a specific tenant.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/messenger/YOUR_TENANT_ID?hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=CHALLENGE_STRING"
```

### Analytics Endpoints

All Analytics endpoints require JWT authentication.

#### GET `/api/v1/analytics/summary`

Get analytics summary for leads and conversations belonging to the authenticated user\'s `tenant_id`.

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/v1/analytics/summary \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### GET `/api/v1/analytics/detailed`
Get detailed analytics for the authenticated user\'s `tenant_id`. Requires JWT authentication.

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/v1/analytics/detailed \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Health Check Endpoints

#### GET `/`

Root endpoint to check if the system is running.

**Example Request:**
```bash
curl http://localhost:8000/
```

#### GET `/health`

Health check endpoint.

**Example Request:**
```bash
curl http://localhost:8000/health
```

## Data Models

### Lead Source Enum
- `website`
- `whatsapp`
- `instagram`

### Lead Intent Enum
- `HOT` - High purchase intent
- `WARM` - Medium purchase intent
- `COLD` - Low purchase intent

### Message Model
```json
{
  "role": "user|assistant",
  "content": "Message content",
  "timestamp": "2023-01-01T00:00:00.000Z"
}
```

## Environment Variables

The system requires the following environment variables:

```env
# AI settings
AI_PROVIDER=gemini  # openai, openrouter, gemini
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
AI_MODEL=gemini-2.5-flash

# WhatsApp settings
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_verify_token
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Instagram settings
INSTAGRAM_WEBHOOK_VERIFY_TOKEN=your_verify_token
INSTAGRAM_ACCESS_TOKEN=your_access_token

# Facebook Messenger settings
FB_PAGE_ACCESS_TOKEN=your_page_access_token
FB_APP_SECRET=your_app_secret
FB_WEBHOOK_VERIFY_TOKEN=your_verify_token

# Notification settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAILS=recipient1@example.com,recipient2@example.com

# Security settings
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30 # Minutes until access token expires
```

## Integration Examples

### JavaScript/React Integration

**1. Register User & Get Token**
```javascript
async function registerUser(email, password, tenantId) {
  const response = await fetch('http://localhost:8000/api/v1/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, tenant_id: tenantId })
  });
  return response.json();
}

async function loginUser(email, password, tenantId) { // tenantId added
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);
  params.append('tenant_id', tenantId); // tenant_id added

  const response = await fetch('http://localhost:8000/api/v1/auth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString()
  });
  return response.json(); // Returns {access_token: "...", token_type: "bearer"}
}
```

**2. Send a Chat Message (Tenant-aware)**
```javascript
// This function does NOT require a JWT, but DOES require tenant_id in payload
async function sendChatMessage(message, userId, tenantId) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/chat/respond', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        user_id: userId,
        source: 'website',
        tenant_id: tenantId // Include tenant_id here
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending message:', error);
  }
}
```

**3. Access Protected Lead Data (Authenticated)**
```javascript
async function getLeads(accessToken) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/lead/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`, // Use the access token
      }
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching leads:', error);
  }
}
```

### Python Integration

**1. Register User & Get Token**
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

def register_user(email, password, tenant_id):
    url = f"{BASE_URL}/auth/register"
    payload = {
        "email": email,
        "password": password,
        "tenant_id": tenant_id
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

def login_user(email, password, tenant_id): # tenant_id added
    url = f"{BASE_URL}/auth/token"
    payload = {
        "username": email,
        "password": password,
        "tenant_id": tenant_id # tenant_id added
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json() # Returns {{'access_token': '...', 'token_type': 'bearer'}}
```

**2. Send a Chat Message (Tenant-aware)**
```python
# This function does NOT require a JWT, but DOES require tenant_id in payload
def send_chat_message(message, user_id, tenant_id):
    url = f"{BASE_URL}/chat/respond"
    payload = {
        "message": message,
        "user_id": user_id,
        "source": "website",
        "tenant_id": tenant_id # Include tenant_id here
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()
```

**3. Access Protected Lead Data (Authenticated)**
```python
def create_lead_authenticated(access_token, name, email, phone, source, intent, tenant_id):
    url = f"{BASE_URL}/lead/"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "name": name,
        "email": email,
        "phone": phone,
        "source": source,
        "intent": intent,
        "tenant_id": tenant_id
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def get_leads_authenticated(access_token):
    url = f"{BASE_URL}/lead/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
```

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing or invalid JWT token)
- `403` - Forbidden (access denied to resource)
- `404` - Not Found
- `500` - Internal Server Error

Error responses include a detail field:
```json
{
  "detail": "Error description"
}
```

## Deployment

The system can be deployed using Docker:

```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`.

## Rate Limiting

The API does not currently implement rate limiting. Consider implementing rate limiting at the reverse proxy level if needed.

## Security Considerations

- Always use HTTPS in production
- Keep `SECRET_KEY` and other sensitive environment variables secure
- Validate and sanitize all input data
- Implement proper webhook signature verification for external services
