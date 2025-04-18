import streamlit as st
import pandas as pd
import requests
import json

def run_improvement5(model_name: str, api_url: str, api_key: str, headers: dict):
    # Check API key
    if not api_key or api_key.startswith("YOUR_"):
        st.error("OpenAI API key not set. Set OPENAI_API_KEY env var or update config.py.")
        return

    uploaded = st.file_uploader("Upload CSV with 'Detected Title' & 'TEXT CHUNK'", type="csv")
    if not uploaded:
        return

    if st.button("Start Enrichment"):
        try:
            df = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Failed to read CSV: {e}")
            return

        # Initialize new columns
        for col in ["ChapterSummary","ChapterOutline","ChapterQuestions",
                    "Wisdom","Reflections","ChunkOutline","ChunkQuestions"]:
            df[col] = ""

        # Chapter-level enrichment
        for title in df['Detected Title'].unique():
            prompt = (
                f"Summarize chapter '{title}' in 50 words; list 3–5 outline bullets; 2 contextual questions."
            )
            try:
                res = requests.post(
                    api_url,
                    headers=headers,
                    json={"model": model_name,
                          "messages":[{"role":"user","content":prompt}]}
                )
                data = res.json()
                if res.status_code != 200 or "choices" not in data:
                    st.error(f"API error for chapter '{title}': {data}")
                    continue
                content = data['choices'][0]['message']['content']
                result = json.loads(content)
            except Exception as e:
                st.error(f"Error processing chapter '{title}': {e}")
                continue
            mask = df['Detected Title'] == title
            df.loc[mask, 'ChapterSummary']   = result.get('ChapterSummary', '')
            df.loc[mask, 'ChapterOutline']   = json.dumps(result.get('ChapterOutline', []))
            df.loc[mask, 'ChapterQuestions'] = json.dumps(result.get('ChapterQuestions', []))

        # Chunk-level enrichment
        for idx, row in df.iterrows():
            chunk = row.get('TEXT CHUNK', '')
            prompt = (
                f"For this chunk, generate Wisdom, Reflections, 3–5 outline bullets, and 1 contextual question."
                f" Text: {chunk}"
            )
            try:
                res = requests.post(
                    api_url,
                    headers=headers,
                    json={"model": model_name,
                          "messages":[{"role":"user","content":prompt}]}
                )
                data = res.json()
                if res.status_code != 200 or "choices" not in data:
                    st.error(f"API error for chunk idx {idx}: {data}")
                    continue
                content = data['choices'][0]['message']['content']
                result = json.loads(content)
            except Exception as e:
                st.error(f"Error processing chunk idx {idx}: {e}")
                continue
            df.at[idx, 'Wisdom']         = result.get('Wisdom','')
            df.at[idx, 'Reflections']    = result.get('Reflections','')
            df.at[idx, 'ChunkOutline']   = json.dumps(result.get('ChunkOutline', []))
            df.at[idx, 'ChunkQuestions']= json.dumps(result.get('ChunkQuestions', []))

        st.download_button(
            "Download Enriched CSV",
            df.to_csv(index=False).encode('utf-8'),
            file_name='enriched_chapters_chunks.csv',
            mime='text/csv'
        )
