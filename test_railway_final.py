#!/usr/bin/env python3
"""Comprehensive test of Railway deployment"""

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

async def test_railway_comprehensive():
    uri = "wss://deckster-diagram-service-production.up.railway.app/ws"
    output_dir = Path("railway_final_test")
    output_dir.mkdir(exist_ok=True)
    
    test_configs = [
        # Matrix tests
        {
            "name": "matrix_2x2_green",
            "diagram_type": "matrix_2x2",
            "labels": ["High Impact", "Quick Wins", "Low Priority", "Time Sinks"],
            "content": "Priority Matrix Analysis",
            "primary_color": "#10b981",
            "color_scheme": "monochromatic"
        },
        {
            "name": "matrix_2x2_blue",
            "diagram_type": "matrix_2x2",
            "labels": ["Urgent Important", "Not Urgent Important", "Urgent Not Important", "Not Urgent Not Important"],
            "content": "Eisenhower Matrix",
            "primary_color": "#3b82f6",
            "color_scheme": "complementary"
        },
        # Hub & Spoke tests
        {
            "name": "hub_spoke_orange",
            "diagram_type": "hub_spoke_4",
            "labels": ["Core System", "Frontend", "Backend", "Database", "Cache"],
            "content": "System Architecture",
            "primary_color": "#f59e0b",
            "color_scheme": "complementary"
        },
        {
            "name": "hub_spoke_purple",
            "diagram_type": "hub_spoke_4",
            "labels": ["Central", "North", "East", "South", "West"],
            "content": "Network Topology",
            "primary_color": "#8b5cf6",
            "color_scheme": "monochromatic"
        },
        # Pyramid tests
        {
            "name": "pyramid_blue",
            "diagram_type": "pyramid_5_level",
            "labels": ["Foundation", "Infrastructure", "Services", "Applications", "User Interface"],
            "content": "Technology Stack",
            "primary_color": "#3b82f6",
            "color_scheme": "monochromatic"
        },
        {
            "name": "pyramid_green",
            "diagram_type": "pyramid_5_level",
            "labels": ["Base", "Layer 2", "Layer 3", "Layer 4", "Peak"],
            "content": "Hierarchy Structure",
            "primary_color": "#10b981",
            "color_scheme": "complementary"
        },
        # Venn diagram tests
        {
            "name": "venn_cyan",
            "diagram_type": "venn_2_circle",
            "labels": ["Set A", "Set B", "Intersection"],
            "content": "Data Overlap",
            "primary_color": "#06b6d4",
            "color_scheme": "complementary"
        },
        {
            "name": "venn_red",
            "diagram_type": "venn_2_circle",
            "labels": ["Group 1", "Group 2", "Common"],
            "content": "Shared Elements",
            "primary_color": "#ef4444",
            "color_scheme": "monochromatic"
        }
    ]
    
    print("=" * 60)
    print("RAILWAY API COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Testing {len(test_configs)} diagram configurations...")
    
    results = []
    
    try:
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            # Wait for connection acknowledgment
            ack = await websocket.recv()
            ack_data = json.loads(ack)
            print(f"✅ Connected to Railway: {ack_data.get('type', 'unknown')}\n")
            
            for i, config in enumerate(test_configs, 1):
                print(f"[{i}/{len(test_configs)}] Testing: {config['name']}")
                print(f"     Type: {config['diagram_type']}")
                print(f"     Color: {config['primary_color']} ({config['color_scheme']})")
                
                # Create message
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
                    
                    # Wait for response
                    complete = False
                    svg_content = None
                    
                    while not complete:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        data = json.loads(response)
                        
                        if data.get("type") == "diagram_response":
                            complete = True
                            payload = data.get("payload", {})
                            svg_content = payload.get("content")
                            
                            if svg_content:
                                # Save SVG
                                output_file = output_dir / f"{config['name']}.svg"
                                with open(output_file, 'w') as f:
                                    f.write(svg_content)
                                
                                # Analyze colors and text contrast
                                import re
                                
                                # Extract fill colors
                                fill_colors = re.findall(r'fill="(#[0-9a-fA-F]{6})"', svg_content)
                                unique_colors = list(set(fill_colors))
                                
                                # Check for text elements with white/black fill
                                white_text = svg_content.count('fill="#ffffff"')
                                black_text = svg_content.count('fill="#000000"')
                                
                                results.append({
                                    "name": config['name'],
                                    "success": True,
                                    "unique_colors": len(unique_colors),
                                    "white_text": white_text,
                                    "black_text": black_text
                                })
                                
                                print(f"     ✅ Success!")
                                print(f"     🎨 Colors: {len(unique_colors)} unique")
                                print(f"     📝 Text: {white_text} white, {black_text} black")
                            else:
                                results.append({"name": config['name'], "success": False, "error": "No SVG content"})
                                print(f"     ❌ No SVG content")
                                
                        elif data.get("type") == "error_response":
                            complete = True
                            error_msg = data.get("payload", {}).get("error_message", "Unknown error")
                            results.append({"name": config['name'], "success": False, "error": error_msg})
                            print(f"     ❌ Error: {error_msg}")
                            
                except asyncio.TimeoutError:
                    results.append({"name": config['name'], "success": False, "error": "Timeout"})
                    print(f"     ❌ Timeout")
                except Exception as e:
                    results.append({"name": config['name'], "success": False, "error": str(e)})
                    print(f"     ❌ Exception: {e}")
                
                print()  # Blank line between tests
                    
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return results
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful
    
    print(f"✅ Successful: {successful}/{len(test_configs)}")
    print(f"❌ Failed: {failed}/{len(test_configs)}")
    
    if successful > 0:
        print(f"\n📁 SVGs saved to: {output_dir.absolute()}")
        
        # Detailed results
        print("\nContrast Analysis:")
        for result in results:
            if result.get("success"):
                print(f"  {result['name']}: {result['white_text']} white text, {result['black_text']} black text")
    
    print("\n✨ Test complete!")
    return results

if __name__ == "__main__":
    asyncio.run(test_railway_comprehensive())