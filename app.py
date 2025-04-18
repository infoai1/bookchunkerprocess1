import streamlit as st
import requests

from combined_enrichment import run_combined_enrichment
from improvement3 import run_improvement3
from improvement4 import run_improvement4
from improvement5 import run_improvement5
import config
import utils

# Page setup
st.set_page_config(page_title="Quran Enricher", layout="wide")

st.title("🕌 Quran Commentary Enrichment")
st.markdown("This app runs 5 enrichment steps in sequence:
1. Combined Enrichment
2. Batch Refinement
3. Thematic Splitting
4. Embeddings Mapping
5. Chapter & Chunk Enrichment
")

# Load config
model_name      = config.MODEL_NAME
api_url         = config.API_URL
embedding_model = config.EMBEDDING_MODEL
embedding_api_url = config.EMBEDDING_API_URL
api_key         = config.API_KEY
headers         = {"Authorization": f"Bearer {api_key}"}

# Step 1
st.header("✨ Step 1: Combined Enrichment")
run_combined_enrichment(model_name, api_url, headers)

# Step 2
st.header("⚙️ Step 2: Batch Refinement")
utils.batch_refinement(model_name, api_url, api_key, headers)

# Step 3
st.header("🧠 Step 3: Thematic Splitting")
run_improvement3(model_name, api_url, api_key, headers)

# Step 4
st.header("🔎 Step 4: Embeddings & Relationship Mapping")
run_improvement4(embedding_model, embedding_api_url, api_key, headers)

# Step 5
st.header("📖 Step 5: Chapter & Chunk Enrichment")
run_improvement5(model_name, api_url, api_key, headers)
