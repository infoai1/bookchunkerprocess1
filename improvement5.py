import pandas as pd
import requests
import json
import streamlit as st

def run_improvement5(uploaded_file, model_name, api_url, api_key):
    """
    Reads uploaded_file (CSV), enriches by chapter & chunk, returns DataFrame.
    """
    if uploaded_file is None:
        return None

    # 1) Load CSV
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"❌ Failed to read CSV: {e}")
        return None

    # 2) Initialize new columns
    for col in [
        "ChapterSummary","ChapterOutline","ChapterQuestions",
        "Wisdom","Reflections","ChunkOutline","ChunkQuestions"
    ]:
        df[col] = ""

    headers = {"Authorization": f"Bearer {api_key}"}

    def _call_api(prompt: str) -> str:
        # Google Gemini:
        if "generativelanguage.googleapis.com" in api_url:
            url = f"{api_url}?key={api_key}"
            payload = {"contents":[{"parts":[{"text": prompt}]}]}
            r = requests.post(url, json=payload, timeout=60)
            if r.status_code != 200:
                raise RuntimeError(r.text)
            return r.json()["candidates"][0]["content"]
        # OpenAI‐compatible (DeepSeek, OpenAI, Anthropic):
        r = requests.post(
            api_url,
            headers=headers,
            json={"model": model_name, "messages":[{"role":"user","content":prompt}]},
            timeout=60
        )
        if r.status_code != 200:
            raise RuntimeError(r.text)
        return r.json()["choices"][0]["message"]["content"]

    # 3) Chapter‐level enrichment
    for title in df.get("Detected Title", pd.Series()).dropna().unique():
        prompt = (
            f"Summarize chapter '{title}' in 50 words; "
            "provide 3–5 outline bullets; then 2 contextual questions as JSON."
        )
        try:
            content = _call_api(prompt).strip()
            result = json.loads(content)
        except Exception as e:
            st.error(f"❌ Chapter '{title}': {e}")
            continue

        mask = df["Detected Title"] == title
        df.loc[mask, "ChapterSummary"]   = result.get("ChapterSummary","")
        df.loc[mask, "ChapterOutline"]   = json.dumps(result.get("ChapterOutline",[]))
        df.loc[mask, "ChapterQuestions"] = json.dumps(result.get("ChapterQuestions",[]))

    # 4) Chunk‐level enrichment
    for idx, row in df.iterrows():
        chunk = row.get("TEXT CHUNK","")
        prompt = (
            f"For this chunk, generate Wisdom, Reflections, 3–5 outline bullets, "
            f"and 1 contextual question as JSON. Text: {chunk}"
        )
        try:
            content = _call_api(prompt).strip()
            result = json.loads(content)
        except Exception as e:
            st.error(f"❌ Chunk {idx}: {e}")
            continue

        df.at[idx, "Wisdom"]         = result.get("Wisdom","")
        df.at[idx, "Reflections"]    = result.get("Reflections","")
        df.at[idx, "ChunkOutline"]   = json.dumps(result.get("ChunkOutline",[]))
        df.at[idx, "ChunkQuestions"] = json.dumps(result.get("ChunkQuestions",[]))

    return df
