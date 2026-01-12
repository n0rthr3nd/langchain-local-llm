"""
MongoDB MCP Configuration
=========================

Configuration management for MongoDB MCP server.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class MongoDBConfig:
    """Configuration for MongoDB connection."""

    def __init__(self):
        self.mongodb_uri: str = os.getenv(
            "MONGODB_URI",
            "mongodb://mongodb:27017"
        )
        self.mongodb_database: str = os.getenv(
            "MONGODB_DATABASE",
            "langchain_db"
        )
        self.mongodb_timeout: int = int(os.getenv(
            "MONGODB_TIMEOUT",
            "5000"
        ))
        self.mongodb_max_pool_size: int = int(os.getenv(
            "MONGODB_MAX_POOL_SIZE",
            "10"
        ))

    def get_connection_params(self) -> dict:
        """Get MongoDB connection parameters."""
        return {
            "host": self.mongodb_uri,
            "serverSelectionTimeoutMS": self.mongodb_timeout,
            "maxPoolSize": self.mongodb_max_pool_size,
        }

    @property
    def database_name(self) -> str:
        """Get the database name."""
        return self.mongodb_database


# Global configuration instance
config = MongoDBConfig()
