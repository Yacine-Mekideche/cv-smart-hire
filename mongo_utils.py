import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))

db = client["aws_rag_db"]
collection = db["documents"]

def insert_chunks(chunks_with_embeddings):
    docs = [{"content": chunk, "embedding": embedding} for chunk, embedding in chunks_with_embeddings]
    collection.insert_many(docs)

def search_similar_chunks(query_embedding, k=3):
    pipeline = [
        {
            "$vectorSearch": {
                "index": "embedding_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": k
            }
        }
    ]
    return list(collection.aggregate(pipeline))


def delete_all_documents():
    result = collection.delete_many({})
    return result.deleted_count

def count_documents():
    return collection.count_documents({})


def insert_chunks(chunks_with_embeddings, source_name):
    docs = [
        {"content": chunk, "embedding": embedding, "source": source_name}
        for chunk, embedding in chunks_with_embeddings
    ]
    collection.insert_many(docs)

def get_distinct_sources():
    return collection.distinct("source")

def delete_documents_by_source(source_name):
    result = collection.delete_many({"source": source_name})
    return result.deleted_count
