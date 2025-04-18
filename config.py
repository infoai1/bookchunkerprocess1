import os

MODEL_NAME        = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")
EMBEDDING_MODEL   = os.getenv("EMBED_MODEL", "text-embedding-ada-002")
API_URL           = os.getenv("CHAT_API_URL", "https://api.openai.com/v1/chat/completions")
EMBEDDING_API_URL = os.getenv("EMBED_API_URL", "https://api.openai.com/v1/embeddings")
API_KEY           = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
