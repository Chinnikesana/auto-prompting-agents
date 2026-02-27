import os
from pathlib import Path
from dotenv import load_dotenv

# Find the root directory and load .env
ROOT_DIR = Path(__file__).parent.parent.absolute()
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Config:
    # LLM Settings
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    
    # MongoDB Settings
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "dynamic_agents")
    
    # Email Settings
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
    EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
    EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    
    # Internal Flags
    TOOL_TEST_MODE = os.getenv("TOOL_TEST_MODE", "false").lower() == "true"

    @classmethod
    def validate_email_config(cls):
        """Helper to check if email credentials are present."""
        return all([cls.EMAIL_SENDER, cls.EMAIL_APP_PASSWORD])
