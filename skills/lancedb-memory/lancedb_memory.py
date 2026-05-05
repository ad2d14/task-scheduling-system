#!/usr/bin/env python3
"""
LanceDB Memory Integration for OpenClaw
Integrates LanceDB with OpenClaw's memory search system
Supports custom embedding providers (doubao-embedding-vision-251215)
"""

import os
import json
import asyncio
import lancedb
import pyarrow as pa
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class OpenClawLanceMemory:
    """LanceDB memory integration for OpenClaw"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.environ.get(
                "LANCEDB_PATH", 
                os.path.expanduser("~/.openclaw/memory/lancedb")
            )
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(self.db_path)
        
        # Embedding configuration
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.base_url = os.environ.get(
            "OPENAI_BASE_URL", 
            "https://ark.cn-beijing.volces.com/api/coding/v3"
        )
        self.embedding_model = os.environ.get(
            "EMBEDDING_MODEL", 
            "doubao-embedding-vision-251215"
        )
        
        # Ensure memory table exists
        if "clawdbot_memory" not in self.db.list_tables():
            self._create_memory_table()
    
    def _create_memory_table(self):
        """Create the memory table with OpenClaw-compatible schema"""
        # Create initial empty table with proper schema
        initial_data = []
        schema = pa.schema([
            pa.field("id", pa.int32(), nullable=False),
            pa.field("timestamp", pa.timestamp('ns'), nullable=False),
            pa.field("content", pa.string(), nullable=False),
            pa.field("metadata", pa.string(), nullable=True),
            pa.field("embedding", pa.list_(pa.float32()), nullable=True)
        ])
        
        table = pa.Table.from_pylist(initial_data, schema=schema)
        self.db.create_table("openclaw_memory", data=table)
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector using custom embedding API"""
        if not self.api_key:
            return None
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.embedding_model,
                "input": text[:8000]  # Limit input length
            }
            
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result and len(result["data"]) > 0:
                    return result["data"][0]["embedding"]
            
            return None
        except Exception as e:
            print(f"Embedding error: {e}")
            return None
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories using semantic similarity"""
        try:
            if "openclaw_memory" not in self.db.list_tables():
                self._create_memory_table()
            
            table = self.db.open_table("openclaw_memory")
            
            if len(table) == 0:
                return []
            
            # Try vector search if we have embeddings
            query_embedding = self.get_embedding(query)
            
            if query_embedding is not None:
                results = table.search(query_embedding).limit(limit).to_list()
            else:
                # Fallback to text search if embedding unavailable
                results = table.search(query).limit(limit).to_list()
            
            # Convert embedding to list for serialization if present
            for r in results:
                if "embedding" in r and r["embedding"] is not None:
                    r["embedding"] = "[vector]"  # Don't return full vector
            
            return results[:limit]
            
        except Exception as e:
            print(f"LanceDB search error: {e}")
            return []
    
    async def add_memory(self, content: str, metadata: Dict[str, Any] = None) -> int:
        """Add a memory to LanceDB with embedding"""
        if "openclaw_memory" not in self.db.list_tables():
            self._create_memory_table()
        
        table = self.db.open_table("openclaw_memory")
        
        # Get next ID
        max_id = table.to_pandas()["id"].max() if len(table) > 0 else 0
        new_id = max_id + 1
        
        # Get embedding if available
        embedding = self.get_embedding(content)
        
        # Create memory entry
        memory_data = {
            "id": new_id,
            "timestamp": datetime.now(),
            "content": content,
            "metadata": json.dumps(metadata or {}),
            "embedding": embedding
        }
        
        table.add([memory_data])
        return new_id
    
    async def get_recent_memories(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent memories"""
        if "openclaw_memory" not in self.db.list_tables():
            self._create_memory_table()
        
        table = self.db.open_table("openclaw_memory")
        if len(table) == 0:
            return []
        
        df = table.to_pandas()
        recent = df.sort_values("timestamp", ascending=False).head(limit)
        return recent.to_dict("records")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        if "openclaw_memory" not in self.db.list_tables():
            return {"total": 0}
        
        table = self.db.open_table("openclaw_memory")
        return {"total_memories": len(table)}

# Global instance
openclaw_lance_memory = OpenClawLanceMemory()

# OpenClaw memory search provider
class LanceMemoryProvider:
    """Memory search provider for OpenClaw"""
    
    def __init__(self):
        self.memory_db = openclaw_lance_memory
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories"""
        return await self.memory_db.search_memories(query, limit)
    
    async def add(self, content: str, metadata: Dict[str, Any] = None) -> int:
        """Add memory"""
        return await self.memory_db.add_memory(content, metadata)
    
    async def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent memories"""
        return await self.memory_db.get_recent_memories(limit)
    
    def stats(self) -> Dict[str, Any]:
        """Get memory stats"""
        return self.memory_db.get_memory_stats()

# Create provider instance
lance_memory_provider = LanceMemoryProvider()

# Test function
async def test_lance_memory():
    """Test the LanceDB memory integration"""
    print("Testing LanceDB memory integration...")
    print(f"API Key configured: {bool(openclaw_lance_memory.api_key)}")
    print(f"Embedding model: {openclaw_lance_memory.embedding_model}")
    print(f"Base URL: {openclaw_lance_memory.base_url}")
    
    # Test embedding
    test_embedding = openclaw_lance_memory.get_embedding("Hello, world!")
    if test_embedding:
        print(f"Embedding OK, dimension: {len(test_embedding)}")
    else:
        print("Embedding: None (API key may not be set or error)")
    
    # Add test memory
    memory_id = await lance_memory_provider.add(
        content="This is a test memory for OpenClaw LanceDB integration",
        metadata={"type": "test", "importance": 8, "skill": "lancedb-memory"}
    )
    print(f"Added memory with ID: {memory_id}")
    
    # Search for memories
    results = await lance_memory_provider.search("test memory")
    print(f"Search results: {len(results)} memories found")
    
    # Get recent memories
    recent = await lance_memory_provider.get_recent(5)
    print(f"Recent memories: {len(recent)} memories")
    
    # Stats
    print(f"Stats: {lance_memory_provider.stats()}")

if __name__ == "__main__":
    asyncio.run(test_lance_memory())