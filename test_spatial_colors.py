#!/usr/bin/env python3
"""Test spatial color assignment for all diagram types"""

import asyncio
import json
import websockets
from uuid import uuid4
import re

async def test_spatial_colors():
    uri = "ws://localhost:8080/ws"
    
    test_configs = [
        {
            "name": "matrix_2x2",
            "diagram_type": "matrix_2x2",
            "labels": ["High/High", "Low/High", "Low/Low", "High/Low"],
            "primary_color": "#10b981",
            "color_scheme": "monochromatic"
        },
        {
            "name": "hub_spoke_4",
            "diagram_type": "hub_spoke_4", 
            "labels": ["Central Hub", "North", "East", "South", "West"],
            "primary_color": "#f59e0b",
            "color_scheme": "monochromatic"
        },
        {
            "name": "pyramid_5",
            "diagram_type": "pyramid_5_level",
            "labels": ["Foundation", "Layer 2", "Layer 3", "Layer 4", "Peak"],
            "primary_color": "#3b82f6",
            "color_scheme": "monochromatic"
        },
        {
            "name": "venn_2",
            "diagram_type": "venn_2_circle",
            "labels": ["Set A", "Set B", "A ∩ B"],
            "primary_color": "#8b5cf6",
            "color_scheme": "monochromatic"
        }
    ]
    
    print("=" * 60)
    print("SPATIAL COLOR ASSIGNMENT TEST")
    print("=" * 60)
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection
        ack = await websocket.recv()
        print(f"Connected: {json.loads(ack)['type']}\n")
        
        for config in test_configs:
            print(f"\nTesting {config['name']}...")
            print(f"  Primary color: {config['primary_color']}")
            
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
                        with open(f"spatial_{config['name']}.svg", "w") as f:
                            f.write(svg_content)
                        
                        # Analyze colors
                        if config['name'] == 'matrix_2x2':
                            # Check quadrant colors
                            q_colors = []
                            for i in range(1, 5):
                                match = re.search(rf'id="q{i}_fill"[^>]*fill="([^"]*)"', svg_content)
                                if match:
                                    q_colors.append(match.group(1))
                            print(f"  Quadrant colors (2D gradient):")
                            print(f"    Q1 (top-right): {q_colors[0] if len(q_colors) > 0 else 'N/A'}")
                            print(f"    Q2 (top-left): {q_colors[1] if len(q_colors) > 1 else 'N/A'}")
                            print(f"    Q3 (bottom-left): {q_colors[2] if len(q_colors) > 2 else 'N/A'}")
                            print(f"    Q4 (bottom-right): {q_colors[3] if len(q_colors) > 3 else 'N/A'}")
                            
                            # Check text colors
                            text_colors = []
                            for i in range(1, 5):
                                match = re.search(rf'id="quadrant_{i}"[^>]*fill="([^"]*)"', svg_content)
                                if match:
                                    text_colors.append(match.group(1))
                            print(f"  Text contrast: {text_colors}")
                        
                        elif config['name'] == 'hub_spoke_4':
                            # Check hub and spoke colors
                            hub_match = re.search(r'id="hub_fill"[^>]*fill="([^"]*)"', svg_content)
                            print(f"  Hub color: {hub_match.group(1) if hub_match else 'N/A'}")
                            
                            spoke_colors = []
                            for i in range(1, 5):
                                match = re.search(rf'id="spoke_{i}_fill"[^>]*fill="([^"]*)"', svg_content)
                                if match:
                                    spoke_colors.append(match.group(1))
                            print(f"  Spoke colors (radial): {spoke_colors}")
                        
                        elif config['name'] == 'pyramid_5':
                            # Check level colors
                            level_colors = []
                            for i in range(1, 6):
                                match = re.search(rf'id="level_{i}"[^>]*fill="([^"]*)"', svg_content)
                                if match:
                                    level_colors.append(match.group(1))
                            print(f"  Level colors (vertical gradient):")
                            for i, color in enumerate(level_colors, 1):
                                print(f"    Level {i}: {color}")
                        
                        elif config['name'] == 'venn_2':
                            # Check circle and intersection colors
                            circle1_match = re.search(r'id="circle_1"[^>]*fill="([^"]*)"', svg_content)
                            circle2_match = re.search(r'id="circle_2"[^>]*fill="([^"]*)"', svg_content)
                            
                            # Look for various intersection patterns
                            intersection_match = None
                            patterns = [
                                r'id="intersection[^"]*"[^>]*fill="([^"]*)"',
                                r'id="overlap[^"]*"[^>]*fill="([^"]*)"',
                                r'class="intersection[^"]*"[^>]*fill="([^"]*)"'
                            ]
                            for pattern in patterns:
                                intersection_match = re.search(pattern, svg_content)
                                if intersection_match:
                                    break
                            
                            print(f"  Circle 1: {circle1_match.group(1) if circle1_match else 'N/A'}")
                            print(f"  Circle 2: {circle2_match.group(1) if circle2_match else 'N/A'}")
                            print(f"  Intersection (blended): {intersection_match.group(1) if intersection_match else 'Not found'}")
                        
                        print(f"  ✅ Saved as spatial_{config['name']}.svg")
                    else:
                        print(f"  ❌ No SVG content")
                        
                elif data.get("type") == "error_response":
                    complete = True
                    print(f"  ❌ Error: {data.get('payload', {}).get('error_message')}")
    
    print("\n" + "=" * 60)
    print("Test complete! Check the generated SVG files")
    print("Expected results:")
    print("  - Matrix: 2D gradient with smooth transitions")
    print("  - Hub & Spoke: Radial color progression")
    print("  - Pyramid: Vertical gradient (dark to light)")
    print("  - Venn: Darker intersection for proper text contrast")

if __name__ == "__main__":
    asyncio.run(test_spatial_colors())