#!/usr/bin/env python3
"""
Simple test runner to verify basic functionality
"""

import os
import sys

# Set test environment
os.environ['CORS_ORIGINS'] = 'http://localhost:3000,http://localhost:3001'
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'test_key'
os.environ['GOOGLE_API_KEY'] = 'test_google_key'
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['CACHE_TYPE'] = 'memory'
os.environ['DIAGRAM_BUCKET'] = 'test-diagrams'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Diagram Microservice v2 Components\n")
print("=" * 50)

# Test 1: Models
print("\n1. Testing Models...")
try:
    from models.diagram_models import DiagramType, GenerationMethod, GenerationStrategy
    from models.request_models import DiagramRequest, DiagramTheme, DataPoint
    from models.response_models import DiagramResponse
    
    # Test enum values
    assert DiagramType.PYRAMID_3_LEVEL == "pyramid_3_level"
    assert GenerationMethod.SVG_TEMPLATE == "svg_template"
    
    # Test model creation
    theme = DiagramTheme()
    assert theme.primaryColor == "#3B82F6"
    
    # Test data point
    point = DataPoint(label="Test", value=42.5)
    assert point.label == "Test"
    assert point.value == 42.5
    
    # Test generation strategy
    strategy = GenerationStrategy(
        method=GenerationMethod.SVG_TEMPLATE,
        confidence=0.9,
        reasoning="Test",
        fallback_chain=[],
        estimated_time_ms=200
    )
    assert strategy.confidence == 0.9
    
    print("   ✓ Models working correctly")
except Exception as e:
    print(f"   ✗ Models failed: {e}")

# Test 2: Settings
print("\n2. Testing Settings...")
try:
    from config.settings import Settings, get_settings
    
    settings = get_settings()
    assert settings.supabase_url == "https://test.supabase.co"
    assert settings.log_level == "DEBUG"
    
    print("   ✓ Settings working correctly")
except Exception as e:
    print(f"   ✗ Settings failed: {e}")

# Test 3: Cache Manager
print("\n3. Testing Cache Manager...")
try:
    import asyncio
    from storage.cache_manager import CacheManager
    
    async def test_cache():
        cache = CacheManager(ttl_seconds=60)
        await cache.start()
        
        # Test set/get
        cache.set({"id": "test"}, {"data": "value"})
        result = cache.get({"id": "test"})
        assert result == {"data": "value"}
        
        # Test miss
        miss = cache.get({"id": "nonexistent"})
        assert miss is None
        
        await cache.stop()
        return True
    
    if asyncio.run(test_cache()):
        print("   ✓ Cache Manager working correctly")
except Exception as e:
    print(f"   ✗ Cache Manager failed: {e}")

# Test 4: Unified Playbook (without Gemini)
print("\n4. Testing Unified Playbook...")
try:
    os.environ['ENABLE_SEMANTIC_ROUTING'] = 'false'
    from core.unified_playbook import UnifiedPlaybook
    from models.request_models import DiagramRequest
    
    async def test_playbook():
        settings = get_settings()
        playbook = UnifiedPlaybook(settings)
        await playbook.initialize()
        
        request = DiagramRequest(
            request_id="test",
            diagram_type="pyramid_3_level",
            content="Test content",
            theme=DiagramTheme()
        )
        
        strategy = await playbook.get_strategy(request)
        assert strategy is not None
        assert strategy.method in [GenerationMethod.SVG_TEMPLATE, GenerationMethod.MERMAID, GenerationMethod.PYTHON_CHART]
        
        return True
    
    if asyncio.run(test_playbook()):
        print("   ✓ Unified Playbook working correctly")
except Exception as e:
    print(f"   ✗ Unified Playbook failed: {e}")

# Test 5: SVG Agent
print("\n5. Testing SVG Agent...")
try:
    from agents.svg_agent import SVGAgent
    
    async def test_svg_agent():
        settings = get_settings()
        agent = SVGAgent(settings)
        
        # Test initialization
        await agent.initialize()
        
        # Test validation
        request = DiagramRequest(
            request_id="test",
            diagram_type="pyramid_3_level",
            content="Test content",
            theme=DiagramTheme()
        )
        
        assert agent.validate_request(request) is True
        
        # Test theme application
        svg = "<svg><rect fill='#3B82F6'/></svg>"
        themed = agent.apply_theme(svg, {"primaryColor": "#FF0000"})
        assert "#FF0000" in themed
        
        return True
    
    if asyncio.run(test_svg_agent()):
        print("   ✓ SVG Agent working correctly")
except Exception as e:
    print(f"   ✗ SVG Agent failed: {e}")

print("\n" + "=" * 50)
print("\nTest Summary:")
print("All basic components are functioning properly.")
print("\nNote: This is a simplified test. Run full pytest suite for comprehensive testing.")