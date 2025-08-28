#!/usr/bin/env python3
"""
Test improved SVG text parsing with real feedback examples
"""

import asyncio
import json
import websockets
import uuid
from datetime import datetime
import ssl
import certifi
import time

# Test with local WebSocket
WS_URL = "ws://127.0.0.1:8001/ws"

# Use the exact examples from user feedback that were problematic
TEST_CASES = [
    # Pyramid tests - from user feedback
    ("pyramid_3_level", "Strategic goals at top. Tactical initiatives in middle. Operational tasks at bottom."),
    ("pyramid_4_level", "Vision. Strategy. Tactics. Operations."),
    ("pyramid_5_level", "CEO level. VP level. Director level. Manager level. Individual contributors."),
    
    # Cycle tests - from user feedback  
    ("cycle_3_step", "Plan phase. Execute phase. Review phase."),
    ("cycle_4_step", "Analyze. Design. Implement. Evaluate."),
    ("cycle_5_step", "Define. Measure. Analyze. Improve. Control."),
    
    # Venn tests - from user feedback
    ("venn_2_circle", "Product features. Customer needs."),
    ("venn_3_circle", "Technology. Business. Design."),
    
    # Additional problematic templates
    ("honeycomb_3", "Core service. Support system. Infrastructure."),
    ("honeycomb_5", "Sales. Marketing. Product. Engineering. Operations."),
    ("matrix_2x2", "High impact high effort. High impact low effort. Low impact high effort. Low impact low effort."),
    ("hub_spoke_4", "Central platform. Mobile app. Web app. API."),
    ("funnel_3_stage", "Awareness: 1000 visitors. Consideration: 200 leads. Conversion: 50 customers."),
    ("process_flow_3", "Input data. Process information. Output results."),
    ("timeline_horizontal", "2024 Q1: Planning. 2024 Q2: Development. 2024 Q3: Testing. 2024 Q4: Launch."),
]


async def test_diagram(websocket, session_id, diagram_type, content):
    """Test a single diagram and analyze text distribution"""
    
    request_id = f"req_{uuid.uuid4()}"
    
    request = {
        "message_id": f"msg_{uuid.uuid4()}",
        "correlation_id": request_id,
        "request_id": request_id,
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "type": "diagram_request",
        "payload": {
            "content": content,
            "diagram_type": diagram_type,
            "output_format": "svg",
            "theme": {
                "primaryColor": "#3B82F6",
                "backgroundColor": "#FFFFFF"
            }
        }
    }
    
    await websocket.send(json.dumps(request))
    
    timeout = 30.0
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            response_json = json.loads(response)
            
            if response_json.get("type") in ["response", "diagram_response"]:
                payload = response_json.get("payload", {})
                svg_content = payload.get("content", "")
                
                if svg_content:
                    # Analyze text distribution in SVG
                    text_elements = analyze_svg_text(svg_content)
                    
                    # Check if content was properly distributed
                    content_parts = content.split('. ')
                    expected_parts = len(content_parts)
                    
                    return {
                        "diagram_type": diagram_type,
                        "success": True,
                        "text_elements": text_elements,
                        "expected_parts": expected_parts,
                        "actual_parts": len(text_elements),
                        "properly_distributed": len(text_elements) >= min(3, expected_parts),
                        "svg_snippet": svg_content[:500]
                    }
                else:
                    return {
                        "diagram_type": diagram_type,
                        "success": False,
                        "error": "Empty SVG content"
                    }
                    
            elif response_json.get("type") == "error":
                return {
                    "diagram_type": diagram_type,
                    "success": False,
                    "error": response_json.get("payload", {}).get("message", "Unknown error")
                }
                
        except asyncio.TimeoutError:
            continue
            
    return {"diagram_type": diagram_type, "success": False, "error": "Timeout"}


def analyze_svg_text(svg_content):
    """Extract and analyze text elements from SVG"""
    import re
    
    # Find all text content between <text> tags
    text_pattern = r'<text[^>]*>([^<]+)</text>'
    texts = re.findall(text_pattern, svg_content)
    
    # Also find tspan elements
    tspan_pattern = r'<tspan[^>]*>([^<]+)</tspan>'
    tspans = re.findall(tspan_pattern, svg_content)
    
    # Combine and filter out empty or default placeholder texts
    all_texts = texts + tspans
    
    # Filter out common placeholders and empty strings
    filtered_texts = []
    placeholders = ["Title", "Subtitle", "Label", "Text", "Value", "Item", ""]
    
    for text in all_texts:
        text = text.strip()
        if text and not any(placeholder.lower() in text.lower() for placeholder in placeholders if placeholder):
            filtered_texts.append(text)
    
    return filtered_texts


async def main():
    print("=" * 80)
    print("TESTING IMPROVED SVG TEXT PARSING")
    print("=" * 80)
    
    session_id = str(uuid.uuid4())
    
    try:
        # Test local WebSocket
        async with websockets.connect(
            f"{WS_URL}?session_id={session_id}&user_id=parse_test"
        ) as websocket:
            
            results = []
            passed = 0
            failed = 0
            
            print(f"\nTesting {len(TEST_CASES)} diagrams with improved parsing...\n")
            
            for i, (diagram_type, content) in enumerate(TEST_CASES, 1):
                print(f"[{i}/{len(TEST_CASES)}] Testing {diagram_type:20} ", end="")
                
                result = await test_diagram(websocket, session_id, diagram_type, content)
                
                if result["success"]:
                    if result["properly_distributed"]:
                        print(f"✅ Text properly distributed: {result['actual_parts']} elements")
                        passed += 1
                        
                        # Show the extracted text for verification
                        print(f"    Extracted text: {result['text_elements'][:3]}...")
                    else:
                        print(f"⚠️ Text not distributed: {result['actual_parts']} elements (expected ≥ {min(3, result['expected_parts'])})")
                        print(f"    Found: {result['text_elements']}")
                        failed += 1
                else:
                    print(f"❌ Error: {result['error']}")
                    failed += 1
                
                results.append(result)
                await asyncio.sleep(0.5)
            
            print("\n" + "=" * 80)
            print("RESULTS SUMMARY")
            print("=" * 80)
            print(f"✅ Passed: {passed}/{len(TEST_CASES)}")
            print(f"❌ Failed: {failed}/{len(TEST_CASES)}")
            print(f"📊 Success rate: {(passed/len(TEST_CASES))*100:.1f}%")
            
            # Show detailed failures
            if failed > 0:
                print("\n❌ Failed tests:")
                for result in results:
                    if result["success"] and not result.get("properly_distributed"):
                        print(f"  - {result['diagram_type']}: Only {result['actual_parts']} text elements found")
                    elif not result["success"]:
                        print(f"  - {result['diagram_type']}: {result.get('error', 'Unknown error')}")
            
            # Save results for analysis
            with open("improved_parsing_results.json", "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n📁 Detailed results saved to: improved_parsing_results.json")
            
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        print("Make sure the WebSocket server is running on port 8001")


if __name__ == "__main__":
    asyncio.run(main())