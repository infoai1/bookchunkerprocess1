import streamlit as st
import pandas as pd
import requests
import json

def run_improvement5(model_name: str, api_url: str, api_key: str, headers: dict):
    st.file_uploader("Upload CSV with 'Detected Title' & 'TEXT CHUNK'", type="csv", key="up5")
    if st.button("Start Enrichment", key="btn5"):
        uploaded = st.session_state["up5"]
        df = pd.read_csv(uploaded)
        # New columns
        df["ChapterSummary"] = ""
        df["ChapterOutline"] = ""
        df["ChapterQuestions"] = ""
        df["Wisdom"] = ""
        df["Reflections"] = ""
        df["ChunkOutline"] = ""
        df["ChunkQuestions"] = ""

        # Chapter-level
        for title in df['Detected Title'].unique():
            prompt = (
                f"Summarize chapter '{title}' in 50 words; list 3–5 outline bullets; 2 contextual questions."
            )
            res = requests.post(api_url, headers=headers,
                                json={"model": model_name,
                                      "messages":[{"role":"user","content":prompt}]})
            result = json.loads(res.json()['choices'][0]['message']['content'])
            mask = df['Detected Title']==title
            df.loc[mask, 'ChapterSummary']   = result.get('ChapterSummary', '')
            df.loc[mask, 'ChapterOutline']   = json.dumps(result.get('ChapterOutline', []))
            df.loc[mask, 'ChapterQuestions'] = json.dumps(result.get('ChapterQuestions', []))

        # Chunk-level
        for idx, row in df.iterrows():
            chunk = row['TEXT CHUNK']
            prompt = (
                f"For this chunk, generate Wisdom, Reflections, 3–5 outline bullets, and 1 question. Text: {chunk}"
            )
            res = requests.post(api_url, headers=headers,
                                json={"model": model_name,
                                      "messages":[{"role":"user","content":prompt}]})
            result = json.loads(res.json()['choices'][0]['message']['content'])
            df.at[idx, 'Wisdom']          = result.get('Wisdom','')
            df.at[idx, 'Reflections']     = result.get('Reflections','')
            df.at[idx, 'ChunkOutline']    = json.dumps(result.get('ChunkOutline', []))
            df.at[idx, 'ChunkQuestions']  = json.dumps(result.get('ChunkQuestions', []))

        st.download_button(
            "Download Enriched CSV",
            df.to_csv(index=False).encode('utf-8'),
            file_name='enriched_chapters_chunks.csv',
            mime='text/csv'
        )
