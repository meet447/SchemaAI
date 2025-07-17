import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICE = os.getenv("SERVICE")
MODEL = os.getenv("MODEL")