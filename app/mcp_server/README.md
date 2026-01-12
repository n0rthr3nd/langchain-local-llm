# MongoDB MCP Server

Model Context Protocol (MCP) server for MongoDB operations. This server provides tools that allow LLM agents to interact with MongoDB databases.

## Features

- **Query Operations**: Find documents with filters, pagination, and projections
- **Insert Operations**: Insert single or multiple documents
- **Update Operations**: Update one or multiple documents with upsert support
- **Delete Operations**: Delete one or multiple documents
- **Aggregation Pipelines**: Execute complex aggregation queries
- **Collection Management**: List collections and count documents
- **Connection Pooling**: Efficient connection management
- **Error Handling**: Comprehensive error handling and reporting

## Architecture

```
app/mcp_server/
├── __init__.py          # Package initialization
├── config.py            # Configuration management
├── tools.py             # MongoDB operation tools
├── mongodb_mcp.py       # Main MCP server implementation
├── example_usage.py     # Usage examples
└── README.md            # This file
```

## Installation

The MongoDB MCP dependencies are already included in the project's `requirements.txt`:

```bash
# From project root
pip install -r requirements.txt
```

## Configuration

Configure MongoDB connection via environment variables (`.env` file):

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DATABASE=langchain_db
MONGODB_TIMEOUT=5000
MONGODB_MAX_POOL_SIZE=10
```

## Docker Setup

MongoDB is configured in `docker-compose.yml`:

```bash
# Start all services including MongoDB
docker-compose up -d

# Check MongoDB is running
docker-compose ps mongodb

# View MongoDB logs
docker-compose logs -f mongodb
```

## Quick Start

### 1. Test MongoDB Connection

```python
from mcp_server import MongoDBMCPServer

server = MongoDBMCPServer()

# List collections
result = server.execute_tool("mongodb_list_collections", {})
print(result)

server.close()
```

### 2. Basic CRUD Operations

```python
import json
from mcp_server import create_mongodb_mcp_server

server = create_mongodb_mcp_server()

# Insert a document
result = server.execute_tool("mongodb_insert", {
    "collection": "users",
    "document_json": json.dumps({
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30
    })
})

# Find documents
result = server.execute_tool("mongodb_find", {
    "collection": "users",
    "filter_json": json.dumps({"age": {"$gte": 25}}),
    "limit": 10
})

# Update document
result = server.execute_tool("mongodb_update", {
    "collection": "users",
    "filter_json": json.dumps({"name": "Alice"}),
    "update_json": json.dumps({"$set": {"age": 31}})
})

# Delete document
result = server.execute_tool("mongodb_delete", {
    "collection": "users",
    "filter_json": json.dumps({"name": "Alice"})
})

server.close()
```

## Available Tools

### 1. mongodb_find
Find documents with optional filtering, pagination, and projection.

**Parameters:**
- `collection` (string, required): Collection name
- `filter_json` (string): JSON filter (default: `"{}"`)
- `limit` (integer): Max documents to return (default: 10)
- `skip` (integer): Documents to skip (default: 0)
- `projection` (string): Fields to include/exclude

**Example:**
```python
server.execute_tool("mongodb_find", {
    "collection": "users",
    "filter_json": '{"status": "active"}',
    "limit": 20,
    "projection": '{"name": 1, "email": 1}'
})
```

### 2. mongodb_find_one
Find a single document.

**Parameters:**
- `collection` (string, required): Collection name
- `filter_json` (string, required): JSON filter
- `projection` (string): Fields to include/exclude

### 3. mongodb_insert
Insert a single document.

**Parameters:**
- `collection` (string, required): Collection name
- `document_json` (string, required): JSON document to insert

### 4. mongodb_insert_many
Insert multiple documents.

**Parameters:**
- `collection` (string, required): Collection name
- `documents_json` (string, required): JSON array of documents

### 5. mongodb_update
Update one or many documents.

**Parameters:**
- `collection` (string, required): Collection name
- `filter_json` (string, required): JSON filter
- `update_json` (string, required): JSON update operations
- `upsert` (boolean): Create if not found (default: false)
- `update_many` (boolean): Update all matches (default: false)

### 6. mongodb_delete
Delete one or many documents.

**Parameters:**
- `collection` (string, required): Collection name
- `filter_json` (string, required): JSON filter
- `delete_many` (boolean): Delete all matches (default: false)

### 7. mongodb_aggregate
Execute aggregation pipeline.

**Parameters:**
- `collection` (string, required): Collection name
- `pipeline_json` (string, required): JSON array of pipeline stages

**Example:**
```python
pipeline = [
    {"$match": {"status": "active"}},
    {"$group": {"_id": "$category", "count": {"$sum": 1}}}
]
server.execute_tool("mongodb_aggregate", {
    "collection": "users",
    "pipeline_json": json.dumps(pipeline)
})
```

### 8. mongodb_list_collections
List all collections in the database.

**Parameters:** None

### 9. mongodb_count
Count documents matching a filter.

**Parameters:**
- `collection` (string, required): Collection name
- `filter_json` (string): JSON filter (default: `"{}"`)

## Usage Examples

Run the included examples:

```bash
# From app directory
cd /app/mcp_server
python example_usage.py
```

Or test the server directly:

```bash
python mongodb_mcp.py
```

## Use Cases

### 1. Chat History Storage
Store and retrieve conversation history:

```python
# Store message
server.execute_tool("mongodb_insert", {
    "collection": "chat_history",
    "document_json": json.dumps({
        "session_id": "session_123",
        "role": "user",
        "content": "Hello!",
        "timestamp": "2024-01-15T10:00:00Z"
    })
})

