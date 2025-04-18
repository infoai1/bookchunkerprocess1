# Chapter & Chunk Enricher

Process a CSV with columns 'Detected Title' and 'TEXT CHUNK' to:

1. Summarize each chapter
2. Enrich each chunk with wisdom, reflections, outline, and questions
3. Generate embeddings for each chunk

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your_key_here"
streamlit run app.py
