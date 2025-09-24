from bson import ObjectId
from pymongo import MongoClient

from smartStudy_backend import settings


class MongoRepository:
    info_str = "info: "
    doc_not_found = {info_str: "Document not found"}

    def __init__(self):
        client = MongoClient(settings.MONGO_URI)
        self.db = client.get_database()

    def collection(self, name: str):
        return self.db[name]

    def get_document_by_id(self, collection_name: str, doc_id: str) -> dict | None:
        return self.collection(collection_name).find_one({"_id": ObjectId(doc_id)})

    def get_document_by_field(self, collection_name: str, field: str, value: str) -> dict | None:
        return self.collection(collection_name).find_one({field: value})

    def insert_document(self, collection_name: str, data: dict) -> str:
        result = self.collection(collection_name).insert_one(data)
        return str(result.inserted_id)

    def update_document(
            self,
            collection_name: str,
            doc_id: str,
            update_data: dict,
            action: str = "set",
            array_filters: list[dict] | None = None
    ) -> dict:
        """
        Підтримує push, set, unset для оновлення документа.
        Можна передавати array_filters для онновлення елементів масиву.
        """
        update_query = {f"${action}": update_data}

        result = self.collection(collection_name).find_one_and_update(
            {"_id": ObjectId(doc_id)},
            update_query,
            return_document=True,
            array_filters=array_filters
        )
        return {self.info_str: "Update success", "data": result} if result else self.doc_not_found

    def replace_document(self, collection_name: str, doc_id: str, new_data: dict) -> dict:
        result = self.collection(collection_name).replace_one(
            {"_id": ObjectId(doc_id)},
            new_data
        )
        return {self.info_str: "Replace success", "data": result} if result.modified_count else self.doc_not_found

    def delete_document_by_id(self, collection_name: str, doc_id: str) -> bool:
        result = self.collection(collection_name).delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0


mongo_repo = MongoRepository()
