#!/usr/bin/env python3
"""
Test SVG Generation on Railway
===============================
Debug why SVG diagrams are failing.
"""

import asyncio
import json
import websockets
import ssl
from datetime import datetime

async def test_svg_diagram():
    """Test a simple SVG diagram request"""
    
    print("🔍 Testing SVG Diagram Generation")
    print("=" * 60)
    
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = f"svg-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    full_url = f"{url}?session_id={session_id}&user_id=test"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Test a simple pyramid diagram
    test_cases = [
        {
            "type": "pyramid",
            "content": "Simple pyramid with 3 levels: Top Level, Middle Level, Bottom Level"
        },
        {
            "type": "funnel", 
            "content": "Sales funnel: Visitors (1000), Leads (200), Customers (50)"
        },
        {
            "type": "venn",
            "content": "Two circles: Circle A (Item 1, Item 2), Circle B (Item 3, Item 4), Overlap (Shared)"
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting {test_case['type']}...")
        print(f"Content: {test_case['content']}")
        
        try:
            async with websockets.connect(full_url, ssl=ssl_context, ping_timeout=20) as ws:
                # Get welcome message
                welcome = await ws.recv()
                welcome_data = json.loads(welcome)
                print(f"Connected. Version: {welcome_data.get('payload', {}).get('version')}")
                print(f"Capabilities: {welcome_data.get('payload', {}).get('capabilities')}")
                
                # Send SVG diagram request
                request = {
                    "type": "diagram_request",
                    "correlation_id": f"svg-{test_case['type']}-test",
                    "data": {
                        "diagram_type": test_case["type"],
                        "content": test_case["content"],
                        "theme": {
                            "primaryColor": "#3B82F6",
                            "secondaryColor": "#60A5FA"
                        }
                    }
                }
                
                print(f"\nSending request...")
                await ws.send(json.dumps(request))
                
                # Collect responses
                for i in range(10):
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=10)
                        msg = json.loads(response)
                        
                        print(f"Response {i+1}: Type = {msg.get('type')}")
                        
                        if msg.get("type") == "status_update":
                            payload = msg.get("payload", {})
                            print(f"  Status: {payload.get('status')}")
                            print(f"  Message: {payload.get('message')}")
                            
                        elif msg.get("type") == "diagram_response":
                            payload = msg.get("payload", {})
                            print(f"  ✅ SUCCESS - Diagram generated")
                            print(f"  Content type: {payload.get('content_type')}")
                            print(f"  Has content: {bool(payload.get('content'))}")
                            
                            metadata = payload.get("metadata", {})
                            print(f"  Generation method: {metadata.get('generation_method')}")
                            print(f"  Fallback used: {metadata.get('fallback_used')}")
                            
                            # Check if it's actually SVG
                            content = payload.get('content', '')
                            if content.startswith('<svg'):
                                print(f"  ✅ Valid SVG content (length: {len(content)})")
                            else:
                                print(f"  ⚠️ Not SVG content")
                            break
                            
                        elif msg.get("type") == "error_response":
                            payload = msg.get("payload", {})
                            print(f"  ❌ ERROR: {payload.get('error_message')}")
                            print(f"  Details: {payload.get('details')}")
                            
                            # Print stack trace if available
                            if payload.get('stack_trace'):
                                print(f"  Stack trace (first 500 chars):")
                                print(f"  {payload.get('stack_trace')[:500]}")
                            break
                            
                    except asyncio.TimeoutError:
                        print(f"  Timeout waiting for response {i+1}")
                        continue
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("SVG Test Complete")
    print("\nPossible issues if SVG failed:")
    print("1. SVG templates not found in deployment")
    print("2. SVG agent not enabled in Railway config")
    print("3. File path issues in production environment")
    print("4. Missing dependencies for SVG generation")

if __name__ == "__main__":
    asyncio.run(test_svg_diagram())