import os
from typing import List
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer


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

    # Save embeddings
    np.save("./data/embeddings.npy", embeddings)
    df.to_csv("./data/links_metadata.csv", index=False)
    print("Embeddings are generated and saved")


def generate_feed_embeddings(model, device):
    # Load and preprocess the links
    df = pd.read_csv("./data/feeds.csv")
    df.drop_duplicates(inplace=True)

    # Generate embeddings
    checkpoint_dir = "checkpoints"
    embeddings = build_embedding(
        df["Description"], model, batch_size=128, device=device, checkpoint_dir=checkpoint_dir
    )

    # Save embeddings
    np.save("./data/feed_embeddings.npy", embeddings)
    print("Embeddings are generated and saved")


if __name__ == "__main__":
    # Load the model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device: {device}")

    model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

    generate_feed_embeddings(model, device)
    generate_link_embeddings(model, device)
