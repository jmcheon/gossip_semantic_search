from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from ..dependencies import model

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
feed_csv_path = DATA_DIR / "feeds.csv"
feed_embeddings_path = DATA_DIR / "feed_embeddings.npy"

csv_path = DATA_DIR / "links_metadata.csv"
embeddings_path = DATA_DIR / "embeddings.npy"

# Load the feed embeddings and corresponding links
feed_df = pd.read_csv(feed_csv_path)
feed_links = feed_df["Link"].tolist()
feed_embeddings = np.load(feed_embeddings_path)

# Load the link embeddings and corresponding links
df = pd.read_csv(csv_path)
links = df["link"].tolist()
embeddings = np.load(embeddings_path)


def generate_embedding(query: str) -> np.ndarray:
    """
    Generate embedding for a given query.
    """
    return model.encode(query, convert_to_tensor=False)


def search_links(query_embedding: np.ndarray, top_k: int = 5) -> List[dict]:
    """
    Find the top k most similar embeddings for a given qeury embedding.
    """
    # Get scores for feeds data
    feed_scores = np.dot(feed_embeddings, query_embedding) / (
        np.linalg.norm(feed_embeddings, axis=1) * np.linalg.norm(query_embedding)
    )

    feed_top_indices = np.argsort(feed_scores)[::-1][:top_k]

    # Get scores for links data
    scores = np.dot(embeddings, query_embedding) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
    )

    top_indices = np.argsort(scores)[::-1][:top_k]
    # print(feed_top_indices, top_indices)

    # Get link and score pair from the corresponding source
    top_links = [{"link": links[i], "score": scores[i]} for i in top_indices]
    feed_top_links = [{"link": feed_links[i], "score": feed_scores[i]} for i in feed_top_indices]

    # Concatenate the two top links
    top_links.extend(feed_top_links)
    # print(top_links)

    # Return the top k links sorted by score
    return sorted(top_links, key=lambda x: x["score"], reverse=True)[:top_k]
