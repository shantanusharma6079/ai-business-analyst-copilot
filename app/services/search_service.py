from sqlalchemy import text
from app.services.embedding_service import (generate_embedding)

def search_chunks(db, query, limit=5):
    query_embedding = generate_embedding(query)
    
    sql = text("""
        SELECT
            id,
            chunk_text,
            embedding <=> CAST(:embedding AS vector) AS distance
        FROM document_chunks
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """)
    
    result = db.execute(sql, {
        "embedding": str(query_embedding),
        "limit": limit
    })
    
    return result.fetchall()