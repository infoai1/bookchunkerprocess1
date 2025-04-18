import pandas as pd
import requests
import json
import streamlit as st

def enrich_chapters_chunks(uploaded_file, model_name, api_url, api_key):
    if uploaded_file is None:
        return None

    df = pd.read_csv(uploaded_file)
    # init
    for col in ["ChapterSummary","ChapterOutline","ChapterQuestions",
                "Wisdom","Reflections","ChunkOutline","ChunkQuestions"]:
        df[col] = ""

    headers = {"Authorization": f"Bearer {api_key}"}

    def _call(prompt: str) -> str:
        # Gemini branch
        if "generativelanguage.googleapis.com" in api_url:
            url = f"{api_url}?key={api_key}"
            payload = {"contents":[{"parts":[{"text": prompt}]}]}
            r = requests.post(url, json=payload, timeout=60)
            if r.status_code != 200:
                raise RuntimeError(r.text)
            return r.json()["candidates"][0]["content"]
        # Other OpenAI‑compatible
        r = requests.post(
            api_url,
            headers=headers,
            json={"model": model_name, "messages":[{"role":"user","content":prompt}]},
            timeout=60
        )
        if r.status_code != 200:
            raise RuntimeError(r.text)
        return r.json()["choices"][0]["message"]["content"]

    # Chapter‐level
    for title in df["Detected Title"].dropna().unique():
        prompt = (
            f"Summarize chapter '{title}' in 50 words; "
            "provide 3–5 outline bullets; then 2 JSON questions."
        )
        try:
            content = _call(prompt)
            result = json.loads(content)
        except Exception as e:
            st.error(f"Chapter '{title}': {e}")
            continue
        m = df["Detected Title"] == title
        df.loc[m,"ChapterSummary"]   = result.get("ChapterSummary","")
        df.loc[m,"ChapterOutline"]   = json.dumps(result.get("ChapterOutline",[]))
        df.loc[m,"ChapterQuestions"] = json.dumps(result.get("ChapterQuestions",[]))

    # Chunk‐level
    for i,row in df.iterrows():
        chunk = row.get("TEXT CHUNK","")
        prompt = (
            f"For this chunk, generate Wisdom, Reflections, 3–5 outline bullets, "
            f"and 1 JSON question. Text: {chunk}"
        )
        try:
            content = _call(prompt)
            result = json.loads(content)
        except Exception as e:
            st.error(f"Chunk {i}: {e}")
            continue
        df.at[i,"Wisdom"]        = result.get("Wisdom","")
        df.at[i,"Reflections"]   = result.get("Reflections","")
        df.at[i,"ChunkOutline"]  = json.dumps(result.get("ChunkOutline",[]))
        df.at[i,"ChunkQuestions"]= json.dumps(result.get("ChunkQuestions",[]))

    return df
