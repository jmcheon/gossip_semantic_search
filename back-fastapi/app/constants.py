import os

from dotenv import load_dotenv

load_dotenv()

# API KEYS
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

#
VECTOR_DIMENSIONS=365
