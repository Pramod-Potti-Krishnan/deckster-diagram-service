#!/usr/bin/env python3
"""Test Railway deployment with correct message protocol"""

import asyncio
import json
import websockets
import ssl
from pathlib import Path
from uuid import uuid4

# Create SSL context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def test_railway_deployment():
    uri = "wss://deckster-diagram-service-production.up.railway.app/ws"
    output_dir = Path("railway_test_final")
    output_dir.mkdir(exist_ok=True)
    
    test_configs = [
        {
            "name": "pyramid_5_mono",
            "diagram_type": "pyramid_5_level",
            "labels": ["Foundation", "Layer 2", "Layer 3", "Layer 4", "Peak"],
            "content": "5-level pyramid with monochromatic theme",
            "primary_color": "#3b82f6",
            "color_scheme": "monochromatic"
        },
        {
            "name": "pyramid_5_comp",
            "diagram_type": "pyramid_5_level",
            "labels": ["Base", "Level 2", "Level 3", "Level 4", "Top"],
            "content": "5-level pyramid with complementary colors",
            "primary_color": "#8b5cf6",
            "color_scheme": "complementary"
        },
        {
            "name": "matrix_2x2_mono",
            "diagram_type": "matrix_2x2",
            "labels": ["High Impact", "Quick Wins", "Fill Ins", "Time Sinks"],
            "content": "Priority matrix with monochromatic theme",
            "primary_color": "#10b981",
            "color_scheme": "monochromatic"
        },
        {
            "name": "hub_spoke_4",
            "diagram_type": "hub_spoke_4",
            "labels": ["Central Hub", "North", "East", "South", "West"],
            "content": "Hub and spoke network",
            "primary_color": "#f59e0b",
            "color_scheme": "complementary"
        },
        {
            "name": "venn_2_circle",
            "diagram_type": "venn_2_circle",
            "labels": ["Set A", "Set B", "A ∩ B"],
            "content": "Venn diagram",
            "primary_color": "#06b6d4",
            "color_scheme": "complementary"
        }
    ]
    
    print("=" * 60)
    print("Testing Railway Deployment - Final Color Test")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    try:
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            # Wait for connection acknowledgment
            ack = await websocket.recv()
            ack_data = json.loads(ack)
            print(f"✅ Connected: {ack_data.get('type', 'unknown')}")
            
            for config in test_configs:
                print(f"\n📊 Testing: {config['name']}")
                print(f"   Type: {config['diagram_type']}")
                print(f"   Color: {config['primary_color']} ({config['color_scheme']})")
                
                # Create properly formatted message
                message = {
                    "message_id": str(uuid4()),
                    "type": "diagram_request",
                    "payload": {
                        "diagram_type": config["diagram_type"],
                        "data_points": [{'label': label} for label in config["labels"]],
                        "content": config["content"],
                        "theme": {
                            "primaryColor": config["primary_color"],
                            "colorScheme": config["color_scheme"],
                            "useSmartTheming": True
                        },
                        "method": "svg_template"
                    }
                }
                
                try:
                    await websocket.send(json.dumps(message))
                    
                    # Keep receiving until we get a generation_complete message
                    complete = False
                    svg_content = None
                    
                    while not complete:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        data = json.loads(response)
                        
                        if data.get("type") == "diagram_response":
                            complete = True
                            payload = data.get("payload", {})
                            svg_content = payload.get("content")  # SVG is in 'content' field
                            
                            if svg_content:
                                # Save SVG
                                output_file = output_dir / f"{config['name']}.svg"
                                with open(output_file, 'w') as f:
                                    f.write(svg_content)
                                
                                # Analyze colors
                                import re
                                fill_colors = re.findall(r'fill="(#[0-9a-fA-F]{6})"', svg_content)
                                unique_colors = list(set(fill_colors))
                                
                                successful += 1
                                print(f"   ✅ Success!")
                                print(f"   🎨 Unique colors: {len(unique_colors)}")
                                print(f"   🎨 Sample: {', '.join(unique_colors[:5])}")
                            else:
                                failed += 1
                                print(f"   ❌ No SVG content")
                                
                        elif data.get("type") == "error_response":
                            complete = True
                            failed += 1
                            error_msg = data.get("payload", {}).get("error_message", "Unknown error")
                            print(f"   ❌ Error: {error_msg}")
                            
                        elif data.get("type") == "status_update":
                            status = data.get("payload", {}).get("status")
                            if status == "error":
                                complete = True
                                failed += 1
                                msg = data.get("payload", {}).get("message", "Unknown error")
                                print(f"   ❌ Status error: {msg}")
                            else:
                                # Progress update, continue waiting
                                pass
                                
                except asyncio.TimeoutError:
                    failed += 1
                    print(f"   ❌ Timeout")
                except Exception as e:
                    failed += 1
                    print(f"   ❌ Exception: {e}")
                    
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {successful}/{len(test_configs)}")
    print(f"❌ Failed: {failed}/{len(test_configs)}")
    
    if successful > 0:
        print(f"\n📁 SVGs saved to: {output_dir.absolute()}")
    
    print("\n✨ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_railway_deployment())