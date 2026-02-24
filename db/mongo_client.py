"""
MongoDB client singleton for the Dynamic Agent Creator system.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None


def get_client():
    """Get or create the MongoDB client singleton."""
    global _client
    if _client is None:
        from core.config import Config
        uri = Config.MONGO_URI
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client


def get_db():
    """Get the application database."""
    global _db
    if _db is None:
        from core.config import Config
        db_name = Config.MONGO_DB_NAME
        _db = get_client()[db_name]
    return _db


def check_connection():
    """Verify MongoDB is reachable. Returns True/False."""
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False
