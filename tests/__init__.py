# ABOUTME: Test package init.
# ABOUTME: Loads environment variables for integration tests.
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
