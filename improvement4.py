import pandas as pd
import openai
import json
import streamlit as st

def generate_chunk_embeddings(uploaded_file, embedding_model, embedding_api_url, api_key):
    if uploaded_file is None:
        return None

    df = pd.read_csv(uploaded_file)
    if "TEXT CHUNK" not in df:
        st.error("Missing 'TEXT CHUNK'")
        return None

    openai.api_key = api_key
    texts = df["TEXT CHUNK"].astype(str).tolist()
    resp = openai.Embedding.create(model=embedding_model, input=texts)
    df["Embedding"] = [e["embedding"] for e in resp.data]
    df["Embedding"] = df["Embedding"].apply(json.dumps)
    return df
