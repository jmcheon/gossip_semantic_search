import torch
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

from .config import settings

# Sentence Transformer model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)

# Initialize Poincone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

if not pc.has_index(settings.PINECONE_INDEX_NAME):
    print(f"Creating Pinecone index:{settings.PINECONE_INDEX_NAME}")
    pc.create_index(
        name=settings.PINECONE_INDEX_NAME,
        dimension=model.get_sentence_embedding_dimension(),
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(settings.PINECONE_INDEX_NAME)
