"""
WebSocket Communication Models
"""

from typing import Dict, Any, Optional, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
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
    
    @field_validator('session_id', 'user_id')
    @classmethod
    def validate_ids(cls, v):
        """Validate ID format"""
        if not v or len(v) < 3:
            raise ValueError(f"Invalid ID format: {v}")
        return v


class WebSocketMessage(BaseModel):
    """Base WebSocket message envelope following Generic Protocol v1.0.0"""
    
    message_id: str = Field(
        default_factory=lambda: f"msg_{uuid.uuid4()}",
        description="Unique message identifier"
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="Links requests to responses and status updates (preserved throughout flow)"
    )
    session_id: str = Field(
        description="WebSocket session identifier"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Message timestamp"
    )
    type: str = Field(
        description="Message type: request, response, status, error, control"
    )
    subtype: Optional[str] = Field(
        default=None,
        description="Service-specific message subtype"
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Service-specific message payload"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata"
    )
    
    # Deprecated field for backward compatibility
    request_id: Optional[str] = Field(
        default=None,
        description="DEPRECATED: Use correlation_id instead"
    )
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Validate message type according to Generic Protocol"""
        # High-level message types from generic protocol
        generic_types = ['request', 'response', 'status', 'error', 'control']
        
        # Legacy types for backward compatibility
        legacy_types = [
            "diagram_request", "diagram_response",
            "status_update", "error_response",
            "user_input", "cancel_request",
            "connection_init", "connection_ack", "connection_close",
            "ping", "pong"
        ]
        
        if v not in generic_types and v not in legacy_types:
            raise ValueError(f"Invalid message type: {v}")
        return v
    
    @model_validator(mode='before')
    @classmethod
    def handle_correlation_id(cls, values):
        """Handle correlation_id and backward compatibility with request_id"""
        if isinstance(values, dict):
            # Sync correlation_id and request_id
            correlation_id = values.get('correlation_id')
            request_id = values.get('request_id')
            
            if not correlation_id and request_id:
                values['correlation_id'] = request_id
            elif correlation_id and not request_id:
                values['request_id'] = correlation_id
        
        return values
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        import json
        # Use model's JSON encoder to handle datetime and nested models
        json_str = self.json()
        return json.loads(json_str)
    
    def ensure_correlation_id(self) -> str:
        """Ensure correlation_id exists (for responses and status updates)"""
        if not self.correlation_id and not self.request_id:
            # Generate one if neither exists
            self.correlation_id = f"corr_{uuid.uuid4()}"
        elif not self.correlation_id:
            # Use request_id as correlation_id for backward compatibility
            self.correlation_id = self.request_id
        return self.correlation_id
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DiagramRequestMessage(WebSocketMessage):
    """Diagram request message following Generic Protocol"""
    
    type: Literal["request"] = "request"
    subtype: Literal["diagram_request"] = "diagram_request"
    
    def __init__(self, **data):
        if 'type' not in data:
            data['type'] = "request"
        if 'subtype' not in data:
            data['subtype'] = "diagram_request"
        super().__init__(**data)
    
    @field_validator('payload')
    @classmethod
    def validate_payload(cls, v):
        """Ensure payload contains required fields"""
        required = ['content', 'diagram_type']
        for field in required:
            if field not in v:
                raise ValueError(f"Missing required field in payload: {field}")
        return v


class DiagramResponseMessage(WebSocketMessage):
    """Diagram response message following Generic Protocol"""
    
    type: Literal["response"] = "response"
    subtype: Literal["diagram_response"] = "diagram_response"
    
    def __init__(self, **data):
        if 'type' not in data:
            data['type'] = "response"
        if 'subtype' not in data:
            data['subtype'] = "diagram_response"
        super().__init__(**data)
    
    @field_validator('payload')
    @classmethod
    def validate_payload(cls, v):
        """Ensure payload contains required fields"""
        required = ['diagram_type', 'content', 'metadata']
        for field in required:
            if field not in v:
                raise ValueError(f"Missing required field in payload: {field}")
        return v


class StatusUpdateMessage(WebSocketMessage):
    """Status update message following Generic Protocol"""
    
    type: Literal["status"] = "status"
    subtype: Literal["progress_update"] = "progress_update"
    
    def __init__(self, **data):
        if 'type' not in data:
            data['type'] = "status"
        if 'subtype' not in data:
            data['subtype'] = "progress_update"
        super().__init__(**data)
    
    @field_validator('payload')
    @classmethod
    def validate_payload(cls, v):
        """Ensure payload contains required fields"""
        required = ['status', 'message']
        for field in required:
            if field not in v:
                raise ValueError(f"Missing required field in payload: {field}")
        return v


class ErrorResponseMessage(WebSocketMessage):
    """Error response message following Generic Protocol"""
    
    type: Literal["error"] = "error"
    subtype: Literal["generation_error"] = "generation_error"
    
    def __init__(self, **data):
        if 'type' not in data:
            data['type'] = "error"
        if 'subtype' not in data:
            data['subtype'] = "generation_error"
        super().__init__(**data)
    
    @field_validator('payload')
    @classmethod
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