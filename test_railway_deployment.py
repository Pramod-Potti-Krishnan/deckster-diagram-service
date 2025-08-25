#!/usr/bin/env python3
"""
Test Railway deployment for SVG diagram generation
"""

import asyncio
import json
import websockets
import uuid
from datetime import datetime
import os
import ssl
import certifi

# Railway deployment URL
RAILWAY_BASE_URL = "wss://deckster-diagram-service-production.up.railway.app"

# Create SSL context with proper certificate verification
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

async def test_svg_generation():
    """Test SVG diagram generation on Railway deployment"""
    
    results = []
    test_cases = [
        {
            "name": "Pyramid 3-Level",
            "request": {
                "type": "diagram_request",
                "correlation_id": str(uuid.uuid4()),
                "data": {
                    "diagram_type": "pyramid_3_level",
                    "data_points": [
                        {"label": "Strategic Level", "value": 100},
                        {"label": "Tactical Level", "value": 200},
                        {"label": "Operational Level", "value": 300}
                    ],
                    "theme": {
                        "primaryColor": "#3B82F6",
                        "colorScheme": "monochromatic"
                    }
                }
            }
        },
        {
            "name": "Matrix 2x2 with Complementary Colors",
            "request": {
                "type": "diagram_request",
                "correlation_id": str(uuid.uuid4()),
                "data": {
                    "diagram_type": "matrix_2x2",
                    "data_points": [
                        {"label": "High Impact, High Effort", "value": 85},
                        {"label": "High Impact, Low Effort", "value": 95},
                        {"label": "Low Impact, High Effort", "value": 35},
                        {"label": "Low Impact, Low Effort", "value": 45}
                    ],
                    "theme": {
                        "primaryColor": "#10B981",
                        "secondaryColor": "#F59E0B",
                        "accentColor": "#8B5CF6",
                        "colorScheme": "complementary"
                    }
                }
            }
        },
        {
            "name": "Venn 2-Circle Diagram",
            "request": {
                "type": "diagram_request",
                "correlation_id": str(uuid.uuid4()),
                "data": {
                    "diagram_type": "venn_2_circle",
                    "data_points": [
                        {"label": "Set A Only", "value": 30},
                        {"label": "Intersection", "value": 20},
                        {"label": "Set B Only", "value": 40}
                    ],
                    "theme": {
                        "primaryColor": "#EF4444",
                        "secondaryColor": "#3B82F6",
                        "colorScheme": "complementary"
                    }
                }
            }
        },
        {
            "name": "Hub Spoke 4",
            "request": {
                "type": "diagram_request",
                "correlation_id": str(uuid.uuid4()),
                "data": {
                    "diagram_type": "hub_spoke_4",
                    "data_points": [
                        {"label": "Central Hub", "value": 100},
                        {"label": "North Node", "value": 80},
                        {"label": "East Node", "value": 75},
                        {"label": "South Node", "value": 85},
                        {"label": "West Node", "value": 70}
                    ],
                    "theme": {
                        "primaryColor": "#6366F1",
                        "colorScheme": "monochromatic"
                    }
                }
            }
        },
        {
            "name": "Funnel 3-Stage",
            "request": {
                "type": "diagram_request",
                "correlation_id": str(uuid.uuid4()),
                "data": {
                    "diagram_type": "funnel_3_stage",
                    "data_points": [
                        {"label": "Awareness", "value": 1000},
                        {"label": "Consideration", "value": 500},
                        {"label": "Conversion", "value": 150}
                    ],
                    "theme": {
                        "primaryColor": "#EC4899",
                        "secondaryColor": "#F97316",
                        "accentColor": "#14B8A6",
                        "colorScheme": "complementary"
                    }
                }
            }
        }
    ]
    
    print(f"\n{'='*60}")
    print(f"Testing Railway Deployment: {RAILWAY_BASE_URL}")
    print(f"{'='*60}\n")
    
    # First test without query parameters (should work with our fix)
    print("\nTesting WITHOUT query parameters (should auto-generate)...")
    ws_url = f"{RAILWAY_BASE_URL}/ws"
    
    for i, test_case in enumerate(test_cases[:2]):
        print(f"\nTesting: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Connect to WebSocket with SSL context
            async with websockets.connect(ws_url, ssl=ssl_context) as websocket:
                print("✓ Connected to WebSocket")
                
                # Wait for connection acknowledgment
                ack = await websocket.recv()
                ack_data = json.loads(ack)
                if ack_data.get("type") == "connection_ack":
                    print(f"✓ Connection acknowledged: v{ack_data['payload'].get('version', 'unknown')}")
                
                # Send diagram request
                await websocket.send(json.dumps(test_case["request"]))
                print("✓ Request sent")
                
                # Collect responses
                diagram_received = False
                start_time = datetime.now()
                
                while not diagram_received:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        response_data = json.loads(response)
                        
                        if response_data["type"] == "status_update":
                            status = response_data["payload"]["status"]
                            message = response_data["payload"]["message"]
                            progress = response_data["payload"].get("progress", "")
                            if progress:
                                print(f"  Status: {status} - {message} ({progress}%)")
                            else:
                                print(f"  Status: {status} - {message}")
                        
                        elif response_data["type"] == "diagram_response":
                            end_time = datetime.now()
                            duration = (end_time - start_time).total_seconds()
                            
                            payload = response_data["payload"]
                            content_length = len(payload.get("content", ""))
                            
                            print(f"✓ Diagram received!")
                            print(f"  - Content length: {content_length:,} bytes")
                            print(f"  - Generation time: {duration:.2f}s")
                            print(f"  - Delivery method: {payload.get('content_delivery', 'unknown')}")
                            
                            # Check if labels were replaced
                            content = payload.get("content", "")
                            request_data = test_case["request"]["data"]
                            labels_found = []
                            labels_missing = []
                            
                            for dp in request_data["data_points"]:
                                if dp["label"] in content:
                                    labels_found.append(dp["label"])
                                else:
                                    labels_missing.append(dp["label"])
                            
                            if labels_found:
                                print(f"  - Labels found: {len(labels_found)}/{len(request_data['data_points'])}")
                            if labels_missing:
                                print(f"  ⚠ Missing labels: {labels_missing}")
                            
                            # Save to file
                            os.makedirs("railway_test_output", exist_ok=True)
                            filename = f"railway_test_output/{test_case['name'].lower().replace(' ', '_')}.svg"
                            with open(filename, 'w') as f:
                                f.write(content)
                            print(f"  - Saved to: {filename}")
                            
                            results.append({
                                "test": test_case["name"],
                                "status": "SUCCESS",
                                "duration": duration,
                                "size": content_length,
                                "labels_replaced": len(labels_found) == len(request_data["data_points"])
                            })
                            
                            diagram_received = True
                        
                        elif response_data["type"] == "error_response":
                            error = response_data["payload"]
                            print(f"✗ Error: {error.get('error_message', 'Unknown error')}")
                            results.append({
                                "test": test_case["name"],
                                "status": "ERROR",
                                "error": error.get('error_message')
                            })
                            diagram_received = True
                    
                    except asyncio.TimeoutError:
                        print("✗ Timeout waiting for response")
                        results.append({
                            "test": test_case["name"],
                            "status": "TIMEOUT"
                        })
                        break
        
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            results.append({
                "test": test_case["name"],
                "status": "CONNECTION_FAILED",
                "error": str(e)
            })
    
    # Now test WITH query parameters (backward compatibility)
    print("\n\nTesting WITH query parameters (backward compatibility)...")
    ws_url_with_params = f"{RAILWAY_BASE_URL}/ws?session_id=test-session&user_id=test-user"
    
    for test_case in test_cases[2:4]:  # Test a couple more with parameters
        print(f"\nTesting: {test_case['name']} (with params)")
        print("-" * 40)
        
        try:
            # Connect to WebSocket with SSL context and parameters
            async with websockets.connect(ws_url_with_params, ssl=ssl_context) as websocket:
                print("✓ Connected to WebSocket with query parameters")
                
                # Wait for connection acknowledgment
                ack = await websocket.recv()
                ack_data = json.loads(ack)
                if ack_data.get("type") == "connection_ack":
                    print(f"✓ Connection acknowledged: v{ack_data['payload'].get('version', 'unknown')}")
                
                # Send diagram request
                await websocket.send(json.dumps(test_case["request"]))
                print("✓ Request sent")
                
                # Collect responses
                diagram_received = False
                start_time = datetime.now()
                
                while not diagram_received:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        response_data = json.loads(response)
                        
                        if response_data["type"] == "status_update":
                            status = response_data["payload"]["status"]
                            message = response_data["payload"]["message"]
                            progress = response_data["payload"].get("progress", "")
                            if progress:
                                print(f"  Status: {status} - {message} ({progress}%)")
                            else:
                                print(f"  Status: {status} - {message}")
                        
                        elif response_data["type"] == "diagram_response":
                            end_time = datetime.now()
                            duration = (end_time - start_time).total_seconds()
                            
                            payload = response_data["payload"]
                            content_length = len(payload.get("content", ""))
                            
                            print(f"✓ Diagram received!")
                            print(f"  - Content length: {content_length:,} bytes")
                            print(f"  - Generation time: {duration:.2f}s")
                            print(f"  - Delivery method: {payload.get('content_delivery', 'unknown')}")
                            
                            # Check if labels were replaced
                            content = payload.get("content", "")
                            request_data = test_case["request"]["data"]
                            labels_found = []
                            labels_missing = []
                            
                            for dp in request_data["data_points"]:
                                if dp["label"] in content:
                                    labels_found.append(dp["label"])
                                else:
                                    labels_missing.append(dp["label"])
                            
                            if labels_found:
                                print(f"  - Labels found: {len(labels_found)}/{len(request_data['data_points'])}")
                            if labels_missing:
                                print(f"  ⚠ Missing labels: {labels_missing}")
                            
                            # Save to file
                            os.makedirs("railway_test_output", exist_ok=True)
                            filename = f"railway_test_output/{test_case['name'].lower().replace(' ', '_')}_with_params.svg"
                            with open(filename, 'w') as f:
                                f.write(content)
                            print(f"  - Saved to: {filename}")
                            
                            results.append({
                                "test": f"{test_case['name']} (with params)",
                                "status": "SUCCESS",
                                "duration": duration,
                                "size": content_length,
                                "labels_replaced": len(labels_found) == len(request_data["data_points"])
                            })
                            
                            diagram_received = True
                        
                        elif response_data["type"] == "error_response":
                            error = response_data["payload"]
                            print(f"✗ Error: {error.get('error_message', 'Unknown error')}")
                            results.append({
                                "test": f"{test_case['name']} (with params)",
                                "status": "ERROR",
                                "error": error.get('error_message')
                            })
                            diagram_received = True
                    
                    except asyncio.TimeoutError:
                        print("✗ Timeout waiting for response")
                        results.append({
                            "test": f"{test_case['name']} (with params)",
                            "status": "TIMEOUT"
                        })
                        break
        
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            results.append({
                "test": f"{test_case['name']} (with params)",
                "status": "CONNECTION_FAILED",
                "error": str(e)
            })
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}\n")
    
    success_count = sum(1 for r in results if r.get("status") == "SUCCESS")
    total_count = len(results)
    
    print(f"Results: {success_count}/{total_count} tests passed\n")
    
    for result in results:
        status_symbol = "✓" if result["status"] == "SUCCESS" else "✗"
        print(f"{status_symbol} {result['test']}: {result['status']}")
        if result.get("duration"):
            print(f"  Duration: {result['duration']:.2f}s")
        if result.get("error"):
            print(f"  Error: {result['error']}")
        if "labels_replaced" in result:
            label_status = "✓" if result["labels_replaced"] else "⚠"
            print(f"  {label_status} Label replacement: {'Complete' if result['labels_replaced'] else 'Incomplete'}")
    
    # Create HTML viewer
    if success_count > 0:
        create_html_viewer(results)
        print(f"\n✓ HTML viewer created: railway_test_output/viewer.html")
    
    return results