# Retrieve history
server.execute_tool("mongodb_find", {
    "collection": "chat_history",
    "filter_json": '{"session_id": "session_123"}',
    "limit": 50
})
```

### 2. RAG Document Metadata
Store metadata about ingested documents:

```python
server.execute_tool("mongodb_insert", {
    "collection": "document_metadata",
    "document_json": json.dumps({
        "filename": "report.pdf",
        "upload_date": "2024-01-15",
        "num_chunks": 50,
        "chroma_collection": "documents_v1",
        "status": "processed"
    })
})
```

### 3. User Preferences
Store user settings and preferences:

```python
server.execute_tool("mongodb_update", {
    "collection": "user_preferences",
    "filter_json": '{"user_id": "user_123"}',
    "update_json": '{"$set": {"theme": "dark", "model": "llama3.2"}}',
    "upsert": True
})
```

## Integration with LangChain

You can integrate MongoDB MCP tools with LangChain agents:

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from mcp_server import create_mongodb_mcp_server

# Create MCP server
mcp_server = create_mongodb_mcp_server()

# Create LangChain tools from MCP tools
tools = []
for tool_meta in mcp_server.get_tools_metadata():
    def make_tool_func(tool_name):
        def tool_func(**kwargs):
            return mcp_server.execute_tool(tool_name, kwargs)
        return tool_func

    tool = Tool(
        name=tool_meta["name"],
        description=tool_meta["description"],
        func=make_tool_func(tool_meta["name"])
    )
    tools.append(tool)

# Use tools with your agent
# agent = create_tool_calling_agent(llm, tools, prompt)
# agent_executor = AgentExecutor(agent=agent, tools=tools)
```

## MongoDB Access

### Via Docker Container

```bash
# Connect to MongoDB shell
docker exec -it mongodb-server mongosh

# Use database
use langchain_db

# Show collections
show collections

# Query documents
db.users.find()
```

### Via Python

```bash
# Install MongoDB shell tools
pip install pymongo

# Run Python scripts
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print(client.list_database_names())"
```

## Troubleshooting

### Connection Issues

1. Check MongoDB is running:
   ```bash
   docker-compose ps mongodb
   ```

2. Check MongoDB logs:
   ```bash
   docker-compose logs mongodb
   ```

3. Test connection:
   ```bash
   docker exec -it mongodb-server mongosh --eval "db.adminCommand('ping')"
   ```

### Environment Variables

Ensure all MongoDB variables are set in `.env`:
```bash
cat .env | grep MONGODB
```

### Permission Issues

If you see permission errors, check MongoDB data directory:
```bash
ls -la ./mongodb_data/
```

## Performance Tips

1. **Connection Pooling**: The server uses connection pooling automatically
2. **Indexes**: Create indexes for frequently queried fields
3. **Projection**: Use projection to retrieve only needed fields
4. **Aggregation**: Use aggregation pipelines for complex queries
5. **Pagination**: Use `skip` and `limit` for large result sets

## Security Considerations

1. **Authentication**: Add MongoDB authentication for production
2. **Network**: Restrict MongoDB network access
3. **Input Validation**: All inputs are validated and sanitized
4. **Error Messages**: Errors don't expose sensitive information

## Next Steps

1. Add MongoDB authentication
2. Implement data validation schemas
3. Add monitoring and metrics
4. Create backup/restore utilities
5. Add vector search support with MongoDB Atlas

## Support

For issues or questions:
- Check MongoDB logs: `docker-compose logs mongodb`
- Review example usage: `python example_usage.py`
- Test server: `python mongodb_mcp.py`

## License

Part of the langchain-local-llm project.
