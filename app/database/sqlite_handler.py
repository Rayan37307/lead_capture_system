import aiosqlite
import os
import uuid
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.models.lead import LeadCreate, LeadUpdate
from app.constants.enums import LeadIntent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_DIR = "tenant_data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

def get_db_path(tenant_id: str) -> str:
    """Constructs the path to the tenant's database file."""
    return os.path.join(DB_DIR, f"{tenant_id}.db")

@asynccontextmanager
async def get_db_connection(tenant_id: str):
    """
    Ensures tables exist and provides an async database connection 
    as a context manager.
    """
    db_path = get_db_path(tenant_id)
    conn = None
    try:
        conn = await aiosqlite.connect(db_path)
        # Ensure tables exist on every connection. `IF NOT EXISTS` is cheap.
        await create_tables(conn)
        conn.row_factory = aiosqlite.Row
        yield conn
    except aiosqlite.Error as e:
        logger.error(f"Database error for tenant '{tenant_id}': {e}")
        raise
    finally:
        if conn:
            await conn.close()

async def create_tables(conn: aiosqlite.Connection):
    """Creates all necessary tables in the database."""
    # User Table
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        tenant_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        name TEXT,
        email TEXT,
        phone TEXT,
        source TEXT NOT NULL,
        intent TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        facebook_id TEXT UNIQUE
    );
    """)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (lead_id) REFERENCES leads (id) ON DELETE CASCADE
    );
    """)
    # Note: The products table is not included here as it was part of a separate plan.
    # If products are to be managed per-tenant in the same DB, the table creation
    # statement should be added here.
    
    await conn.commit()
    logger.info("Tables created or verified successfully.")

def _row_to_dict(row: aiosqlite.Row) -> Dict[str, Any]:
    """Converts a aiosqlite.Row object to a dictionary."""
    return dict(row) if row else None

async def fetch_lead_and_messages(conn: aiosqlite.Connection, lead_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a lead and its associated messages."""
    lead_row = await conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    lead = _row_to_dict(await lead_row.fetchone())
    if not lead:
        return None

    messages_cursor = await conn.execute("SELECT * FROM messages WHERE lead_id = ? ORDER BY timestamp ASC", (lead_id,))
    messages = [_row_to_dict(row) for row in await messages_cursor.fetchall()]
    lead['messages'] = messages
    return lead

async def create_lead(tenant_id: str, lead_data: LeadCreate) -> Dict[str, Any]:
    """Creates a new lead in the database."""
    async with get_db_connection(tenant_id) as conn:
        now = datetime.utcnow().isoformat()
        lead_id = str(uuid.uuid4())
        
        await conn.execute(
            """
            INSERT INTO leads (id, tenant_id, name, email, phone, source, intent, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lead_id, tenant_id, lead_data.name, lead_data.email, lead_data.phone,
                lead_data.source.value, lead_data.intent.value, now, now
            )
        )
        await conn.commit()
        
        logger.info(f"Successfully created lead {lead_id} for tenant {tenant_id}")
        return await fetch_lead_and_messages(conn, lead_id)

async def get_lead_by_id(tenant_id: str, lead_id: str) -> Optional[Dict[str, Any]]:
    """Gets a lead by its ID."""
    async with get_db_connection(tenant_id) as conn:
        return await fetch_lead_and_messages(conn, lead_id)

async def get_lead_by_facebook_id(tenant_id: str, facebook_id: str) -> Optional[Dict[str, Any]]:
    """Gets a lead by its Facebook ID."""
    async with get_db_connection(tenant_id) as conn:
        cursor = await conn.execute("SELECT id FROM leads WHERE facebook_id = ?", (facebook_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        return await fetch_lead_and_messages(conn, row['id'])

async def add_message_to_lead(tenant_id: str, lead_id: str, role: str, content: str) -> Optional[Dict[str, Any]]:
    """Adds a message to a lead's conversation history."""
    async with get_db_connection(tenant_id) as conn:
        now = datetime.utcnow().isoformat()
        
        # Add message
        await conn.execute(
            "INSERT INTO messages (lead_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (lead_id, role, content, now)
        )
        # Update lead's updated_at timestamp
        await conn.execute("UPDATE leads SET updated_at = ? WHERE id = ?", (now, lead_id))
        
        await conn.commit()
        return await fetch_lead_and_messages(conn, lead_id)

async def update_lead_intent(tenant_id: str, lead_id: str, intent: LeadIntent) -> Optional[Dict[str, Any]]:
    """Updates a lead's intent."""
    async with get_db_connection(tenant_id) as conn:
        now = datetime.utcnow().isoformat()
        await conn.execute(
            "UPDATE leads SET intent = ?, updated_at = ? WHERE id = ?",
            (intent.value, now, lead_id)
        )
        await conn.commit()
        return await fetch_lead_and_messages(conn, lead_id)

async def get_all_leads(tenant_id: str) -> List[Dict[str, Any]]:
    """Gets all leads for a tenant."""
    async with get_db_connection(tenant_id) as conn:
        leads_cursor = await conn.execute("SELECT id FROM leads WHERE tenant_id = ?", (tenant_id,))
        lead_ids = [row['id'] for row in await leads_cursor.fetchall()]
        
        leads = []
        for lead_id in lead_ids:
            lead = await fetch_lead_and_messages(conn, lead_id)
            if lead:
                leads.append(lead)
        return leads
# ... (existing functions) ...

# User Management Functions

async def create_user(tenant_id: str, email: str, hashed_password: str) -> Dict[str, Any]:
    """Creates a new user in the database."""
    async with get_db_connection(tenant_id) as conn:
        now = datetime.utcnow().isoformat()
        user_id = str(uuid.uuid4())
        
        await conn.execute(
            """
            INSERT INTO users (id, tenant_id, email, hashed_password, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, tenant_id, email, hashed_password, now, now)
        )
        await conn.commit()
        
        logger.info(f"Successfully created user {email} for tenant {tenant_id}")
        cursor = await conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return _row_to_dict(await cursor.fetchone())

async def get_user_by_email(tenant_id: str, email: str) -> Optional[Dict[str, Any]]:
    """Gets a user by their email."""
    async with get_db_connection(tenant_id) as conn:
        cursor = await conn.execute("SELECT * FROM users WHERE email = ? AND tenant_id = ?", (email, tenant_id))
        return _row_to_dict(await cursor.fetchone())
