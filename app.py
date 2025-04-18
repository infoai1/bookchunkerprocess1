import os
import streamlit as st
import config
from improvement5 import run_improvement5
from improvement4 import run_improvement4

st.set_page_config(page_title="Chapter & Chunk Enricher", layout="wide")
st.title("📑 Chapter & Chunk Enricher")

# API Key input
api_key = st.text_input("🔑 Enter your API Key", type="password")
if not api_key:
    st.info("Please paste your API key to proceed.")
    st.stop()
headers = {"Authorization": f"Bearer {api_key}"}

# Model dropdowns
CHAT_MODELS = {
    "DeepSeek Reasoner": (config.DEEPSEEK_MODEL, config.DEEPSEEK_API_URL),
    "OpenAI GPT":        (config.MODEL_NAME,    config.API_URL),
    "Anthropic Claude":  (config.ANTHROPIC_MODEL, config.ANTHROPIC_API_URL),
    "Google Gemini Pro": (config.GEMINI_MODEL,  config.GEMINI_API_URL),
}
EMBED_MODELS = {
    "Small Embedding": (config.EMBEDDING_MODEL, config.EMBEDDING_API_URL),
}

# Selections
selected_chat = st.selectbox("🤖 Choose AI Chat Model", list(CHAT_MODELS.keys()))
selected_embed = st.selectbox("🔎 Choose Embedding Model", list(EMBED_MODELS.keys()))

st.markdown(
    f"""**Using Chat Model:** {selected_chat}  
**Using Embedding:** {selected_embed}"""
)

# Unpack endpoints
chat_model, chat_url = CHAT_MODELS[selected_chat]
embed_model, embed_url = EMBED_MODELS[selected_embed]

# --- Enrichment ---
st.header("🚀 Enrich Chapters & Chunks")
uploaded = st.file_uploader("Upload CSV with 'Detected Title' & 'TEXT CHUNK'", type="csv")
if uploaded:
    if st.button("Start Enrichment"):
        enriched_df = run_improvement5(
            uploaded_file=uploaded,
            model_name=chat_model,
            api_url=chat_url,
            api_key=api_key,
            headers=headers,
        )
        if enriched_df is not None:
            st.download_button(
                "⬇️ Download Enriched CSV",
                enriched_df.to_csv(index=False).encode("utf-8"),
                file_name="enriched_chapters_chunks.csv",
                mime="text/csv",
            )

st.markdown("---")
st.header("🔗 Generate Chunk Embeddings")
uploaded2 = st.file_uploader("Upload Enriched CSV (with 'TEXT CHUNK')", key="up2", type="csv")
if uploaded2:
    if st.button("Generate Embeddings"):
        emb_df = run_improvement4(
            uploaded_file=uploaded2,
            embedding_model=embed_model,
            embedding_api_url=embed_url,
            api_key=api_key,
            headers=headers,
        )
        if emb_df is not None:
            st.download_button(
                "⬇️ Download Embeddings CSV",
                emb_df.to_csv(index=False).encode("utf-8"),
                file_name="chunks_with_embeddings.csv",
                mime="text/csv",
            )
```python
import os
import streamlit as st
import config
from improvement5 import run_improvement5
from improvement4 import run_improvement4

st.set_page_config(page_title="Chapter & Chunk Enricher", layout="wide")
st.title("📑 Chapter & Chunk Enricher")

# API Key input
API_KEY = st.text_input("🔑 Enter your API Key", type="password")
if not API_KEY:
    st.info("Please paste your API key to proceed.")
    st.stop()
headers = {"Authorization": f"Bearer {API_KEY}"}

# Chat model selection with endpoints
CHAT_MODELS = {
    "DeepSeek Reasoner": (config.DEEPSEEK_MODEL, config.DEEPSEEK_API_URL),
    "OpenAI GPT":        (config.MODEL_NAME,    config.API_URL),
    "Anthropic Claude":  (config.ANTHROPIC_MODEL, config.ANTHROPIC_API_URL),
    "Google Gemini Pro": (config.GEMINI_MODEL,  config.GEMINI_API_URL),
}
# Embedding model selection
EMBED_MODELS = {
    "Small Embedding": (config.EMBEDDING_MODEL, config.EMBEDDING_API_URL),
}

# Dropdowns
selected_chat = st.selectbox("🤖 Choose AI Chat Model", list(CHAT_MODELS.keys()))
selected_embed = st.selectbox("🔎 Choose Embedding Model", list(EMBED_MODELS.keys()))

st.markdown(
    f"""**Using Chat Model:** {selected_chat}  
**Using Embedding:** {selected_embed}"""
)
**Using Embedding:** {selected_embed}")

# Unpack endpoints
chat_model, chat_url = CHAT_MODELS[selected_chat]
embed_model, embed_url = EMBED_MODELS[selected_embed]

# --- Enrichment ---
st.header("🚀 Enrich Chapters & Chunks")
enriched_df = run_improvement5(
    uploaded_file=st.file_uploader("Upload CSV with 'Detected Title' & 'TEXT CHUNK'", type="csv"),
    model_name=chat_model,
    api_url=chat_url,
    api_key=API_KEY,
    headers=headers
)
if enriched_df is not None:
    st.download_button(
        "⬇️ Download Enriched CSV",
        enriched_df.to_csv(index=False).encode("utf-8"),
        file_name="enriched_chapters_chunks.csv",
        mime="text/csv"
    )

# --- Embeddings ---
st.markdown("---")
st.header("🔗 Generate Chunk Embeddings")
emb_df = run_improvement4(
    uploaded_file=st.file_uploader("Upload Enriched CSV (with 'TEXT CHUNK')", key="up2", type="csv"),
    embedding_model=embed_model,
    embedding_api_url=embed_url,
    api_key=API_KEY,
    headers=headers
)
if emb_df is not None:
    st.download_button(
        "⬇️ Download Embeddings CSV",
        emb_df.to_csv(index=False).encode("utf-8"),
        file_name="chunks_with_embeddings.csv",
        mime="text/csv"
    )
```python
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
