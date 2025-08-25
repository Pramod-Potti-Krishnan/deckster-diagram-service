#!/usr/bin/env python3
"""
Debug routing for quadrantChart
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import components
from config.settings import Settings
from core.unified_playbook_v2 import UnifiedPlaybookV2
from models import DiagramRequest
from models.request_models import DiagramTheme

async def debug_routing():
    """Debug routing for quadrantChart"""
    
    # Initialize settings
    settings = Settings()
    
    # Initialize playbook
    playbook = UnifiedPlaybookV2(settings)
    
    # Test request
    request = DiagramRequest(
        request_id="test-quadrant",
        session_id="test-session",
        user_id="test-user",
        diagram_type="quadrantChart",
        content="Risk matrix with high risk items",
        theme=DiagramTheme(primaryColor="#3B82F6")
    )
    
    print(f"Request diagram_type: {request.diagram_type}")
    print(f"Lowercase: {request.diagram_type.lower()}")
    
    # Check the mapping
    print(f"\nMermaid type map keys (first 10):")
    for i, key in enumerate(list(playbook.mermaid_type_map.keys())[:10]):
        print(f"  '{key}'")
    
    # Check if it's in the map
    diagram_type_lower = request.diagram_type.lower().replace(" ", "_")
    print(f"\nLooking for: '{diagram_type_lower}'")
    print(f"In map? {diagram_type_lower in playbook.mermaid_type_map}")
    
    # Try rule-based routing
    strategy, context = playbook._try_rule_based_routing(request)
    
    if strategy:
        print(f"\nRule-based routing SUCCESS:")
        print(f"  Method: {strategy.method}")
        print(f"  Confidence: {strategy.confidence}")
        print(f"  Specific type: {context.get('specific_type')}")
    else:
        print(f"\nRule-based routing FAILED")
    
    # Try full routing
    strategy, context = await playbook.get_strategy_with_context(request)
    print(f"\nFinal routing:")
    print(f"  Method: {strategy.method}")
    print(f"  Confidence: {strategy.confidence}")
    if context:
        print(f"  Specific type: {context.get('specific_type')}")

if __name__ == "__main__":
    asyncio.run(debug_routing())