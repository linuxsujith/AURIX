"""
Memory Agent — Stores and retrieves user data using ChromaDB.
"""

import json
import datetime
from typing import Optional, List
from config.settings import get_settings


class MemoryAgent:
    """Handles long-term memory, context recall, and personalization using ChromaDB."""

    def __init__(self):
        settings = get_settings()
        self.db_path = settings.memory.chromadb_path
        self.collection_name = settings.memory.collection_name
        self.client = None
        self.collection = None
        self._initialized = False

    def _ensure_init(self):
        """Lazy initialization of ChromaDB."""
        if self._initialized:
            return
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self._initialized = True
        except Exception as e:
            print(f"[Memory] ChromaDB init error: {e}")

    async def execute(self, action: dict) -> dict:
        """Execute a memory action."""
        action_type = action.get("action", "")
        params = action.get("params", {})

        if action_type == "remember":
            return self.store_memory(params.get("content", ""), params.get("category", "general"))
        elif action_type == "recall":
            return self.recall(params.get("query", ""), params.get("n_results", 5))

        return {"success": False, "error": f"Unknown memory action: {action_type}"}

    def store_memory(self, content: str, category: str = "general", metadata: dict = None) -> dict:
        """Store a piece of information in long-term memory."""
        self._ensure_init()
        if not self._initialized:
            return {"success": False, "error": "Memory system not initialized"}

        try:
            import uuid
            memory_id = str(uuid.uuid4())
            timestamp = datetime.datetime.now().isoformat()

            meta = {
                "category": category,
                "timestamp": timestamp,
            }
            if metadata:
                meta.update(metadata)

            self.collection.add(
                documents=[content],
                metadatas=[meta],
                ids=[memory_id]
            )
            return {"success": True, "id": memory_id, "message": "Memory stored"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def recall(self, query: str, n_results: int = 5) -> dict:
        """Recall relevant memories based on a query."""
        self._ensure_init()
        if not self._initialized:
            return {"success": False, "error": "Memory system not initialized"}

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, 20)
            )

            memories = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    meta = results["metadatas"][0][i] if results["metadatas"] else {}
                    memories.append({
                        "content": doc,
                        "category": meta.get("category", ""),
                        "timestamp": meta.get("timestamp", ""),
                        "relevance": round(1 - (results["distances"][0][i] if results["distances"] else 0), 3)
                    })

            return {"success": True, "memories": memories, "count": len(memories)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def store_preference(self, key: str, value: str) -> dict:
        """Store a user preference."""
        return self.store_memory(
            f"User preference: {key} = {value}",
            category="preference",
            metadata={"pref_key": key}
        )

    def store_conversation_summary(self, summary: str) -> dict:
        """Store a conversation summary for long-term context."""
        return self.store_memory(summary, category="conversation")

    def get_memory_stats(self) -> dict:
        """Get memory system statistics."""
        self._ensure_init()
        if not self._initialized:
            return {"success": False, "error": "Memory system not initialized"}

        try:
            count = self.collection.count()
            return {"success": True, "total_memories": count}
        except Exception as e:
            return {"success": False, "error": str(e)}
