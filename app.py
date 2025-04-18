import os
import streamlit as st
import requests

from improvement5 import run_improvement5
from improvement4 import run_improvement4
import config

# Securely load API key from environment
API_KEY = os.getenv("OPENAI_API_KEY", config.API_KEY)
headers = {"Authorization": f"Bearer {API_KEY}"}

# Page setup
st.set_page_config(page_title="Chapter & Chunk Enricher", layout="wide")
st.title("📑 Chapter & Chunk Enricher")

st.markdown(
    """
This app processes your CSV with 'Detected Title' and 'TEXT CHUNK':

1. Enrich Chapters
2. Enrich Chunks
3. Generate Embeddings for each chunk
""",
    unsafe_allow_html=True
)

# Step 1 & 2: Chapter & Chunk enrichment
st.markdown("---")
st.header("🚀 Enrich Chapters & Chunks")
run_improvement5(
    model_name=config.MODEL_NAME,
    api_url=config.API_URL,
    api_key=API_KEY,
    headers=headers
)

# Step 3: Embeddings
st.markdown("---")
st.header("🔗 Generate Chunk Embeddings")
run_improvement4(
    embedding_model=config.EMBEDDING_MODEL,
    embedding_api_url=config.EMBEDDING_API_URL,
    api_key=API_KEY,
    headers=headers
)
