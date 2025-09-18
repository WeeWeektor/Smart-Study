from bson import ObjectId
from pymongo import MongoClient

from smartStudy_backend import settings


class MongoRepository:
    def __init__(self):
        client = MongoClient(settings.MONGO_URI)
        self.db = client.get_database()

    def collection(self, name: str):
        return self.db[name]

    def get_document_by_id(self, collection_name: str, doc_id: str) -> dict | None:
        return self.collection(collection_name).find_one({"_id": ObjectId(doc_id)})

    def get_documents(self, collection_name: str, query: dict) -> list:
        return list(self.collection(collection_name).find(query))

    def insert_document(self, collection_name: str, data: dict) -> str:
        result = self.collection(collection_name).insert_one(data)
        return str(result.inserted_id)

    def update_document(self, collection_name: str, doc_id: str, update_data: dict) -> dict:
        result = self.collection(collection_name).find_one_and_update(
            {"_id": ObjectId(doc_id)},
            {"$set": update_data},
            return_document=True
        )
        return {"info: ": "Update success", "data": result} if result else {"info: ": "Document not found"}

    def delete_document_by_id(self, collection_name: str, doc_id: str) -> bool:
        result = self.collection(collection_name).delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0

    def delete_documents(self, collection_name: str, query: dict) -> str:
        result = self.collection(collection_name).delete_many(query)
        return f"Deleted {result.deleted_count} documents."


mongo_repo = MongoRepository()
