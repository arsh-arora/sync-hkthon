from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_EXECUTION = "tool_execution"
    ERROR = "error"

class ToolStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ContentType(str, Enum):
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    DATA = "data"
    ERROR = "error"

class ToolResult(BaseModel):
    tool_name: str
    status: ToolStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class MessageContent(BaseModel):
    type: ContentType
    content: Union[str, Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    type: MessageType
    content: List[MessageContent]
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tool_results: Optional[List[ToolResult]] = None

class UserQuery(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    message_id: str
    response_type: MessageType
    content: List[MessageContent]
    tools_used: Optional[List[str]] = None
    processing_time: Optional[float] = None
    session_id: Optional[str] = None

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    required_params: List[str]
    category: str
    enabled: bool = True

class IntentClassification(BaseModel):
    intent: str
    confidence: float
    suggested_tools: List[str]
    parameters: Dict[str, Any]
    reasoning: Optional[str] = None

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]
