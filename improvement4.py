import pandas as pd
import openai

def run_improvement4(uploaded_file, embedding_model: str, embedding_api_url: str, api_key: str):
    df = pd.read_csv(uploaded_file)
    texts = df["TEXT CHUNK"].astype(str).tolist()

    openai.api_key = api_key
    resp = openai.Embedding.create(model=embedding_model, input=texts)
    df["Embedding"] = [item["embedding"] for item in resp.data]
    df["Embedding"] = df["Embedding"].apply(json.dumps)

    return df
