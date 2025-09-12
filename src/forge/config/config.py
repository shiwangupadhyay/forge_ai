import json
import time
from pathlib import Path

from .constants import PROVIDER_MAP

class ForgeConfig:
    """
    Manages loading and saving of configuration data from a JSON file.
    This class is NOT responsible for managing the database connection.
    """
    CONFIG_DIR = Path(".forge")
    CONFIG_DB = CONFIG_DIR / "memory.db"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self, provider: str, api_key: str, model: str | None = None):
        if provider not in PROVIDER_MAP:
            raise ValueError(f"Unknown provider '{provider}'. Valid: {list(PROVIDER_MAP.keys())}")

        self.provider = provider
        self.api_key = api_key
        self.model = model or PROVIDER_MAP[provider]["default_model"]
        llm_class = PROVIDER_MAP[provider]["class"]
        self.llm = llm_class(model=self.model, api_key=self.api_key)

        ForgeConfig.CONFIG_DIR.mkdir(exist_ok=True)

    def save(self):
        """Save provider, api_key, and model into config.json"""
        data = {
            "provider": self.provider,
            "api_key": self.api_key,
            "model": self.model,
        }
        with open(ForgeConfig.CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls):
        """Load config from config.json"""
        if not cls.CONFIG_FILE.exists():
            raise FileNotFoundError("No config.json found. Please set up first.")
        with open(cls.CONFIG_FILE) as f:
            data = json.load(f)
        return cls(**data)

    @classmethod
    def delete(cls):
        """
        Delete stored config files, the DB, and the .forge directory itself.
        Assumes any active connection has already been closed by the caller.
        """
        # Delete files first
        if cls.CONFIG_FILE.exists():
            cls.CONFIG_FILE.unlink()

        if cls.CONFIG_DB.exists():
            # Use a robust retry loop for Windows file lock issues
            attempts = 5
            for i in range(attempts):
                try:
                    cls.CONFIG_DB.unlink()
                    break  # Success
                except PermissionError:
                    if i < attempts - 1:
                        time.sleep(0.1 * (2**i))
                    else:
                        raise # Re-raise after final attempt
        
        # Now, delete the directory itself
        if cls.CONFIG_DIR.exists():
            try:
                cls.CONFIG_DIR.rmdir()
            except OSError as e:
                # This helps debug if the directory isn't empty for some reason
                print(f"Could not remove .forge directory: {e}. It may not be empty.")