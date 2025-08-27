#!/usr/bin/env python3
"""
Comprehensive Test Script - Tests all diagram types
"""

import asyncio
import json
import websockets
import uuid
from datetime import datetime
import os
import time

# Configuration
WS_URL = "ws://127.0.0.1:8001/ws"
OUTPUT_DIR = "test_results_comprehensive"

# Create output directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/svg_templates", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/mermaid_code", exist_ok=True)

# Comprehensive test cases
TEST_CASES = {
    "svg_templates": [
        # Pyramid diagrams
        {
            "name": "pyramid_3_level",
            "request": {
                "content": "Three-tier strategy: Vision at top - Long-term organizational goals. Strategy in middle - Key initiatives and objectives. Operations at base - Daily execution and tasks.",
                "diagram_type": "pyramid_3_level",
                "theme": {"primaryColor": "#3B82F6", "secondaryColor": "#60A5FA"}
            }
        },
        {
            "name": "pyramid_4_level", 
            "request": {
                "content": "Business hierarchy: CEO/Board - Strategic direction. VPs - Department leadership. Managers - Team coordination. Staff - Operational execution.",
                "diagram_type": "pyramid_4_level",
                "theme": {"primaryColor": "#10B981", "secondaryColor": "#34D399"}
            }
        },
        {
            "name": "pyramid_5_level",
            "request": {
                "content": "Maslow's needs: Self-actualization - Personal growth. Esteem - Recognition and status. Social - Belonging and relationships. Safety - Security and stability. Physiological - Basic survival needs.",
                "diagram_type": "pyramid_5_level",
                "theme": {"primaryColor": "#F59E0B", "secondaryColor": "#FCD34D"}
            }
        },
        
        # Cycle diagrams
        {
            "name": "cycle_3_step",
            "request": {
                "content": "Agile development: Plan - Define sprint goals. Build - Develop features. Review - Get feedback and iterate.",
                "diagram_type": "cycle_3_step",
                "theme": {"primaryColor": "#8B5CF6", "secondaryColor": "#A78BFA"}
            }
        },
        {
            "name": "cycle_4_step",
            "request": {
                "content": "PDCA cycle: Plan - Identify problem and solution. Do - Implement solution. Check - Evaluate results. Act - Standardize if successful.",
                "diagram_type": "cycle_4_step",
                "theme": {"primaryColor": "#EC4899", "secondaryColor": "#F9A8D4"}
            }
        },
        {
            "name": "cycle_5_step",
            "request": {
                "content": "Design thinking: Empathize - Understand users. Define - Frame the problem. Ideate - Generate solutions. Prototype - Build models. Test - Validate with users.",
                "diagram_type": "cycle_5_step",
                "theme": {"primaryColor": "#14B8A6", "secondaryColor": "#5EEAD4"}
            }
        },
        
        # Venn diagrams
        {
            "name": "venn_2_circle",
            "request": {
                "content": "Skills overlap: Technical Skills - Programming, databases, cloud. Soft Skills - Communication, leadership, teamwork. Intersection - Problem-solving, project management.",
                "diagram_type": "venn_2_circle",
                "theme": {"primaryColor": "#0EA5E9", "secondaryColor": "#38BDF8"}
            }
        },
        {
            "name": "venn_3_circle",
            "request": {
                "content": "Product success: Desirable - Users want it. Feasible - We can build it. Viable - Business can sustain it. Sweet spot - All three overlap.",
                "diagram_type": "venn_3_circle",
                "theme": {"primaryColor": "#DC2626", "secondaryColor": "#F87171"}
            }
        },
        
        # Honeycomb diagrams
        {
            "name": "honeycomb_3",
            "request": {
                "content": "Core values: Innovation - Push boundaries. Quality - Excellence in delivery. Collaboration - Work together.",
                "diagram_type": "honeycomb_3",
                "theme": {"primaryColor": "#059669", "secondaryColor": "#34D399"}
            }
        },
        {
            "name": "honeycomb_5",
            "request": {
                "content": "Service pillars: Reliability - 99.9% uptime. Security - Data protection. Performance - Fast response. Support - 24/7 help. Innovation - New features.",
                "diagram_type": "honeycomb_5",
                "theme": {"primaryColor": "#7C3AED", "secondaryColor": "#A78BFA"}
            }
        },
        {
            "name": "honeycomb_7",
            "request": {
                "content": "Team competencies: Leadership - Guide teams. Technical - Deep expertise. Communication - Clear messaging. Strategy - Long-term vision. Execution - Get things done. Innovation - Creative solutions. Collaboration - Work together.",
                "diagram_type": "honeycomb_7",
                "theme": {"primaryColor": "#EA580C", "secondaryColor": "#FB923C"}
            }
        },
        
        # Matrix diagrams
        {
            "name": "matrix_2x2",
            "request": {
                "content": "Priority matrix: High Impact High Effort - Schedule strategically. High Impact Low Effort - Do immediately. Low Impact High Effort - Delegate or drop. Low Impact Low Effort - Quick wins.",
                "diagram_type": "matrix_2x2",
                "theme": {"primaryColor": "#0891B2", "secondaryColor": "#22D3EE"}
            }
        },
        {
            "name": "matrix_3x3",
            "request": {
                "content": "Risk assessment grid with nine zones: probability (low/medium/high) vs impact (low/medium/high). Critical risks in high-high quadrant.",
                "diagram_type": "matrix_3x3",
                "theme": {"primaryColor": "#B91C1C", "secondaryColor": "#EF4444"}
            }
        },
        {
            "name": "swot_matrix",
            "request": {
                "content": "SWOT Analysis: Strengths - Market leader, strong brand. Weaknesses - High costs, limited reach. Opportunities - New markets, partnerships. Threats - Competition, regulations.",
                "diagram_type": "swot_matrix",
                "theme": {"primaryColor": "#065F46", "secondaryColor": "#10B981"}
            }
        },
        
        # Hub and spoke
        {
            "name": "hub_spoke_4",
            "request": {
                "content": "Central platform: Core System - Main processing. API Gateway - External connections. Database - Data storage. Analytics - Insights engine. All connected to central hub.",
                "diagram_type": "hub_spoke_4",
                "theme": {"primaryColor": "#1E40AF", "secondaryColor": "#3B82F6"}
            }
        },
        {
            "name": "hub_spoke_6",
            "request": {
                "content": "Business ecosystem: Central HQ coordinates with: Sales - Revenue generation. Marketing - Brand awareness. Engineering - Product development. Support - Customer service. Finance - Budget control. HR - Talent management.",
                "diagram_type": "hub_spoke_6",
                "theme": {"primaryColor": "#7C2D12", "secondaryColor": "#EA580C"}
            }
        },
        
        # Funnel diagrams
        {
            "name": "funnel_3_stage",
            "request": {
                "content": "Sales funnel: Awareness - 10,000 visitors. Consideration - 1,000 leads. Purchase - 100 customers.",
                "diagram_type": "funnel_3_stage",
                "theme": {"primaryColor": "#166534", "secondaryColor": "#22C55E"}
            }
        },
        {
            "name": "funnel_4_stage",
            "request": {
                "content": "Marketing funnel: Attract - Content and SEO. Engage - Email and social. Convert - Sales calls. Retain - Customer success.",
                "diagram_type": "funnel_4_stage",
                "theme": {"primaryColor": "#581C87", "secondaryColor": "#9333EA"}
            }
        },
        {
            "name": "funnel_5_stage",
            "request": {
                "content": "User journey: Discovery - Find product. Research - Compare options. Trial - Test features. Purchase - Buy license. Advocacy - Recommend to others.",
                "diagram_type": "funnel_5_stage",
                "theme": {"primaryColor": "#991B1B", "secondaryColor": "#DC2626"}
            }
        },
        
        # Process flow
        {
            "name": "process_flow_3",
            "request": {
                "content": "Simple workflow: Input data received. Process and validate. Output results generated.",
                "diagram_type": "process_flow_3",
                "theme": {"primaryColor": "#0C4A6E", "secondaryColor": "#0EA5E9"}
            }
        },
        {
            "name": "process_flow_5",
            "request": {
                "content": "Development pipeline: Requirements gathering. Design and architecture. Implementation. Testing and QA. Deployment to production.",
                "diagram_type": "process_flow_5",
                "theme": {"primaryColor": "#831843", "secondaryColor": "#EC4899"}
            }
        },
        
        # Other diagrams
        {
            "name": "fishbone_4_bone",
            "request": {
                "content": "Problem analysis: Main problem - Low sales. Causes: People - Lack of training. Process - Inefficient workflow. Technology - Outdated systems. Market - Strong competition.",
                "diagram_type": "fishbone_4_bone",
                "theme": {"primaryColor": "#134E4A", "secondaryColor": "#14B8A6"}
            }
        },
        {
            "name": "gears_3",
            "request": {
                "content": "System integration: Frontend UI - User interface. Backend API - Business logic. Database - Data persistence. All gears work together.",
                "diagram_type": "gears_3",
                "theme": {"primaryColor": "#713F12", "secondaryColor": "#F59E0B"}
            }
        },
        {
            "name": "roadmap_quarterly_4",
            "request": {
                "content": "2024 Roadmap: Q1 - Foundation and planning. Q2 - Core development. Q3 - Beta testing and feedback. Q4 - Launch and scale.",
                "diagram_type": "roadmap_quarterly_4",
                "theme": {"primaryColor": "#4C1D95", "secondaryColor": "#8B5CF6"}
            }
        },
        {
            "name": "timeline_horizontal",
            "request": {
                "content": "Project timeline: Jan - Project kickoff. Mar - Phase 1 complete. Jun - Mid-year review. Sep - Phase 2 complete. Dec - Final delivery.",
                "diagram_type": "timeline_horizontal",
                "theme": {"primaryColor": "#1F2937", "secondaryColor": "#6B7280"}
            }
        }
    ],
    
    "mermaid": [
        {
            "name": "flowchart",
            "request": {
                "content": "Order processing system: Customer places order. System validates payment. If approved, check inventory. If in stock, ship order and send confirmation. If not in stock, backorder and notify customer. If payment fails, cancel order.",
                "diagram_type": "flowchart",
                "output_format": "mermaid",
                "theme": {"primaryColor": "#3B82F6"}
            }
        },
        {
            "name": "erDiagram",
            "request": {
                "content": "E-commerce database: Customer entity with id, name, email. Order entity with id, date, total. Product entity with id, name, price. Customer has many orders. Order contains many products.",
                "diagram_type": "erDiagram",
                "output_format": "mermaid",
                "theme": {"primaryColor": "#10B981"}
            }
        },
        {
            "name": "journey",
            "request": {
                "content": "Customer support experience: User reports issue - frustrated. Support acknowledges - neutral. Troubleshooting steps - hopeful. Problem identified - relieved. Solution implemented - satisfied. Follow-up check - delighted.",
                "diagram_type": "journey",
                "output_format": "mermaid",
                "theme": {"primaryColor": "#F59E0B"}
            }
        },
        {
            "name": "gantt",
            "request": {
                "content": "Website redesign project: Research phase 2 weeks. Design mockups 3 weeks after research. Frontend development 4 weeks after design. Backend integration 3 weeks parallel with frontend. Testing 2 weeks after development. Launch 1 week after testing.",
                "diagram_type": "gantt",
                "output_format": "mermaid",
                "theme": {"primaryColor": "#8B5CF6"}
            }
        },
        {
            "name": "quadrantChart",
            "request": {
                "content": "Feature prioritization: High value high effort - Major features. High value low effort - Quick wins. Low value high effort - Avoid these. Low value low effort - Fill-ins. Plot 8 features across quadrants.",
                "diagram_type": "quadrantChart",
                "output_format": "mermaid",
                "theme": {"primaryColor": "#EC4899"}
            }
        },
        {
            "name": "timeline",
            "request": {
                "content": "Company milestones: 2020 - Company founded. 2021 - First product launch. 2022 - Series A funding. 2023 - International expansion. 2024 - IPO preparation.",
                "diagram_type": "timeline",
                "output_format": "mermaid",
                "theme": {"primaryColor": "#14B8A6"}
            }
        },
        {
            "name": "kanban",
            "request": {
                "content": "Sprint board with columns: Backlog - User stories waiting. In Progress - Active development. Code Review - Awaiting review. Testing - QA validation. Done - Completed items. Add sample tasks in each column.",
                "diagram_type": "kanban",
                "output_format": "mermaid",
                "theme": {"primaryColor": "#DC2626"}
            }
        }
    ]
}


