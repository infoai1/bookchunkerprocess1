# --- START OF FILE bookchunkerprocess1-main/config.py ---
import os

# ==============================================================================
# Configuration File for Chapter & Chunk Enricher
# ==============================================================================
# ... (Explanations remain the same) ...
# ==============================================================================

# --- OpenAI GPT Configuration ---
MODEL_NAME = os.getenv("OPENAI_MODEL", "o4-mini-2025-04-16")
API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")

# --- DeepSeek Configuration ---
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

# --- Anthropic Claude Configuration ---
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219") 
ANTHROPIC_API_URL = os.getenv("ANTHROPIC_API_URL", "https://api.anthropic.com/v1/messages")

# --- Google Gemini Configuration ---
# Used when you select "Google Gemini Pro" in the app
# *** IMPORTANT: Updated to use the specific model 'gemini-2.5-pro-preview-03-25' AS REQUESTED ***
# WARNING: This model identifier is NOT found in standard public Google API documentation.
# Using it with the standard 'generativelanguage.googleapis.com' endpoint below
# is VERY LIKELY TO FAIL (e.g., 404 Not Found error).
# Ensure this model identifier is correct AND that you are using the correct API endpoint
# if you have special access to this experimental/preview model.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-03-25") # Using the specific identifier requested by the user.
GEMINI_API_URL = os.getenv(
    "GEMINI_API_URL",
    # This URL includes the specific '2.5' model name requested.
    # If this URL doesn't work, the model likely requires a different base URL or access method.
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-03-25:generateContent"
)

# --- Embeddings Configuration (Using OpenAI) ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL", "https://api.openai.com/v1/embeddings")

# ==============================================================================
# End of Configuration
# ==============================================================================

# --- END OF FILE bookchunkerprocess1-main/config.py ---
