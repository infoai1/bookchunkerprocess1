# app.py

import streamlit as st
import config
from improvement5 import enrich_chapters_chunks
from improvement4 import generate_chunk_embeddings

# Page setup
st.set_page_config(page_title="Chapter & Chunk Enricher", layout="wide")
st.title("📑 Chapter & Chunk Enricher")

# 1) Paste your API key
api_key = st.text_input("🔑 Paste your API Key", type="password")
if not api_key:
    st.warning("An API Key is required to proceed.")
    st.stop()

# 2) Choose your models
CHAT_MODELS = {
    "DeepSeek Reasoner": (config.DEEPSEEK_MODEL, config.DEEPSEEK_API_URL),
    "OpenAI GPT":        (config.MODEL_NAME,    config.API_URL),
    "Anthropic Claude":  (config.ANTHROPIC_MODEL, config.ANTHROPIC_API_URL),
    "Google Gemini Pro": (config.GEMINI_MODEL,  config.GEMINI_API_URL),
}
EMBED_MODELS = {
    "Small Embedding": (config.EMBEDDING_MODEL, config.EMBEDDING_API_URL),
}

chat_choice  = st.selectbox("🤖 Choose Chat Model",      list(CHAT_MODELS.keys()))
embed_choice = st.selectbox("🔎 Choose Embedding Model", list(EMBED_MODELS.keys()))

st.markdown(f"**Using Chat Model:** {chat_choice}  \n**Using Embedding:** {embed_choice}")

chat_model, chat_url   = CHAT_MODELS[chat_choice]
embed_model, embed_url = EMBED_MODELS[embed_choice]

# 3) Enrich Chapters & Chunks
st.header("🚀 Enrich Chapters & Chunks")
uploaded1 = st.file_uploader("Upload CSV with 'Detected Title' & 'TEXT CHUNK'", key="step1", type="csv")
if uploaded1 and st.button("Start Enrichment"):
    df_enriched = enrich_chapters_chunks(
        uploaded_file=uploaded1,
        model_name=chat_model,
        api_url=chat_url,
        api_key=api_key
    )
    if df_enriched is not None:
        st.download_button(
            "⬇️ Download Enriched CSV",
            df_enriched.to_csv(index=False).encode("utf-8"),
            file_name="enriched_chapters_chunks.csv",
            mime="text/csv"
        )

# 4) Generate Chunk Embeddings
st.markdown("---")
st.header("🔗 Generate Chunk Embeddings")
uploaded2 = st.file_uploader("Upload enriched CSV (with 'TEXT CHUNK')", key="step2", type="csv")
if uploaded2 and st.button("Generate Embeddings"):
    df_emb = generate_chunk_embeddings(
        uploaded_file=uploaded2,
        embedding_model=embed_model,
        embedding_api_url=embed_url,
        api_key=api_key
    )
    if df_emb is not None:
        st.download_button(
            "⬇️ Download Embeddings CSV",
            df_emb.to_csv(index=False).encode("utf-8"),
            file_name="chunks_with_embeddings.csv",
            mime="text/csv"
        )
