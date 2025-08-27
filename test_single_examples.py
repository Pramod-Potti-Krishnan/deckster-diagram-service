#!/usr/bin/env python3
"""
Single Example Test Script - Tests one of each diagram type
"""

import asyncio
import json
import websockets
import uuid
from datetime import datetime
import os

# Configuration
WS_URL = "ws://127.0.0.1:8001/ws"
OUTPUT_DIR = "test_results"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/svg_templates", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/mermaid_code", exist_ok=True)


async def test_websocket_connection():
    """Test WebSocket connection with single examples"""
    
    # Test cases for validation
    test_cases = [
        # SVG Template Test
        {
            "name": "pyramid_3_level",
            "type": "svg_template",
            "request": {
                "content": "Strategic Planning Pyramid - Level 1: Vision and Mission - Define long-term organizational goals. Level 2: Strategic Objectives - Key measurable targets for 3-5 years. Level 3: Operational Tactics - Day-to-day actions and initiatives.",
                "diagram_type": "pyramid_3_level",
                "theme": {
                    "primaryColor": "#3B82F6",
                    "secondaryColor": "#60A5FA",
                    "backgroundColor": "#FFFFFF",
                    "textColor": "#1F2937"
                }
            }
        },
        # Mermaid Flowchart Test
        {
            "name": "flowchart",
            "type": "mermaid",
            "request": {
                "content": "User Login Process Flow: User enters credentials -> System validates -> If valid, create session and redirect to dashboard. If invalid, show error and allow retry (max 3 attempts). After 3 failed attempts, lock account for 15 minutes.",
                "diagram_type": "flowchart",
                "output_format": "mermaid",
                "theme": {
                    "primaryColor": "#10B981",
                    "secondaryColor": "#34D399",
                    "backgroundColor": "#FFFFFF",
                    "textColor": "#1F2937"
                }
            }
        }
    ]
    
    results = []
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    async with websockets.connect(f"{WS_URL}?session_id={session_id}&user_id=test_user") as websocket:
        print(f"Connected to WebSocket server at {WS_URL}")
        print(f"Session ID: {session_id}")
        print("-" * 60)
        
        for test in test_cases:
            print(f"\n🧪 Testing: {test['name']} ({test['type']})")
            
            # Create request message
            request_id = f"req_{uuid.uuid4()}"
            message = {
                "message_id": f"msg_{uuid.uuid4()}",
                "correlation_id": request_id,
                "request_id": request_id,  # Include for backward compatibility
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "diagram_request",  # Use legacy type for now
                "payload": test["request"]
            }
            
            # Send request
            await websocket.send(json.dumps(message))
            print(f"📤 Sent request for {test['name']}")
            
            # Receive responses
            response_data = None
            status_updates = []
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    response_json = json.loads(response)
                    
                    msg_type = response_json.get("type")
                    
                    if msg_type == "status":
                        status = response_json.get("payload", {}).get("status")
                        message = response_json.get("payload", {}).get("message", "")
                        print(f"  ⚡ Status: {status} - {message}")
                        status_updates.append({"status": status, "message": message})
                        
                    elif msg_type == "response":
                        print(f"  ✅ Received response!")
                        response_data = response_json
                        break
                        
                    elif msg_type == "error":
                        print(f"  ❌ Error: {response_json.get('payload', {})}")
                        response_data = response_json
                        break
                        
                except asyncio.TimeoutError:
                    print(f"  ⏱️ Timeout waiting for response")
                    break
                except Exception as e:
                    print(f"  ❌ Error receiving message: {e}")
                    break
            
            # Process and save result
            if response_data:
                result = {
                    "test_name": test["name"],
                    "type": test["type"],
                    "request_id": request_id,
                    "status_updates": status_updates,
                    "response": response_data
                }
                results.append(result)
                
                # Save output based on type
                if response_data.get("type") == "response":
                    payload = response_data.get("payload", {})
                    content = payload.get("content", "")
                    diagram_type = payload.get("diagram_type", test["name"])
                    
                    if test["type"] == "svg_template":
                        # Save SVG
                        filename = f"{OUTPUT_DIR}/svg_templates/{test['name']}.svg"
                        with open(filename, "w") as f:
                            f.write(content)
                        print(f"  💾 Saved SVG to {filename}")
                        
                    elif test["type"] == "mermaid":
                        # Save Mermaid code
                        filename = f"{OUTPUT_DIR}/mermaid_code/{test['name']}.mmd"
                        with open(filename, "w") as f:
                            f.write(content)
                        print(f"  💾 Saved Mermaid code to {filename}")
    
    # Save results summary
    summary_file = f"{OUTPUT_DIR}/test_summary.json"
    with open(summary_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n📊 Test results saved to {summary_file}")
    
    return results


async def main():
    """Main test function"""
    print("=" * 60)
    print("DIAGRAM MICROSERVICE V2 - SINGLE EXAMPLE TEST")
    print("=" * 60)
    
    try:
        results = await test_websocket_connection()
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        successful = 0
        failed = 0
        
        for result in results:
            if result.get("response", {}).get("type") == "response":
                print(f"✅ {result['test_name']}: SUCCESS")
                successful += 1
            else:
                print(f"❌ {result['test_name']}: FAILED")
                failed += 1
        
        print("-" * 60)
        print(f"Total: {successful + failed} | Success: {successful} | Failed: {failed}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())