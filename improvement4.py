import pandas as pd
import openai
import json
import streamlit as st

def generate_chunk_embeddings(uploaded_file, embedding_model: str, embedding_api_url: str, api_key: str):
    """
    Reads enriched CSV, generates embeddings for TEXT CHUNK, returns DataFrame.
    """
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read CSV for embeddings: {e}")
        return None

    if "TEXT CHUNK" not in df.columns:
        st.error("Missing 'TEXT CHUNK' column")
        return None

    openai.api_key = api_key
    texts = df["TEXT CHUNK"].astype(str).tolist()
    try:
        resp = openai.Embedding.create(model=embedding_model, input=texts)
    except Exception as e:
        st.error(f"Embedding API error: {e}")
        return None

    df["Embedding"] = [item["embedding"] for item in resp.data]
    df["Embedding"] = df["Embedding"].apply(json.dumps)
    return df
