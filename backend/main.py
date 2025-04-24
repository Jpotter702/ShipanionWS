from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import time
import uuid
import logging
from datetime import timedelta

# Import security utilities
from backend.security import (
    authenticate_user,
    create_access_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TEST_TOKEN
)

# Import message handlers
from backend.handlers import dispatch_message

# Import session tracking
from backend.session import create_session, get_session, update_session_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token response models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TestToken(BaseModel):
    test_token: str
    note: str

# User model
class User(BaseModel):
    username: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # Store user information with each connection
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
        # Store session IDs with each connection
        self.sessions: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, user_info: Dict[str, Any], session_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_info[websocket] = user_info

        # Create a new session or use the provided one
        if not session_id:
            session_id = create_session(user_info)

        # Store the session ID with the connection
        self.sessions[websocket] = session_id
        websocket.session_id = session_id

        logger.info(f"Client connected: {user_info.get('username')} (Session: {session_id})")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

        # Remove user info
        if websocket in self.connection_info:
            del self.connection_info[websocket]

        # Remove session mapping
        if websocket in self.sessions:
            session_id = self.sessions[websocket]
            del self.sessions[websocket]
            logger.info(f"Client disconnected from session: {session_id}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

    async def broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast a message to all connections in a session."""
        for connection in self.active_connections:
            if self.sessions.get(connection) == session_id:
                await connection.send_json(message)

    def get_connections_by_session(self, session_id: str) -> List[WebSocket]:
        """Get all connections for a session."""
        return [conn for conn in self.active_connections if self.sessions.get(conn) == session_id]

manager = ConnectionManager()

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Token endpoint for obtaining JWT tokens
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Authenticate the user
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with expiration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    }

# Endpoint to get the test token
@app.get("/test-token", response_model=TestToken)
async def get_test_token():
    """Get a pre-generated test token for the 'user' account.
    This is for testing purposes only and should not be used in production.
    """
    return {
        "test_token": TEST_TOKEN,
        "note": "This token is for testing only. It is valid for the 'user' account and does not expire."
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: Optional[str] = Query(None)):
    # Extract token from query parameters
    token = websocket.query_params.get("token")

    # Validate the token
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
        return

    # Verify JWT token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired token")
        return

    # Extract user information from token
    username = payload.get("sub")
    if not username:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token payload")
        return

    # Store user information
    user_info = {"username": username}

    # Check if a session ID was provided
    if session_id:
        # Validate the session
        session = get_session(session_id)
        if not session or session["user_info"].get("username") != username:
            # Invalid session or session belongs to another user
            logger.warning(f"Invalid session ID: {session_id} for user: {username}")
            session_id = None

    # If token is valid, proceed with connection
    await manager.connect(websocket, user_info, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            logger.info(f"Received message from {username}: {data.get('type')}")

            # Get the session ID for this connection
            session_id = manager.sessions.get(websocket)

            # Add session ID to the message if available
            if session_id and not data.get('session_id'):
                data['session_id'] = session_id

            # Process the message using the dispatcher
            response, contextual_update = await dispatch_message(data, user_info)

            # Send the response back to the client
            await websocket.send_json(response)

            # If there's a contextual update, broadcast it to the session
            if contextual_update and session_id:
                # Add session ID to the contextual update
                contextual_update['session_id'] = session_id
                await manager.broadcast_to_session(session_id, contextual_update)
            # If there's a contextual update but no session, broadcast to all
            elif contextual_update:
                await manager.broadcast(contextual_update)

            # If the message should be broadcast to all clients, do so
            elif data.get('broadcast', False):
                await manager.broadcast(response)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {username}")
        manager.disconnect(websocket)


class IncomingMessage(BaseModel):
    type: str
    payload: dict


@app.post("/send-message")
async def send_message(message: IncomingMessage):
    enriched_message = {
        "type": message.type,
        "payload": message.payload,
        "timestamp": time.time(),
        "requestId": str(uuid.uuid4())
    }
    await manager.broadcast(enriched_message)
    return {"status": "sent", "broadcast": enriched_message}