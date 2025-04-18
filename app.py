# improvement5.py

import pandas as pd
import requests
import json
import streamlit as st

def run_improvement5(uploaded_file, model_name: str, api_url: str, api_key: str, headers: dict):
    """
    uploaded_file: the Streamlit uploader return
    model_name, api_url, api_key, headers: from app.py
    Returns: enriched DataFrame or None
    """
    if uploaded_file is None:
        return None

    # Load CSV
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"❌ Failed to read uploaded CSV: {e}")
        return None

    # Prepare new columns
    for col in [
        "ChapterSummary","ChapterOutline","ChapterQuestions",
        "Wisdom","Reflections","ChunkOutline","ChunkQuestions"
    ]:
        df[col] = ""

    # Chapter‐level enrichment
    for title in df["Detected Title"].dropna().unique():
        prompt = (
            f"Summarize chapter '{title}' in 50 words; "
            "list 3–5 outline bullets; provide 2 contextual questions."
        )
        try:
            resp = requests.post(
                api_url,
                headers=headers,
                json={
                  "model": model_name,
                  "messages": [{"role": "user", "content": prompt}]
                },
                timeout=60
            )
            data = resp.json()
        except Exception as e:
            st.error(f"❌ API request failed for chapter '{title}': {e}")
            continue

        if resp.status_code != 200 or "choices" not in data:
            st.error(f"❌ API error for chapter '{title}': {data}")
            continue

        try:
            result = json.loads(data["choices"][0]["message"]["content"])
        except Exception as e:
            st.error(f"❌ JSON parse error for chapter '{title}': {e}")
            continue

        mask = df["Detected Title"] == title
        df.loc[mask, "ChapterSummary"]   = result.get("ChapterSummary", "")
        df.loc[mask, "ChapterOutline"]   = json.dumps(result.get("ChapterOutline", []))
        df.loc[mask, "ChapterQuestions"] = json.dumps(result.get("ChapterQuestions", []))

    # Chunk‐level enrichment
    for idx, row in df.iterrows():
        chunk_text = row.get("TEXT CHUNK", "")
        prompt = (
            f"For this text chunk, generate Wisdom, Reflections, "
            f"3–5 outline bullets, and 1 contextual question. Text: {chunk_text}"
        )
        try:
            resp = requests.post(
                api_url,
                headers=headers,
                json={
                  "model": model_name,
                  "messages": [{"role": "user", "content": prompt}]
                },
                timeout=60
            )
            data = resp.json()
        except Exception as e:
            st.error(f"❌ API request failed for chunk at row {idx}: {e}")
            continue

        if resp.status_code != 200 or "choices" not in data:
            st.error(f"❌ API error for chunk at row {idx}: {data}")
            continue

        try:
            result = json.loads(data["choices"][0]["message"]["content"])
        except Exception as e:
            st.error(f"❌ JSON parse error for chunk at row {idx}: {e}")
            continue

        df.at[idx, "Wisdom"]         = result.get("Wisdom", "")
        df.at[idx, "Reflections"]    = result.get("Reflections", "")
        df.at[idx, "ChunkOutline"]   = json.dumps(result.get("ChunkOutline", []))
        df.at[idx, "ChunkQuestions"] = json.dumps(result.get("ChunkQuestions", []))

    return df
