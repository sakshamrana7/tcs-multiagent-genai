"""
RAG Pipeline for TCS Multi-Agent GenAI
Uses ChromaDB for vector storage and document retrieval
"""

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# ChromaDB client
client = chromadb.Client()
CHROMA_DB_PATH = Path(__file__).parent / "chroma_db"
CHROMA_DB_PATH.mkdir(exist_ok=True)

# Initialize persistent client
persistent_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))


def create_collection(collection_name: str):
    """Create or get a ChromaDB collection."""
    try:
        collection = persistent_client.get_collection(name=collection_name)
    except:
        collection = persistent_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    return collection


def add_documents(collection_name: str, documents: List[Dict[str, str]]):
    """
    Add documents to ChromaDB collection.
    
    Args:
        collection_name: Name of the collection
        documents: List of dicts with 'id', 'content', and optionally 'metadata'
    """
    collection = create_collection(collection_name)
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    all_chunks = []
    chunk_ids = []
    chunk_metadatas = []
    
    for doc in documents:
        doc_id = doc.get("id", "")
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        
        # Split content into chunks
        chunks = text_splitter.split_text(content)
        
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            chunk_ids.append(f"{doc_id}_chunk_{i}")
            chunk_metadatas.append({
                "doc_id": doc_id,
                "chunk_index": i,
                **metadata
            })
    
    # Add to collection
    if all_chunks:
        collection.add(
            ids=chunk_ids,
            documents=all_chunks,
            metadatas=chunk_metadatas
        )
    
    return len(all_chunks)


def search_documents(
    collection_name: str,
    query: str,
    n_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search documents in ChromaDB collection.
    
    Args:
        collection_name: Name of the collection
        query: Search query
        n_results: Number of results to return
    
    Returns:
        List of matching documents with scores
    """
    collection = create_collection(collection_name)
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    # Format results
    formatted_results = []
    if results["documents"] and len(results["documents"]) > 0:
        docs = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]
        
        for doc, distance, metadata in zip(docs, distances, metadatas):
            # Convert distance to similarity (cosine distance to similarity)
            similarity = 1 - distance
            formatted_results.append({
                "content": doc,
                "similarity": similarity,
                "metadata": metadata
            })
    
    return formatted_results


def delete_collection(collection_name: str):
    """Delete a ChromaDB collection."""
    try:
        persistent_client.delete_collection(name=collection_name)
        return True
    except:
        return False


def clear_collection(collection_name: str):
    """Clear all documents from a collection."""
    try:
        delete_collection(collection_name)
        create_collection(collection_name)
        return True
    except:
        return False


def get_collection_info(collection_name: str) -> Dict[str, Any]:
    """Get information about a collection."""
    try:
        collection = create_collection(collection_name)
        return {
            "name": collection_name,
            "count": collection.count(),
            "exists": True
        }
    except:
        return {
            "name": collection_name,
            "count": 0,
            "exists": False
        }


def seed_sample_documents():
    """Initialize collections without seeding samples (user uploads documents)."""
    create_collection("policies_faqs")
    return 0


if __name__ == "__main__":
    # Initialize collections
    seed_sample_documents()
    print("✅ Collections initialized (ready for user documents)")
