"""Load settings from the repository .env without relying on the working folder."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "code"
load_dotenv(ROOT / ".env")
PROVIDER = os.getenv("PROVIDER", "ollama")
MODEL = os.getenv("MODEL", "llama3.2")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
MAX_STEPS = int(os.getenv("MAX_STEPS", "5"))
KNOWLEDGE_DIR = Path(os.getenv("KNOWLEDGE_DIR", str(BASE / "knowledge")))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
RATES_URL = os.getenv("RATES_URL", "https://open.er-api.com/v6/latest")
WEATHER_URL = os.getenv("WEATHER_URL", "https://api.open-meteo.com/v1/forecast")
if MAX_STEPS < 1 or not 0 <= CHUNK_OVERLAP < CHUNK_SIZE:
    raise ValueError("Require MAX_STEPS > 0 and 0 <= CHUNK_OVERLAP < CHUNK_SIZE")

def make_model(temperature: float = TEMPERATURE):
    """Choose a local or installed cloud integration from configuration."""
    from langchain.chat_models import init_chat_model
    options = {"client_kwargs":{"timeout":60}} if PROVIDER == "ollama" else {}
    return init_chat_model(MODEL, model_provider=PROVIDER, temperature=temperature, **options)
