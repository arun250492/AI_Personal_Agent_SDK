"""
Configuration management for the Personal Agent
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """
    Configuration class for the Personal Agent SDK
    """

    def __init__(self, env_file: Optional[str] = None):
        if env_file:
            load_dotenv(env_file, override=True)
        else:
            load_dotenv(override=True)

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.zapier_api_key = os.getenv("ZAPIER_API_KEY")
        self.google_credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        self.data_storage_path = os.getenv("DATA_STORAGE_PATH", "./agent_data")
        self.ui_port = int(os.getenv("UI_PORT", "8080"))
        self.monitoring_interval = int(os.getenv("MONITORING_INTERVAL", "60"))

        # Validate required configs
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")

    @classmethod
    def from_dict(cls, config_dict: dict) -> 'Config':
        """Create config from dictionary"""
        # Set environment variables temporarily
        for key, value in config_dict.items():
            os.environ[key.upper()] = str(value)
        return cls()

    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            "OPENAI_API_KEY": self.openai_api_key,
            "ZAPIER_API_KEY": self.zapier_api_key,
            "GOOGLE_CREDENTIALS_PATH": self.google_credentials_path,
            "ENCRYPTION_KEY": self.encryption_key,
            "DATA_STORAGE_PATH": self.data_storage_path,
            "UI_PORT": str(self.ui_port),
            "MONITORING_INTERVAL": str(self.monitoring_interval),
        }