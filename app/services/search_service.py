from sqlalchemy import text
from app.services.embedding_service import (generate_embedding)

def search_chunks(db, query, limit=5):
    query_embedding = generate_embedding(query)
    
    sql = text("""
        SELECT
            c.id,
            c.chunk_text,
            c.embedding <=> CAST(:embedding AS vector) AS distance,
            c.document_id,
            d.file_name,
            c.page
        FROM document_chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE d.status = 'ready'
        ORDER BY c.embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """)
    
    result = db.execute(sql, {
        "embedding": str(query_embedding),
        "limit": limit
    })
    
    return result.fetchall()