import streamlit as st
import pandas as pd
import openai
import json

def run_improvement4(embedding_model: str, embedding_api_url: str, api_key: str, headers: dict):
    # Check API key
    if not api_key or api_key.startswith("YOUR_"):
        st.error("OpenAI API key not set. Set OPENAI_API_KEY env var or update config.py.")
        return

    uploaded = st.file_uploader("Upload enriched CSV (with 'TEXT CHUNK')", type="csv")
    if not uploaded:
        return

    if st.button("Generate Embeddings"):
        try:
            df = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Failed to read CSV: {e}")
            return

        if 'TEXT CHUNK' not in df.columns:
            st.error("CSV missing 'TEXT CHUNK' column.")
            return

        openai.api_key = api_key
        texts = df['TEXT CHUNK'].astype(str).tolist()
        try:
            response = openai.Embedding.create(model=embedding_model, input=texts)
        except Exception as e:
            st.error(f"Embedding API error: {e}")
            return
        embeddings = [e['embedding'] for e in response.data]
        df['Embedding'] = embeddings
        df['Embedding'] = df['Embedding'].apply(json.dumps)

        st.download_button(
            "Download Embeddings CSV",
            df.to_csv(index=False).encode('utf-8'),
            file_name='chunks_with_embeddings.csv',
            mime='text/csv'
        )
