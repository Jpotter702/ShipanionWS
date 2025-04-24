"""
Configuration settings for the backend application.
"""
import os

# Authentication token for WebSocket connections
# In a production environment, this should be loaded from environment variables
# or a secure configuration system
WS_AUTH_TOKEN = os.environ.get("WS_AUTH_TOKEN", "your-secure-token-here")
