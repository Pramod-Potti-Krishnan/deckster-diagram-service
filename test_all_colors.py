#!/usr/bin/env python3
"""Test all diagram types for color uniqueness"""

import asyncio
import json
import websockets
from uuid import uuid4
import re

async def test_diagram(websocket, diagram_type, labels, primary_color="#10b981"):
    """Test a single diagram type"""
    message = {
        "message_id": str(uuid4()),
        "type": "diagram_request",
        "payload": {
            "diagram_type": diagram_type,
            "data_points": [{'label': label} for label in labels],
            "content": f"Test {diagram_type}",
            "theme": {
                "primaryColor": primary_color,
                "colorScheme": "monochromatic",
                "useSmartTheming": True
            },
            "method": "svg_template"
        }
    }
    
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
                # Extract all fill colors
                fill_colors = re.findall(r'fill="(#[0-9a-fA-F]{6})"', svg_content)
                unique_colors = list(set(fill_colors))
                
                # Save for inspection
                with open(f"test_output_{diagram_type}.svg", "w") as f:
                    f.write(svg_content)
                
                return {
                    "diagram_type": diagram_type,
                    "total_fills": len(fill_colors),
                    "unique_colors": len(unique_colors),
                    "colors": unique_colors[:10]  # First 10 unique colors
                }
            else:
                return {"diagram_type": diagram_type, "error": "No SVG content"}
        elif data.get("type") == "error_response":
            complete = True
            return {"diagram_type": diagram_type, "error": data.get("payload", {}).get("error_message")}

async def test_all():
    uri = "ws://localhost:8080/ws"
    
    test_cases = [
        ("matrix_2x2", ["Q1", "Q2", "Q3", "Q4"]),
        ("pyramid_5_level", ["Base", "L2", "L3", "L4", "Top"]),
        ("hub_spoke_4", ["Hub", "N", "E", "S", "W"]),
        ("venn_2_circle", ["A", "B", "A∩B"]),
        ("honeycomb", ["C", "N", "E", "SE", "S", "SW", "W"]),
    ]
    
    print("=" * 60)
    print("COLOR UNIQUENESS TEST")
    print("=" * 60)
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection
        ack = await websocket.recv()
        print(f"Connected: {json.loads(ack)['type']}\n")
        
        for diagram_type, labels in test_cases:
            print(f"\nTesting {diagram_type}...")
            result = await test_diagram(websocket, diagram_type, labels)
            
            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                print(f"  Total fill commands: {result['total_fills']}")
                print(f"  Unique colors: {result['unique_colors']}")
                print(f"  Sample colors: {', '.join(result['colors'][:5])}")
                
                # Check for specific known issues
                if diagram_type == "matrix_2x2":
                    # Should have at least 4 different colors for quadrants
                    if result['unique_colors'] < 4:
                        print(f"  ⚠️ WARNING: Matrix should have 4+ unique colors")
                elif diagram_type == "hub_spoke_4":
                    # Should have at least 5 different colors (hub + 4 spokes)
                    if result['unique_colors'] < 5:
                        print(f"  ⚠️ WARNING: Hub-spoke should have 5+ unique colors")
    
    print("\n" + "=" * 60)
    print("Test complete! Check test_output_*.svg files")

if __name__ == "__main__":
    asyncio.run(test_all())