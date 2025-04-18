import streamlit as st
import pandas as pd
import requests
import json

def run_improvement5(model_name, api_url, api_key, headers):
    st.header("📖 Improvement 5: Chapter & Chunk Enrichment")
    uploaded = st.file_uploader("Upload CSV with 'Detected Title' & 'TEXT CHUNK'", type="csv")
    if not uploaded:
        return
    if st.button("🚀 Enrich Chapters & Chunks"):
        df = pd.read_csv(uploaded)
        # initialize new columns
        for col in ["ChapterSummary","ChapterOutline","ChapterQuestions",
                    "Wisdom","Reflections","ChunkOutline","ChunkQuestions"]:
            df[col] = ""
        # Chapter-level
        for title in df['Detected Title'].unique():
            prompt = (
                f"Summarize chapter '{title}' in 50 words, list 3–5 outline bullets, and 2 questions."
            )
            res = requests.post(api_url, headers=headers,
                                json={"model":model_name,
                                      "messages":[{"role":"user","content":prompt}]})
            obj = json.loads(res.json()['choices'][0]['message']['content'])
            mask = df['Detected Title']==title
            df.loc[mask, 'ChapterSummary']  = obj.get('ChapterSummary', '')
            df.loc[mask, 'ChapterOutline']  = json.dumps(obj.get('ChapterOutline', []))
            df.loc[mask, 'ChapterQuestions']= json.dumps(obj.get('ChapterQuestions', []))
        # Chunk-level
        for i, row in df.iterrows():
            chunk = row['TEXT CHUNK']
            prompt = (
                f"For this text chunk, generate Wisdom, Reflections, 3–5 outline bullets, and 1 question."
                f" Text: {chunk}"
            )
            res = requests.post(api_url, headers=headers,
                                json={"model":model_name,
                                      "messages":[{"role":"user","content":prompt}]})
            obj = json.loads(res.json()['choices'][0]['message']['content'])
            df.at[i, 'Wisdom']       = obj.get('Wisdom','')
            df.at[i, 'Reflections']  = obj.get('Reflections','')
            df.at[i, 'ChunkOutline'] = json.dumps(obj.get('ChunkOutline', []))
            df.at[i, 'ChunkQuestions']=json.dumps(obj.get('ChunkQuestions', []))
        # download
        st.download_button("Download enriched CSV",
                           df.to_csv(index=False).encode('utf-8'),
                           file_name='enriched_full.csv',
                           mime='text/csv')
