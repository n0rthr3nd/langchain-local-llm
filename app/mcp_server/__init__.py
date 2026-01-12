"""
MongoDB MCP Server
==================

Model Context Protocol server for MongoDB operations.
Provides tools for CRUD operations, queries, and aggregations.
"""

from .mongodb_mcp import MongoDBMCPServer

__all__ = ["MongoDBMCPServer"]
