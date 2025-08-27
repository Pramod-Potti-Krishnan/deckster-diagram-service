#!/usr/bin/env python3
"""
Debug Mermaid Generation
"""

import asyncio
import json
import websockets
import uuid
from datetime import datetime

async def test_mermaid():
    """Test a single Mermaid flowchart generation"""
    
    ws_url = "ws://127.0.0.1:8001/ws"
    session_id = str(uuid.uuid4())
    
    async with websockets.connect(f"{ws_url}?session_id={session_id}&user_id=debug_test") as websocket:
        print("Connected to WebSocket server")
        
        # Simple flowchart request
        request = {
            "message_id": f"msg_{uuid.uuid4()}",
            "correlation_id": f"req_{uuid.uuid4()}",
            "request_id": f"req_{uuid.uuid4()}",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "diagram_request",
            "payload": {
                "content": "Simple login flow: User enters username and password. System validates. If valid, redirect to dashboard. If invalid, show error.",
                "diagram_type": "flowchart",
                "output_format": "mermaid",
                "theme": {
                    "primaryColor": "#3B82F6",
                    "backgroundColor": "#FFFFFF"
                }
            }
        }
        
        # Send request
        await websocket.send(json.dumps(request))
        print("Sent flowchart request")
        
        # Collect all responses
        responses = []
        start_time = datetime.now()
        
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                response_json = json.loads(response)
                responses.append(response_json)
                
                msg_type = response_json.get("type")
                print(f"Received: {msg_type}")
                
                if msg_type == "status":
                    payload = response_json.get("payload", {})
                    print(f"  Status: {payload.get('status')} - {payload.get('message')}")
                    
                elif msg_type in ["response", "diagram_response"]:
                    print("  ✅ Got response!")
                    payload = response_json.get("payload", {})
                    
                    # Check what we got
                    if "mermaid_code" in payload.get("metadata", {}):
                        print(f"  Mermaid code in metadata: {len(payload['metadata']['mermaid_code'])} chars")
                    
                    if "content" in payload:
                        print(f"  Content type: {payload.get('content_type')}")
                        print(f"  Content length: {len(payload['content'])} chars")
                        
                        # Check if it's our client-renderable SVG
                        if "application/mermaid+json" in payload['content']:
                            print("  ✅ Got client-renderable SVG with embedded Mermaid!")
                            
                            # Extract Mermaid code from SVG
                            import re
                            match = re.search(r'"code":\s*"([^"]+)"', payload['content'])
                            if match:
                                mermaid_code = match.group(1).replace("\\n", "\n")
                                print(f"  Extracted Mermaid code:")
                                print("  " + "-" * 40)
                                print(mermaid_code)
                                print("  " + "-" * 40)
                    
                    break
                    
                elif msg_type == "error":
                    print(f"  ❌ Error: {response_json.get('payload', {})}")
                    break
                    
            except asyncio.TimeoutError:
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"  ⏱️ Timeout after {elapsed:.1f}s")
                break
            except Exception as e:
                print(f"  ❌ Exception: {e}")
                break
        
        # Save all responses for debugging
        with open("mermaid_debug_responses.json", "w") as f:
            json.dump(responses, f, indent=2)
        print(f"\nSaved {len(responses)} responses to mermaid_debug_responses.json")

if __name__ == "__main__":
    asyncio.run(test_mermaid())