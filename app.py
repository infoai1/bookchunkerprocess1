import streamlit as st
import config
from improvement5 import run_improvement5
from improvement4 import generate_chunk_embeddings

st.set_page_config(page_title="Chapter & Chunk Enricher", layout="wide")
st.title("📑 Chapter & Chunk Enricher")

# 1) API Key
api_key = st.text_input("🔑 Paste your API Key", type="password")
if not api_key:
    st.warning("API Key is required.") 
    st.stop()

# 2) Model selections
CHAT_MODELS = {
    "DeepSeek Reasoner": (config.DEEPSEEK_MODEL,    config.DEEPSEEK_API_URL),
    "OpenAI GPT":        (config.MODEL_NAME,        config.API_URL),
    "Anthropic Claude":  (config.ANTHROPIC_MODEL,   config.ANTHROPIC_API_URL),
    "Google Gemini Pro": (config.GEMINI_MODEL,      config.GEMINI_API_URL),
}
EMBED_MODELS = {
    "Small Embedding":   (config.EMBEDDING_MODEL,   config.EMBEDDING_API_URL),
}

chat_choice  = st.selectbox("🤖 Choose Chat Model",      list(CHAT_MODELS.keys()))
embed_choice = st.selectbox("🔎 Choose Embedding Model", list(EMBED_MODELS.keys()))

st.markdown(f"**Using Chat:** {chat_choice}  \n**Embedding:** {embed_choice}")

chat_model, chat_url   = CHAT_MODELS[chat_choice]
embed_model, embed_url = EMBED_MODELS[embed_choice]

# 3) Enrichment
st.header("🚀 Enrich Chapters & Chunks")
file1 = st.file_uploader("Upload CSV with 'Detected Title' & 'TEXT CHUNK'", key="step1", type="csv")
if file1 and st.button("Start Enrichment"):
    df1 = run_improvement5(file1, chat_model, chat_url, api_key)
    if df1 is not None:
        st.download_button(
            "⬇️ Download Enriched CSV",
            df1.to_csv(index=False).encode("utf-8"),
            file_name="enriched_chapters_chunks.csv",
            mime="text/csv"
        )

# 4) Embeddings
st.markdown("---")
st.header("🔗 Generate Chunk Embeddings")
file2 = st.file_uploader("Upload enriched CSV", key="step2", type="csv")
if file2 and st.button("Generate Embeddings"):
    df2 = generate_chunk_embeddings(file2, embed_model, embed_url, api_key)
    if df2 is not None:
        st.download_button(
            "⬇️ Download Embeddings CSV",
            df2.to_csv(index=False).encode("utf-8"),
            file_name="chunks_with_embeddings.csv",
            mime="text/csv"
        )
