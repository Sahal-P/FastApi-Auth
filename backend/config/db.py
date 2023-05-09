from pymongo import MongoClient

connection = MongoClient()
db=connection['Auth']
# mongodb://127.0.0.1:27017

async def get_connection() -> MongoClient:
    return connection['Auth']


from motor.motor_asyncio import AsyncIOMotorClient


class DataBase:
	client: AsyncIOMotorClient = None


db_auth = DataBase()

async def get_database() -> AsyncIOMotorClient:
	return db_auth.client['Auth']