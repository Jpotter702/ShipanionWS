"""
Settings for the WebSocket server.

This module contains configuration settings for the WebSocket server.
"""
import os
from typing import Dict, Any

# API settings
SHIPVOX_API_URL = os.environ.get("SHIPVOX_API_URL", "http://localhost:8003/api")

# Authentication settings
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# WebSocket settings
# In settings.py
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,https://shipanionws.onrender.com").split(",")

# Debug settings
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Toggle for using internal function calls vs REST API
USE_INTERNAL = os.environ.get("USE_INTERNAL", "False").lower() == "true"

# Test token for development
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.dNsYhOKsYlKZzUmOJl8Zpf9SbJ4DJxhd3AU6pO-PWko"

def get_settings() -> Dict[str, Any]:
    """
    Get all settings as a dictionary.

    Returns:
        Dictionary containing all settings
    """
    return {
        "SHIPVOX_API_URL": SHIPVOX_API_URL,
        "SECRET_KEY": SECRET_KEY,
        "ACCESS_TOKEN_EXPIRE_MINUTES": ACCESS_TOKEN_EXPIRE_MINUTES,
        "ALLOWED_ORIGINS": ALLOWED_ORIGINS,
        "DEBUG": DEBUG,
        "USE_INTERNAL": USE_INTERNAL,
        "TEST_TOKEN": TEST_TOKEN
    }
