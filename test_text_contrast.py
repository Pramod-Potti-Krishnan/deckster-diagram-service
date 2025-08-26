#!/usr/bin/env python3
"""Test text contrast after fix"""

import asyncio
import json
import websockets
from uuid import uuid4
import re

async def test_text_contrast():
    uri = "ws://localhost:8080/ws"
    output_dir = "test_contrast_output"
    
    test_configs = [
        {
            "name": "matrix_2x2",
            "diagram_type": "matrix_2x2",
            "labels": ["High Impact", "Quick Wins", "Fill Ins", "Time Sinks"],
            "primary_color": "#10b981",
            "color_scheme": "monochromatic"
        },
        {
            "name": "hub_spoke_4",
            "diagram_type": "hub_spoke_4", 
            "labels": ["Central Hub", "North", "East", "South", "West"],
            "primary_color": "#f59e0b",
            "color_scheme": "complementary"
        },
        {
            "name": "pyramid_5",
            "diagram_type": "pyramid_5_level",
            "labels": ["Foundation", "Layer 2", "Layer 3", "Layer 4", "Peak"],
            "primary_color": "#3b82f6",
            "color_scheme": "monochromatic"
        }
    ]
    
    print("=" * 60)
    print("TEXT CONTRAST TEST - After Fix")
    print("=" * 60)
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection
        ack = await websocket.recv()
        print(f"Connected: {json.loads(ack)['type']}\n")
        
        for config in test_configs:
            print(f"\nTesting {config['name']}...")
            
            message = {
                "message_id": str(uuid4()),
                "type": "diagram_request",
                "payload": {
                    "diagram_type": config["diagram_type"],
                    "data_points": [{'label': label} for label in config["labels"]],
                    "content": f"Test {config['name']}",
                    "theme": {
                        "primaryColor": config["primary_color"],
                        "colorScheme": config["color_scheme"],
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
                        # Save SVG
                        with open(f"{config['name']}_contrast.svg", "w") as f:
                            f.write(svg_content)
                        
                        # Analyze text colors for specific elements
                        if config['name'] == 'matrix_2x2':
                            # Check Q4 (Time Sinks) text color - should be white on dark green
                            q4_text_match = re.search(r'id="quadrant_4"[^>]*fill="([^"]*)"', svg_content)
                            if q4_text_match:
                                q4_text_color = q4_text_match.group(1)
                                print(f"  Q4 'Time Sinks' text: {q4_text_color} (should be white/light)")
                        
                        elif config['name'] == 'hub_spoke_4':
                            # Check North text color - should be black on light orange
                            north_text_match = re.search(r'id="spoke_1_text"[^>]*fill="([^"]*)"', svg_content)
                            if north_text_match:
                                north_text_color = north_text_match.group(1)
                                print(f"  North text: {north_text_color} (should be black/dark)")
                            
                            # Check South text color - should be white on dark brown
                            south_text_match = re.search(r'id="spoke_3_text"[^>]*fill="([^"]*)"', svg_content)
                            if south_text_match:
                                south_text_color = south_text_match.group(1)
                                print(f"  South text: {south_text_color} (should be white/light)")
                        
                        elif config['name'] == 'pyramid_5':
                            # Check Layer 2 text color
                            layer2_text_match = re.search(r'id="level_2"[^>]*fill="([^"]*)"', svg_content)
                            if layer2_text_match:
                                layer2_text_color = layer2_text_match.group(1)
                                print(f"  Layer 2 text: {layer2_text_color}")
                        
                        print(f"  ✅ Saved as {config['name']}_contrast.svg")
    
    print("\n" + "=" * 60)
    print("Test complete! Check the generated SVG files")

if __name__ == "__main__":
    asyncio.run(test_text_contrast())