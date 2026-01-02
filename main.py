import uvicorn
from fastapi import FastAPI
from app.main import app
from app.database.mongodb import connect_to_mongo, close_mongo_connection


@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)