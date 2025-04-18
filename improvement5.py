import pandas as pd
import requests
import json

def run_improvement5(uploaded_file, model_name: str, api_url: str, api_key: str):
    df = pd.read_csv(uploaded_file)

    # Prepare columns
    for col in ["ChapterSummary","ChapterOutline","ChapterQuestions",
                "Wisdom","Reflections","ChunkOutline","ChunkQuestions"]:
        df[col] = ""

    # Chapter‐level
    for title in df["Detected Title"].unique():
        prompt = (
            f"Summarize chapter '{title}' in 50 words; "
            "list 3–5 outline bullets; 2 contextual questions."
        )
        resp = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model_name, "messages":[{"role":"user","content":prompt}]},
            timeout=60,
        )
        data = resp.json()
        if resp.status_code != 200 or "choices" not in data:
            continue
        result = json.loads(data["choices"][0]["message"]["content"])
        mask = df["Detected Title"] == title
        df.loc[mask, "ChapterSummary"]   = result.get("ChapterSummary", "")
        df.loc[mask, "ChapterOutline"]   = json.dumps(result.get("ChapterOutline", []))
        df.loc[mask, "ChapterQuestions"] = json.dumps(result.get("ChapterQuestions", []))

    # Chunk‐level
    for i, row in df.iterrows():
        chunk = row.get("TEXT CHUNK", "")
        prompt = (
            f"For this chunk, generate Wisdom, Reflections, 3–5 outline bullets, "
            f"and 1 contextual question. Text: {chunk}"
        )
        resp = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model_name, "messages":[{"role":"user","content":prompt}]},
            timeout=60,
        )
        data = resp.json()
        if resp.status_code != 200 or "choices" not in data:
            continue
        result = json.loads(data["choices"][0]["message"]["content"])
        df.at[i, "Wisdom"]        = result.get("Wisdom", "")
        df.at[i, "Reflections"]   = result.get("Reflections", "")
        df.at[i, "ChunkOutline"]  = json.dumps(result.get("ChunkOutline", []))
        df.at[i, "ChunkQuestions"]= json.dumps(result.get("ChunkQuestions", []))

    return df
