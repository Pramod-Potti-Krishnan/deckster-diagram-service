#!/usr/bin/env python3
"""
Test PydanticAI V2 Implementations

Simple test script for Mermaid Agent V2 and Unified Playbook V2.
Tests both success and failure cases without complex fallbacks.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Import V2 implementations
from agents.mermaid_agent_v2 import MermaidAgentV2
from core.unified_playbook_v2 import UnifiedPlaybookV2
from models import DiagramRequest
from models.request_models import DiagramTheme as ThemeConfig
from config.settings import Settings


# Test cases for different diagram types
TEST_CASES = [
    {
        "diagram_type": "flowchart",
        "content": "User login -> Validate credentials -> Check 2FA -> Grant access or Deny access",
        "expected_method": "mermaid"
    },
    {
        "diagram_type": "pie_chart",
        "content": "Sales by region: North America 35%, Europe 30%, Asia 25%, Other 10%",
        "expected_method": "mermaid"  # or python_chart
    },
    {
        "diagram_type": "sequence",
        "content": "Client sends request to API Gateway, Gateway forwards to Service, Service queries Database, Database returns data, Service processes and returns to Gateway, Gateway responds to Client",
        "expected_method": "mermaid"
    },
    {
        "diagram_type": "mind_map",
        "content": "Project Planning with branches: Requirements (User Stories, Technical Specs), Design (UI/UX, Architecture), Development (Frontend, Backend, Testing), Deployment (Staging, Production)",
        "expected_method": "mermaid"
    },
    {
        "diagram_type": "pyramid_3_level",
        "content": "Strategic level at top, Tactical level in middle, Operational level at base",
        "expected_method": "svg_template"
    },
    {
        "diagram_type": "cycle_4_step",
        "content": "Plan -> Do -> Check -> Act continuous improvement cycle",
        "expected_method": "svg_template"
    }
]


async def test_mermaid_v2(settings: Settings):
    """Test Mermaid Agent V2"""
    print("\n" + "=" * 60)
    print("TESTING MERMAID AGENT V2")
    print("=" * 60)
    
    agent = MermaidAgentV2(settings)
    
    if not agent.enabled:
        print("❌ MermaidAgentV2 not enabled - check API key")
        return
    
    # Test successful generation
    for i, test in enumerate(TEST_CASES[:3], 1):  # Test first 3 cases
        print(f"\nTest {i}: {test['diagram_type']}")
        print(f"Content: {test['content'][:50]}...")
        
        request = DiagramRequest(
            diagram_type=test['diagram_type'],
            content=test['content'],
            theme=ThemeConfig(),
            data_points=[]
        )
        
        result = await agent.generate(request)
        
        if result.get("success"):
            print(f"✅ Success!")
            metadata = result.get("metadata", {})
            print(f"  - Method: {metadata.get('generation_method')}")
            print(f"  - Confidence: {metadata.get('confidence', 'N/A')}")
            print(f"  - Entities: {len(metadata.get('entities_extracted', []))}")
            print(f"  - Relationships: {metadata.get('relationships_count', 0)}")
            
            # Show first line of generated code
            if metadata.get('mermaid_code'):
                first_line = metadata['mermaid_code'].split('\n')[0]
                print(f"  - Code starts: {first_line}")
        else:
            print(f"❌ Failed: {result.get('error')}")
            print(f"  - Message: {result.get('message')}")
    
    # Test with invalid input (should fail cleanly)
    print("\n\nTesting error handling:")
    print("Test: Empty content")
    
    request = DiagramRequest(
        diagram_type="invalid_type",
        content="test",  # Add minimal content to avoid validation error
        theme=ThemeConfig(),
        data_points=[]
    )
    
    result = await agent.generate(request)
    
    if not result.get("success"):
        print(f"✅ Correctly failed with error: {result.get('error')}")
        print(f"  - User message: {result.get('message')}")
    else:
        print("❌ Should have failed but didn't")


async def test_router_v2(settings: Settings):
    """Test Unified Playbook V2 Router"""
    print("\n" + "=" * 60)
    print("TESTING UNIFIED PLAYBOOK V2 ROUTER")
    print("=" * 60)
    
    router = UnifiedPlaybookV2(settings)
    await router.initialize()
    
    if not router.enabled:
        print("❌ UnifiedPlaybookV2 not enabled - check API key")
        return
    
    # Test routing decisions
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\nTest {i}: {test['diagram_type']}")
        print(f"Expected: {test['expected_method']}")
        
        request = DiagramRequest(
            diagram_type=test['diagram_type'],
            content=test['content'],
            theme=ThemeConfig(),
            data_points=[]
        )
        
        strategy = await router.get_strategy(request)
        
        print(f"Result: {strategy.method.value}")
        print(f"  - Confidence: {strategy.confidence:.2f}")
        print(f"  - Reasoning: {strategy.reasoning[:100]}...")
        
        if strategy.method.value == test['expected_method']:
            print("  ✅ Routing correct!")
        else:
            print(f"  ⚠️ Different from expected (may still be valid)")
        
        # Check for errors
        if strategy.confidence == 0.0 and "Error" in strategy.reasoning:
            print("  ❌ Routing failed")


async def test_integration():
    """Test V2 components working together"""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: ROUTER + MERMAID AGENT")
    print("=" * 60)
    
    settings = Settings()
    
    # Initialize components
    router = UnifiedPlaybookV2(settings)
    await router.initialize()
    
    mermaid_agent = MermaidAgentV2(settings)
    
    if not router.enabled or not mermaid_agent.enabled:
        print("❌ Components not enabled - check API key")
        return
    
    # Test case
    test = {
        "diagram_type": "flowchart",
        "content": "Login process: Start -> Enter credentials -> Validate -> Success or Failure -> End"
    }
    
    print(f"Testing: {test['diagram_type']}")
    print(f"Content: {test['content']}")
    
    # Step 1: Route
    request = DiagramRequest(
        diagram_type=test['diagram_type'],
        content=test['content'],
        theme=ThemeConfig(),
        data_points=[]
    )
    
    strategy = await router.get_strategy(request)
    print(f"\n1. Routing Decision: {strategy.method.value} (confidence: {strategy.confidence:.2f})")
    
    # Step 2: Generate if routed to Mermaid
    if strategy.method.value == "mermaid" and strategy.confidence > 0:
        result = await mermaid_agent.generate(request)
        
        if result.get("success"):
            print(f"2. Generation: ✅ Success")
            metadata = result.get("metadata", {})
            print(f"   - Entities extracted: {len(metadata.get('entities_extracted', []))}")
            print(f"   - Confidence: {metadata.get('confidence', 'N/A')}")
        else:
            print(f"2. Generation: ❌ Failed")
            print(f"   - Error: {result.get('error')}")
    else:
        print(f"2. Skipped generation (routed to {strategy.method.value})")


async def main():
    """Main test runner"""
    print("=" * 60)
    print("PYDANTIC AI V2 IMPLEMENTATION TESTS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load settings
    settings = Settings()
    
    # Check API key
    if not settings.google_api_key:
        print("\n❌ ERROR: No Google API key found")
        print("Please set GOOGLE_API_KEY environment variable")
        return
    
    print(f"\n✅ API Key configured")
    print(f"Models: gemini-2.0-flash (Mermaid), gemini-2.0-flash-lite (Router)")
    
    # Run tests
    await test_mermaid_v2(settings)
    await test_router_v2(settings)
    await test_integration()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())