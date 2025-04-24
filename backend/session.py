"""
Session Tracking Module

This module provides functionality for tracking sessions across WebSocket connections.
"""
import logging
import time
import uuid
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory session store (in a production environment, this would be a database)
sessions: Dict[str, Dict[str, Any]] = {}

def create_session(user_info: Dict[str, Any]) -> str:
    """
    Create a new session for a user.
    
    Args:
        user_info: Information about the authenticated user
        
    Returns:
        The session ID
    """
    session_id = str(uuid.uuid4())
    
    sessions[session_id] = {
        "user_info": user_info,
        "created_at": time.time(),
        "last_active": time.time(),
        "state": {}
    }
    
    logger.info(f"Created session {session_id} for user {user_info.get('username')}")
    return session_id

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a session by ID.
    
    Args:
        session_id: The session ID
        
    Returns:
        The session data, or None if not found
    """
    session = sessions.get(session_id)
    
    if session:
        # Update last active time
        session["last_active"] = time.time()
    
    return session

def update_session_state(session_id: str, key: str, value: Any) -> bool:
    """
    Update a value in the session state.
    
    Args:
        session_id: The session ID
        key: The state key to update
        value: The new value
        
    Returns:
        True if successful, False if session not found
    """
    session = get_session(session_id)
    
    if not session:
        return False
    
    session["state"][key] = value
    return True

def get_session_state(session_id: str, key: str) -> Optional[Any]:
    """
    Get a value from the session state.
    
    Args:
        session_id: The session ID
        key: The state key to get
        
    Returns:
        The value, or None if not found
    """
    session = get_session(session_id)
    
    if not session:
        return None
    
    return session["state"].get(key)

def delete_session(session_id: str) -> bool:
    """
    Delete a session.
    
    Args:
        session_id: The session ID
        
    Returns:
        True if successful, False if session not found
    """
    if session_id in sessions:
        user = sessions[session_id]["user_info"].get("username")
        del sessions[session_id]
        logger.info(f"Deleted session {session_id} for user {user}")
        return True
    
    return False

def cleanup_expired_sessions(max_age_seconds: int = 3600) -> int:
    """
    Clean up expired sessions.
    
    Args:
        max_age_seconds: Maximum age of a session in seconds
        
    Returns:
        Number of sessions deleted
    """
    now = time.time()
    expired_sessions = [
        session_id for session_id, session in sessions.items()
        if now - session["last_active"] > max_age_seconds
    ]
    
    for session_id in expired_sessions:
        delete_session(session_id)
    
    if expired_sessions:
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    return len(expired_sessions)
