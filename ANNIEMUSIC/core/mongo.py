from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_DB_URI

from ..logging import LOGGER

LOGGER(__name__).info("Connecting to your Mongo Database...")
try:
    _mongo_async_ = AsyncIOMotorClient(
        MONGO_DB_URI,
        maxPoolSize=100,  # Increased from 50 for faster DB access
        minPoolSize=20,   # Increased from 10
        serverSelectionTimeoutMS=3000,  # Reduced from 5000 for quicker fail
        connectTimeoutMS=5000,          # Reduced from 10000
        socketTimeoutMS=10000,          # Reduced from 20000
        retryWrites=True,
        retryReads=True,
    )
    mongodb = _mongo_async_.Anon
    # Test connection
    _mongo_async_.admin.command('ping')
    LOGGER(__name__).info("Connected to your Mongo Database.")
except Exception as e:
    LOGGER(__name__).error(f"Failed to connect to your Mongo Database: {e}")
    exit()
