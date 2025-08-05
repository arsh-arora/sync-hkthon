from typing import Dict, Any
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from ..models.schemas import UserQuery, WebSocketMessage, MessageType
from ..agents.agent_orchestrator import agent_orchestrator

class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, str] = {}  # session_id -> connection_id
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        print(f"WebSocket connection established: {connection_id}")
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from session mapping
        session_to_remove = None
        for session_id, conn_id in self.session_connections.items():
            if conn_id == connection_id:
                session_to_remove = session_id
                break
        
        if session_to_remove:
            del self.session_connections[session_to_remove]
        
        print(f"WebSocket connection closed: {connection_id}")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending message to {connection_id}: {str(e)}")
                self.disconnect(connection_id)
    
    async def send_to_session(self, message: dict, session_id: str):
        """Send a message to a specific session."""
        if session_id in self.session_connections:
            connection_id = self.session_connections[session_id]
            await self.send_personal_message(message, connection_id)
    
    def associate_session(self, connection_id: str, session_id: str):
        """Associate a connection with a session."""
        self.session_connections[session_id] = connection_id
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)

# Global connection manager
manager = ConnectionManager()

class WebSocketHandler:
    """Handles WebSocket communication for the chat interface."""
    
    def __init__(self):
        self.manager = manager
    
    async def handle_connection(self, websocket: WebSocket, connection_id: str):
        """Handle a WebSocket connection lifecycle."""
        await self.manager.connect(websocket, connection_id)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Process the message
                await self.process_message(message_data, connection_id)
                
        except WebSocketDisconnect:
            self.manager.disconnect(connection_id)
        except Exception as e:
            print(f"WebSocket error for {connection_id}: {str(e)}")
            await self.send_error_message(connection_id, str(e))
            self.manager.disconnect(connection_id)
    
    async def process_message(self, message_data: dict, connection_id: str):
        """Process incoming WebSocket messages."""
        message_type = message_data.get("type")
        
        if message_type == "chat_message":
            await self.handle_chat_message(message_data, connection_id)
        elif message_type == "session_init":
            await self.handle_session_init(message_data, connection_id)
        elif message_type == "session_history":
            await self.handle_session_history(message_data, connection_id)
        elif message_type == "ping":
            await self.handle_ping(connection_id)
        else:
            await self.send_error_message(connection_id, f"Unknown message type: {message_type}")
    
    async def handle_chat_message(self, message_data: dict, connection_id: str):
        """Handle incoming chat messages."""
        try:
            # Extract message details
            user_message = message_data.get("data", {}).get("message", "")
            session_id = message_data.get("data", {}).get("session_id")
            user_id = message_data.get("data", {}).get("user_id")
            
            if not user_message.strip():
                await self.send_error_message(connection_id, "Empty message received")
                return
            
            # Associate connection with session
            if session_id:
                self.manager.associate_session(connection_id, session_id)
            
            # Create user query
            query = UserQuery(
                message=user_message,
                session_id=session_id,
                user_id=user_id
            )
            
            # Send acknowledgment
            await self.send_message(connection_id, {
                "type": "message_received",
                "data": {"message_id": query.session_id}
            })
            
            # Create progress callback
            async def progress_callback(message: str, progress: float):
                await self.send_message(connection_id, {
                    "type": "progress_update",
                    "data": {
                        "message": message,
                        "progress": progress,
                        "session_id": session_id
                    }
                })
            
            # Process the query through the agent orchestrator
            response = await agent_orchestrator.process_query(query, progress_callback)
            
            # Send the response back to the client
            await self.send_message(connection_id, {
                "type": "agent_response",
                "data": {
                    "message_id": response.message_id,
                    "content": [content.dict() for content in response.content],
                    "tools_used": response.tools_used,
                    "processing_time": response.processing_time,
                    "session_id": response.session_id
                }
            })
            
        except Exception as e:
            await self.send_error_message(connection_id, f"Error processing chat message: {str(e)}")
    
    async def handle_session_init(self, message_data: dict, connection_id: str):
        """Handle session initialization."""
        try:
            session_id = message_data.get("data", {}).get("session_id")
            
            if session_id:
                self.manager.associate_session(connection_id, session_id)
                
                # Send session confirmation
                await self.send_message(connection_id, {
                    "type": "session_initialized",
                    "data": {
                        "session_id": session_id,
                        "status": "connected"
                    }
                })
            else:
                await self.send_error_message(connection_id, "No session_id provided")
                
        except Exception as e:
            await self.send_error_message(connection_id, f"Error initializing session: {str(e)}")
    
    async def handle_session_history(self, message_data: dict, connection_id: str):
        """Handle session history requests."""
        try:
            session_id = message_data.get("data", {}).get("session_id")
            
            if not session_id:
                await self.send_error_message(connection_id, "No session_id provided")
                return
            
            # Get session history
            history = await agent_orchestrator.get_session_history(session_id)
            
            # Convert to serializable format
            history_data = []
            for message in history:
                history_data.append({
                    "id": message.id,
                    "type": message.type,
                    "content": [content.dict() for content in message.content],
                    "timestamp": message.timestamp.isoformat(),
                    "tool_results": [result.dict() for result in message.tool_results] if message.tool_results else None
                })
            
            await self.send_message(connection_id, {
                "type": "session_history",
                "data": {
                    "session_id": session_id,
                    "history": history_data
                }
            })
            
        except Exception as e:
            await self.send_error_message(connection_id, f"Error retrieving session history: {str(e)}")
    
    async def handle_ping(self, connection_id: str):
        """Handle ping messages for connection health check."""
        await self.send_message(connection_id, {
            "type": "pong",
            "data": {"timestamp": asyncio.get_event_loop().time()}
        })
    
    async def send_message(self, connection_id: str, message: dict):
        """Send a message to a specific connection."""
        await self.manager.send_personal_message(message, connection_id)
    
    async def send_error_message(self, connection_id: str, error: str):
        """Send an error message to a connection."""
        await self.send_message(connection_id, {
            "type": "error",
            "data": {
                "error": error,
                "timestamp": asyncio.get_event_loop().time()
            }
        })
    
    async def broadcast_system_message(self, message: str):
        """Broadcast a system message to all connected clients."""
        system_message = {
            "type": "system_message",
            "data": {
                "message": message,
                "timestamp": asyncio.get_event_loop().time()
            }
        }
        
        for connection_id in self.manager.active_connections.keys():
            await self.send_message(connection_id, system_message)

# Global WebSocket handler
websocket_handler = WebSocketHandler()
