"""
WebSocket Handler for Diagram Generation

Manages WebSocket connections and message routing following Phase 1 patterns.
"""

import asyncio
import json
from typing import Dict, Set, Optional, Any
from datetime import datetime
import uuid
from fastapi import WebSocket, WebSocketDisconnect

from models import (
    WebSocketMessage,
    DiagramRequest,
    DiagramResponse,
    StatusUpdate,
    ErrorResponse,
    DiagramMetadata
)
from core.conductor import DiagramConductor
from utils.logger import setup_logger
from config import get_settings, ERROR_CODES, STATUS_MESSAGES

logger = setup_logger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket, metadata: Dict[str, Any]):
        """Add new connection"""
        self.active_connections[session_id] = websocket
        self.connection_metadata[session_id] = metadata
        logger.info(f"Connection established: {session_id}")
    
    async def disconnect(self, session_id: str):
        """Remove connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            del self.connection_metadata[session_id]
            logger.info(f"Connection closed: {session_id}")
    
    async def send_message(self, session_id: str, message: WebSocketMessage):
        """Send message to specific connection"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message.to_json())
    
    async def broadcast(self, message: WebSocketMessage, exclude: Optional[Set[str]] = None):
        """Broadcast message to all connections"""
        exclude = exclude or set()
        for session_id, websocket in self.active_connections.items():
            if session_id not in exclude:
                await websocket.send_json(message.to_json())
    
    def get_connection_count(self) -> int:
        """Get active connection count"""
        return len(self.active_connections)


