#!/usr/bin/env python3
"""Test Railway deployment with improved color distribution"""

import asyncio
import json
import websockets
import ssl
from pathlib import Path

# Create SSL context that doesn't verify certificates (for testing)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def test_railway_deployment():
    # Railway deployment URL
    uri = "wss://deckster-diagram-service-production.up.railway.app/ws"
    output_dir = Path("railway_color_test")
    output_dir.mkdir(exist_ok=True)
    
    # Test configurations covering different scenarios
    test_configs = [
        {
            "name": "pyramid_5_level_mono",
            "request": {
                "diagramType": "pyramid_5_level",
                "labels": ["Foundation", "Layer 2", "Layer 3", "Layer 4", "Peak"],
                "content": "5-level pyramid with monochromatic theme",
                "theme": {
                    "primaryColor": "#3b82f6",
                    "colorScheme": "monochromatic"
                }
            }
        },
        {
            "name": "pyramid_5_level_comp",
            "request": {
                "diagramType": "pyramid_5_level",
                "labels": ["Base", "Level 2", "Level 3", "Level 4", "Top"],
                "content": "5-level pyramid with complementary colors",
                "theme": {
                    "primaryColor": "#8b5cf6",
                    "colorScheme": "complementary"
                }
            }
        },
        {
            "name": "matrix_2x2_mono",
            "request": {
                "diagramType": "matrix_2x2",
                "labels": ["High Impact", "Quick Wins", "Fill Ins", "Time Sinks"],
                "content": "Priority matrix with monochromatic theme",
                "theme": {
                    "primaryColor": "#10b981",
                    "colorScheme": "monochromatic"
                }
            }
        },
        {
            "name": "matrix_2x2_comp",
            "request": {
                "diagramType": "matrix_2x2",
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "content": "2x2 Matrix with complementary colors",
                "theme": {
                    "primaryColor": "#ef4444",
                    "colorScheme": "complementary"
                }
            }
        },
        {
            "name": "hub_spoke_4_mono",
            "request": {
                "diagramType": "hub_spoke_4",
                "labels": ["Central Hub", "North", "East", "South", "West"],
                "content": "Hub and spoke with monochromatic theme",
                "theme": {
                    "primaryColor": "#f59e0b",
                    "colorScheme": "monochromatic"
                }
            }
        },
        {
            "name": "venn_2_circle_comp",
            "request": {
                "diagramType": "venn_2_circle",
                "labels": ["Set A", "Set B", "Intersection"],
                "content": "Venn diagram with complementary colors",
                "theme": {
                    "primaryColor": "#06b6d4",
                    "colorScheme": "complementary"
                }
            }
        },
        {
            "name": "honeycomb_7_mono",
            "request": {
                "diagramType": "honeycomb_7",
                "labels": ["Center", "Cell 1", "Cell 2", "Cell 3", "Cell 4", "Cell 5", "Cell 6"],
                "content": "7-cell honeycomb with monochromatic theme",
                "theme": {
                    "primaryColor": "#ec4899",
                    "colorScheme": "monochromatic"
                }
            }
        },
        {
            "name": "funnel_5_stage_comp",
            "request": {
                "diagramType": "funnel_5_stage",
                "labels": ["Awareness", "Interest", "Consideration", "Intent", "Purchase"],
                "content": "Sales funnel with complementary colors",
                "theme": {
                    "primaryColor": "#14b8a6",
                    "colorScheme": "complementary"
                }
            }
        }
    ]
    
    results = []
    successful = 0
    failed = 0
    
    print("=" * 60)
    print("Testing Railway Deployment - Color Distribution")
    print("=" * 60)
    print(f"URL: {uri}")
    print(f"Tests to run: {len(test_configs)}")
    print("-" * 60)
    
    try:
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            for config in test_configs:
                print(f"\n📊 Testing: {config['name']}")
                print(f"   Type: {config['request']['diagramType']}")
                print(f"   Color: {config['request']['theme']['primaryColor']}")
                print(f"   Scheme: {config['request']['theme']['colorScheme']}")
                
                try:
                    # Send request
                    await websocket.send(json.dumps(config['request']))
                    
                    # Receive response with timeout
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    # Debug: print raw response
                    if data.get("status") != "success":
                        print(f"   📝 Raw response: {json.dumps(data, indent=2)}")
                    
                    if data.get("status") == "success":
                        svg_content = data.get("svg")
                        if svg_content:
                            # Save SVG
                            output_file = output_dir / f"{config['name']}.svg"
                            with open(output_file, 'w') as f:
                                f.write(svg_content)
                            
                            # Analyze colors
                            import re
                            fill_colors = re.findall(r'fill="(#[0-9a-fA-F]{6})"', svg_content)
                            stroke_colors = re.findall(r'stroke="(#[0-9a-fA-F]{6})"', svg_content)
                            all_colors = fill_colors + stroke_colors
                            unique_colors = list(set(all_colors))
                            
                            # Check for near-white colors
                            problematic_colors = []
                            for color in unique_colors:
                                # Check if color is too light (near white)
                                r = int(color[1:3], 16)
                                g = int(color[3:5], 16)
                                b = int(color[5:7], 16)
                                brightness = (r + g + b) / 3
                                if brightness > 250:  # Near white
                                    problematic_colors.append(color)
                            
                            result = {
                                "name": config['name'],
                                "status": "success",
                                "total_colors": len(all_colors),
                                "unique_colors": len(unique_colors),
                                "colors": unique_colors[:8],  # First 8 unique colors
                                "problematic": problematic_colors
                            }
                            results.append(result)
                            successful += 1
                            
                            print(f"   ✅ Success!")
                            print(f"   📈 Colors: {len(unique_colors)} unique out of {len(all_colors)} total")
                            print(f"   🎨 Palette: {', '.join(unique_colors[:5])}")
                            if problematic_colors:
                                print(f"   ⚠️  Near-white colors found: {problematic_colors}")
                        else:
                            results.append({"name": config['name'], "status": "error", "message": "No SVG content"})
                            failed += 1
                            print(f"   ❌ Error: No SVG content received")
                    else:
                        error_msg = data.get("message", "Unknown error")
                        results.append({"name": config['name'], "status": "error", "message": error_msg})
                        failed += 1
                        print(f"   ❌ Error: {error_msg}")
                        
                except asyncio.TimeoutError:
                    results.append({"name": config['name'], "status": "error", "message": "Timeout"})
                    failed += 1
                    print(f"   ❌ Error: Request timeout")
                except Exception as e:
                    results.append({"name": config['name'], "status": "error", "message": str(e)})
                    failed += 1
                    print(f"   ❌ Exception: {e}")
                    
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {successful}/{len(test_configs)}")
    print(f"❌ Failed: {failed}/{len(test_configs)}")
    
    if successful > 0:
        print("\n📊 Color Distribution Analysis:")
        for result in results:
            if result["status"] == "success":
                print(f"\n{result['name']}:")
                print(f"  • Unique colors: {result['unique_colors']}")
                print(f"  • Color variety: {'Good' if result['unique_colors'] >= 3 else 'Poor'}")
                if result['problematic']:
                    print(f"  • ⚠️  Issues: Near-white colors detected")
                else:
                    print(f"  • ✅ No color issues detected")
    
    print(f"\n📁 SVG files saved to: {output_dir.absolute()}")
    print("\n✨ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_railway_deployment())