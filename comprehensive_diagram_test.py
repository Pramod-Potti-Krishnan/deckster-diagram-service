#!/usr/bin/env python3
"""
Comprehensive test of all diagram types supported by the unified playbook
Tests ONLY the diagrams defined in SUPPORTED_DIAGRAM_TYPES
"""

import asyncio
import json
import websockets
import ssl
from datetime import datetime
from typing import Dict, List, Tuple

# From config/constants.py - these are the ONLY diagram types we support
SUPPORTED_DIAGRAM_TYPES = {
    "svg_template": [
        "cycle_3_step", "cycle_4_step", "cycle_5_step",
        "pyramid_3_level", "pyramid_4_level", "pyramid_5_level",
        "venn_2_circle", "venn_3_circle",
        "honeycomb_3", "honeycomb_5", "honeycomb_7",
        "matrix_2x2", "matrix_3x3", "swot", "quadrant",
        "funnel", "timeline", "hub_spoke", "process_flow"
    ],
    "mermaid": [
        "flowchart", "sequence", "gantt", "pie_chart",
        "journey_map", "mind_map", "architecture",
        "network", "concept_map"
    ],
    "python_chart": [
        "pie_chart", "bar_chart", "line_chart",
        "scatter_plot", "sankey", "network",
        "funnel", "quadrant"
    ]
}

# Sample content for each diagram type
DIAGRAM_CONTENT = {
    # SVG Templates
    "cycle_3_step": "Plan\\nExecute\\nReview",
    "cycle_4_step": "Plan\\nDo\\nCheck\\nAct",
    "cycle_5_step": "Define\\nMeasure\\nAnalyze\\nImprove\\nControl",
    "pyramid_3_level": "Foundation: Infrastructure\\nMiddle: Services\\nTop: Applications",
    "pyramid_4_level": "Base: Data Layer\\nCore: Business Logic\\nAPI: Service Layer\\nUI: Presentation",
    "pyramid_5_level": "Infrastructure\\nData\\nServices\\nBusiness\\nPresentation",
    "venn_2_circle": "Set A: Frontend\\nSet B: Backend\\nIntersection: Full Stack",
    "venn_3_circle": "Design: UI/UX\\nCode: Development\\nData: Analytics\\nOverlap: Product",
    "honeycomb_3": "Core\\nInner Ring\\nOuter Ring",
    "honeycomb_5": "Center\\nRing 1\\nRing 2\\nRing 3\\nRing 4",
    "honeycomb_7": "Core\\nLayer1\\nLayer2\\nLayer3\\nLayer4\\nLayer5\\nLayer6",
    "matrix_2x2": "High Impact/High Effort\\nHigh Impact/Low Effort\\nLow Impact/High Effort\\nLow Impact/Low Effort",
    "matrix_3x3": "1,1: Low/Low\\n1,2: Low/Med\\n1,3: Low/High\\n2,1: Med/Low\\n2,2: Med/Med\\n2,3: Med/High\\n3,1: High/Low\\n3,2: High/Med\\n3,3: High/High",
    "swot": "Strengths: Innovation\\nWeaknesses: Resources\\nOpportunities: Market Growth\\nThreats: Competition",
    "quadrant": "Q1: Urgent Important\\nQ2: Not Urgent Important\\nQ3: Urgent Not Important\\nQ4: Not Urgent Not Important",
    "funnel": "Awareness: 1000\\nInterest: 500\\nDesire: 200\\nAction: 50",
    "timeline": "2020: Project Start\\n2021: Development\\n2022: Launch\\n2023: Growth\\n2024: Expansion",
    "hub_spoke": "Hub: Central System\\nSpoke1: Service A\\nSpoke2: Service B\\nSpoke3: Service C\\nSpoke4: Service D",
    "process_flow": "Start->Input->Process->Decision->Output->End",
    
    # Mermaid Diagrams
    "flowchart": "Start->Process A->Decision->Process B->End",
    "sequence": "User->API: Request\\nAPI->Database: Query\\nDatabase->API: Response\\nAPI->User: Result",
    "gantt": "Task 1: 2024-01-01, 30d\\nTask 2: 2024-02-01, 20d\\nTask 3: 2024-03-01, 25d",
    "pie_chart": "React: 35\\nVue: 25\\nAngular: 20\\nSvelte: 20",
    "journey_map": "Awareness->Consideration->Purchase->Retention->Advocacy",
    "mind_map": "Central Idea\\n  Branch 1\\n    Sub 1.1\\n    Sub 1.2\\n  Branch 2\\n    Sub 2.1\\n    Sub 2.2",
    "architecture": "Client Layer->API Gateway->Service Layer->Data Layer",
    "network": "Node A->Node B\\nNode B->Node C\\nNode C->Node D\\nNode D->Node A",
    "concept_map": "Main Concept->Related 1\\nMain Concept->Related 2\\nRelated 1->Detail A\\nRelated 2->Detail B",
    
    # Python Charts (overlaps with some other categories)
    "bar_chart": "Q1: 100\\nQ2: 150\\nQ3: 130\\nQ4: 180",
    "line_chart": "Jan: 10\\nFeb: 20\\nMar: 15\\nApr: 30\\nMay: 25\\nJun: 35",
    "scatter_plot": "Point1: (10, 20)\\nPoint2: (15, 30)\\nPoint3: (20, 25)\\nPoint4: (25, 35)\\nPoint5: (30, 40)",
    "sankey": "Source A->Process 1: 100\\nSource B->Process 1: 50\\nProcess 1->Output X: 80\\nProcess 1->Output Y: 70",
}

