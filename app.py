import os
import streamlit as st
import config
from improvement5 import run_improvement5
from improvement4 import run_improvement4

st.set_page_config(page_title="Chapter & Chunk Enricher", layout="wide")
st.title("📑 Chapter & Chunk Enricher")

# 1) API key input
api_key = st.text_input("🔑 Paste your API Key", type="password")
if not api_key:
    st.info("Please enter your API key to proceed.")
    st.stop()
headers = {"Authorization": f"Bearer {api_key}"}

# 2) Model dropdowns
CHAT_MODELS = {
    "DeepSeek Reasoner": (config.DEEPSEEK_MODEL, config.DEEPSEEK_API_URL),
    "OpenAI GPT":        (config.MODEL_NAME,    config.API_URL),
    "Anthropic Claude":  (config.ANTHROPIC_MODEL, config.ANTHROPIC_API_URL),
    "Google Gemini Pro": (config.GEMINI_MODEL,  config.GEMINI_API_URL),
}
EMBED_MODELS = {
    "Small Embedding": (config.EMBEDDING_MODEL, config.EMBEDDING_API_URL),
}

selected_chat  = st.selectbox("🤖 Choose Chat Model", list(CHAT_MODELS.keys()))
selected_embed = st.selectbox("🔎 Choose Embedding", list(EMBED_MODELS.keys()))

st.markdown(
    f"""**Using Chat Model:** {selected_chat}  
**Using Embedding:** {selected_embed}"""
)

chat_model, chat_url = CHAT_MODELS[selected_chat]
embed_model, embed_url = EMBED_MODELS[selected_embed]

# 3) Enrichment
st.header("🚀 Enrich Chapters & Chunks")
uploaded = st.file_uploader("Upload CSV with 'Detected Title' & 'TEXT CHUNK'", type="csv")
if uploaded and st.button("Start Enrichment"):
    enriched_df = run_improvement5(
        uploaded_file=uploaded,
        model_name=chat_model,
        api_url=chat_url,
        api_key=api_key,
        headers=headers
    )
    if enriched_df is not None:
        st.download_button(
            "⬇️ Download Enriched CSV",
            enriched_df.to_csv(index=False).encode("utf-8"),
            file_name="enriched_chapters_chunks.csv",
            mime="text/csv"
        )

# 4) Embeddings
st.markdown("---")
st.header("🔗 Generate Chunk Embeddings")
uploaded2 = st.file_uploader("Upload enriched CSV", key="up2", type="csv")
if uploaded2 and st.button("Generate Embeddings"):
    emb_df = run_improvement4(
        uploaded_file=uploaded2,
        embedding_model=embed_model,
        embedding_api_url=embed_url,
        api_key=api_key,
        headers=headers
    )
    if emb_df is not None:
        st.download_button(
            "⬇️ Download Embeddings CSV",
            emb_df.to_csv(index=False).encode("utf-8"),
            file_name="chunks_with_embeddings.csv",
            mime="text/csv"
        )