async def test_diagram_type(websocket, session_id, test_case, category):
    """Test a single diagram type"""
    request_id = f"req_{uuid.uuid4()}"
    
    message = {
        "message_id": f"msg_{uuid.uuid4()}",
        "correlation_id": request_id,
        "request_id": request_id,
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "type": "diagram_request",
        "payload": test_case["request"]
    }
    
    # Send request
    await websocket.send(json.dumps(message))
    
    # Collect responses
    start_time = time.time()
    response_data = None
    status_updates = []
    
    while True:
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            response_json = json.loads(response)
            
            msg_type = response_json.get("type")
            
            if msg_type == "status":
                status = response_json.get("payload", {}).get("status")
                message_text = response_json.get("payload", {}).get("message", "")
                status_updates.append({"status": status, "message": message_text})
                
            elif msg_type in ["response", "diagram_response"]:
                response_data = response_json
                break
                
            elif msg_type == "error":
                response_data = response_json
                break
                
        except asyncio.TimeoutError:
            break
        except Exception as e:
            print(f"    ❌ Error: {e}")
            break
    
    elapsed_time = time.time() - start_time
    
    # Process result
    result = {
        "name": test_case["name"],
        "category": category,
        "request_id": request_id,
        "elapsed_time": elapsed_time,
        "status_updates": status_updates,
        "success": False,
        "response": response_data
    }
    
    if response_data and response_data.get("type") in ["response", "diagram_response"]:
        result["success"] = True
        payload = response_data.get("payload", {})
        content = payload.get("content", "")
        
        # Save output
        if category == "svg_templates":
            filename = f"{OUTPUT_DIR}/svg_templates/{test_case['name']}.svg"
            with open(filename, "w") as f:
                f.write(content)
        elif category == "mermaid":
            # Extract Mermaid code from metadata if available
            mermaid_code = payload.get("metadata", {}).get("mermaid_code", "")
            if not mermaid_code and "mermaid" in content.lower():
                # Try to extract from SVG
                import re
                match = re.search(r'"code":\s*"([^"]+)"', content)
                if match:
                    mermaid_code = match.group(1).replace("\\n", "\n")
            
            if mermaid_code:
                filename = f"{OUTPUT_DIR}/mermaid_code/{test_case['name']}.mmd"
                with open(filename, "w") as f:
                    f.write(mermaid_code)
    
    return result