class TestResult:
    """Store test result for a diagram"""
    def __init__(self, diagram_type: str, expected_method: str):
        self.diagram_type = diagram_type
        self.expected_method = expected_method
        self.success = False
        self.actual_method = None
        self.generation_time_ms = None
        self.error_message = None
        self.has_url = False
        self.has_content = False
        self.start_time = None
        self.end_time = None

async def test_single_diagram(websocket, diagram_type: str, content: str, correlation_id: str) -> Dict:
    """Test a single diagram and return results"""
    
    # Send request
    request = {
        "type": "diagram_request",
        "correlation_id": correlation_id,
        "data": {
            "diagram_type": diagram_type,
            "content": content,
            "theme": {"primaryColor": "#3B82F6"}
        }
    }
    
    await websocket.send(json.dumps(request))
    
    # Collect responses
    result = {
        "success": False,
        "method": None,
        "time_ms": None,
        "error": None,
        "has_url": False,
        "has_content": False
    }
    
    # Wait for responses (max 10 messages or 5 seconds)
    for _ in range(10):
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            msg_type = response_data.get("type")
            
            if msg_type == "diagram_response":
                payload = response_data.get("payload", {})
                result["success"] = True
                result["method"] = payload.get("metadata", {}).get("generation_method")
                result["time_ms"] = payload.get("metadata", {}).get("generation_time_ms")
                result["has_url"] = bool(payload.get("url"))
                result["has_content"] = bool(payload.get("content"))
                break
                
            elif msg_type == "error_response":
                payload = response_data.get("payload", {})
                result["error"] = payload.get("error_message", "Unknown error")
                break
                
        except asyncio.TimeoutError:
            result["error"] = "Timeout waiting for response"
            break
    
    return result

