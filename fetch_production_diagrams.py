#!/usr/bin/env python3
"""
Fetch actual diagram content from Railway production
"""

import asyncio
import json
import websockets
import uuid
from datetime import datetime
import ssl
import certifi
import os

WS_URL = "wss://deckster-diagram-service-production.up.railway.app/ws"

# Test configurations from the previous test
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


async def fetch_diagram(websocket, session_id, diagram_type, content, test_type):
    """Fetch a single diagram and return its content"""
    
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
    
    await websocket.send(json.dumps(request))
    
    timeout = 30.0
    while True:
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            response_json = json.loads(response)
            
            if response_json.get("type") in ["response", "diagram_response"]:
                payload = response_json.get("payload", {})
                return {
                    "type": diagram_type,
                    "content": payload.get("content", ""),
                    "mermaid_code": payload.get("metadata", {}).get("mermaid_code", ""),
                    "success": True
                }
                
            elif response_json.get("type") == "error":
                return {
                    "type": diagram_type,
                    "content": "",
                    "error": response_json.get("payload", {}).get("message", "Unknown error"),
                    "success": False
                }
                
        except asyncio.TimeoutError:
            return {"type": diagram_type, "content": "", "error": "Timeout", "success": False}
        except Exception as e:
            return {"type": diagram_type, "content": "", "error": str(e), "success": False}


async def main():
    print("Fetching diagrams from production...")
    
    session_id = str(uuid.uuid4())
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    all_diagrams = []
    
    async with websockets.connect(
        f"{WS_URL}?session_id={session_id}&user_id=fetch_test",
        ssl=ssl_context
    ) as websocket:
        
        # Fetch SVG templates
        print("\nFetching SVG templates...")
        for i, (diagram_type, content) in enumerate(SVG_TEMPLATES, 1):
            print(f"  [{i}/{len(SVG_TEMPLATES)}] {diagram_type}")
            result = await fetch_diagram(websocket, session_id, diagram_type, content, "svg")
            result["category"] = "svg"
            all_diagrams.append(result)
            await asyncio.sleep(0.1)
        
        # Fetch Mermaid diagrams
        print("\nFetching Mermaid diagrams...")
        for i, (diagram_type, content) in enumerate(MERMAID_DIAGRAMS, 1):
            print(f"  [{i}/{len(MERMAID_DIAGRAMS)}] {diagram_type}")
            result = await fetch_diagram(websocket, session_id, diagram_type, content, "mermaid")
            result["category"] = "mermaid"
            all_diagrams.append(result)
            await asyncio.sleep(0.1)
    
    # Save results
    with open("production_diagrams.json", "w") as f:
        json.dump(all_diagrams, f, indent=2)
    
    print(f"\n✅ Fetched {len(all_diagrams)} diagrams")
    print("📁 Saved to production_diagrams.json")


if __name__ == "__main__":
    asyncio.run(main())