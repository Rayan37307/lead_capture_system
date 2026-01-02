from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

# Global variable to hold the database client
client: AsyncIOMotorClient = None
database = None


async def get_database():
    """Return the database instance"""
    return database


async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, database
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.MONGODB_DB_NAME]


async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()