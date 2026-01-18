"""Configuration management."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(Path(__file__).parent.parent / ".env")


class Config:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).parent.parent / 'finances.db'}"
    )


config = Config()
