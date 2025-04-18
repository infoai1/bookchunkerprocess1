import os
import streamlit as st
import requests

from improvement5 import run_improvement5
from improvement4 import run_improvement4
import config

# Securely load API key
API_KEY = os.getenv("OPENAI_API_KEY", config.API_KEY)
headers = {"Authorization": f"Bearer {API_KEY}"}

# Chat model selection with endpoints
CHAT_MODELS = {
    "DeepSeek Reasoner": {"model_name": config.DEEPSEEK_MODEL, "api_url": config.DEEPSEEK_API_URL},
    "OpenAI GPT": {"model_name": config.MODEL_NAME, "api_url": config.API_URL},
    "Anthropic Claude": {"model_name": config.ANTHROPIC_MODEL, "api_url": config.ANTHROPIC_API_URL},
    "Google Gemini Pro": {"model_name": config.GEMINI_MODEL, "api_url": config.GEMINI_API_URL},
}

# Embedding model selection
EMBED_MODELS = {
    "Small Embedding": {"model": config.EMBEDDING_MODEL, "api_url": config.EMBEDDING_API_URL},
}

# Page setup
st.set_page_config(page_title="Chapter & Chunk Enricher", layout="wide")
st.title("📑 Chapter & Chunk Enricher")

# Dropdowns for API selection
st.selectbox("🤖 Choose AI Chat Model", options=list(CHAT_MODELS.keys()), key="sel_chat")
st.selectbox("🔎 Choose Embedding Model", options=list(EMBED_MODELS.keys()), key="sel_embed")

selected_chat = st.session_state.sel_chat
chat_cfg = CHAT_MODELS[selected_chat]
selected_embed = st.session_state.sel_embed
embed_cfg = EMBED_MODELS[selected_embed]

st.markdown(
    f"""
This app processes your CSV with 'Detected Title' and 'TEXT CHUNK' via **{selected_chat}**:

1. Enrich Chapters & Chunks
2. Generate Embeddings with **{selected_embed}**
""",
    unsafe_allow_html=True
)

# Step: Chapter & Chunk enrichment
st.markdown("---")
st.header("🚀 Enrich Chapters & Chunks")
run_improvement5(
    model_name=chat_cfg["model_name"],
    api_url=chat_cfg["api_url"],
    api_key=API_KEY,
    headers=headers
)

# Step: Embeddings
st.markdown("---")
st.header("🔗 Generate Chunk Embeddings")
run_improvement4(
    embedding_model=embed_cfg["model"],
    embedding_api_url=embed_cfg["api_url"],
    api_key=API_KEY,
    headers=headers
)
