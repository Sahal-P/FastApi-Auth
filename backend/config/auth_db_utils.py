from motor.motor_asyncio import AsyncIOMotorClient
from .db import db_auth

async def connect_to_mongo():
	db_auth.client = AsyncIOMotorClient('mongodb://127.0.0.1:27017/')

async def close_mongo_connection():
	db_auth.client.close()