from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_DB_URI

from ..logging import LOGGER

LOGGER(__name__).info("Connecting to your Mongo Database...")
try:
    _mongo_async_ = AsyncIOMotorClient(
        MONGO_DB_URI,
        maxPoolSize=50,
        minPoolSize=10,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=20000,
    )
    mongodb = _mongo_async_.Anon
    # Test connection
    _mongo_async_.admin.command('ping')
    LOGGER(__name__).info("Connected to your Mongo Database.")
except Exception as e:
    LOGGER(__name__).error(f"Failed to connect to your Mongo Database: {e}")
    exit()
