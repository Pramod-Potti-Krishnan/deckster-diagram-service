#!/usr/bin/env python3
"""
Test single diagram type
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import components
from config.settings import Settings
from core import DiagramConductor
from models import DiagramRequest
from models.request_models import DiagramTheme

async def test_single():
    """Test single diagram type"""
    
    # Initialize settings
    settings = Settings()
    
    # Initialize conductor
    conductor = DiagramConductor(settings)
    await conductor.initialize()
    
    # Test quadrantChart
    print("Testing quadrantChart...")
    
    request = DiagramRequest(
        request_id="test-quadrant",
        session_id="test-session",
        user_id="test-user",
        diagram_type="quadrantChart",
        content="Risk matrix with high risk items in upper right",
        theme=DiagramTheme(primaryColor="#3B82F6")
    )
    
    try:
        result = await conductor.generate(request)
        print(f"✅ SUCCESS")
        print(f"  Method: {result.get('metadata', {}).get('generation_method')}")
        print(f"  Diagram type: {result.get('diagram_type')}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Shutdown
    await conductor.shutdown()

if __name__ == "__main__":
    asyncio.run(test_single())