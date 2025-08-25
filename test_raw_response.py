#!/usr/bin/env python3
"""
Test raw response from Railway
"""

import asyncio
import json
import websockets
import ssl

async def test_raw():
    """Test and print raw response"""
    
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = "raw-test"
    full_url = f"{url}?session_id={session_id}&user_id=test"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    print("Testing flowchart (should work)...")
    
    try:
        async with websockets.connect(full_url, ssl=ssl_context) as ws:
            # Print welcome
            welcome = await ws.recv()
            print(f"Welcome: {welcome}\n")
            
            # Send flowchart request
            request = {
                "type": "diagram_request",
                "correlation_id": "test-1",
                "data": {
                    "diagram_type": "flowchart",
                    "content": "Create a simple flow: Start -> Process -> End",
                    "theme": {"primaryColor": "#3B82F6"}
                }
            }
            
            print(f"Sending: {json.dumps(request, indent=2)}\n")
            await ws.send(json.dumps(request))
            
            # Get all responses
            for i in range(3):
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=3.0)
                    data = json.loads(response)
                    print(f"Response {i+1}:")
                    print(json.dumps(data, indent=2))
                    print()
                except asyncio.TimeoutError:
                    print("No more responses")
                    break
                    
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*60)
    print("Testing erDiagram (new name)...")
    
    try:
        async with websockets.connect(full_url, ssl=ssl_context) as ws:
            # Skip welcome
            await ws.recv()
            
            # Send erDiagram request
            request = {
                "type": "diagram_request",
                "correlation_id": "test-2",
                "data": {
                    "diagram_type": "erDiagram",
                    "content": "User entity with id and name, Order entity with id and total",
                    "theme": {"primaryColor": "#3B82F6"}
                }
            }
            
            print(f"Sending: {json.dumps(request, indent=2)}\n")
            await ws.send(json.dumps(request))
            
            # Get response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                print("Response:")
                print(json.dumps(data, indent=2))
            except asyncio.TimeoutError:
                print("Timeout - no response")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_raw())