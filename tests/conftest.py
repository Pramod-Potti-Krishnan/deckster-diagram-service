"""
Pytest configuration and shared fixtures for Diagram Microservice v2 tests
"""

import os
import sys
import asyncio
from typing import AsyncGenerator, Generator, Dict, Any
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
import pytest_asyncio

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config.settings import Settings
from models.request_models import DiagramRequest, DiagramTheme, DataPoint
from storage.supabase_client import DiagramStorage
from storage.diagram_operations import DiagramOperations
from storage.cache_manager import CacheManager
from storage.session_manager import DiagramSessionManager


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Create mock settings for testing"""
    settings = Settings(
        ws_host="localhost",
        ws_port=8001,
        supabase_url="https://test.supabase.co",
        supabase_key="test_key",
        diagram_bucket="test-diagrams",
        storage_public=True,
        cache_type="memory",
        cache_ttl=3600,
        log_level="DEBUG",
        enable_cache=True,
        enable_fallback=True,
        enable_metrics=True,
        templates_dir="templates",
        google_api_key="test_google_key",
        gemini_model="gemini-2.0-flash-lite",
        enable_semantic_routing=True,
        request_timeout=30,
        max_workers=4
    )
    return settings


@pytest.fixture
def sample_diagram_request():
    """Create sample diagram request"""
    return DiagramRequest(
        request_id="test-123",
        session_id="session-456",
        user_id="user-789",
        diagram_type="pyramid_3_level",
        content="Level 1: Foundation\nLevel 2: Middle\nLevel 3: Top",
        theme=DiagramTheme(
            primaryColor="#3B82F6",
            secondaryColor="#60A5FA",
            backgroundColor="#FFFFFF",
            textColor="#1F2937"
        ),
        data_points=[
            DataPoint(label="Foundation", value=100, description="Base level"),
            DataPoint(label="Middle", value=60, description="Middle level"),
            DataPoint(label="Top", value=20, description="Top level")
        ],
        metadata={"test": True}
    )


@pytest.fixture
def mock_supabase_client():
    """Create mock Supabase client"""
    client = MagicMock()
    
    # Mock storage operations
    storage = MagicMock()
    storage.from_.return_value.upload.return_value = {"path": "test/path.svg"}
    storage.from_.return_value.get_public_url.return_value = "https://test.supabase.co/storage/v1/object/public/test/path.svg"
    storage.from_.return_value.download.return_value = b"<svg>test</svg>"
    storage.from_.return_value.remove.return_value = None
    storage.list_buckets.return_value = []
    storage.create_bucket.return_value = {"name": "test-diagrams"}
    
    client.storage = storage
    
    # Mock database operations
    table = MagicMock()
    table.insert.return_value.execute.return_value = {"data": [{"id": "123"}], "error": None}
    table.select.return_value.eq.return_value.execute.return_value = {"data": [{"id": "123"}], "error": None}
    table.update.return_value.eq.return_value.execute.return_value = {"data": [{"id": "123"}], "error": None}
    table.delete.return_value.eq.return_value.execute.return_value = {"data": [], "error": None}
    
    client.table.return_value = table
    
    return client


@pytest.fixture
def mock_gemini_client():
    """Create mock Gemini client"""
    client = MagicMock()
    
    # Mock generate_content response
    response = MagicMock()
    response.text = '''
    {
        "primary_method": "SVG_TEMPLATE",
        "confidence": 0.9,
        "reasoning": "SVG template available for pyramid_3_level",
        "fallback_order": ["MERMAID", "PYTHON_CHART"],
        "quality_estimate": "high",
        "estimated_time_ms": 200
    }
    '''
    
    client.generate_content.return_value = response
    
    return client


@pytest_asyncio.fixture
async def mock_storage(mock_settings, mock_supabase_client):
    """Create mock storage with mocked Supabase client"""
    with patch('storage.supabase_client.get_supabase_client', return_value=mock_supabase_client):
        storage = DiagramStorage(mock_settings)
        yield storage


@pytest_asyncio.fixture
async def mock_cache_manager():
    """Create cache manager for testing"""
    cache = CacheManager(ttl_seconds=3600, max_size=100)
    await cache.start()
    yield cache
    await cache.stop()


@pytest_asyncio.fixture
async def mock_session_manager(mock_storage, mock_supabase_client):
    """Create mock session manager"""
    with patch('storage.supabase_client.get_supabase_client', return_value=mock_supabase_client):
        db_ops = DiagramOperations(mock_supabase_client)
        session_manager = DiagramSessionManager(mock_storage, db_ops)
        await session_manager.start()
        yield session_manager
        await session_manager.stop()


@pytest.fixture
def mock_websocket():
    """Create mock WebSocket connection"""
    ws = AsyncMock()
    ws.send_text = AsyncMock()
    ws.receive_text = AsyncMock()
    ws.close = AsyncMock()
    ws.accept = AsyncMock()
    return ws


@pytest.fixture
def sample_svg_content():
    """Sample SVG content for testing"""
    return '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
        <rect x="50" y="200" width="300" height="60" fill="#3B82F6"/>
        <text x="200" y="235" text-anchor="middle" fill="#FFFFFF">Foundation</text>
        
        <polygon points="100,140 300,140 250,80 150,80" fill="#60A5FA"/>
        <text x="200" y="115" text-anchor="middle" fill="#FFFFFF">Middle</text>
        
        <polygon points="150,80 250,80 200,20" fill="#93C5FD"/>
        <text x="200" y="55" text-anchor="middle" fill="#FFFFFF">Top</text>
    </svg>
    '''


@pytest.fixture
def sample_mermaid_code():
    """Sample Mermaid code for testing"""
    return """
    graph TD
        A[Start] --> B[Process]
        B --> C{Decision}
        C -->|Yes| D[Action 1]
        C -->|No| E[Action 2]
        D --> F[End]
        E --> F
    """


@pytest.fixture
def sample_chart_data():
    """Sample data for chart generation"""
    return {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "values": [25, 35, 30, 40],
        "colors": ["#3B82F6", "#60A5FA", "#93C5FD", "#DBEAFE"]
    }


# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set mock environment variables"""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test_key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test_google_key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.0-flash-lite")