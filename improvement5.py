# improvement5.py

import pandas as pd
import requests
import json
import streamlit as st

def run_improvement5(uploaded_file, model_name, api_url, api_key, headers):
    """
    Enrich CSV by chapter & chunk, supporting both OpenAI‐style and Gemini.
    """
    if uploaded_file is None:
        return None

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        return None

    # prepare columns
    for col in ["ChapterSummary","ChapterOutline","ChapterQuestions",
                "Wisdom","Reflections","ChunkOutline","ChunkQuestions"]:
        df[col] = ""

    def _call_api(prompt: str) -> str:
        # Google Gemini branch
        if "generativelanguage.googleapis.com" in api_url:
            url = f"{api_url}?key={api_key}"
            payload = {"contents":[{"parts":[{"text": prompt}]}]}
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API error: {resp.text}")
            return resp.json()["candidates"][0]["content"]
        # OpenAI‐compatible branch (DeepSeek, OpenAI, Anthropic)
        else:
            resp = requests.post(
                api_url,
                headers=headers,
                json={"model": model_name, "messages":[{"role":"user","content":prompt}]},
                timeout=60
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Chat API error: {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    # Chapter‐level enrichment
    for title in df["Detected Title"].dropna().unique():
        prompt = (
            f"Summarize chapter '{title}' in 50 words; "
            "list 3–5 outline bullets; then 2 contextual questions in JSON."
        )
        try:
            content = _call_api(prompt)
            result = json.loads(content)
        except Exception as e:
            st.error(f"Error for chapter '{title}': {e}")
            continue

        mask = df["Detected Title"] == title
        df.loc[mask, "ChapterSummary"]   = result.get("ChapterSummary","")
        df.loc[mask, "ChapterOutline"]   = json.dumps(result.get("ChapterOutline",[]))
        df.loc[mask, "ChapterQuestions"] = json.dumps(result.get("ChapterQuestions",[]))

    # Chunk‐level enrichment
    for idx, row in df.iterrows():
        chunk = row.get("TEXT CHUNK","")
        prompt = (
            f"For this chunk, generate Wisdom, Reflections, "
            f"3–5 outline bullets, and 1 contextual question in JSON. Text: {chunk}"
        )
        try:
            content = _call_api(prompt)
            result = json.loads(content)
        except Exception as e:
            st.error(f"Error for chunk {idx}: {e}")
            continue

        df.at[idx, "Wisdom"]        = result.get("Wisdom","")
        df.at[idx, "Reflections"]   = result.get("Reflections","")
        df.at[idx, "ChunkOutline"]  = json.dumps(result.get("ChunkOutline",[]))
        df.at[idx, "ChunkQuestions"]= json.dumps(result.get("ChunkQuestions",[]))

    return df
