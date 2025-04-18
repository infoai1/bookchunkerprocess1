# improvement5.py

import pandas as pd
import requests
import json
import streamlit as st

def enrich_chapters_chunks(uploaded_file, model_name, api_url, api_key):
    """
    Reads uploaded_file (CSV), enriches by chapter & chunk, returns DataFrame.
    
    Signature matches: enrich_chapters_chunks(file1, chat_model, chat_url, api_key)
    """
    if uploaded_file is None:
        return None

    # Load CSV
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"❌ Failed to read CSV: {e}")
        return None

    # Initialize new columns
    for col in [
        "ChapterSummary","ChapterOutline","ChapterQuestions",
        "Wisdom","Reflections","ChunkOutline","ChunkQuestions"
    ]:
        df[col] = ""

    headers = {"Authorization": f"Bearer {api_key}"}

    def _call_api(prompt: str) -> str:
        resp = requests.post(
            api_url,
            headers=headers,
            json={"model": model_name, "messages":[{"role":"user","content":prompt}]},
            timeout=60
        )
        if resp.status_code != 200:
            raise RuntimeError(resp.text)
        return resp.json()["choices"][0]["message"]["content"]

    # Chapter‑level enrichment
    for title in df["Detected Title"].dropna().unique():
        prompt = (
            f"Summarize chapter '{title}' in 50 words; "
            "list 3–5 outline bullets; then 2 contextual questions in JSON."
        )
        try:
            result = json.loads(_call_api(prompt))
        except Exception as e:
            st.error(f"❌ Chapter '{title}': {e}")
            continue

        mask = df["Detected Title"] == title
        df.loc[mask, "ChapterSummary"]   = result.get("ChapterSummary", "")
        df.loc[mask, "ChapterOutline"]   = json.dumps(result.get("ChapterOutline", []))
        df.loc[mask, "ChapterQuestions"] = json.dumps(result.get("ChapterQuestions", []))

    # Chunk‑level enrichment
    for idx, row in df.iterrows():
        chunk = row.get("TEXT CHUNK", "")
        prompt = (
            f"For this chunk, generate Wisdom, Reflections, "
            f"3–5 outline bullets, and 1 contextual question in JSON. Text: {chunk}"
        )
        try:
            result = json.loads(_call_api(prompt))
        except Exception as e:
            st.error(f"❌ Chunk {idx}: {e}")
            continue

        df.at[idx, "Wisdom"]         = result.get("Wisdom", "")
        df.at[idx, "Reflections"]    = result.get("Reflections", "")
        df.at[idx, "ChunkOutline"]   = json.dumps(result.get("ChunkOutline", []))
        df.at[idx, "ChunkQuestions"]= json.dumps(result.get("ChunkQuestions", []))

    return df
