import streamlit as st
import config
from improvement5 import enrich_chapters_chunks
from improvement4 import generate_chunk_embeddings

st.set_page_config(page_title="Chapter & Chunk Enricher", layout="wide")
st.title("📑 Chapter & Chunk Enricher")

# API key
api_key = st.text_input("🔑 Paste your API Key", type="password")
if not api_key:
    st.warning("API Key required.")
    st.stop()

# Model picks
CHAT = {
  "DeepSeek Reasoner": (config.DEEPSEEK_MODEL, config.DEEPSEEK_API_URL),
  "OpenAI GPT":        (config.MODEL_NAME,      config.API_URL),
  "Anthropic Claude":  (config.ANTHROPIC_MODEL, config.ANTHROPIC_API_URL),
  "Google Gemini Pro": (config.GEMINI_MODEL,    config.GEMINI_API_URL),
}
EMB = {
  "Small Embedding":   (config.EMBEDDING_MODEL, config.EMBEDDING_API_URL),
}

chat_choice  = st.selectbox("🤖 Chat Model",      list(CHAT.keys()))
embed_choice = st.selectbox("🔎 Embedding Model", list(EMB.keys()))

st.write(f"**Using:** {chat_choice} → {embed_choice}")

cm, cu = CHAT[chat_choice]
em, eu = EMB[embed_choice]

# Enrichment
st.header("🚀 Enrich Chapters & Chunks")
f1 = st.file_uploader("CSV with 'Detected Title' & 'TEXT CHUNK'", key="f1", type="csv")
if f1 and st.button("Start Enrichment"):
    df1 = enrich_chapters_chunks(f1, cm, cu, api_key)
    if df1 is not None:
        st.download_button("Download Enriched CSV", df1.to_csv(index=False).encode(), "enriched.csv")

# Embeddings
st.markdown("---")
st.header("🔗 Generate Chunk Embeddings")
f2 = st.file_uploader("Upload enriched CSV", key="f2", type="csv")
if f2 and st.button("Generate Embeddings"):
    df2 = generate_chunk_embeddings(f2, em, eu, api_key)
    if df2 is not None:
        st.download_button("Download Embeddings CSV", df2.to_csv(index=False).encode(), "embeddings.csv")
