#!/usr/bin/env python3
"""
Diagram Microservice v2 - Main Entry Point

A self-contained WebSocket-based microservice for diagram generation.
"""

import asyncio
import logging
import signal
import sys
from typing import Optional
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import argparse

# Local imports
from config import get_settings
from api.websocket_handler import WebSocketHandler
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Diagram Microservice v2",
    description="WebSocket-based diagram generation service",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global WebSocket handler
ws_handler: Optional[WebSocketHandler] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global ws_handler
    
    logger.info("Starting Diagram Microservice v2...")
    
    # Check environment variables and log status
    import os
    env_status = []
    
    # Check critical environment variables
    if not os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_URL") == "https://test.supabase.co":
        env_status.append("❌ SUPABASE_URL not configured - storage features disabled")
    else:
        env_status.append("✅ SUPABASE_URL configured")
        
    if not os.getenv("SUPABASE_ANON_KEY"):
        env_status.append("❌ SUPABASE_ANON_KEY not configured - storage features disabled")
    else:
        env_status.append("✅ SUPABASE_ANON_KEY configured")
        
    if not os.getenv("GOOGLE_API_KEY"):
        env_status.append("⚠️ GOOGLE_API_KEY not configured - semantic routing disabled")
    else:
        env_status.append("✅ GOOGLE_API_KEY configured")
    
    logger.info("=" * 60)
    logger.info("ENVIRONMENT VARIABLE STATUS:")
    for status in env_status:
        logger.info(status)
    logger.info("=" * 60)
    
    if "❌" in " ".join(env_status):
        logger.warning("Some features are disabled. Add environment variables in Railway dashboard.")
    
    # Initialize WebSocket handler
    ws_handler = WebSocketHandler(settings)
    await ws_handler.initialize()
    
    logger.info("Microservice started successfully (with available features)")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global ws_handler
    
    logger.info("Shutting down Diagram Microservice v2...")
    
    if ws_handler:
        await ws_handler.shutdown()
    
    logger.info("Microservice shut down successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Diagram Microservice v2",
        "version": "2.0.0",
        "status": "running",
        "websocket_url": f"{settings.ws_url}"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": "diagram-microservice-v2",
        "version": "2.0.0"
    }
    
    # Check dependencies
    if ws_handler:
        health_status["websocket_handler"] = "ready"
        health_status["active_connections"] = ws_handler.active_connections_count()
    else:
        health_status["websocket_handler"] = "not_initialized"
        health_status["status"] = "degraded"
    
    # Check cache if enabled
    if settings.enable_cache:
        try:
            # TODO: Add cache health check
            health_status["cache"] = "healthy"
        except Exception as e:
            health_status["cache"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
    
    # Check database if configured
    if settings.supabase_url:
        try:
            # TODO: Add database health check
            health_status["database"] = "healthy"
        except Exception as e:
            health_status["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/metrics")
async def metrics():
    """Metrics endpoint"""
    if not settings.enable_metrics:
        raise HTTPException(status_code=404, detail="Metrics disabled")
    
    metrics_data = {
        "active_connections": ws_handler.active_connections_count() if ws_handler else 0,
        "total_requests": ws_handler.total_requests if ws_handler else 0,
        "total_errors": ws_handler.total_errors if ws_handler else 0,
        # TODO: Add more metrics
    }
    
    return metrics_data


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    api_key: Optional[str] = None
):
    """
    Main WebSocket endpoint for diagram generation
    
    Query parameters (all optional):
    - session_id: Session identifier (auto-generated if not provided)
    - user_id: User identifier (defaults to 'anonymous' if not provided)
    - api_key: Optional API key for authentication
    """
    
    # Accept connection first (before any validation)
    await websocket.accept()
    
    # Generate defaults for missing parameters
    import uuid
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.debug(f"Generated session_id: {session_id}")
    if not user_id:
        user_id = "anonymous"
        logger.debug(f"Using default user_id: {user_id}")
    
    # Validate API key if configured
    if settings.api_key and settings.api_key.strip() and api_key != settings.api_key:
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    if not ws_handler:
        await websocket.close(code=1011, reason="Service not initialized")
        return
    
    # Handle connection
    try:
        await ws_handler.handle_connection(
            websocket=websocket,
            session_id=session_id,
            user_id=user_id
        )
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session={session_id}, user={user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket.close(code=1011, reason="Internal server error")


def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    sys.exit(0)


def main():
    """Main entry point"""
    import os
    
    parser = argparse.ArgumentParser(description="Diagram Microservice v2")
    parser.add_argument(
        "--host",
        default=settings.ws_host,
        help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", settings.ws_port)),  # Railway provides PORT
        help="Port to bind to"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload"
    )
    
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Configure logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run server
    logger.info(f"Starting server on {args.host}:{args.port}")
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="debug" if args.debug else settings.log_level.lower(),
        access_log=args.debug
    )


if __name__ == "__main__":
    main()