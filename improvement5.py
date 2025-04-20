# --- START OF FILE bookchunkerprocess1-main/improvement5.py ---
import pandas as pd
import requests
import json
import streamlit as st
import time # Import time for potential retries or delays if needed

def run_improvement5(uploaded_file, model_name, api_url, api_key):
    """
    Reads uploaded_file (CSV), enriches by chapter & chunk, returns DataFrame.
    Handles potential JSON decoding errors from the API.
    """
    if uploaded_file is None:
        st.warning("⚠️ No file uploaded.")
        return None

    # 1) Load CSV
    try:
        # Explicitly specify dtype to avoid potential parsing issues with mixed types
        # If you know specific columns might be problematic, define them here.
        # For now, treating all as object (string) is safest for reading.
        df = pd.read_csv(uploaded_file, dtype=object)
        # Fill potential NaN values in critical columns with empty strings
        df['Detected Title'] = df['Detected Title'].fillna('')
        df['TEXT CHUNK'] = df['TEXT CHUNK'].fillna('')

    except Exception as e:
        st.error(f"❌ Failed to read CSV: {e}")
        return None

    # --- Check if necessary columns exist ---
    if "Detected Title" not in df.columns:
        st.error("❌ CSV file is missing the required column: 'Detected Title'")
        return None
    if "TEXT CHUNK" not in df.columns:
        st.error("❌ CSV file is missing the required column: 'TEXT CHUNK'")
        return None
    # --- End Check ---

    # 2) Initialize new columns if they don't exist
    new_cols = [
        "ChapterSummary", "ChapterOutline", "ChapterQuestions",
        "Wisdom", "Reflections", "ChunkOutline", "ChunkQuestions"
    ]
    for col in new_cols:
        if col not in df.columns:
            df[col] = ""
        # Ensure existing columns are treated as strings initially for consistency
        df[col] = df[col].astype(str).fillna('')


    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def _call_api(prompt: str) -> str:
        max_retries = 2
        retry_delay = 3 # seconds
        for attempt in range(max_retries):
            try:
                # --- Google Gemini Specific Payload ---
                if "generativelanguage.googleapis.com" in api_url:
                    # Ensure the key is passed in the URL, not header
                    url = f"{api_url}?key={api_key}"
                    payload = json.dumps({"contents":[{"parts":[{"text": prompt}]}]})
                    # Use standard requests POST, no special headers needed beyond Content-Type
                    r = requests.post(url, data=payload, headers={"Content-Type": "application/json"}, timeout=90) # Increased timeout
                # --- OpenAI‐compatible (DeepSeek, OpenAI, Anthropic) ---
                # Note: Anthropic might need specific headers/payload structure if not using their specific SDK
                else:
                    payload = json.dumps({
                        "model": model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        # Add optional parameters if needed, e.g., max_tokens, temperature
                        # "max_tokens": 1000
                    })
                    r = requests.post(api_url, headers=headers, data=payload, timeout=90) # Increased timeout

                # --- Check Status Code ---
                r.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

                # --- Extract Content based on API type ---
                response_data = r.json()
                if "generativelanguage.googleapis.com" in api_url:
                     # Safer access for Gemini response structure
                    if response_data.get("candidates") and \
                       len(response_data["candidates"]) > 0 and \
                       response_data["candidates"][0].get("content") and \
                       response_data["candidates"][0]["content"].get("parts") and \
                       len(response_data["candidates"][0]["content"]["parts"]) > 0:
                        return response_data["candidates"][0]["content"]["parts"][0].get("text", "").strip()
                    else:
                        st.warning(f"⚠️ Unexpected Gemini response format: {response_data}")
                        return "" # Return empty string on unexpected format
                else: # OpenAI-compatible
                    # Safer access for OpenAI-compatible response structure
                    if response_data.get("choices") and \
                       len(response_data["choices"]) > 0 and \
                       response_data["choices"][0].get("message") and \
                       response_data["choices"][0]["message"].get("content"):
                         return response_data["choices"][0]["message"]["content"].strip()
                    else:
                        st.warning(f"⚠️ Unexpected OpenAI-compatible response format: {response_data}")
                        return "" # Return empty string on unexpected format

            except requests.exceptions.Timeout:
                st.warning(f"⏳ API call timed out (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            except requests.exceptions.RequestException as e:
                st.error(f"❌ API Request Failed (attempt {attempt + 1}/{max_retries}): {e}. Raw Response: {r.text if 'r' in locals() else 'N/A'}")
                # Don't retry on definite errors like 401 Unauthorized or 400 Bad Request immediately
                if hasattr(e, 'response') and e.response is not None and 400 <= e.response.status_code < 500:
                     st.error(f"❌ Client-side error ({e.response.status_code}). Check API Key, Model Name, or Prompt. Stopping retries.")
                     return "" # Return empty string, no point retrying
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    st.error(f"❌ API Request Failed after {max_retries} attempts.")
                    return "" # Return empty string after final failure
            except Exception as e: # Catch other potential errors during the call
                st.error(f"❌ An unexpected error occurred during API call: {e}")
                return "" # Return empty string

        # If all retries fail
        return ""


    # --- Create a progress bar ---
    total_operations = len(df.get("Detected Title", pd.Series()).dropna().unique()) + len(df)
    progress_bar = st.progress(0)
    operations_done = 0

    st.info("ℹ️ Starting Chapter Enrichment...")
    # 3) Chapter‐level enrichment
    # Use .items() for potentially better performance if title list is huge, but unique() is fine here.
    unique_titles = df.get("Detected Title", pd.Series()).dropna().unique()
    for title in unique_titles:
        if not title: # Skip empty titles if any exist
             continue

        # Check if chapter already has data (simple check, assumes if one field is filled, all are)
        mask = df["Detected Title"] == title
        if not df.loc[mask, "ChapterSummary"].iloc[0] == "":
             st.write(f"⏩ Skipping already processed chapter: '{title}'")
             operations_done += 1
             progress_bar.progress(operations_done / total_operations)
             continue

        st.write(f"⏳ Processing Chapter: '{title}'")
        prompt = (
            f"Here is the title of a chapter: '{title}'. "
            f"Please provide a concise summary (around 50 words), a 3-5 bullet point outline, "
            f"and 2 relevant, contextual questions about this chapter's likely themes. "
            f"Strictly return ONLY a valid JSON object with keys: 'ChapterSummary', 'ChapterOutline' (list of strings), and 'ChapterQuestions' (list of strings)."
            f"Example: {{\"ChapterSummary\": \"Summary text...\", \"ChapterOutline\": [\"Point 1\", \"Point 2\"], \"ChapterQuestions\": [\"Question 1?\", \"Question 2?\"]}}"
        )
        content = _call_api(prompt)

        result = {} # Default to empty dict
        if content:
            try:
                # Attempt to parse the JSON
                result = json.loads(content)
                if not isinstance(result, dict): # Ensure it's a dictionary
                    st.warning(f"⚠️ Chapter '{title}': API returned valid JSON, but it wasn't a dictionary object. Content: '{content}'")
                    result = {} # Reset if not a dict
            except json.JSONDecodeError as json_e:
                # This is the specific error from the screenshot
                st.error(f"❌ Chapter '{title}': Failed to decode JSON response from API. Error: {json_e}. Raw Content: '{content}'")
                # Keep result as {}
            except Exception as e:
                st.error(f"❌ Chapter '{title}': An unexpected error occurred processing API response: {e}. Raw Content: '{content}'")
                # Keep result as {}
        else:
            st.warning(f"⚠️ Chapter '{title}': Received empty or failed response from API.")
            # Keep result as {}

        # Safely assign values using .get() with default values
        df.loc[mask, "ChapterSummary"]   = str(result.get("ChapterSummary", "")) # Ensure string
        # Ensure outlines/questions are stored as JSON strings (lists)
        df.loc[mask, "ChapterOutline"]   = json.dumps(result.get("ChapterOutline", []))
        df.loc[mask, "ChapterQuestions"] = json.dumps(result.get("ChapterQuestions", []))

        operations_done += 1
        progress_bar.progress(operations_done / total_operations)
        time.sleep(0.1) # Small delay to prevent overwhelming the API/UI


    st.info("ℹ️ Starting Chunk Enrichment...")
    # 4) Chunk‐level enrichment
    for idx, row in df.iterrows():
        # Check if chunk already has data
        if not row.get("Wisdom", "") == "":
            # st.write(f"⏩ Skipping already processed chunk {idx}") # Optional: uncomment for verbose skipping
            operations_done += 1
            progress_bar.progress(operations_done / total_operations)
            continue

        chunk = row.get("TEXT CHUNK", "")
        if not chunk or pd.isna(chunk): # Skip if chunk is empty or NaN
            st.warning(f"⚠️ Skipping empty chunk at index {idx}")
            operations_done += 1
            progress_bar.progress(operations_done / total_operations)
            continue

        st.write(f"⏳ Processing Chunk {idx}...")
        prompt = (
             f"Analyze the following text chunk:\n---START CHUNK---\n{chunk}\n---END CHUNK---\n\n"
             f"Based SOLELY on this chunk, provide: \n"
             f"1. 'Wisdom': A single, concise insight or piece of wisdom (1-2 sentences).\n"
             f"2. 'Reflections': A brief reflection on the chunk's meaning or implication (1-2 sentences).\n"
             f"3. 'ChunkOutline': A 3-5 bullet point outline summarizing the key points or flow of the chunk.\n"
             f"4. 'ChunkQuestions': ONE relevant, contextual question that arises directly from this chunk's content.\n"
             f"Strictly return ONLY a valid JSON object with keys: 'Wisdom' (string), 'Reflections' (string), 'ChunkOutline' (list of strings), and 'ChunkQuestions' (list containing ONE string question)."
             f"Example: {{\"Wisdom\": \"Wisdom text...\", \"Reflections\": \"Reflection text...\", \"ChunkOutline\": [\"Point 1\", \"Point 2\"], \"ChunkQuestions\": [\"Question 1?\"]}}"
        )
        content = _call_api(prompt)

        result = {} # Default to empty dict
        if content:
            try:
                result = json.loads(content)
                if not isinstance(result, dict):
                     st.warning(f"⚠️ Chunk {idx}: API returned valid JSON, but it wasn't a dictionary object. Content: '{content}'")
                     result = {}
            except json.JSONDecodeError as json_e:
                st.error(f"❌ Chunk {idx}: Failed to decode JSON response from API. Error: {json_e}. Raw Content: '{content}'")
            except Exception as e:
                st.error(f"❌ Chunk {idx}: An unexpected error occurred processing API response: {e}. Raw Content: '{content}'")
        else:
            st.warning(f"⚠️ Chunk {idx}: Received empty or failed response from API.")

        # Safely assign values using .get()
        df.at[idx, "Wisdom"]         = str(result.get("Wisdom", "")) # Ensure string
        df.at[idx, "Reflections"]    = str(result.get("Reflections", "")) # Ensure string
        df.at[idx, "ChunkOutline"]   = json.dumps(result.get("ChunkOutline", []))
        df.at[idx, "ChunkQuestions"] = json.dumps(result.get("ChunkQuestions", []))

        operations_done += 1
        progress_bar.progress(min(operations_done / total_operations, 1.0)) # Ensure progress doesn't exceed 1.0
        time.sleep(0.1) # Small delay

    st.success("✅ Enrichment process completed!")
    progress_bar.progress(1.0) # Ensure bar reaches 100%
    return df
# --- END OF FILE bookchunkerprocess1-main/improvement5.py ---
