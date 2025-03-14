from typing import List

import numpy as np

from ..dependencies import index, model


def generate_embedding(query: str) -> np.ndarray:
    """
    Generate embedding for a given query.
    """
    return model.encode(query, convert_to_tensor=False).tolist()


def search_links(query_embedding: np.ndarray, top_k: int = 5) -> List[dict]:
    """
    Find the top k most similar embeddings for a given qeury embedding.
    """
    # Get scores for feeds data
    feed_results = index.query(
        vector=query_embedding, top_k=top_k, include_metadata=True, namespace="feeds"
    )
    print(feed_results)

    # Get scores for links data
    link_results = index.query(
        vector=query_embedding, top_k=top_k, include_metadata=True, namespace="links"
    )
    print(link_results)

    # Get link and score pair from the corresponding source
    top_links = [
        {"link": match["metadata"]["text"], "score": match["score"]}
        for match in link_results["matches"]
    ]
    feed_top_links = [
        {"link": match["metadata"]["text"], "score": match["score"]}
        for match in feed_results["matches"]
    ]

    return sorted(top_links + feed_top_links, key=lambda x: x["score"], reverse=True)[:top_k]