async def run_comprehensive_tests():
    """Run all tests"""
    print("=" * 80)
    print("COMPREHENSIVE DIAGRAM TEST SUITE")
    print("=" * 80)
    
    all_results = []
    session_id = str(uuid.uuid4())
    
    async with websockets.connect(f"{WS_URL}?session_id={session_id}&user_id=test_comprehensive") as websocket:
        print(f"Connected to WebSocket server")
        print(f"Session ID: {session_id}\n")
        
        # Test SVG Templates
        print("📊 Testing SVG Templates")
        print("-" * 40)
        for i, test_case in enumerate(TEST_CASES["svg_templates"], 1):
            print(f"  [{i:2d}/25] {test_case['name']:25s} ", end="", flush=True)
            result = await test_diagram_type(websocket, session_id, test_case, "svg_templates")
            all_results.append(result)
            
            if result["success"]:
                print(f"✅ ({result['elapsed_time']:.2f}s)")
            else:
                print(f"❌ Failed")
        
        print("\n📈 Testing Mermaid Diagrams")
        print("-" * 40)
        for i, test_case in enumerate(TEST_CASES["mermaid"], 1):
            print(f"  [{i:2d}/7] {test_case['name']:25s} ", end="", flush=True)
            result = await test_diagram_type(websocket, session_id, test_case, "mermaid")
            all_results.append(result)
            
            if result["success"]:
                print(f"✅ ({result['elapsed_time']:.2f}s)")
            else:
                print(f"❌ Failed")
    
    # Save comprehensive results
    with open(f"{OUTPUT_DIR}/comprehensive_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    return all_results


def generate_summary(results):
    """Generate test summary"""
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    svg_results = [r for r in results if r["category"] == "svg_templates"]
    mermaid_results = [r for r in results if r["category"] == "mermaid"]
    
    svg_success = sum(1 for r in svg_results if r["success"])
    mermaid_success = sum(1 for r in mermaid_results if r["success"])
    
    print(f"\n📊 SVG Templates: {svg_success}/{len(svg_results)} passed")
    print(f"📈 Mermaid Diagrams: {mermaid_success}/{len(mermaid_results)} passed")
    
    total_success = svg_success + mermaid_success
    total_tests = len(results)
    success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n🎯 Overall: {total_success}/{total_tests} passed ({success_rate:.1f}%)")
    
    # Calculate average times
    svg_times = [r["elapsed_time"] for r in svg_results if r["success"]]
    mermaid_times = [r["elapsed_time"] for r in mermaid_results if r["success"]]
    
    if svg_times:
        print(f"\n⏱️  Average SVG generation time: {sum(svg_times)/len(svg_times):.2f}s")
    if mermaid_times:
        print(f"⏱️  Average Mermaid generation time: {sum(mermaid_times)/len(mermaid_times):.2f}s")
    
    # List failures
    failures = [r for r in results if not r["success"]]
    if failures:
        print(f"\n❌ Failed tests ({len(failures)}):")
        for f in failures:
            print(f"   - {f['name']} ({f['category']})")
    
    return {
        "total_tests": total_tests,
        "successful": total_success,
        "failed": len(failures),
        "success_rate": success_rate,
        "svg_success": svg_success,
        "mermaid_success": mermaid_success,
        "failures": [f["name"] for f in failures]
    }


async def main():
    """Main function"""
    try:
        results = await run_comprehensive_tests()
        summary = generate_summary(results)
        
        # Save summary
        with open(f"{OUTPUT_DIR}/test_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print("\n✅ Test suite completed!")
        print(f"📁 Results saved to {OUTPUT_DIR}/")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())