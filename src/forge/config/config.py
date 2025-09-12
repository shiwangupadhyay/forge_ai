import sys
import json
from pathlib import Path
import sqlite3

from .constants import PROVIDER_MAP

class ForgeConfig:
    CONFIG_DIR = Path(".forge")
    CONFIG_DB = CONFIG_DIR / "memory.db"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self, provider: str, api_key: str, model: str | None = None):
        if provider not in PROVIDER_MAP:
            raise ValueError(f"Unknown provider '{provider}'. Valid: {list(PROVIDER_MAP.keys())}")

        self.provider = provider
        self.api_key = api_key
        self.model = model or PROVIDER_MAP[provider]["default_model"]

        # Ensure config dir exists
        ForgeConfig.CONFIG_DIR.mkdir(exist_ok=True)

        # DB connection
        self.conn = sqlite3.connect(ForgeConfig.CONFIG_DB)

        # LLM instance
        llm_class = PROVIDER_MAP[provider]["class"]
        self.llm = llm_class(model=self.model, api_key=self.api_key)

    def save(self):
        """Save config.json"""
        data = {
            "provider": self.provider,
            "api_key": self.api_key,
            "model": self.model,
        }
        with open(ForgeConfig.CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls):
        """Load from config.json"""
        if not cls.CONFIG_FILE.exists():
            raise FileNotFoundError("No config.json found. Please set up first.")
        with open(cls.CONFIG_FILE) as f:
            data = json.load(f)
        return cls(**data)

    @classmethod
    def delete(cls):
        """Delete all stored config + db"""
        if cls.CONFIG_FILE.exists():
            cls.CONFIG_FILE.unlink()
        if cls.CONFIG_DB.exists():
            cls.CONFIG_DB.unlink()

    def close(self):
        """Close db connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

