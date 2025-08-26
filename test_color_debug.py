#!/usr/bin/env python3
"""Debug test for color duplication issue"""

import asyncio
import json
import websockets
from uuid import uuid4
import re

async def test_colors():
    uri = "ws://localhost:8080/ws"
    
    # Test matrix_2x2 for duplicate colors
    message = {
        "message_id": str(uuid4()),
        "type": "diagram_request",
        "payload": {
            "diagram_type": "matrix_2x2",
            "data_points": [
                {'label': 'Q1'}, 
                {'label': 'Q2'}, 
                {'label': 'Q3'}, 
                {'label': 'Q4'}
            ],
            "content": "Test matrix",
            "theme": {
                "primaryColor": "#10b981",
                "colorScheme": "monochromatic",
                "useSmartTheming": True
            },
            "method": "svg_template"
        }
    }
    
    print("Testing Matrix 2x2...")
    async with websockets.connect(uri) as websocket:
        # Wait for connection
        ack = await websocket.recv()
        print(f"Connected: {json.loads(ack)['type']}")
        
        # Send request
        await websocket.send(json.dumps(message))
        
        # Get response
        complete = False
        while not complete:
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("type") == "diagram_response":
                complete = True
                svg_content = data.get("payload", {}).get("content")
                
                if svg_content:
                    # Extract all fill colors for q1-q4
                    quadrant_colors = {}
                    for i in range(1, 5):
                        match = re.search(rf'id="q{i}_fill"[^>]*fill="([^"]*)"', svg_content)
                        if match:
                            quadrant_colors[f"Q{i}"] = match.group(1)
                    
                    print("\nQuadrant Colors:")
                    for q, color in quadrant_colors.items():
                        print(f"  {q}: {color}")
                    
                    # Check for duplicates
                    colors = list(quadrant_colors.values())
                    if len(colors) != len(set(colors)):
                        print("\n❌ DUPLICATE COLORS FOUND!")
                        for i, c1 in enumerate(colors):
                            for j, c2 in enumerate(colors[i+1:], i+1):
                                if c1 == c2:
                                    keys = list(quadrant_colors.keys())
                                    print(f"   {keys[i]} and {keys[j]} both have {c1}")
                    else:
                        print("\n✅ All colors are unique")
                    
                    # Save for inspection
                    with open("debug_matrix.svg", "w") as f:
                        f.write(svg_content)
                    print("\nSaved to debug_matrix.svg")

if __name__ == "__main__":
    asyncio.run(test_colors())