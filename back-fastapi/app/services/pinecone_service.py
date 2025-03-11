from pinecone import Pinecone, ServerlessSpec

from ..constants import PINECONE_API_KEY

pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "gossip_search_engine"

pc.create_index(
    name=index_name, dimension=2, metric=2, spec=ServerlessSpec(cloud="aws", region="us-east-1")
)
