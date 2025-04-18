import streamlit as st
import pandas as pd
import openai
import json

def run_improvement4(embedding_model: str, embedding_api_url: str, api_key: str, headers: dict):
    st.file_uploader("Upload enriched CSV (with 'TEXT CHUNK')", type="csv", key="up4")
    if st.button("Generate Embeddings", key="btn4"):
        uploaded = st.session_state["up4"]
        df = pd.read_csv(uploaded)
        openai.api_key = api_key
        texts = df['TEXT CHUNK'].astype(str).tolist()
        response = openai.Embedding.create(model=embedding_model, input=texts)
        embeddings = [e['embedding'] for e in response.data]
        df['Embedding'] = embeddings
        df['Embedding'] = df['Embedding'].apply(json.dumps)
        st.download_button(
            "Download Embeddings CSV",
            df.to_csv(index=False).encode('utf-8'),
            file_name='chunks_with_embeddings.csv',
            mime='text/csv'
        )
