#!/usr/bin/env python3
"""
Test V2 implementations locally
"""

import asyncio
from models import DiagramRequest
from models.request_models import DiagramTheme
from agents import MermaidAgent
from core.unified_playbook import UnifiedPlaybook
from config.settings import Settings

async def test_local():
    """Test V2 components locally"""
    
    # Load settings
    settings = Settings()
    
    # Initialize components
    print("Initializing components...")
    playbook = UnifiedPlaybook(settings)
    await playbook.initialize()
    
    mermaid_agent = MermaidAgent(settings)
    
    # Test request
    request = DiagramRequest(
        diagram_type="flowchart",
        content="User login -> Validate -> Success or Error -> End",
        theme=DiagramTheme(),
        data_points=[]
    )
    
    # Test routing
    print("\n1. Testing routing...")
    strategy = await playbook.get_strategy(request)
    print(f"   Route: {strategy.method.value} (confidence: {strategy.confidence:.2f})")
    print(f"   Reasoning: {strategy.reasoning[:100]}...")
    
    # Test generation if routed to Mermaid
    if strategy.method.value == "mermaid":
        print("\n2. Testing Mermaid generation...")
        try:
            result = await mermaid_agent.generate(request)
            print(f"   Success! Generated {result['diagram_type']}")
            print(f"   Method: {result['metadata'].get('generation_method')}")
            print(f"   Has content: {bool(result.get('content'))}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_local())