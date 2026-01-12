"""
MongoDB MCP Tools
=================

Tools for MongoDB operations exposed through MCP.
"""

from typing import Any, Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import json
from bson import json_util, ObjectId
from .config import config


class MongoDBTools:
    """Tools for MongoDB operations."""

    def __init__(self):
        """Initialize MongoDB connection."""
        self.client: Optional[MongoClient] = None
        self.db = None

    def connect(self):
        """Establish connection to MongoDB."""
        if self.client is None:
            try:
                self.client = MongoClient(**config.get_connection_params())
                self.db = self.client[config.database_name]
                # Test connection
                self.client.admin.command('ping')
                print(f"✓ Connected to MongoDB: {config.database_name}")
            except PyMongoError as e:
                print(f"✗ Failed to connect to MongoDB: {e}")
                raise

    def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            print("✓ Disconnected from MongoDB")

    def _serialize_result(self, data: Any) -> str:
        """Serialize MongoDB result to JSON string."""
        return json.dumps(data, default=json_util.default, indent=2)

    def _parse_filter(self, filter_str: str) -> dict:
        """Parse filter string to dict, handling ObjectId."""
        if not filter_str or filter_str.strip() == "{}":
            return {}

        filter_dict = json.loads(filter_str)

        # Convert _id string to ObjectId if present
        if "_id" in filter_dict and isinstance(filter_dict["_id"], str):
            try:
                filter_dict["_id"] = ObjectId(filter_dict["_id"])
            except:
                pass  # Keep as string if invalid ObjectId

        return filter_dict

    def find_documents(
        self,
        collection: str,
        filter_json: str = "{}",
        limit: int = 10,
        skip: int = 0,
        projection: Optional[str] = None
    ) -> str:
        """
        Find documents in a MongoDB collection.

        Args:
            collection: Collection name
            filter_json: JSON string for query filter (e.g., '{"status": "active"}')
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            projection: Optional projection fields (e.g., '{"name": 1, "email": 1}')

        Returns:
            JSON string with query results
        """
        try:
            self.connect()
            coll = self.db[collection]

            query_filter = self._parse_filter(filter_json)
            proj = json.loads(projection) if projection else None

            cursor = coll.find(query_filter, proj).skip(skip).limit(limit)
            results = list(cursor)

            return self._serialize_result({
                "success": True,
                "collection": collection,
                "count": len(results),
                "documents": results
            })
        except Exception as e:
            return self._serialize_result({
                "success": False,
                "error": str(e)
            })

    def find_one_document(
        self,
        collection: str,
        filter_json: str,
        projection: Optional[str] = None
    ) -> str:
        """
        Find a single document in a MongoDB collection.

        Args:
            collection: Collection name
            filter_json: JSON string for query filter
            projection: Optional projection fields

        Returns:
            JSON string with the document or error
        """
        try:
            self.connect()
            coll = self.db[collection]

            query_filter = self._parse_filter(filter_json)
            proj = json.loads(projection) if projection else None

            result = coll.find_one(query_filter, proj)

            return self._serialize_result({
                "success": True,
                "collection": collection,
                "document": result
            })
        except Exception as e:
            return self._serialize_result({
                "success": False,
                "error": str(e)
            })

    def insert_document(
        self,
        collection: str,
        document_json: str
    ) -> str:
        """
        Insert a document into a MongoDB collection.

        Args:
            collection: Collection name
            document_json: JSON string of the document to insert

        Returns:
            JSON string with the inserted document ID
        """
        try:
            self.connect()
            coll = self.db[collection]

            document = json.loads(document_json)
            result = coll.insert_one(document)

            return self._serialize_result({
                "success": True,
                "collection": collection,
                "inserted_id": str(result.inserted_id),
                "acknowledged": result.acknowledged
            })
        except Exception as e:
            return self._serialize_result({
                "success": False,
                "error": str(e)
            })

    def insert_many_documents(
        self,
        collection: str,
        documents_json: str
    ) -> str:
        """
        Insert multiple documents into a MongoDB collection.

        Args:
            collection: Collection name
            documents_json: JSON array string of documents to insert

        Returns:
            JSON string with the inserted document IDs
        """
        try:
            self.connect()
            coll = self.db[collection]

            documents = json.loads(documents_json)
            if not isinstance(documents, list):
                raise ValueError("documents_json must be a JSON array")

            result = coll.insert_many(documents)

            return self._serialize_result({
                "success": True,
                "collection": collection,
                "inserted_ids": [str(id) for id in result.inserted_ids],
                "count": len(result.inserted_ids),
                "acknowledged": result.acknowledged
            })
        except Exception as e:
            return self._serialize_result({
                "success": False,
                "error": str(e)
            })

    def update_documents(
        self,
        collection: str,
        filter_json: str,
        update_json: str,
        upsert: bool = False,
        update_many: bool = False
    ) -> str:
        """
        Update documents in a MongoDB collection.

        Args:
            collection: Collection name
            filter_json: JSON string for query filter
            update_json: JSON string for update operations (e.g., '{"$set": {"status": "done"}}')
            upsert: Create document if not found
            update_many: Update all matching documents (False = update one)

        Returns:
            JSON string with update results
        """
        try:
            self.connect()
            coll = self.db[collection]

            query_filter = self._parse_filter(filter_json)
            update_doc = json.loads(update_json)

            if update_many:
                result = coll.update_many(query_filter, update_doc, upsert=upsert)
            else:
                result = coll.update_one(query_filter, update_doc, upsert=upsert)

            return self._serialize_result({
                "success": True,
                "collection": collection,
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                "acknowledged": result.acknowledged
            })
        except Exception as e:
            return self._serialize_result({
                "success": False,
                "error": str(e)
            })

    def delete_documents(
        self,
        collection: str,
        filter_json: str,
        delete_many: bool = False
    ) -> str:
        """
        Delete documents from a MongoDB collection.

        Args:
            collection: Collection name
            filter_json: JSON string for query filter
            delete_many: Delete all matching documents (False = delete one)

        Returns:
            JSON string with delete results
        """
        try:
            self.connect()
            coll = self.db[collection]

            query_filter = self._parse_filter(filter_json)

            if delete_many:
                result = coll.delete_many(query_filter)
            else:
                result = coll.delete_one(query_filter)

            return self._serialize_result({
                "success": True,
                "collection": collection,
                "deleted_count": result.deleted_count,
                "acknowledged": result.acknowledged
            })
        except Exception as e:
            return self._serialize_result({
                "success": False,
                "error": str(e)
            })

    def aggregate(
        self,
        collection: str,
        pipeline_json: str
    ) -> str:
        """
        Run an aggregation pipeline on a MongoDB collection.

        Args:
            collection: Collection name
            pipeline_json: JSON array string of aggregation pipeline stages

        Returns:
            JSON string with aggregation results
        """
        try:
            self.connect()
            coll = self.db[collection]

            pipeline = json.loads(pipeline_json)
            if not isinstance(pipeline, list):
                raise ValueError("pipeline_json must be a JSON array")

            results = list(coll.aggregate(pipeline))

            return self._serialize_result({
                "success": True,
                "collection": collection,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return self._serialize_result({
                "success": False,
                "error": str(e)
            })

    def list_collections(self) -> str:
        """
        List all collections in the database.

        Returns:
            JSON string with collection names
        """
        try:
            self.connect()
            collections = self.db.list_collection_names()

            return self._serialize_result({
                "success": True,
                "database": config.database_name,
                "collections": collections,
                "count": len(collections)
            })
        except Exception as e:
            return self._serialize_result({
                "success": False,
                "error": str(e)
            })

    def count_documents(
        self,
        collection: str,
        filter_json: str = "{}"
    ) -> str:
        """
        Count documents in a collection matching a filter.

        Args:
            collection: Collection name
            filter_json: JSON string for query filter

        Returns:
            JSON string with document count
        """
        try:
            self.connect()
            coll = self.db[collection]

            query_filter = self._parse_filter(filter_json)
            count = coll.count_documents(query_filter)

            return self._serialize_result({
                "success": True,
                "collection": collection,
                "count": count
            })
        except Exception as e:
            return self._serialize_result({
                "success": False,
                "error": str(e)
            })
