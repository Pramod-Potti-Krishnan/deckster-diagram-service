"""
WebSocket Communication Models
"""

from typing import Dict, Any, Optional, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid


class MessageType(str, Enum):
    """WebSocket message types"""
    
    # Client -> Server
    DIAGRAM_REQUEST = "diagram_request"
    USER_INPUT = "user_input"
    CANCEL_REQUEST = "cancel_request"
    PING = "ping"
    
    # Server -> Client
    DIAGRAM_RESPONSE = "diagram_response"
    STATUS_UPDATE = "status_update"
    ERROR_RESPONSE = "error_response"
    PONG = "pong"
    
    # Bidirectional
    CONNECTION_INIT = "connection_init"
    CONNECTION_ACK = "connection_ack"
    CONNECTION_CLOSE = "connection_close"


class ConnectionParams(BaseModel):
    """WebSocket connection parameters"""
    
    session_id: str = Field(
        description="Session identifier"
    )
    user_id: str = Field(
        description="User identifier"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="Optional API key for authentication"
    )
    client_version: Optional[str] = Field(
        default=None,
        description="Client version for compatibility"
    )
    
    @validator('session_id', 'user_id')
    def validate_ids(cls, v):
        """Validate ID format"""
        if not v or len(v) < 3:
            raise ValueError(f"Invalid ID format: {v}")
        return v


class WebSocketMessage(BaseModel):
    """Base WebSocket message envelope"""
    
    message_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique message identifier"
    )
    session_id: str = Field(
        description="Session identifier"
    )
    type: str = Field(
        description="Message type"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Message timestamp"
    )
    payload: Dict[str, Any] = Field(
        description="Message payload"
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="ID to correlate request/response"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata"
    )
    
    @validator('type')
    def validate_type(cls, v):
        """Validate message type"""
        valid_types = [
            "diagram_request", "diagram_response",
            "status_update", "error_response",
            "user_input", "cancel_request",
            "connection_init", "connection_ack", "connection_close",
            "ping", "pong"
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid message type: {v}")
        return v
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        import json
        # Use model's JSON encoder to handle datetime and nested models
        json_str = self.json()
        return json.loads(json_str)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DiagramRequestMessage(WebSocketMessage):
    """Diagram request message"""
    
    type: Literal["diagram_request"] = "diagram_request"
    
    def __init__(self, **data):
        if 'type' not in data:
            data['type'] = "diagram_request"
        super().__init__(**data)
    
    @validator('payload')
    def validate_payload(cls, v):
        """Ensure payload contains required fields"""
        required = ['content', 'diagram_type']
        for field in required:
            if field not in v:
                raise ValueError(f"Missing required field in payload: {field}")
        return v


class DiagramResponseMessage(WebSocketMessage):
    """Diagram response message"""
    
    type: Literal["diagram_response"] = "diagram_response"
    
    def __init__(self, **data):
        if 'type' not in data:
            data['type'] = "diagram_response"
        super().__init__(**data)
    
    @validator('payload')
    def validate_payload(cls, v):
        """Ensure payload contains required fields"""
        required = ['diagram_type', 'content', 'metadata']
        for field in required:
            if field not in v:
                raise ValueError(f"Missing required field in payload: {field}")
        return v


class StatusUpdateMessage(WebSocketMessage):
    """Status update message"""
    
    type: Literal["status_update"] = "status_update"
    
    def __init__(self, **data):
        if 'type' not in data:
            data['type'] = "status_update"
        super().__init__(**data)
    
    @validator('payload')
    def validate_payload(cls, v):
        """Ensure payload contains required fields"""
        required = ['status', 'message']
        for field in required:
            if field not in v:
                raise ValueError(f"Missing required field in payload: {field}")
        return v


class ErrorResponseMessage(WebSocketMessage):
    """Error response message"""
    
    type: Literal["error_response"] = "error_response"
    
    def __init__(self, **data):
        if 'type' not in data:
            data['type'] = "error_response"
        super().__init__(**data)
    
    @validator('payload')
    def validate_payload(cls, v):
        """Ensure payload contains required fields"""
        required = ['error_code', 'error_message']
        for field in required:
            if field not in v:
                raise ValueError(f"Missing required field in payload: {field}")
        return v


# Type alias for all message types
from enum import Enum
AnyWebSocketMessage = Union[
    WebSocketMessage,
    DiagramRequestMessage,
    DiagramResponseMessage,
    StatusUpdateMessage,
    ErrorResponseMessage
]