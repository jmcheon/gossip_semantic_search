import requests
import streamlit as st

st.title("Gossip Semantic Search")

query = st.text_input("Search", "")

BACKEND_URL = "http://localhost:8000/search"

if st.button("Search") and query:
    try:
        response = requests.post(BACKEND_URL, json={"query": query, "top_k": 5})
        response.raise_for_status()
        results = response.json()

        st.write("Results: Link - Score")
        if results:
            for result in results:
                st.write(f"{result['link']} - {result['score']}")
        else:
            st.write("No results found.")
    except Exception as e:
        st.error(f"Error: {e}")
