"""
MongoDB MCP Server
==================

MCP (Model Context Protocol) server implementation for MongoDB operations.
This server exposes MongoDB tools that can be used by LLM agents.
"""

from typing import Any, Dict, List
from .tools import MongoDBTools
from .config import config


class MongoDBMCPServer:
    """
    MCP Server for MongoDB operations.

    This server provides tools for interacting with MongoDB, including:
    - Query operations (find, find_one)
    - Insert operations (insert_one, insert_many)
    - Update operations (update_one, update_many)
    - Delete operations (delete_one, delete_many)
    - Aggregation pipelines
    - Collection management
    """

    def __init__(self):
        """Initialize the MongoDB MCP server."""
        self.tools = MongoDBTools()
        self.name = "mongodb"
        self.version = "1.0.0"
        self.description = "MongoDB MCP Server for database operations"

    def get_tools_metadata(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all available tools.

        Returns:
            List of tool metadata dictionaries
        """
        return [
            {
                "name": "mongodb_find",
                "description": "Find documents in a MongoDB collection with optional filtering, pagination, and projection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the MongoDB collection"
                        },
                        "filter_json": {
                            "type": "string",
                            "description": "JSON string for query filter (e.g., '{\"status\": \"active\"}'). Use '{}' for all documents.",
                            "default": "{}"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of documents to return",
                            "default": 10
                        },
                        "skip": {
                            "type": "integer",
                            "description": "Number of documents to skip",
                            "default": 0
                        },
                        "projection": {
                            "type": "string",
                            "description": "Optional projection fields (e.g., '{\"name\": 1, \"email\": 1}')",
                            "default": None
                        }
                    },
                    "required": ["collection"]
                }
            },
            {
                "name": "mongodb_find_one",
                "description": "Find a single document in a MongoDB collection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the MongoDB collection"
                        },
                        "filter_json": {
                            "type": "string",
                            "description": "JSON string for query filter"
                        },
                        "projection": {
                            "type": "string",
                            "description": "Optional projection fields",
                            "default": None
                        }
                    },
                    "required": ["collection", "filter_json"]
                }
            },
            {
                "name": "mongodb_insert",
                "description": "Insert a document into a MongoDB collection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the MongoDB collection"
                        },
                        "document_json": {
                            "type": "string",
                            "description": "JSON string of the document to insert"
                        }
                    },
                    "required": ["collection", "document_json"]
                }
            },
            {
                "name": "mongodb_insert_many",
                "description": "Insert multiple documents into a MongoDB collection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the MongoDB collection"
                        },
                        "documents_json": {
                            "type": "string",
                            "description": "JSON array string of documents to insert"
                        }
                    },
                    "required": ["collection", "documents_json"]
                }
            },
            {
                "name": "mongodb_update",
                "description": "Update documents in a MongoDB collection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the MongoDB collection"
                        },
                        "filter_json": {
                            "type": "string",
                            "description": "JSON string for query filter"
                        },
                        "update_json": {
                            "type": "string",
                            "description": "JSON string for update operations (e.g., '{\"$set\": {\"status\": \"done\"}}')"
                        },
                        "upsert": {
                            "type": "boolean",
                            "description": "Create document if not found",
                            "default": False
                        },
                        "update_many": {
                            "type": "boolean",
                            "description": "Update all matching documents (False = update one)",
                            "default": False
                        }
                    },
                    "required": ["collection", "filter_json", "update_json"]
                }
            },
            {
                "name": "mongodb_delete",
                "description": "Delete documents from a MongoDB collection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the MongoDB collection"
                        },
                        "filter_json": {
                            "type": "string",
                            "description": "JSON string for query filter"
                        },
                        "delete_many": {
                            "type": "boolean",
                            "description": "Delete all matching documents (False = delete one)",
                            "default": False
                        }
                    },
                    "required": ["collection", "filter_json"]
                }
            },
            {
                "name": "mongodb_aggregate",
                "description": "Run an aggregation pipeline on a MongoDB collection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the MongoDB collection"
                        },
                        "pipeline_json": {
                            "type": "string",
                            "description": "JSON array string of aggregation pipeline stages (e.g., '[{\"$match\": {\"status\": \"active\"}}, {\"$group\": {\"_id\": \"$category\", \"count\": {\"$sum\": 1}}}]')"
                        }
                    },
                    "required": ["collection", "pipeline_json"]
                }
            },
            {
                "name": "mongodb_list_collections",
                "description": "List all collections in the database",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "mongodb_count",
                "description": "Count documents in a collection matching a filter",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the MongoDB collection"
                        },
                        "filter_json": {
                            "type": "string",
                            "description": "JSON string for query filter. Use '{}' to count all documents.",
                            "default": "{}"
                        }
                    },
                    "required": ["collection"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """
        Execute a tool with given parameters.

        Args:
            tool_name: Name of the tool to execute
            parameters: Dictionary of parameters for the tool

        Returns:
            JSON string with tool execution results
        """
        tool_map = {
            "mongodb_find": self.tools.find_documents,
            "mongodb_find_one": self.tools.find_one_document,
            "mongodb_insert": self.tools.insert_document,
            "mongodb_insert_many": self.tools.insert_many_documents,
            "mongodb_update": self.tools.update_documents,
            "mongodb_delete": self.tools.delete_documents,
            "mongodb_aggregate": self.tools.aggregate,
            "mongodb_list_collections": self.tools.list_collections,
            "mongodb_count": self.tools.count_documents,
        }

        if tool_name not in tool_map:
            return f'{{"success": false, "error": "Unknown tool: {tool_name}"}}'

        try:
            tool_function = tool_map[tool_name]
            result = tool_function(**parameters)
            return result
        except Exception as e:
            return f'{{"success": false, "error": "Tool execution failed: {str(e)}"}}'

    def close(self):
        """Close MongoDB connections."""
        self.tools.disconnect()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience function for creating server instance
def create_mongodb_mcp_server() -> MongoDBMCPServer:
    """Create and return a MongoDB MCP server instance."""
    return MongoDBMCPServer()


# Example usage and testing
if __name__ == "__main__":
    import json

    print("=" * 60)
    print("MongoDB MCP Server Test")
    print("=" * 60)

    # Create server
    server = create_mongodb_mcp_server()

    print(f"\nServer: {server.name} v{server.version}")
    print(f"Description: {server.description}")
    print(f"\nAvailable tools: {len(server.get_tools_metadata())}")

    # List available tools
    print("\n" + "-" * 60)
    print("Available Tools:")
    print("-" * 60)
    for tool in server.get_tools_metadata():
        print(f"\n📦 {tool['name']}")
        print(f"   {tool['description']}")

    # Test connection and list collections
    print("\n" + "=" * 60)
    print("Testing MongoDB Connection")
    print("=" * 60)

    try:
        result = server.execute_tool("mongodb_list_collections", {})
        result_data = json.loads(result)

        if result_data.get("success"):
            print("✓ MongoDB connection successful!")
            print(f"\nDatabase: {result_data['database']}")
            print(f"Collections found: {result_data['count']}")
            if result_data['collections']:
                print("\nCollections:")
                for coll in result_data['collections']:
                    print(f"  - {coll}")
        else:
            print(f"✗ Connection failed: {result_data.get('error')}")

    except Exception as e:
        print(f"✗ Error testing connection: {e}")

    finally:
        server.close()

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)
