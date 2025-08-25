#!/usr/bin/env python3
"""
Test Railway deployment status and configuration
"""

import asyncio
import json
import websockets
import ssl

async def test_deployment():
    """Test what the Railway service supports"""
    
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = "deployment-test"
    full_url = f"{url}?session_id={session_id}&user_id=test"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Test with the new type names
    test_types = [
        ("flowchart", "Create a simple flow: A -> B -> C"),
        ("erDiagram", "Create entities: User with id and name, Order with id and total"),
        ("journey", "User buys product: Browse (4), Purchase (5)"),
        ("gantt", "Week 1: Task A, Week 2: Task B"),
        ("quadrantChart", "Plot risks: High risk at 0.8,0.8"),
        ("timeline", "2020: Founded, 2021: Growth, 2022: IPO"),
        ("kanban", "Todo: Task1, In Progress: Task2, Done: Task3")
    ]
    
    print("Testing Railway deployment with new diagram types...")
    print("=" * 60)
    
    for diagram_type, content in test_types:
        try:
            async with websockets.connect(full_url, ssl=ssl_context, ping_timeout=10) as ws:
                # Skip welcome
                await ws.recv()
                
                # Send request
                request = {
                    "type": "diagram_request",
                    "correlation_id": f"test-{diagram_type}",
                    "data": {
                        "diagram_type": diagram_type,
                        "content": content,
                        "theme": {"primaryColor": "#3B82F6"}
                    }
                }
                
                await ws.send(json.dumps(request))
                
                # Get response
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "diagram_response":
                        print(f"✅ {diagram_type}: SUCCESS")
                        payload = data.get("payload", {})
                        if payload.get("metadata"):
                            method = payload["metadata"].get("generation_method", "unknown")
                            print(f"   Method: {method}")
                    elif data.get("type") == "error_response":
                        error = data.get("payload", {}).get("error_message", "Unknown")
                        print(f"❌ {diagram_type}: {error}")
                    else:
                        print(f"❓ {diagram_type}: Unexpected response type")
                        
                except asyncio.TimeoutError:
                    print(f"⏱️  {diagram_type}: Timeout")
                    
        except Exception as e:
            print(f"💥 {diagram_type}: Connection error - {str(e)}")
            
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_deployment())