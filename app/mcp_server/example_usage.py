"""
MongoDB MCP Server - Usage Examples
====================================

This file demonstrates how to use the MongoDB MCP server with various operations.
"""

import json
from mongodb_mcp import create_mongodb_mcp_server


def example_basic_operations():
    """Example: Basic CRUD operations."""
    print("\n" + "=" * 70)
    print("Example 1: Basic CRUD Operations")
    print("=" * 70)

    server = create_mongodb_mcp_server()

    try:
        # 1. List collections
        print("\n1. Listing collections...")
        result = server.execute_tool("mongodb_list_collections", {})
        print(json.dumps(json.loads(result), indent=2))

        # 2. Insert a document
        print("\n2. Inserting a document...")
        document = {
            "name": "Alice",
            "email": "alice@example.com",
            "age": 30,
            "role": "developer"
        }
        result = server.execute_tool("mongodb_insert", {
            "collection": "users",
            "document_json": json.dumps(document)
        })
        print(json.dumps(json.loads(result), indent=2))

        # 3. Find documents
        print("\n3. Finding all users...")
        result = server.execute_tool("mongodb_find", {
            "collection": "users",
            "filter_json": "{}",
            "limit": 10
        })
        print(json.dumps(json.loads(result), indent=2))

        # 4. Find one document
        print("\n4. Finding user by name...")
        result = server.execute_tool("mongodb_find_one", {
            "collection": "users",
            "filter_json": json.dumps({"name": "Alice"})
        })
        print(json.dumps(json.loads(result), indent=2))

        # 5. Update document
        print("\n5. Updating user...")
        result = server.execute_tool("mongodb_update", {
            "collection": "users",
            "filter_json": json.dumps({"name": "Alice"}),
            "update_json": json.dumps({"$set": {"age": 31, "status": "active"}}),
            "update_many": False
        })
        print(json.dumps(json.loads(result), indent=2))

        # 6. Count documents
        print("\n6. Counting users...")
        result = server.execute_tool("mongodb_count", {
            "collection": "users",
            "filter_json": "{}"
        })
        print(json.dumps(json.loads(result), indent=2))

    finally:
        server.close()


def example_batch_operations():
    """Example: Batch insert operations."""
    print("\n" + "=" * 70)
    print("Example 2: Batch Operations")
    print("=" * 70)

    server = create_mongodb_mcp_server()

    try:
        # Insert multiple documents
        print("\n1. Inserting multiple users...")
        documents = [
            {"name": "Bob", "email": "bob@example.com", "age": 25, "role": "designer"},
            {"name": "Carol", "email": "carol@example.com", "age": 28, "role": "manager"},
            {"name": "Dave", "email": "dave@example.com", "age": 35, "role": "developer"},
        ]
        result = server.execute_tool("mongodb_insert_many", {
            "collection": "users",
            "documents_json": json.dumps(documents)
        })
        print(json.dumps(json.loads(result), indent=2))

        # Update multiple documents
        print("\n2. Updating all developers...")
        result = server.execute_tool("mongodb_update", {
            "collection": "users",
            "filter_json": json.dumps({"role": "developer"}),
            "update_json": json.dumps({"$set": {"department": "engineering"}}),
            "update_many": True
        })
        print(json.dumps(json.loads(result), indent=2))

    finally:
        server.close()


def example_queries():
    """Example: Advanced queries with filters and projections."""
    print("\n" + "=" * 70)
    print("Example 3: Advanced Queries")
    print("=" * 70)

    server = create_mongodb_mcp_server()

    try:
        # Query with filter
        print("\n1. Finding users older than 28...")
        result = server.execute_tool("mongodb_find", {
            "collection": "users",
            "filter_json": json.dumps({"age": {"$gt": 28}}),
            "limit": 10
        })
        print(json.dumps(json.loads(result), indent=2))

        # Query with projection
        print("\n2. Finding users (name and email only)...")
        result = server.execute_tool("mongodb_find", {
            "collection": "users",
            "filter_json": "{}",
            "projection": json.dumps({"name": 1, "email": 1, "_id": 0}),
            "limit": 5
        })
        print(json.dumps(json.loads(result), indent=2))

        # Query with pagination
        print("\n3. Paginated results (skip 2, limit 2)...")
        result = server.execute_tool("mongodb_find", {
            "collection": "users",
            "filter_json": "{}",
            "skip": 2,
            "limit": 2
        })
        print(json.dumps(json.loads(result), indent=2))

    finally:
        server.close()


