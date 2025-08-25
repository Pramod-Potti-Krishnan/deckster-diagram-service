#!/usr/bin/env python3
"""
Specific Gantt Chart Test
=========================
Debug why Gantt charts are failing on Railway.
"""

import asyncio
import json
import websockets
import ssl
import time
from datetime import datetime

async def test_gantt_debug():
    """Test Gantt chart with detailed logging"""
    
    print("🔍 Gantt Chart Debug Test")
    print("=" * 60)
    
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = f"gantt-debug-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    full_url = f"{url}?session_id={session_id}&user_id=test"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        print("Connecting to WebSocket...")
        async with websockets.connect(full_url, ssl=ssl_context, ping_timeout=20) as ws:
            # Get welcome message
            welcome = await ws.recv()
            print(f"Welcome: {welcome}")
            
            # Send Gantt request
            request = {
                "type": "diagram_request",
                "correlation_id": "gantt-test",
                "data": {
                    "diagram_type": "gantt",
                    "content": "Create a simple Gantt chart with 3 tasks: Planning (Week 1), Development (Week 2-3), Testing (Week 4)",
                    "theme": {
                        "primaryColor": "#3B82F6",
                        "secondaryColor": "#60A5FA"
                    }
                }
            }
            
            print(f"\nSending request: {json.dumps(request, indent=2)}")
            await ws.send(json.dumps(request))
            
            # Collect all responses
            print("\nReceiving responses:")
            for i in range(15):  # Try up to 15 messages
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=10)
                    msg = json.loads(response)
                    
                    print(f"\n[Message {i+1}] Type: {msg.get('type')}")
                    
                    if msg.get("type") == "status_update":
                        payload = msg.get("payload", {})
                        print(f"  Status: {payload.get('status')}")
                        print(f"  Message: {payload.get('message')}")
                        
                    elif msg.get("type") == "diagram_response":
                        payload = msg.get("payload", {})
                        print(f"  ✅ SUCCESS - Diagram generated")
                        print(f"  Has content: {bool(payload.get('content'))}")
                        print(f"  Content type: {payload.get('content_type')}")
                        
                        metadata = payload.get("metadata", {})
                        print(f"  Metadata: {json.dumps(metadata, indent=4)}")
                        
                        # Check for Mermaid code
                        if "mermaid_code" in metadata:
                            code = metadata["mermaid_code"]
                            print(f"\n  Generated Mermaid code:")
                            print("  " + "\n  ".join(code.split("\n")))
                        
                        return True
                        
                    elif msg.get("type") == "error_response":
                        payload = msg.get("payload", {})
                        print(f"  ❌ ERROR: {payload.get('error_message')}")
                        print(f"  Details: {payload.get('details')}")
                        print(f"  Stack: {payload.get('stack_trace', '')[:500]}")
                        return False
                        
                except asyncio.TimeoutError:
                    print(f"  Timeout waiting for message {i+1}")
                    continue
            
            print("\n⚠️ No final response received after all attempts")
            return False
            
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main entry point"""
    
    success = await test_gantt_debug()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Gantt chart generated successfully!")
    else:
        print("❌ Gantt chart generation failed")
        print("\nPossible issues:")
        print("1. The validator changes haven't been deployed yet")
        print("2. Gemini API key not configured in Railway")
        print("3. LLM still generating invalid syntax")

if __name__ == "__main__":
    asyncio.run(main())