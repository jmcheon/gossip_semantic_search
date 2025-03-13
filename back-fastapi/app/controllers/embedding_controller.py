from fastapi import APIRouter

from ..dependencies import device, model
from ..services import embedding_service

router = APIRouter(prefix="/embed", tags=["Embeddings"])


@router.post("/links")
def embed_links():
    """
    Generate and store link embeddings
    """
    return embedding_service.generate_link_embeddings(model, device)


@router.post("/feeds")
def embed_feeds():
    """
    Generate and store feed embeddings
    """
    return embedding_service.generate_feed_embeddings(model, device)
