import os

# OpenAI GPT
MODEL_NAME        = os.getenv("OPENAI_MODEL",    "gpt-3.5-turbo")
API_URL           = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")

# DeepSeek Reasoner (OpenAI‑compatible)
DEEPSEEK_MODEL    = os.getenv("DEEPSEEK_MODEL",    "deepseek-reasoner")
DEEPSEEK_API_URL  = os.getenv("DEEPSEEK_API_URL",  "https://api.deepseek.com/v1/chat/completions")

# Anthropic Claude
ANTHROPIC_MODEL   = os.getenv("ANTHROPIC_MODEL",   "claude-2.5")
ANTHROPIC_API_URL = os.getenv("ANTHROPIC_API_URL", "https://api.anthropic.com/v1/complete")

# Google Gemini Pro
GEMINI_MODEL      = os.getenv("GEMINI_MODEL",      "gemini-2.0-flash")
GEMINI_API_URL    = os.getenv(
    "GEMINI_API_URL",
    "https://generativelanguage.googleapis.com/v1beta2/models/gemini-2.0-flash:generateContent"
)

# Embeddings (OpenAI)
EMBEDDING_MODEL   = os.getenv("EMBEDDING_MODEL",   "text-embedding-ada-002")
EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL", "https://api.openai.com/v1/embeddings")
