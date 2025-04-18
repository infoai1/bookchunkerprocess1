import pandas as pd
import openai
import json
import streamlit as st

def generate_chunk_embeddings(uploaded_file, embedding_model, embedding_api_url, api_key):
    """
    Reads enriched CSV, generates embeddings for 'TEXT CHUNK', returns DataFrame.
    """
    if uploaded_file is None:
        return None

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"❌ Failed to read CSV for embeddings: {e}")
        return None

    if "TEXT CHUNK" not in df:
        st.error("❌ Missing 'TEXT CHUNK' column")
        return None

    openai.api_key = api_key
    texts = df["TEXT CHUNK"].astype(str).tolist()
    resp = openai.Embedding.create(model=embedding_model, input=texts)
    df["Embedding"] = [item["embedding"] for item in resp.data]
    df["Embedding"] = df["Embedding"].apply(json.dumps)
    return df
