#!/usr/bin/env python3
"""
Debug Railway response to see what's being returned
"""

import asyncio
import json
import websockets
import ssl

async def debug_response():
    """Debug what Railway is returning"""
    
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = "debug-test"
    full_url = f"{url}?session_id={session_id}&user_id=test"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    print("Connecting to Railway...")
    
    try:
        async with websockets.connect(full_url, ssl=ssl_context, ping_timeout=10) as ws:
            # Get welcome message
            welcome = await ws.recv()
            print(f"Welcome: {welcome}\n")
            
            # Send a simple flowchart request
            request = {
                "type": "diagram_request",
                "correlation_id": "test-1",
                "data": {
                    "diagram_type": "flowchart",
                    "content": "Simple flow: Start -> Process -> End",
                    "theme": {"primaryColor": "#3B82F6"}
                }
            }
            
            print(f"Sending: {json.dumps(request, indent=2)}\n")
            await ws.send(json.dumps(request))
            
            # Get all responses
            for i in range(10):
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    print(f"Response {i+1}:")
                    
                    # Try to parse as JSON
                    try:
                        data = json.loads(response)
                        print(json.dumps(data, indent=2))
                    except json.JSONDecodeError:
                        print(f"Raw: {response}")
                    
                    print()
                except asyncio.TimeoutError:
                    print("No more responses (timeout)")
                    break
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_response())