import json

from chromadb import Collection


class KnowledgeBase:
    def __init__(self, collection: Collection):
        self.collection = collection

    def add_knowledge(self, documents, metadata):
        """Add a business rule."""
        self.collection.add(documents=[documents], metadatas=[metadata])

    def query_knowledge(self, query_text, top_k=3):
        results = self.collection.query(
            query_texts=[json.dumps(query_text)], n_results=top_k
        )
        return results
