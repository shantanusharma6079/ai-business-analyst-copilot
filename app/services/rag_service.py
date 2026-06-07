from app.services.search_service import (search_chunks)
from app.services.llm_service import (generate_response)

def ask_question(db, question):
    chunks = search_chunks(db, question)
    
    context = "\n\n".join([row.chunk_text for row in chunks])
    
    prompt = f"""
        You are a senior business analyst.

        Answer ONLY using the provided context.

        If the answer is not found,
        say you don't know.

        Context:

        {context}

        Question:

        {question}
    """

    answer = generate_response(prompt)

    return {
        "answer": answer,
        "sources": len(chunks)
    }