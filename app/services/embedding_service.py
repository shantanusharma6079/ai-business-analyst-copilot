from sentence_transformers import (SentenceTransformer)

model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

def generate_embedding(text: str):
    embedding = model.encode(text)
    return embedding.tolist()

def generate_embeddings(texts: list[str]):
    # One call: the model encodes the texts in batches instead of one by one.
    # batch_size=8 measured fastest on CPU; larger batches waste time on padding.
    embeddings = model.encode(texts, batch_size=8)
    return embeddings.tolist()