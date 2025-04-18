try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"❌ Failed to read CSV: {e}")
    return None

# Initialize columns
for col in [
    "ChapterSummary", "ChapterOutline", "ChapterQuestions",
    "Wisdom", "Reflections", "ChunkOutline", "ChunkQuestions"
]:
    df[col] = ""

headers = {"Authorization": f"Bearer {api_key}"}

def _call_api(prompt: str) -> str:
    # Determine provider by URL
    if "generativelanguage.googleapis.com" in api_url:
        # Google Gemini Pro
        url = f"{api_url}?key={api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=60)
        text = resp.text
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini error {resp.status_code}: {text}")
        data = resp.json()
        return data.get("candidates", [{}])[0].get("content", "")
    else:
        # OpenAI-compatible (DeepSeek, OpenAI, Anthropic)
        resp = requests.post(
            api_url,
            headers=headers,
            json={"model": model_name, "messages": [{"role": "user", "content": prompt}]},
            timeout=60
        )
        text = resp.text
        if resp.status_code != 200:
            raise RuntimeError(f"Chat error {resp.status_code}: {text}")
        data = resp.json()
        # safe access
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"No choices in response: {data}")
        return choices[0].get("message", {}).get("content", "")

# Chapter-level enrichment
for title in df.get("Detected Title", pd.Series()).dropna().unique():
    prompt = (
        f"Summarize chapter '{title}' in 50 words; "
        "provide 3–5 outline bullets; then 2 contextual questions as JSON."
    )
    try:
        content = _call_api(prompt).strip()
        if not content:
            st.error(f"Empty response for chapter '{title}'")
            continue
        result = json.loads(content)
    except json.JSONDecodeError:
        st.error(f"Invalid JSON for chapter '{title}': {repr(content)}")
        continue
    except Exception as e:
        st.error(f"Error for chapter '{title}': {e}")
        continue

    mask = df['Detected Title'] == title
    df.loc[mask, 'ChapterSummary']   = result.get('ChapterSummary', '')
    df.loc[mask, 'ChapterOutline']   = json.dumps(result.get('ChapterOutline', []))
    df.loc[mask, 'ChapterQuestions'] = json.dumps(result.get('ChapterQuestions', []))

# Chunk-level enrichment
for idx, row in df.iterrows():
    chunk = row.get('TEXT CHUNK', '')
    prompt = (
        f"For this chunk, generate Wisdom, Reflections, 3–5 outline bullets, "
        f"and 1 contextual question as JSON. Text: {chunk}"
    )
    try:
        content = _call_api(prompt).strip()
        if not content:
            st.error(f"Empty response for chunk {idx}")
            continue
        result = json.loads(content)
    except json.JSONDecodeError:
        st.error(f"Invalid JSON for chunk {idx}: {repr(content)}")
        continue
    except Exception as e:
        st.error(f"Error for chunk {idx}: {e}")
        continue

    df.at[idx, 'Wisdom']         = result.get('Wisdom', '')
    df.at[idx, 'Reflections']    = result.get('Reflections', '')
    df.at[idx, 'ChunkOutline']   = json.dumps(result.get('ChunkOutline', []))
    df.at[idx, 'ChunkQuestions'] = json.dumps(result.get('ChunkQuestions', []))

return df
