import pandas as pd
import openai
import json

def run_improvement4(uploaded_file, embedding_model: str, embedding_api_url: str, api_key: str, headers: dict):
    df = pd.read_csv(uploaded_file)
    texts = df["TEXT CHUNK"].astype(str).tolist()

    openai.api_key = api_key
    response = openai.Embedding.create(model=embedding_model, input=texts)
    df["Embedding"] = [item["embedding"] for item in response.data]
    df["Embedding"] = df["Embedding"].apply(json.dumps)

    return df
