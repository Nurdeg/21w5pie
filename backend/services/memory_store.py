# backend/services/memory_store.py
import chromadb
from chromadb.utils import embedding_functions
import uuid
from backend.utils.logger import logger

class MemoryStore:
    def __init__(self):
        # 1. Initialize local database (saved to /data folder)
        self.client = chromadb.PersistentClient(path="./data/chroma_db")
        
        # 2. Use a standard, fast embedding model
        # This turns text into a list of numbers (vectors)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # 3. Create or Get the collection (like a table in SQL)
        self.collection = self.client.get_or_create_collection(
            name="analysis_history",
            embedding_function=self.embedding_fn
        )
        logger.info("🧠 Memory Store initialized.")

    def save_analysis(self, text: str, analysis: dict):
        """
        Save the original text + the AI's analysis into the vector DB.
        """
        try:
            # We store the 'summary' and 'sentiment' as metadata 
            # so we can filter by them later.
            self.collection.add(
                documents=[text],
                metadatas=[{
                    "sentiment": analysis["sentiment"],
                    "summary": analysis["summary"],
                    "intent": analysis["intent"],
                    "timestamp": str(uuid.uuid4()) # simple unique ID
                }],
                ids=[str(uuid.uuid4())]
            )
            logger.info("💾 Analysis saved to long-term memory.")
        except Exception as e:
            logger.error(f"Failed to save to memory: {e}")

    def search_similar(self, query: str, n_results=3):
        """
        Find past analyses that match the meaning of the query.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results