#!/usr/bin/env python3
"""
Fetch diagrams from Railway production and save as individual files
"""

import asyncio
import json
import websockets
import uuid
from datetime import datetime
import ssl
import certifi
import os
import re

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


def extract_mermaid_from_svg(svg_content):
    """Extract Mermaid code from SVG with embedded JSON"""
    if 'application/mermaid+json' in svg_content:
        match = re.search(r'"code":\s*"([^"]+)"', svg_content)
        if match:
            return match.group(1).replace('\\n', '\n')
    return None


async def main():
    print("=" * 80)
    print("FETCHING AND SAVING RAILWAY PRODUCTION DIAGRAMS")
    print("=" * 80)
    
    # Create output directories
    os.makedirs("railway_outputs", exist_ok=True)
    os.makedirs("railway_outputs/svg", exist_ok=True)
    os.makedirs("railway_outputs/mermaid", exist_ok=True)
    
    session_id = str(uuid.uuid4())
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    diagram_index = []
    
    async with websockets.connect(
        f"{WS_URL}?session_id={session_id}&user_id=save_test",
        ssl=ssl_context
    ) as websocket:
        
        # Fetch SVG templates
        print("\n📊 Fetching and saving SVG templates...")
        for i, (diagram_type, content) in enumerate(SVG_TEMPLATES, 1):
            print(f"  [{i}/{len(SVG_TEMPLATES)}] {diagram_type:20}", end=" ")
            
            result = await fetch_diagram(websocket, session_id, diagram_type, content, "svg")
            
            if result["success"] and result["content"]:
                # Save SVG file
                filename = f"railway_outputs/svg/{diagram_type}.svg"
                with open(filename, 'w') as f:
                    f.write(result["content"])
                
                # Check if it contains Mermaid code
                mermaid_code = extract_mermaid_from_svg(result["content"])
                if mermaid_code:
                    mermaid_filename = f"railway_outputs/mermaid/{diagram_type}.mmd"
                    with open(mermaid_filename, 'w') as f:
                        f.write(mermaid_code)
                    print(f"✅ (SVG + Mermaid)")
                else:
                    print(f"✅")
                
                diagram_index.append({
                    "type": diagram_type,
                    "category": "svg",
                    "file": f"svg/{diagram_type}.svg",
                    "has_mermaid": mermaid_code is not None
                })
            else:
                print(f"❌ {result.get('error', 'Failed')}")
                diagram_index.append({
                    "type": diagram_type,
                    "category": "svg",
                    "error": result.get('error', 'Failed')
                })
            
            await asyncio.sleep(0.1)
        
        # Fetch Mermaid diagrams
        print("\n📈 Fetching and saving Mermaid diagrams...")
        for i, (diagram_type, content) in enumerate(MERMAID_DIAGRAMS, 1):
            print(f"  [{i}/{len(MERMAID_DIAGRAMS)}] {diagram_type:15}", end=" ")
            
            result = await fetch_diagram(websocket, session_id, diagram_type, content, "mermaid")
            
            if result["success"]:
                saved_files = []
                
                # Save SVG content if available
                if result["content"]:
                    filename = f"railway_outputs/svg/{diagram_type}_mermaid.svg"
                    with open(filename, 'w') as f:
                        f.write(result["content"])
                    saved_files.append(f"svg/{diagram_type}_mermaid.svg")
                
                # Extract and save Mermaid code
                mermaid_code = result.get("mermaid_code") or extract_mermaid_from_svg(result.get("content", ""))
                if mermaid_code:
                    mermaid_filename = f"railway_outputs/mermaid/{diagram_type}.mmd"
                    with open(mermaid_filename, 'w') as f:
                        f.write(mermaid_code)
                    saved_files.append(f"mermaid/{diagram_type}.mmd")
                
                if saved_files:
                    print(f"✅")
                    diagram_index.append({
                        "type": diagram_type,
                        "category": "mermaid",
                        "files": saved_files,
                        "has_mermaid": True
                    })
                else:
                    print(f"⚠️ No content")
                    diagram_index.append({
                        "type": diagram_type,
                        "category": "mermaid",
                        "error": "No content received"
                    })
            else:
                print(f"❌ {result.get('error', 'Failed')}")
                diagram_index.append({
                    "type": diagram_type,
                    "category": "mermaid",
                    "error": result.get('error', 'Failed')
                })
            
            await asyncio.sleep(0.1)
    
    # Save index file
    with open("railway_outputs/index.json", 'w') as f:
        json.dump(diagram_index, f, indent=2)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    svg_count = len([d for d in diagram_index if d.get("category") == "svg" and "error" not in d])
    mermaid_count = len([d for d in diagram_index if d.get("category") == "mermaid" and "error" not in d])
    
    print(f"✅ SVG templates saved: {svg_count}/{len(SVG_TEMPLATES)}")
    print(f"✅ Mermaid diagrams saved: {mermaid_count}/{len(MERMAID_DIAGRAMS)}")
    print(f"📁 Files saved to: railway_outputs/")
    print(f"📋 Index file: railway_outputs/index.json")


if __name__ == "__main__":
    asyncio.run(main())