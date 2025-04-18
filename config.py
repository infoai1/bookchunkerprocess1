```python
# config.py

import os

# OpenAI GPT settings
MODEL_NAME        = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")
API_URL           = os.getenv("CHAT_API_URL", "https://api.openai.com/v1/chat/completions")

# Embedding settings
EMBEDDING_MODEL   = os.getenv("EMBED_MODEL", "text-embedding-ada-002")
EMBEDDING_API_URL = os.getenv("EMBED_API_URL", "https://api.openai.com/v1/embeddings")

# DeepSeek Reasoner settings
DEEPSEEK_MODEL    = os.getenv("DEEPSEEK_MODEL", "deeplens-reasoner-001")
DEEPSEEK_API_URL  = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/reasoning")

# Anthropic Claude settings
ANTHROPIC_MODEL   = os.getenv("ANTHROPIC_MODEL", "claude-2.5")
ANTHROPIC_API_URL = os.getenv("ANTHROPIC_API_URL", "https://api.anthropic.com/v1/complete")

# Google Gemini Pro settings
GEMINI_MODEL      = os.getenv("GEMINI_MODEL", "gemini-pro-2.5")
GEMINI_API_URL    = os.getenv("GEMINI_API_URL", "https://api.generative.google.com/v1beta2/models/gemini_pro_2p5:generateText")

# Shared API key (must be set as an environment variable)
API_KEY           = os.getenv("OPENAI_API_KEY", "")
```
