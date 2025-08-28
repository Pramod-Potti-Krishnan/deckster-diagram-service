#!/usr/bin/env python3
"""
Test Railway Production Deployment
Tests all diagram types against the deployed service
"""

import asyncio
import json
import websockets
import uuid
from datetime import datetime
from typing import Dict, Any, List
import ssl
import certifi

# Production WebSocket URL
WS_URL = "wss://deckster-diagram-service-production.up.railway.app/ws"

# Test configurations
SVG_TEMPLATES = [
    ("pyramid_3_level", "Strategic goals at top. Tactical initiatives in middle. Operational tasks at bottom."),
    ("pyramid_4_level", "Vision. Strategy. Tactics. Operations."),
    ("pyramid_5_level", "CEO level. VP level. Director level. Manager level. Individual contributors."),
    ("cycle_3_step", "Plan phase. Execute phase. Review phase."),
    ("cycle_4_step", "Analyze. Design. Implement. Evaluate."),
    ("cycle_5_step", "Define. Measure. Analyze. Improve. Control."),
    ("venn_2_circle", "Product features. Customer needs."),
    ("venn_3_circle", "Technology. Business. Design."),
    ("honeycomb_3", "Core service. Support system. Infrastructure."),
    ("honeycomb_5", "Sales. Marketing. Product. Engineering. Operations."),
    ("honeycomb_7", "CEO. CTO. CFO. CMO. COO. CPO. CHRO."),
    ("matrix_2x2", "High impact high effort. High impact low effort. Low impact high effort. Low impact low effort."),
    ("matrix_3x3", "Top priority. High priority. Medium priority. Low priority. Minimal priority. No priority. Future consideration. Maybe later. Not now."),
    ("swot_matrix", "Strengths: Strong brand, Good team. Weaknesses: Limited resources. Opportunities: New markets. Threats: Competition."),
    ("hub_spoke_4", "Central platform. Mobile app. Web app. API. Database."),
    ("hub_spoke_6", "Core system. Frontend. Backend. Database. Cache. Queue."),
    ("funnel_3_stage", "Awareness: 1000 visitors. Consideration: 200 leads. Conversion: 50 customers."),
    ("funnel_4_stage", "Visitors: 10000. Leads: 1000. Qualified: 200. Customers: 50."),
    ("funnel_5_stage", "Awareness. Interest. Consideration. Intent. Purchase."),
    ("process_flow_3", "Input data. Process information. Output results."),
    ("process_flow_5", "Receive request. Validate data. Process logic. Store results. Send response."),
    ("fishbone_4_bone", "Problem: Low sales. People factors. Process issues. Technology gaps. Market conditions."),
    ("gears_3", "Engineering team. Product team. Design team."),
    ("roadmap_quarterly_4", "Q1: Foundation. Q2: Features. Q3: Scale. Q4: Optimize."),
    ("timeline_horizontal", "2024 Q1: Planning. 2024 Q2: Development. 2024 Q3: Testing. 2024 Q4: Launch."),
]

MERMAID_DIAGRAMS = [
    ("flowchart", "User login flow: User enters credentials, system validates, if valid redirect to dashboard, if invalid show error"),
    ("erDiagram", "Database schema: User has id, name, email. Order has id, user_id, total. User has many orders."),
    ("journey", "Customer journey: Browse products, add to cart, checkout, receive order, leave review"),
    ("gantt", "Project timeline: Planning from Jan to Feb, Development from Feb to April, Testing from April to May"),
    ("quadrantChart", "Priority matrix with urgency and importance axes. Task A is urgent and important. Task B is not urgent but important."),
    ("timeline", "Company milestones: 2020 Founded, 2021 Seed funding, 2022 Product launch, 2023 Series A, 2024 Expansion"),
    ("kanban", "Sprint board: Todo has 5 tasks, In Progress has 3 tasks, Testing has 2 tasks, Done has 8 tasks")
]


async def test_single_diagram(websocket, session_id: str, diagram_type: str, content: str, test_type: str) -> Dict[str, Any]:
    """Test a single diagram generation"""
    
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
            "output_format": "svg" if test_type == "svg" else "mermaid",
            "theme": {
                "primaryColor": "#3B82F6",
                "backgroundColor": "#FFFFFF"
            }
        }
    }
    
    # Send request
    await websocket.send(json.dumps(request))
    
    # Wait for response
    start_time = datetime.now()
    timeout = 30.0  # 30 second timeout for production
    
    while True:
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            response_json = json.loads(response)
            
            msg_type = response_json.get("type")
            
            if msg_type in ["response", "diagram_response"]:
                elapsed = (datetime.now() - start_time).total_seconds()
                payload = response_json.get("payload", {})
                
                # Check for success
                if "content" in payload or "mermaid_code" in payload.get("metadata", {}):
                    return {
                        "success": True,
                        "time": elapsed,
                        "has_content": bool(payload.get("content")),
                        "has_mermaid": bool(payload.get("metadata", {}).get("mermaid_code"))
                    }
                else:
                    return {
                        "success": False,
                        "time": elapsed,
                        "error": "No content in response"
                    }
                    
            elif msg_type == "error":
                elapsed = (datetime.now() - start_time).total_seconds()
                return {
                    "success": False,
                    "time": elapsed,
                    "error": response_json.get("payload", {}).get("message", "Unknown error")
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "time": timeout,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "time": (datetime.now() - start_time).total_seconds(),
                "error": str(e)
            }


