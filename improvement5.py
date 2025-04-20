# --- START OF FILE bookchunkerprocess1-main/improvement5.py ---
import pandas as pd
import requests
import json
import streamlit as st
import time
import chardet # Library to detect encoding

def run_improvement5(uploaded_file, model_name, api_url, api_key):
    """
    Reads uploaded_file (CSV), enriches by chapter & chunk, returns DataFrame.
    Handles potential JSON decoding errors from the API and attempts common CSV encodings.
    """
    if uploaded_file is None:
        st.warning("⚠️ No file uploaded.")
        return None

    # 1) Load CSV with robust encoding detection and error handling
    df = None
    potential_encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    detected_encoding = None

    try:
        # --- Try detecting encoding first ---
        # Read the first few KB to guess encoding - more robust for larger files
        raw_data = uploaded_file.read(5000) # Read 5KB
        uploaded_file.seek(0) # Reset file pointer to the beginning!
        result = chardet.detect(raw_data)
        detected_encoding = result['encoding']
        if detected_encoding:
            st.info(f"ℹ️ Detected encoding: {detected_encoding} (Confidence: {result['confidence']:.2f}). Trying this first.")
            potential_encodings.insert(0, detected_encoding) # Prioritize detected encoding
            # Remove duplicates if detected was already in the list
            potential_encodings = list(dict.fromkeys(potential_encodings))
        else:
             st.warning("⚠️ Could not auto-detect encoding. Trying common ones.")

    except Exception as detect_err:
        st.warning(f"⚠️ Error during encoding detection: {detect_err}. Proceeding with common encodings.")
        uploaded_file.seek(0) # Ensure file pointer is reset even if detection failed


    # --- Try reading with potential encodings ---
    last_exception = None
    for encoding in potential_encodings:
        try:
            st.write(f"⏳ Trying to read CSV with encoding: {encoding}...")
            # Explicitly setting delimiter and header, using object dtype
            df = pd.read_csv(
                uploaded_file,
                encoding=encoding,
                delimiter=',',    # Explicitly set comma delimiter
                header=0,         # Explicitly state header is row 0
                dtype=object,     # Read all as strings initially
                on_bad_lines='warn' # Warn about problematic lines instead of erroring immediately
            )
            st.success(f"✅ Successfully read CSV using encoding: {encoding}")
            last_exception = None # Clear last exception if successful
            break # Exit loop if read is successful
        except UnicodeDecodeError:
            st.warning(f"⚠️ Failed to decode using {encoding}.")
            uploaded_file.seek(0) # IMPORTANT: Reset stream position for next try
            last_exception = f"UnicodeDecodeError with encoding '{encoding}'"
        except pd.errors.ParserError as pe:
            st.warning(f"⚠️ Parser error with {encoding}: {pe}")
            uploaded_file.seek(0) # Reset stream position
            last_exception = f"ParserError with encoding '{encoding}': {pe}"
        except Exception as e:
            st.warning(f"⚠️ An unexpected error occurred while reading with {encoding}: {e}")
            uploaded_file.seek(0) # Reset stream position
            # Store the last exception encountered
            last_exception = e # Keep the most recent generic exception

    if df is None:
        st.error(f"❌ Failed to read CSV after trying multiple encodings. Last error encountered: {last_exception}")
        st.error("Please ensure the file is a valid CSV and try saving it with UTF-8 encoding in your spreadsheet program (File -> Save As -> CSV UTF-8).")
        return None

    # --- Post-read processing (Fill NaNs, Check Columns) ---
    try:
        df.fillna('', inplace=True) # Replace NaN/None with empty strings globally AFTER reading
    except Exception as fill_e:
         st.error(f"❌ Error during post-read NaN filling: {fill_e}")
         return None # Stop if we can't even clean the data

    # --- Check if necessary columns exist ---
    required_columns = ["Detected Title", "TEXT CHUNK"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"❌ CSV file is missing the required column(s): {', '.join(missing_columns)}")
        st.error(f"Detected columns are: {', '.join(df.columns)}")
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
        # Ensure existing columns are treated as strings for consistency
        df[col] = df[col].astype(str)


    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def _call_api(prompt: str) -> str:
        max_retries = 2
        retry_delay = 3 # seconds
        for attempt in range(max_retries):
            try:
                # --- Google Gemini Specific Payload ---
                if "generativelanguage.googleapis.com" in api_url:
                    url = f"{api_url}?key={api_key}"
                    payload = json.dumps({"contents":[{"parts":[{"text": prompt}]}]})
                    r = requests.post(url, data=payload, headers={"Content-Type": "application/json"}, timeout=90)
                # --- OpenAI‐compatible ---
                else:
                    payload = json.dumps({
                        "model": model_name,
                        "messages": [{"role": "user", "content": prompt}],
                    })
                    r = requests.post(api_url, headers=headers, data=payload, timeout=90)

                r.raise_for_status() # Raises HTTPError for bad responses

                response_data = r.json()
                if "generativelanguage.googleapis.com" in api_url:
                    if response_data.get("candidates") and \
                       len(response_data["candidates"]) > 0 and \
                       response_data["candidates"][0].get("content") and \
                       response_data["candidates"][0]["content"].get("parts") and \
                       len(response_data["candidates"][0]["content"]["parts"]) > 0:
                        return response_data["candidates"][0]["content"]["parts"][0].get("text", "").strip()
                    else:
                        st.warning(f"⚠️ Unexpected Gemini response format: {response_data}")
                        return ""
                else: # OpenAI-compatible
                    if response_data.get("choices") and \
                       len(response_data["choices"]) > 0 and \
                       response_data["choices"][0].get("message") and \
                       response_data["choices"][0]["message"].get("content"):
                         return response_data["choices"][0]["message"]["content"].strip()
                    else:
                        st.warning(f"⚠️ Unexpected OpenAI-compatible response format: {response_data}")
                        return ""

            except requests.exceptions.Timeout:
                st.warning(f"⏳ API call timed out (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            except requests.exceptions.RequestException as e:
                st.error(f"❌ API Request Failed (attempt {attempt + 1}/{max_retries}): {e}. Raw Response: {r.text if 'r' in locals() else 'N/A'}")
                if hasattr(e, 'response') and e.response is not None and 400 <= e.response.status_code < 500:
                     st.error(f"❌ Client-side error ({e.response.status_code}). Check API Key, Model Name, or Prompt. Stopping retries.")
                     return ""
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    st.error(f"❌ API Request Failed after {max_retries} attempts.")
                    return ""
            except Exception as e:
                st.error(f"❌ An unexpected error occurred during API call: {e}")
                return ""
        return ""


    # --- Create a progress bar ---
    total_operations = len(df['Detected Title'].dropna().unique()) + len(df)
    progress_bar = st.progress(0)
    operations_done = 0

    st.info("ℹ️ Starting Chapter Enrichment...")
    # 3) Chapter‐level enrichment
    unique_titles = df['Detected Title'].astype(str).dropna().unique() # Ensure titles are strings
    unique_titles = [title for title in unique_titles if title] # Filter out empty strings

    for title in unique_titles:
        mask = df["Detected Title"] == title
        # Simple check if data exists (assumes if summary is filled, all are)
        # Use .iloc[0] because mask might select multiple rows for the same chapter
        if not df.loc[mask, "ChapterSummary"].iloc[0] == "":
             # st.write(f"⏩ Skipping already processed chapter: '{title}'") # Optional verbosity
             operations_done += 1
             progress_bar.progress(min(operations_done / total_operations, 1.0))
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

        result = {}
        if content:
            try:
                result = json.loads(content)
                if not isinstance(result, dict):
                    st.warning(f"⚠️ Chapter '{title}': API returned valid JSON, but it wasn't a dictionary object. Content: '{content}'")
                    result = {}
            except json.JSONDecodeError as json_e:
                st.error(f"❌ Chapter '{title}': Failed to decode JSON response from API. Error: {json_e}. Raw Content: '{content}'")
            except Exception as e:
                st.error(f"❌ Chapter '{title}': An unexpected error occurred processing API response: {e}. Raw Content: '{content}'")
        else:
            st.warning(f"⚠️ Chapter '{title}': Received empty or failed response from API.")

        df.loc[mask, "ChapterSummary"]   = str(result.get("ChapterSummary", ""))
        df.loc[mask, "ChapterOutline"]   = json.dumps(result.get("ChapterOutline", []))
        df.loc[mask, "ChapterQuestions"] = json.dumps(result.get("ChapterQuestions", []))

        operations_done += 1
        progress_bar.progress(min(operations_done / total_operations, 1.0))
        time.sleep(0.1)


    st.info("ℹ️ Starting Chunk Enrichment...")
    # 4) Chunk‐level enrichment
    for idx, row in df.iterrows():
        # Check if chunk already has data
        if not row.get("Wisdom", "") == "":
            operations_done += 1
            progress_bar.progress(min(operations_done / total_operations, 1.0))
            continue

        chunk = row.get("TEXT CHUNK", "")
        # Also check for NaN explicitly although fillna should have caught it
        if not chunk or pd.isna(chunk):
            st.warning(f"⚠️ Skipping empty chunk at index {idx}")
            operations_done += 1
            progress_bar.progress(min(operations_done / total_operations, 1.0))
            continue

        # st.write(f"⏳ Processing Chunk {idx}...") # Can be too verbose, keep commented unless debugging
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

        result = {}
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

        df.at[idx, "Wisdom"]         = str(result.get("Wisdom", ""))
        df.at[idx, "Reflections"]    = str(result.get("Reflections", ""))
        df.at[idx, "ChunkOutline"]   = json.dumps(result.get("ChunkOutline", []))
        df.at[idx, "ChunkQuestions"] = json.dumps(result.get("ChunkQuestions", []))

        operations_done += 1
        progress_bar.progress(min(operations_done / total_operations, 1.0))
        # Reduce sleep time slightly as chunk processing is faster
        time.sleep(0.05)

    st.success("✅ Enrichment process completed!")
    progress_bar.progress(1.0)
    return df
# --- END OF FILE bookchunkerprocess1-main/improvement5.py ---
