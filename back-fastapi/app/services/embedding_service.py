import os
from typing import List
from urllib.parse import urlparse

import numpy as np
import pandas as pd

from ..dependencies import index


def preprocess_link(link):
    """
    Process a link to extract the meaningful text in the url
    """

    path = urlparse(link).path

    # Extract the last segment of the link
    segment = path.split("/")[-1]

    # If the segment is empty, use the path
    if not segment.strip():
        # print(f"link: {link}\npath.strip('/'): {path.strip('/')}\n\n")
        segment = path.strip("/")
    return segment.replace("-", " ").strip()


def build_embedding(
    df, model, batch_size=64, device="cpu", checkpoint_dir=None
) -> List[np.ndarray]:
    """
    Generate embeddings for the processed text.
    """
    embeddings = []

    if checkpoint_dir and not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)

    for i in range(0, len(df), batch_size):
        batch = df.iloc[i : i + batch_size]
        print(batch)

        if checkpoint_dir:
            checkpoint_path = os.path.join(checkpoint_dir, f"batch_{i}.npy")
            if os.path.exists(checkpoint_path):
                # print(f"Loading checkpoint for batch {i}...")
                batch_embeddings = np.load(checkpoint_path)
            else:
                # print(f"Batch {i}...")
                batch_embeddings = model.encode(
                    batch.tolist(), convert_to_tensor=False, device=device, show_progress_bar=False
                )
                np.save(checkpoint_path, batch_embeddings)
        else:
            # print(f"Batch {i}...")
            batch_embeddings = model.encode(
                batch.tolist(), convert_to_tensor=False, device=device, show_progress_bar=False
            )
        embeddings.extend(batch_embeddings)

    return embeddings


def upsert_to_pinecone(embeddings, metadata_list, namespace="default", batch_size=200):
    """
    Upsert embeddings to Pinecone with metadata
    """
    vectors = [(str(i), embeddings[i], metadata_list[i]) for i in range(len(embeddings))]
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        index.upsert(vectors=batch, namespace=namespace)
    return {"message": f"{len(embeddings)} {namespace} embeddings upserted to pinecone"}


def generate_link_embeddings(model, device):
    # Load and preprocess the links
    df = pd.read_csv("./data/links.csv")
    df.drop_duplicates(inplace=True)
    df["processed_text"] = df["link"].apply(preprocess_link)

    # Remove public.fr and vsd.fr links
    df = df[df["processed_text"].str.strip() != ""]

    # Generate embeddings
    checkpoint_dir = "checkpoints"
    embeddings = build_embedding(
        df["processed_text"], model, batch_size=128, device=device, checkpoint_dir=checkpoint_dir
    )

    metadata = [{"text": text} for text in df["processed_text"].tolist()]

    # # Save embeddings
    # np.save("./data/embeddings.npy", embeddings)
    # df.to_csv("./data/links_metadata.csv", index=False)
    # print("Embeddings are generated and saved")
    return upsert_to_pinecone(embeddings, metadata, namespace="links")


def generate_feed_embeddings(model, device):
    # Load and preprocess the links
    df = pd.read_csv("./data/feeds.csv")
    df.drop_duplicates(inplace=True)

    # Generate embeddings
    checkpoint_dir = "feed_checkpoints"
    embeddings = build_embedding(
        df["Description"], model, batch_size=128, device=device, checkpoint_dir=checkpoint_dir
    )

    metadata = [{"text": text} for text in df["Description"].tolist()]

    # # Save embeddings
    # np.save("./data/feed_embeddings.npy", embeddings)
    # print("Embeddings are generated and saved")
    return upsert_to_pinecone(embeddings, metadata, namespace="feeds")