async def main():
    """Run comprehensive test suite against production"""
    
    print("=" * 80)
    print("RAILWAY PRODUCTION TEST")
    print(f"Testing: {WS_URL}")
    print("=" * 80)
    
    session_id = str(uuid.uuid4())
    results = {
        "svg_templates": [],
        "mermaid_diagrams": [],
        "summary": {}
    }
    
    # Create SSL context
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    try:
        # Connect to production WebSocket with SSL context
        print("\n🔌 Connecting to production WebSocket...")
        async with websockets.connect(
            f"{WS_URL}?session_id={session_id}&user_id=production_test",
            ssl=ssl_context
        ) as websocket:
            print("✅ Connected successfully!")
            
            # Test SVG Templates
            print("\n📊 Testing SVG Templates")
            print("-" * 40)
            
            svg_passed = 0
            for i, (diagram_type, content) in enumerate(SVG_TEMPLATES, 1):
                print(f"  [{i:2}/{len(SVG_TEMPLATES)}] {diagram_type:20}", end=" ")
                
                result = await test_single_diagram(websocket, session_id, diagram_type, content, "svg")
                
                if result["success"]:
                    print(f"✅ ({result['time']:.2f}s)")
                    svg_passed += 1
                else:
                    print(f"❌ {result.get('error', 'Failed')}")
                
                results["svg_templates"].append({
                    "type": diagram_type,
                    **result
                })
                
                # Small delay between requests
                await asyncio.sleep(0.1)
            
            # Test Mermaid Diagrams
            print("\n📈 Testing Mermaid Diagrams")
            print("-" * 40)
            
            mermaid_passed = 0
            for i, (diagram_type, content) in enumerate(MERMAID_DIAGRAMS, 1):
                print(f"  [{i}/{len(MERMAID_DIAGRAMS)}] {diagram_type:15}", end=" ")
                
                result = await test_single_diagram(websocket, session_id, diagram_type, content, "mermaid")
                
                if result["success"]:
                    print(f"✅ ({result['time']:.2f}s)")
                    mermaid_passed += 1
                else:
                    print(f"❌ {result.get('error', 'Failed')}")
                
                results["mermaid_diagrams"].append({
                    "type": diagram_type,
                    **result
                })
                
                # Small delay between requests
                await asyncio.sleep(0.1)
            
            # Calculate summary
            total_tests = len(SVG_TEMPLATES) + len(MERMAID_DIAGRAMS)
            total_passed = svg_passed + mermaid_passed
            
            results["summary"] = {
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_tests - total_passed,
                "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
                "svg_passed": svg_passed,
                "svg_total": len(SVG_TEMPLATES),
                "mermaid_passed": mermaid_passed,
                "mermaid_total": len(MERMAID_DIAGRAMS),
                "timestamp": datetime.now().isoformat()
            }
            
            # Print summary
            print("\n" + "=" * 80)
            print("TEST SUMMARY")
            print("=" * 80)
            print(f"\n📊 SVG Templates: {svg_passed}/{len(SVG_TEMPLATES)} passed")
            print(f"📈 Mermaid Diagrams: {mermaid_passed}/{len(MERMAID_DIAGRAMS)} passed")
            print(f"\n🎯 Overall: {total_passed}/{total_tests} passed ({results['summary']['success_rate']:.1f}%)")
            
            # Calculate average times
            svg_times = [r["time"] for r in results["svg_templates"] if r["success"]]
            mermaid_times = [r["time"] for r in results["mermaid_diagrams"] if r["success"]]
            
            if svg_times:
                print(f"\n⏱️  Average SVG generation time: {sum(svg_times)/len(svg_times):.2f}s")
            if mermaid_times:
                print(f"⏱️  Average Mermaid generation time: {sum(mermaid_times)/len(mermaid_times):.2f}s")
            
            # Show failures if any
            failures = []
            for r in results["svg_templates"]:
                if not r["success"]:
                    failures.append(f"  - {r['type']} (SVG): {r.get('error', 'Unknown')}")
            for r in results["mermaid_diagrams"]:
                if not r["success"]:
                    failures.append(f"  - {r['type']} (Mermaid): {r.get('error', 'Unknown')}")
            
            if failures:
                print(f"\n❌ Failed tests ({len(failures)}):")
                for f in failures:
                    print(f)
            else:
                print("\n✅ All tests passed successfully!")
            
            # Save results
            with open("railway_production_results.json", "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n📁 Detailed results saved to railway_production_results.json")
            
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nPossible issues:")
        print("  - Service might not be deployed yet")
        print("  - WebSocket endpoint might be different")
        print("  - SSL/TLS certificate issues")
        return
    
    print("\n✅ Production test completed!")


if __name__ == "__main__":
    asyncio.run(main())