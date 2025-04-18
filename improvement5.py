import pandas as pd
import requests
import json
import streamlit as st

def enrich_chapters_chunks(uploaded_file, model_name: str, api_url: str, api_key: str):
    """
    Reads uploaded_file (CSV), enriches by chapter & chunk, returns DataFrame.
    """
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        return None

    # Prepare columns
    for col in ["ChapterSummary","ChapterOutline","ChapterQuestions",
                "Wisdom","Reflections","ChunkOutline","ChunkQuestions"]:
        df[col] = ""

    headers = {"Authorization": f"Bearer {api_key}"}

    # Chapter-level
    for title in df["Detected Title"].dropna().unique():
        prompt = (
            f"Summarize chapter '{title}' in 50 words; "
            "list 3–5 bullet points as an outline; then 2 contextual questions."
        )
        resp = requests.post(
            api_url,
            headers=headers,
            json={"model": model_name, "messages":[{"role":"user","content":prompt}]},
            timeout=60
        )
        if resp.status_code != 200:
            st.error(f"API error for chapter '{title}': {resp.text}")
            continue
        try:
            result = json.loads(resp.json()["choices"][0]["message"]["content"])
        except Exception as e:
            st.error(f"Parse error for chapter '{title}': {e}")
            continue

        mask = df["Detected Title"] == title
        df.loc[mask, "ChapterSummary"]   = result.get("ChapterSummary", "")
        df.loc[mask, "ChapterOutline"]   = json.dumps(result.get("ChapterOutline", []))
        df.loc[mask, "ChapterQuestions"] = json.dumps(result.get("ChapterQuestions", []))

    # Chunk-level
    for idx, row in df.iterrows():
        chunk = row.get("TEXT CHUNK", "")
        prompt = (
            f"For this text chunk, generate Wisdom, Reflections, "
            f"3–5 outline bullets, and 1 contextual question. Text: {chunk}"
        )
        resp = requests.post(
            api_url,
            headers=headers,
            json={"model": model_name, "messages":[{"role":"user","content":prompt}]},
            timeout=60
        )
        if resp.status_code != 200:
            st.error(f"API error for chunk {idx}: {resp.text}")
            continue
        try:
            result = json.loads(resp.json()["choices"][0]["message"]["content"])
        except Exception as e:
            st.error(f"Parse error for chunk {idx}: {e}")
            continue

        df.at[idx, "Wisdom"]        = result.get("Wisdom", "")
        df.at[idx, "Reflections"]   = result.get("Reflections", "")
        df.at[idx, "ChunkOutline"]  = json.dumps(result.get("ChunkOutline", []))
        df.at[idx, "ChunkQuestions"]= json.dumps(result.get("ChunkQuestions", []))

    return df