class WebSocketHandler:
    """Main WebSocket handler for diagram generation"""
    
    def __init__(self, settings):
        self.settings = settings
        self.connection_manager = ConnectionManager()
        self.conductor: Optional[DiagramConductor] = None
        self.total_requests = 0
        self.total_errors = 0
        self.active_requests: Dict[str, asyncio.Task] = {}
    
    async def initialize(self):
        """Initialize handler and dependencies"""
        logger.info("Initializing WebSocket handler...")
        
        # Initialize conductor
        self.conductor = DiagramConductor(self.settings)
        await self.conductor.initialize()
        
        logger.info("WebSocket handler initialized")
    
    async def shutdown(self):
        """Cleanup on shutdown"""
        logger.info("Shutting down WebSocket handler...")
        
        # Cancel active requests
        for task in self.active_requests.values():
            task.cancel()
        
        # Close all connections
        for session_id in list(self.connection_manager.active_connections.keys()):
            await self.connection_manager.disconnect(session_id)
        
        # Cleanup conductor
        if self.conductor:
            await self.conductor.shutdown()
        
        logger.info("WebSocket handler shut down")
    
    async def handle_connection(
        self,
        websocket: WebSocket,
        session_id: str,
        user_id: str
    ):
        """Handle individual WebSocket connection"""
        
        # Store connection
        await self.connection_manager.connect(
            session_id,
            websocket,
            {
                "user_id": user_id,
                "connected_at": datetime.utcnow(),
                "request_count": 0
            }
        )
        
        # Send connection acknowledgment
        await self._send_connection_ack(session_id)
        
        try:
            # Message loop
            while True:
                # Receive message
                data = await websocket.receive_text()
                
                # Parse and handle message
                try:
                    message_data = json.loads(data)
                    await self._handle_message(session_id, message_data)
                except json.JSONDecodeError as e:
                    await self._send_error(
                        session_id,
                        ERROR_CODES["INVALID_REQUEST"],
                        f"Invalid JSON: {str(e)}"
                    )
                except Exception as e:
                    logger.error(f"Message handling error: {e}", exc_info=True)
                    await self._send_error(
                        session_id,
                        ERROR_CODES["INTERNAL_ERROR"],
                        "An internal error occurred"
                    )
        
        except WebSocketDisconnect:
            pass
        finally:
            # Cancel any active requests for this session
            if session_id in self.active_requests:
                self.active_requests[session_id].cancel()
                del self.active_requests[session_id]
            
            # Remove connection
            await self.connection_manager.disconnect(session_id)
    
    async def _handle_message(self, session_id: str, message_data: Dict[str, Any]):
        """Route message to appropriate handler"""
        
        message_type = message_data.get("type")
        
        if message_type == "diagram_request":
            await self._handle_diagram_request(session_id, message_data)
        elif message_type == "cancel_request":
            await self._handle_cancel_request(session_id, message_data)
        elif message_type == "ping":
            await self._handle_ping(session_id)
        else:
            await self._send_error(
                session_id,
                ERROR_CODES["INVALID_REQUEST"],
                f"Unknown message type: {message_type}"
            )
    
    async def _handle_diagram_request(self, session_id: str, message_data: Dict[str, Any]):
        """Handle diagram generation request following Generic Protocol"""
        
        self.total_requests += 1
        # Extract correlation_id (with backward compatibility for request_id)
        correlation_id = message_data.get("correlation_id")
        if not correlation_id:
            # For backward compatibility, check request_id
            correlation_id = message_data.get("request_id")
        if not correlation_id:
            # Generate one if client didn't provide it
            correlation_id = f"corr_{uuid.uuid4()}"
            logger.warning(f"No correlation_id provided by client for session {session_id}, generated: {correlation_id}")
        
        # Cancel any existing request for this session
        if session_id in self.active_requests:
            self.active_requests[session_id].cancel()
        
        # Create task for diagram generation with preserved correlation_id
        task = asyncio.create_task(
            self._generate_diagram(session_id, correlation_id, message_data)
        )
        self.active_requests[session_id] = task
        
        # Update connection metadata
        if session_id in self.connection_manager.connection_metadata:
            self.connection_manager.connection_metadata[session_id]["request_count"] += 1
    
    async def _generate_diagram(
        self,
        session_id: str,
        correlation_id: str,
        message_data: Dict[str, Any]
    ):
        """Generate diagram asynchronously with preserved correlation_id"""
        
        try:
            # Send initial status with preserved correlation_id
            await self._send_status(
                session_id,
                "thinking",
                STATUS_MESSAGES["thinking"],
                correlation_id=correlation_id
            )
            
            # Parse request
            payload = message_data.get("data", message_data.get("payload", {}))
            logger.info(f"Payload received: {list(payload.keys())}")
            if 'method' in payload:
                logger.info(f"Method field found: {payload['method']}")
            diagram_request = DiagramRequest(
                **payload,
                session_id=session_id,
                user_id=self.connection_manager.connection_metadata[session_id]["user_id"],
                request_id=correlation_id,  # Use correlation_id as request_id for internal tracking
                correlation_id=correlation_id  # Also pass as correlation_id
            )
            
            # Send generating status with preserved correlation_id
            await self._send_status(
                session_id,
                "generating",
                STATUS_MESSAGES["generating"],
                progress=25,
                correlation_id=correlation_id
            )
            
            # Generate diagram
            if not self.conductor:
                raise ValueError("Conductor not initialized")
            
            result = await self.conductor.generate(diagram_request)
            
            # Send response with preserved correlation_id
            await self._send_diagram_response(
                session_id,
                correlation_id,
                result
            )
            
            # Send complete status with preserved correlation_id
            await self._send_status(
                session_id,
                "complete",
                STATUS_MESSAGES["complete"],
                progress=100,
                correlation_id=correlation_id
            )
        
        except asyncio.CancelledError:
            logger.info(f"Request cancelled: {correlation_id}")
            await self._send_status(
                session_id,
                "idle",
                "Request cancelled",
                correlation_id=correlation_id
            )
        except Exception as e:
            self.total_errors += 1
            logger.error(f"Generation error: {e}", exc_info=True)
            await self._send_error(
                session_id,
                ERROR_CODES["GENERATION_FAILED"],
                str(e),
                correlation_id=correlation_id
            )
        finally:
            # Remove from active requests
            if session_id in self.active_requests:
                del self.active_requests[session_id]
    
    async def _handle_cancel_request(self, session_id: str, message_data: Dict[str, Any]):
        """Handle request cancellation"""
        
        if session_id in self.active_requests:
            self.active_requests[session_id].cancel()
            await self._send_status(
                session_id,
                "idle",
                "Request cancelled"
            )
    
    async def _handle_ping(self, session_id: str):
        """Handle ping message following Generic Protocol"""
        
        message = WebSocketMessage(
            session_id=session_id,
            type="control",
            subtype="pong",
            payload={
                "timestamp": datetime.utcnow().isoformat(),
                "latency_ms": 0  # Could calculate actual latency if needed
            }
        )
        await self.connection_manager.send_message(session_id, message)
    
    async def _send_connection_ack(self, session_id: str):
        """Send connection acknowledgment following Generic Protocol"""
        
        message = WebSocketMessage(
            session_id=session_id,
            type="control",
            subtype="connection_ack",
            payload={
                "status": "connected",
                "version": "1.0.0",  # Generic Protocol version
                "capabilities": ["svg_template", "mermaid", "python_chart", "correlation_id"],
                "protocol": "generic_v1"
            }
        )
        await self.connection_manager.send_message(session_id, message)
    
    async def _send_status(
        self,
        session_id: str,
        status: str,
        message_text: str,
        progress: Optional[int] = None,
        correlation_id: Optional[str] = None
    ):
        """Send status update with preserved correlation_id"""
        
        status_update = StatusUpdate(
            status=status,
            message=message_text,
            progress=progress,
            session_id=session_id,
            request_id=correlation_id  # For backward compatibility
        )
        
        message = WebSocketMessage(
            session_id=session_id,
            type="status",
            subtype="progress_update",
            payload=status_update.dict(),
            correlation_id=correlation_id,  # Preserve correlation_id
            request_id=correlation_id  # Also set for backward compatibility
        )
        
        await self.connection_manager.send_message(session_id, message)
    
    async def _send_diagram_response(
        self,
        session_id: str,
        correlation_id: str,
        result: Dict[str, Any]
    ):
        """Send diagram response with preserved correlation_id"""
        
        response = DiagramResponse(
            diagram_type=result["diagram_type"],
            diagram_id=result.get("diagram_id", ""),
            url=result.get("url", ""),
            content=result["content"],
            content_type=result.get("content_type", "svg"),
            content_delivery=result.get("content_delivery", "inline"),
            metadata=DiagramMetadata(**result.get("metadata", {})),
            session_id=session_id,
            request_id=correlation_id,  # For backward compatibility
            correlation_id=correlation_id  # Primary field
        )
        
        message = WebSocketMessage(
            session_id=session_id,
            type="response",
            subtype="diagram_response",
            payload=response.dict(),
            correlation_id=correlation_id,  # Preserve correlation_id
            request_id=correlation_id  # Also set for backward compatibility
        )
        
        await self.connection_manager.send_message(session_id, message)
    
    async def _send_error(
        self,
        session_id: str,
        error_code: str,
        error_message: str,
        correlation_id: Optional[str] = None
    ):
        """Send error response with preserved correlation_id"""
        
        error_response = ErrorResponse(
            error_code=error_code,
            error_message=error_message,
            session_id=session_id,
            request_id=correlation_id,  # For backward compatibility
            correlation_id=correlation_id  # Primary field
        )
        
        message = WebSocketMessage(
            session_id=session_id,
            type="error",
            subtype="generation_error",
            payload=error_response.dict(),
            correlation_id=correlation_id,  # Preserve correlation_id
            request_id=correlation_id  # Also set for backward compatibility
        )
        
        await self.connection_manager.send_message(session_id, message)
        
        # Also send error status with preserved correlation_id
        await self._send_status(
            session_id,
            "error",
            STATUS_MESSAGES["error"],
            correlation_id=correlation_id
        )
    
    def active_connections_count(self) -> int:
        """Get active connection count"""
        return self.connection_manager.get_connection_count()