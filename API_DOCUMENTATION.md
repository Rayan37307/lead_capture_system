# Lead Capture System API Documentation

## Overview

The Lead Capture System is a Python-based system built with FastAPI that enables capturing and automating leads from multiple channels (Website, WhatsApp, Instagram). It features an AI-powered assistant that can engage with users, track conversations, and classify leads by intent (hot, warm, cold).

## Base URL

The API is accessible at: `http://localhost:8000` (or your deployed domain)

All API endpoints are prefixed with `/api/v1`

## Authentication

Most endpoints require an API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

Or as a header:
```
X-API-Key: YOUR_API_KEY
```

## API Endpoints

### Chat Endpoints

#### POST `/api/v1/chat/respond`

Generate an AI response for a chat message.

**Request Body:**
```json
{
  "message": "User's message",
  "user_id": "Unique identifier for the user",
  "source": "website|whatsapp|instagram"
}
```

**Response:**
```json
{
  "response": "AI-generated response",
  "intent": "HOT|WARM|COLD|NEUTRAL",
  "follow_up": true
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/respond \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am interested in your product",
    "user_id": "web_user_12345",
    "source": "website"
  }'
```

### Lead Management Endpoints

#### POST `/api/v1/lead/`

Create a new lead.

**Request Body:**
```json
{
  "name": "Lead's name",
  "email": "lead@example.com",
  "phone": "+1234567890",
  "source": "website|whatsapp|instagram",
  "intent": "HOT|WARM|COLD"
}
```

**Response:**
```json
{
  "id": "lead_object_id",
  "name": "Lead's name",
  "email": "lead@example.com",
  "phone": "+1234567890",
  "source": "website",
  "intent": "COLD",
  "messages": [],
  "created_at": "2023-01-01T00:00:00.000Z",
  "updated_at": "2023-01-01T00:00:00.000Z"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/lead/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "name": "Test Lead",
    "email": "test@example.com",
    "phone": "+1234567890",
    "source": "website",
    "intent": "WARM"
  }'
```

#### GET `/api/v1/lead/{lead_id}`

Get a lead by ID.

**Response:**
```json
{
  "id": "lead_object_id",
  "name": "Lead's name",
  "email": "lead@example.com",
  "phone": "+1234567890",
  "source": "website",
  "intent": "HOT",
  "messages": [
    {
      "role": "user",
      "content": "I want to buy your product",
      "timestamp": "2023-01-01T00:00:00.000Z"
    },
    {
      "role": "assistant", 
      "content": "Great! Let me get your contact details",
      "timestamp": "2023-01-01T00:01:00.000Z"
    }
  ],
  "created_at": "2023-01-01T00:00:00.000Z",
  "updated_at": "2023-01-01T00:01:00.000Z"
}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/v1/lead/YOUR_LEAD_ID \
  -H "X-API-Key: YOUR_API_KEY"
```

### Webhook Endpoints

#### POST `/api/v1/webhook/whatsapp`

Handle incoming WhatsApp messages via webhook.

**Expected Payload:**
The payload format follows the WhatsApp Cloud API webhook format.

#### POST `/api/v1/webhook/instagram`

Handle incoming Instagram messages via webhook.

**Expected Payload:**
The payload format follows the Instagram Messaging API webhook format.

### Analytics Endpoints

#### GET `/api/v1/analytics/summary`

Get analytics summary for leads and conversations.

**Response:**
```json
{
  "total_conversations": 150,
  "leads_captured": 120,
  "hot_leads": 25,
  "warm_leads": 40,
  "cold_leads": 55,
  "avg_response_time": 12.5,
  "conversion_rate": 15.5
}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/v1/analytics/summary \
  -H "X-API-Key: YOUR_API_KEY"
```

### Health Check Endpoints

#### GET `/`

Root endpoint to check if the system is running.

**Response:**
```json
{
  "message": "AI Lead Capture & Automation System is running!"
}
```

**Example Request:**
```bash
curl http://localhost:8000/
```

#### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

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
# Database settings
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=lead_capture_db

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

# Notification settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAILS=recipient1@example.com,recipient2@example.com

# Security settings
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

## Integration Examples

### JavaScript/React Integration

```javascript
// Send a message to the chat API
async function sendMessage(message, userId) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/chat/respond', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        user_id: userId,
        source: 'website'
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending message:', error);
  }
}
```

### Python Integration

```python
import requests

def send_message(message, user_id):
    url = "http://localhost:8000/api/v1/chat/respond"
    payload = {
        "message": message,
        "user_id": user_id,
        "source": "website"
    }
    
    response = requests.post(url, json=payload)
    return response.json()
```

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing or invalid API key)
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
- Keep API keys secure and rotate them regularly
- Validate and sanitize all input data
- Implement proper webhook signature verification for external services