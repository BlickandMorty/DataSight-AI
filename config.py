import os
from dotenv import load_dotenv

# config.py = small knobs for the app
# if you want a different tone, edit the prompt below

AUDIT_PROMPT = (
    "You are a Senior Data Auditor. Analyze this metadata: {metadata}. "
    "Identify outliers, logic errors, and missing values."
)

def get_model_candidates():
    # read .env at call time so changes apply immediately
    load_dotenv()
    env_model = os.getenv("GEMINI_MODEL", "").strip()
    return [env_model] if env_model else ["gemini-2.0-flash"]