def example_aggregation():
    """Example: Aggregation pipeline."""
    print("\n" + "=" * 70)
    print("Example 4: Aggregation Pipeline")
    print("=" * 70)

    server = create_mongodb_mcp_server()

    try:
        # Group by role and count
        print("\n1. Grouping users by role...")
        pipeline = [
            {"$group": {
                "_id": "$role",
                "count": {"$sum": 1},
                "avgAge": {"$avg": "$age"}
            }},
            {"$sort": {"count": -1}}
        ]
        result = server.execute_tool("mongodb_aggregate", {
            "collection": "users",
            "pipeline_json": json.dumps(pipeline)
        })
        print(json.dumps(json.loads(result), indent=2))

        # Match and project
        print("\n2. Finding developers with specific fields...")
        pipeline = [
            {"$match": {"role": "developer"}},
            {"$project": {
                "name": 1,
                "age": 1,
                "isExperienced": {"$gte": ["$age", 30]}
            }}
        ]
        result = server.execute_tool("mongodb_aggregate", {
            "collection": "users",
            "pipeline_json": json.dumps(pipeline)
        })
        print(json.dumps(json.loads(result), indent=2))

    finally:
        server.close()


def example_chat_history():
    """Example: Storing and retrieving chat history."""
    print("\n" + "=" * 70)
    print("Example 5: Chat History Storage")
    print("=" * 70)

    server = create_mongodb_mcp_server()

    try:
        # Store a conversation
        print("\n1. Storing chat messages...")
        messages = [
            {
                "session_id": "session_123",
                "role": "user",
                "content": "What is the capital of France?",
                "timestamp": "2024-01-15T10:00:00Z"
            },
            {
                "session_id": "session_123",
                "role": "assistant",
                "content": "The capital of France is Paris.",
                "timestamp": "2024-01-15T10:00:05Z"
            },
            {
                "session_id": "session_123",
                "role": "user",
                "content": "What's the population?",
                "timestamp": "2024-01-15T10:00:10Z"
            }
        ]
        result = server.execute_tool("mongodb_insert_many", {
            "collection": "chat_history",
            "documents_json": json.dumps(messages)
        })
        print(json.dumps(json.loads(result), indent=2))

        # Retrieve conversation history
        print("\n2. Retrieving chat history for session...")
        result = server.execute_tool("mongodb_find", {
            "collection": "chat_history",
            "filter_json": json.dumps({"session_id": "session_123"}),
            "limit": 50
        })
        print(json.dumps(json.loads(result), indent=2))

        # Count messages per session
        print("\n3. Counting messages per session...")
        pipeline = [
            {"$group": {
                "_id": "$session_id",
                "message_count": {"$sum": 1}
            }}
        ]
        result = server.execute_tool("mongodb_aggregate", {
            "collection": "chat_history",
            "pipeline_json": json.dumps(pipeline)
        })
        print(json.dumps(json.loads(result), indent=2))

    finally:
        server.close()


def example_document_metadata():
    """Example: Storing RAG document metadata."""
    print("\n" + "=" * 70)
    print("Example 6: RAG Document Metadata")
    print("=" * 70)

    server = create_mongodb_mcp_server()

    try:
        # Store document metadata
        print("\n1. Storing document metadata...")
        document_meta = {
            "filename": "technical_report.pdf",
            "file_type": "pdf",
            "upload_date": "2024-01-15T10:00:00Z",
            "num_pages": 25,
            "num_chunks": 50,
            "status": "processed",
            "chroma_collection": "documents_v1",
            "metadata": {
                "author": "John Doe",
                "category": "technical",
                "tags": ["AI", "ML", "Deep Learning"]
            }
        }
        result = server.execute_tool("mongodb_insert", {
            "collection": "document_metadata",
            "document_json": json.dumps(document_meta)
        })
        print(json.dumps(json.loads(result), indent=2))

        # Find documents by category
        print("\n2. Finding technical documents...")
        result = server.execute_tool("mongodb_find", {
            "collection": "document_metadata",
            "filter_json": json.dumps({"metadata.category": "technical"}),
            "limit": 10
        })
        print(json.dumps(json.loads(result), indent=2))

    finally:
        server.close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("MongoDB MCP Server - Usage Examples")
    print("=" * 70)
    print("\nMake sure MongoDB is running and accessible at the configured URI.")
    print("Press Ctrl+C to stop at any time.")
    print()

    try:
        # Run all examples
        example_basic_operations()
        example_batch_operations()
        example_queries()
        example_aggregation()
        example_chat_history()
        example_document_metadata()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\n\nError running examples: {e}")
        import traceback
        traceback.print_exc()