async def run_comprehensive_test():
    """Run comprehensive test of all diagram types"""
    
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = f"comprehensive-test-{int(datetime.now().timestamp())}"
    user_id = "test-user"
    full_url = f"{url}?session_id={session_id}&user_id={user_id}"
    
    print("=" * 80)
    print("COMPREHENSIVE DIAGRAM SERVICE TEST")
    print("=" * 80)
    print(f"Service URL: {url}")
    print(f"Session ID: {session_id}")
    print(f"Testing all {sum(len(types) for types in SUPPORTED_DIAGRAM_TYPES.values())} diagram types")
    print("=" * 80)
    
    # SSL context for Railway
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Results storage
    all_results = []
    
    try:
        async with websockets.connect(full_url, ssl=ssl_context) as websocket:
            print("✅ Connected to WebSocket\n")
            
            # Receive welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"Welcome message: {welcome_data.get('type')}\n")
            
            # Test each category
            for method, diagram_types in SUPPORTED_DIAGRAM_TYPES.items():
                print(f"\n{'=' * 60}")
                print(f"Testing {method.upper()} Diagrams ({len(diagram_types)} types)")
                print("=" * 60)
                
                for diagram_type in diagram_types:
                    # Get content or use default
                    content = DIAGRAM_CONTENT.get(diagram_type, f"Sample content for {diagram_type}")
                    correlation_id = f"test-{method}-{diagram_type}"
                    
                    print(f"\nTesting: {diagram_type}...", end=" ")
                    
                    # Run test
                    result = await test_single_diagram(websocket, diagram_type, content, correlation_id)
                    
                    # Store result
                    test_result = TestResult(diagram_type, method)
                    test_result.success = result["success"]
                    test_result.actual_method = result["method"]
                    test_result.generation_time_ms = result["time_ms"]
                    test_result.error_message = result["error"]
                    test_result.has_url = result["has_url"]
                    test_result.has_content = result["has_content"]
                    
                    all_results.append(test_result)
                    
                    # Print immediate result
                    if result["success"]:
                        print(f"✅ Success ({result['method']}, {result['time_ms']}ms)")
                    else:
                        print(f"❌ Failed: {result['error']}")
                    
                    # Small delay between tests
                    await asyncio.sleep(0.5)
            
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        return all_results
    
    return all_results

def print_summary(results: List[TestResult]):
    """Print summary of test results"""
    
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    # Overall stats
    total = len(results)
    successful = sum(1 for r in results if r.success)
    failed = total - successful
    success_rate = (successful / total * 100) if total > 0 else 0
    
    print(f"\nOverall Success Rate: {successful}/{total} ({success_rate:.1f}%)")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    # By category
    for method in SUPPORTED_DIAGRAM_TYPES.keys():
        method_results = [r for r in results if r.expected_method == method]
        method_success = sum(1 for r in method_results if r.success)
        print(f"\n{method.upper()}: {method_success}/{len(method_results)} successful")
    
    # Failed diagrams
    if failed > 0:
        print("\n" + "=" * 60)
        print("FAILED DIAGRAMS:")
        print("=" * 60)
        for r in results:
            if not r.success:
                print(f"❌ {r.diagram_type} ({r.expected_method}): {r.error_message}")
    
    # Method mismatches
    mismatches = [r for r in results if r.success and r.actual_method != r.expected_method]
    if mismatches:
        print("\n" + "=" * 60)
        print("METHOD FALLBACKS (Expected → Actual):")
        print("=" * 60)
        for r in mismatches:
            print(f"⚠️ {r.diagram_type}: {r.expected_method} → {r.actual_method}")
    
    # Performance stats
    successful_results = [r for r in results if r.success and r.generation_time_ms]
    if successful_results:
        avg_time = sum(r.generation_time_ms for r in successful_results) / len(successful_results)
        min_time = min(r.generation_time_ms for r in successful_results)
        max_time = max(r.generation_time_ms for r in successful_results)
        
        print("\n" + "=" * 60)
        print("PERFORMANCE METRICS:")
        print("=" * 60)
        print(f"Average generation time: {avg_time:.0f}ms")
        print(f"Fastest: {min_time}ms")
        print(f"Slowest: {max_time}ms")
    
    # Storage status
    with_url = sum(1 for r in results if r.has_url)
    with_content = sum(1 for r in results if r.has_content)
    print("\n" + "=" * 60)
    print("STORAGE STATUS:")
    print("=" * 60)
    print(f"Diagrams with URLs (Supabase): {with_url}/{successful}")
    print(f"Diagrams with inline content: {with_content}/{successful}")

async def main():
    """Main test runner"""
    print("Starting comprehensive diagram test...")
    
    # Run tests
    results = await run_comprehensive_test()
    
    # Print summary
    print_summary(results)
    
    # Return exit code based on results
    failed = sum(1 for r in results if not r.success)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)