def create_html_viewer(results):
    """Create an HTML file to view the generated SVGs"""
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Railway Deployment Test Results</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .test-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        .test-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .test-card h3 {
            margin: 0 0 15px 0;
            color: #333;
        }
        .svg-container {
            background: #f7f7f7;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }
        .status.success {
            background: #10b981;
            color: white;
        }
        .status.error {
            background: #ef4444;
            color: white;
        }
        .meta {
            margin-top: 10px;
            font-size: 14px;
            color: #666;
        }
        .timestamp {
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Railway Deployment Test Results</h1>
        <div class="test-grid">
"""
    
    for result in results:
        if result["status"] == "SUCCESS":
            filename = f"{result['test'].lower().replace(' ', '_')}.svg"
            html_content += f"""
            <div class="test-card">
                <h3>{result['test']} <span class="status success">SUCCESS</span></h3>
                <div class="svg-container">
                    <object data="{filename}" type="image/svg+xml" width="100%" height="300">
                        SVG Preview
                    </object>
                </div>
                <div class="meta">
                    Duration: {result.get('duration', 0):.2f}s | 
                    Size: {result.get('size', 0):,} bytes |
                    Labels: {'✓' if result.get('labels_replaced') else '⚠'}
                </div>
            </div>
            """
    
    html_content += f"""
        </div>
        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
    
    with open("railway_test_output/viewer.html", 'w') as f:
        f.write(html_content)

if __name__ == "__main__":
    asyncio.run(test_svg_generation())