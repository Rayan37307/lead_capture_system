from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import webhook, chat, lead, analytics, auth, messenger # Import auth and messenger routers
from app.config.settings import settings


app = FastAPI(
    title="AI Lead Capture & Automation System",
    description="Python-based system for capturing and automating leads from multiple channels",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(webhook.router, prefix=settings.API_V1_STR + "/webhook", tags=["webhook"])
app.include_router(chat.router, prefix=settings.API_V1_STR + "/chat", tags=["chat"])
app.include_router(lead.router, prefix=settings.API_V1_STR + "/lead", tags=["lead"])
app.include_router(analytics.router, prefix=settings.API_V1_STR + "/analytics", tags=["analytics"])
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["auth"]) # Add auth router
app.include_router(messenger.router, prefix=settings.API_V1_STR + "/messenger", tags=["messenger"]) # Add messenger router

@app.get("/")
async def root():
    return {"message": "AI Lead Capture & Automation System is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}