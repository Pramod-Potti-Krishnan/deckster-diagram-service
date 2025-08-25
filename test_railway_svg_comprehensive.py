#!/usr/bin/env python3
"""
Comprehensive SVG Template Test for Railway Deployment
Tests all 25 SVG templates on the deployed service
"""

import asyncio
import json
import websockets
import ssl
from datetime import datetime
import os
from pathlib import Path
from typing import Dict, List, Any

# Comprehensive SVG template test cases
SVG_TEST_CASES = [
    # Pyramids (3 templates)
    {
        "name": "3-Level Pyramid",
        "diagram_type": "pyramid_3_level",
        "content": "Strategic pyramid with Foundation layer for core infrastructure, Operations layer for business processes, and Executive layer for strategic decisions",
        "data_points": [
            {"label": "Foundation Layer", "value": 40},
            {"label": "Operations Layer", "value": 35},
            {"label": "Executive Layer", "value": 25}
        ]
    },
    {
        "name": "4-Level Pyramid",
        "diagram_type": "pyramid_4_level",
        "content": "Organizational hierarchy with Base Operations, Middle Management, Senior Leadership, and C-Suite",
        "data_points": [
            {"label": "Base Operations", "value": 40},
            {"label": "Middle Management", "value": 30},
            {"label": "Senior Leadership", "value": 20},
            {"label": "C-Suite", "value": 10}
        ]
    },
    {
        "name": "5-Level Pyramid",
        "diagram_type": "pyramid_5_level",
        "content": "Maslow's hierarchy of needs from Physiological to Self-Actualization",
        "data_points": [
            {"label": "Physiological Needs", "value": 30},
            {"label": "Safety Needs", "value": 25},
            {"label": "Love & Belonging", "value": 20},
            {"label": "Esteem", "value": 15},
            {"label": "Self-Actualization", "value": 10}
        ]
    },
    
    # Cycles (3 templates)
    {
        "name": "3-Step Cycle",
        "diagram_type": "cycle_3_step",
        "content": "Plan-Do-Check continuous improvement cycle",
        "data_points": [
            {"label": "Plan", "value": 33},
            {"label": "Do", "value": 34},
            {"label": "Check", "value": 33}
        ]
    },
    {
        "name": "4-Step Cycle",
        "diagram_type": "cycle_4_step",
        "content": "PDCA cycle: Plan, Do, Check, Act",
        "data_points": [
            {"label": "Plan", "value": 25},
            {"label": "Do", "value": 25},
            {"label": "Check", "value": 25},
            {"label": "Act", "value": 25}
        ]
    },
    {
        "name": "5-Step Cycle",
        "diagram_type": "cycle_5_step",
        "content": "DMAIC process improvement methodology",
        "data_points": [
            {"label": "Define", "value": 20},
            {"label": "Measure", "value": 20},
            {"label": "Analyze", "value": 20},
            {"label": "Improve", "value": 20},
            {"label": "Control", "value": 20}
        ]
    },
    
    # Venn Diagrams (2 templates)
    {
        "name": "2-Circle Venn",
        "diagram_type": "venn_2_circle",
        "content": "Technical Skills and Soft Skills overlap analysis",
        "data_points": [
            {"label": "Technical Skills", "value": 45},
            {"label": "Soft Skills", "value": 45},
            {"label": "Both Skills", "value": 10}  # Intersection
        ]
    },
    {
        "name": "3-Circle Venn",
        "diagram_type": "venn_3_circle",
        "content": "Product, Engineering, and Design team collaboration areas",
        "data_points": [
            {"label": "Product", "value": 30},
            {"label": "Engineering", "value": 30},
            {"label": "Design", "value": 30},
            {"label": "Product ∩ Engineering", "value": 5},  # Intersection of Product and Engineering
            {"label": "Product ∩ Design", "value": 5},       # Intersection of Product and Design
            {"label": "Engineering ∩ Design", "value": 5},   # Intersection of Engineering and Design
            {"label": "All Three", "value": 5}               # Central intersection of all three
        ]
    },
    
    # Funnels (3 templates)
    {
        "name": "3-Stage Funnel",
        "diagram_type": "funnel_3_stage",
        "content": "Sales pipeline: Leads, Qualified Prospects, Customers",
        "data_points": [
            {"label": "Leads", "value": 1000},
            {"label": "Qualified Prospects", "value": 300},
            {"label": "Customers", "value": 50}
        ]
    },
    {
        "name": "4-Stage Funnel",
        "diagram_type": "funnel_4_stage",
        "content": "AIDA marketing model implementation",
        "data_points": [
            {"label": "Awareness", "value": 10000},
            {"label": "Interest", "value": 5000},
            {"label": "Decision", "value": 2000},
            {"label": "Action", "value": 500}
        ]
    },
    {
        "name": "5-Stage Funnel",
        "diagram_type": "funnel_5_stage",
        "content": "Complete customer journey from discovery to loyalty",
        "data_points": [
            {"label": "Discovery", "value": 100000},
            {"label": "Consideration", "value": 50000},
            {"label": "Evaluation", "value": 20000},
            {"label": "Purchase", "value": 5000},
            {"label": "Loyalty", "value": 1000}
        ]
    },
    
    # Matrices (3 templates)
    {
        "name": "2x2 Matrix",
        "diagram_type": "matrix_2x2",
        "content": "Eisenhower priority matrix for task management",
        "data_points": [
            {"label": "Urgent & Important", "value": 25},
            {"label": "Not Urgent & Important", "value": 25},
            {"label": "Urgent & Not Important", "value": 25},
            {"label": "Not Urgent & Not Important", "value": 25}
        ]
    },
    {
        "name": "3x3 Matrix",
        "diagram_type": "matrix_3x3",
        "content": "Risk assessment matrix with probability and impact",
        "data_points": [
            {"label": "Low-Low", "value": 11}, {"label": "Low-Med", "value": 11}, {"label": "Low-High", "value": 11},
            {"label": "Med-Low", "value": 11}, {"label": "Med-Med", "value": 12}, {"label": "Med-High", "value": 11},
            {"label": "High-Low", "value": 11}, {"label": "High-Med", "value": 11}, {"label": "High-High", "value": 11}
        ]
    },
    {
        "name": "SWOT Matrix",
        "diagram_type": "swot_matrix",
        "content": "Business SWOT analysis framework",
        "data_points": [
            {"label": "Strengths", "value": 25},
            {"label": "Weaknesses", "value": 25},
            {"label": "Opportunities", "value": 25},
            {"label": "Threats", "value": 25}
        ]
    },
    
    # Hub and Spoke (2 templates)
    {
        "name": "Hub-Spoke 4",
        "diagram_type": "hub_spoke_4",
        "content": "Central API hub with four service connections",
        "data_points": [
            {"label": "API Gateway", "value": 40},
            {"label": "Auth Service", "value": 15},
            {"label": "Data Service", "value": 15},
            {"label": "Cache Service", "value": 15},
            {"label": "Queue Service", "value": 15}
        ]
    },
    {
        "name": "Hub-Spoke 6",
        "diagram_type": "hub_spoke_6",
        "content": "Microservices architecture with central orchestrator",
        "data_points": [
            {"label": "Orchestrator", "value": 30},
            {"label": "User Service", "value": 12},
            {"label": "Order Service", "value": 12},
            {"label": "Payment Service", "value": 12},
            {"label": "Inventory Service", "value": 12},
            {"label": "Shipping Service", "value": 11},
            {"label": "Notification Service", "value": 11}
        ]
    },
    
    # Honeycombs (3 templates)
    {
        "name": "3-Cell Honeycomb",
        "diagram_type": "honeycomb_3",
        "content": "Core platform components structure",
        "data_points": [
            {"label": "Frontend", "value": 33},
            {"label": "Backend", "value": 33},
            {"label": "Database", "value": 34}
        ]
    },
    {
        "name": "5-Cell Honeycomb",
        "diagram_type": "honeycomb_5",
        "content": "Team structure for agile development",
        "data_points": [
            {"label": "Product Team", "value": 20},
            {"label": "Dev Team", "value": 20},
            {"label": "QA Team", "value": 20},
            {"label": "DevOps Team", "value": 20},
            {"label": "Support Team", "value": 20}
        ]
    },
    {
        "name": "7-Cell Honeycomb",
        "diagram_type": "honeycomb_7",
        "content": "Complete service mesh architecture",
        "data_points": [
            {"label": "API Gateway", "value": 14},
            {"label": "Auth Service", "value": 14},
            {"label": "User Service", "value": 14},
            {"label": "Data Service", "value": 14},
            {"label": "Analytics", "value": 15},
            {"label": "Monitoring", "value": 15},
            {"label": "Logging", "value": 14}
        ]
    },
    
    # Process Flows (2 templates)
    {
        "name": "3-Step Process",
        "diagram_type": "process_flow_3",
        "content": "Simple ETL pipeline: Extract, Transform, Load",
        "data_points": [
            {"label": "Extract", "value": 33},
            {"label": "Transform", "value": 34},
            {"label": "Load", "value": 33}
        ]
    },
    {
        "name": "5-Step Process",
        "diagram_type": "process_flow_5",
        "content": "Manufacturing process from raw materials to shipping",
        "data_points": [
            {"label": "Raw Materials", "value": 20},
            {"label": "Processing", "value": 20},
            {"label": "Assembly", "value": 20},
            {"label": "Quality Check", "value": 20},
            {"label": "Packaging", "value": 20}
        ]
    },
    
    # Specialized Diagrams (4 templates)
    {
        "name": "Fishbone Diagram",
        "diagram_type": "fishbone_4_bone",
        "content": "Root cause analysis for production issues",
        "data_points": [
            {"label": "People", "value": 25},
            {"label": "Process", "value": 25},
            {"label": "Equipment", "value": 25},
            {"label": "Materials", "value": 25}
        ]
    },
    {
        "name": "Gears System",
        "diagram_type": "gears_3",
        "content": "Interconnected business systems",
        "data_points": [
            {"label": "Sales Engine", "value": 40},
            {"label": "Marketing Drive", "value": 30},
            {"label": "Support System", "value": 30}
        ]
    },
    {
        "name": "Timeline",
        "diagram_type": "timeline_horizontal",
        "content": "Quarterly project milestones for 2024",
        "data_points": [
            {"label": "Q1 Planning", "value": 25},
            {"label": "Q2 Development", "value": 25},
            {"label": "Q3 Testing", "value": 25},
            {"label": "Q4 Launch", "value": 25}
        ]
    },
    {
        "name": "Roadmap",
        "diagram_type": "roadmap_quarterly_4",
        "content": "Product development roadmap for 2024",
        "data_points": [
            {"label": "Q1: Foundation", "value": 25},
            {"label": "Q2: Core Features", "value": 25},
            {"label": "Q3: Integrations", "value": 25},
            {"label": "Q4: Scale", "value": 25}
        ]
    }
]


async def test_single_svg(websocket, test_case: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Test a single SVG diagram generation"""
    
    correlation_id = f"svg-test-{index:02d}-{test_case['diagram_type']}"
    
    # Prepare request
    request = {
        "type": "diagram_request",
        "correlation_id": correlation_id,
        "data": {
            "diagram_type": test_case["diagram_type"],
            "content": test_case["content"],
            "data_points": test_case.get("data_points", []),
            "theme": {
                "primaryColor": "#3B82F6",
                "backgroundColor": "#ffffff",
                "textColor": "#1F2937"
            }
        }
    }
    
    print(f"  📤 Sending request for {test_case['diagram_type']}...")
    start_time = datetime.now()
    
    await websocket.send(json.dumps(request))
    
    # Wait for response
    result = None
    for attempt in range(15):  # Wait for up to 15 messages
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
            response_data = json.loads(response)
            msg_type = response_data.get("type")
            msg_correlation = response_data.get("correlation_id")
            
            # Skip messages for other requests
            if msg_correlation != correlation_id:
                continue
            
            if msg_type == "diagram_response":
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                payload = response_data.get("payload", {})
                result = {
                    "success": True,
                    "name": test_case["name"],
                    "diagram_type": test_case["diagram_type"],
                    "content": payload.get("content"),
                    "url": payload.get("url"),
                    "metadata": payload.get("metadata", {}),
                    "response_time": response_time,
                    "data_points_sent": len(test_case.get("data_points", [])),
                    "timestamp": datetime.now().isoformat()
                }
                break
                
            elif msg_type == "error_response":
                payload = response_data.get("payload", {})
                result = {
                    "success": False,
                    "name": test_case["name"],
                    "diagram_type": test_case["diagram_type"],
                    "error": payload.get("error_message", "Unknown error"),
                    "error_code": payload.get("error_code"),
                    "timestamp": datetime.now().isoformat()
                }
                break
                
        except asyncio.TimeoutError:
            result = {
                "success": False,
                "name": test_case["name"],
                "diagram_type": test_case["diagram_type"],
                "error": "Timeout waiting for response",
                "timestamp": datetime.now().isoformat()
            }
            break
    
    if not result:
        result = {
            "success": False,
            "name": test_case["name"],
            "diagram_type": test_case["diagram_type"],
            "error": "No valid response received",
            "timestamp": datetime.now().isoformat()
        }
    
    return result


async def run_svg_tests():
    """Run all SVG template tests"""
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"railway_svg_test_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    
    # Railway WebSocket URL
    base_url = "deckster-diagram-service-production.up.railway.app"
    ws_url = f"wss://{base_url}/ws"
    session_id = f"svg-test-{timestamp}"
    user_id = "svg-test-user"
    full_url = f"{ws_url}?session_id={session_id}&user_id={user_id}"
    
    print("=" * 80)
    print("🚀 RAILWAY SVG TEMPLATE COMPREHENSIVE TEST")
    print("=" * 80)
    print(f"Service: {base_url}")
    print(f"Testing: {len(SVG_TEST_CASES)} SVG templates")
    print(f"Output: {output_dir}")
    print("=" * 80)
    
    # SSL context - disable verification for testing
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    results = []
    
    try:
        async with websockets.connect(full_url, ssl=ssl_context) as websocket:
            print("✅ Connected to Railway WebSocket service\n")
            
            # Receive welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"📨 Welcome: {welcome_data.get('type')}\n")
            
            # Test each SVG template
            for i, test_case in enumerate(SVG_TEST_CASES, 1):
                print(f"\n[{i}/{len(SVG_TEST_CASES)}] Testing: {test_case['name']}")
                
                result = await test_single_svg(websocket, test_case, i)
                results.append(result)
                
                if result["success"]:
                    metadata = result.get("metadata", {})
                    method = metadata.get("generation_method", "unknown")
                    time_str = f"{result.get('response_time', 0):.2f}s"
                    
                    print(f"  ✅ Success - Method: {method} - Time: {time_str}")
                    
                    # Validate SVG content
                    svg_content = result.get("content", "")
                    if svg_content:
                        # Check SVG structure
                        has_svg_tags = "<svg" in svg_content and "</svg>" in svg_content
                        
                        # Check label replacements
                        labels_found = 0
                        if test_case.get("data_points"):
                            for dp in test_case["data_points"]:
                                if dp["label"] in svg_content:
                                    labels_found += 1
                        
                        print(f"  📊 SVG valid: {has_svg_tags} | Labels: {labels_found}/{result['data_points_sent']}")
                        
                        # Save SVG file
                        svg_filename = f"{i:02d}_{test_case['diagram_type']}.svg"
                        svg_path = output_dir / svg_filename
                        with open(svg_path, "w", encoding="utf-8") as f:
                            f.write(svg_content)
                        
                        result["saved_file"] = str(svg_path)
                        result["svg_valid"] = has_svg_tags
                        result["labels_found"] = labels_found
                    else:
                        print(f"  ⚠️  No SVG content received")
                else:
                    print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
                
                # Small delay between tests
                await asyncio.sleep(0.2)
            
    except Exception as e:
        print(f"\n❌ Connection error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return results, output_dir


def generate_dashboard(results: List[Dict], output_dir: Path) -> Path:
    """Generate HTML dashboard for test results"""
    
    # Calculate statistics
    total = len(results)
    successful = sum(1 for r in results if r.get("success", False))
    failed = total - successful
    success_rate = (successful / total * 100) if total > 0 else 0
    
    # Average response time for successful requests
    response_times = [r.get("response_time", 0) for r in results if r.get("success", False)]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Group by category
    categories = {
        "Pyramids": ["pyramid_3_level", "pyramid_4_level", "pyramid_5_level"],
        "Cycles": ["cycle_3_step", "cycle_4_step", "cycle_5_step"],
        "Venn Diagrams": ["venn_2_circle", "venn_3_circle"],
        "Funnels": ["funnel_3_stage", "funnel_4_stage", "funnel_5_stage"],
        "Matrices": ["matrix_2x2", "matrix_3x3", "swot_matrix"],
        "Hub & Spoke": ["hub_spoke_4", "hub_spoke_6"],
        "Honeycombs": ["honeycomb_3", "honeycomb_5", "honeycomb_7"],
        "Process Flows": ["process_flow_3", "process_flow_5"],
        "Specialized": ["fishbone_4_bone", "gears_3", "timeline_horizontal", "roadmap_quarterly_4"]
    }
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Railway SVG Test Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        h1 {{
            color: white;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .success {{ color: #10B981; }}
        .failed {{ color: #EF4444; }}
        .warning {{ color: #F59E0B; }}
        .info {{ color: #3B82F6; }}
        .category {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        .category-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        .diagrams-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        .diagram-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e5e7eb;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .diagram-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }}
        .diagram-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .diagram-title {{
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
        }}
        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .badge-success {{
            background: #D1FAE5;
            color: #065F46;
        }}
        .badge-failed {{
            background: #FEE2E2;
            color: #991B1B;
        }}
        .svg-container {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 20px;
            min-height: 300px;
            max-height: 400px;
            overflow: auto;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .svg-container svg {{
            max-width: 100%;
            height: auto;
        }}
        .metadata {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e5e7eb;
            font-size: 0.85em;
            color: #666;
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }}
        .error-message {{
            background: #FEE2E2;
            color: #991B1B;
            padding: 20px;
            border-radius: 6px;
            text-align: center;
        }}
        .timestamp {{
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Railway SVG Template Test Results</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value success">{successful}</div>
                <div class="stat-label">Successful</div>
            </div>
            <div class="stat-card">
                <div class="stat-value failed">{failed}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value info">{success_rate:.1f}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value warning">{avg_response_time:.2f}s</div>
                <div class="stat-label">Avg Response Time</div>
            </div>
        </div>
"""
    
    # Add diagrams by category
    for category_name, diagram_types in categories.items():
        category_results = [r for r in results if r.get("diagram_type") in diagram_types]
        if not category_results:
            continue
        
        html += f"""
        <div class="category">
            <h2 class="category-title">{category_name}</h2>
            <div class="diagrams-grid">
"""
        
        for result in category_results:
            status = "success" if result.get("success") else "failed"
            badge_class = "badge-success" if result.get("success") else "badge-failed"
            
            html += f"""
                <div class="diagram-card">
                    <div class="diagram-header">
                        <span class="diagram-title">{result.get('name', 'Unknown')}</span>
                        <span class="status-badge {badge_class}">
                            {status.upper()}
                        </span>
                    </div>
"""
            
            if result.get("success") and result.get("saved_file"):
                # Read and embed SVG
                svg_path = Path(result["saved_file"])
                if svg_path.exists():
                    with open(svg_path, "r", encoding="utf-8") as f:
                        svg_content = f.read()
                    html += f"""
                    <div class="svg-container">
                        {svg_content}
                    </div>
"""
                else:
                    html += """
                    <div class="error-message">SVG file not found</div>
"""
                
                # Add metadata
                metadata = result.get("metadata", {})
                html += f"""
                    <div class="metadata">
                        <div><strong>Type:</strong> {result.get('diagram_type', 'N/A')}</div>
                        <div><strong>Method:</strong> {metadata.get('generation_method', 'N/A')}</div>
                        <div><strong>Response:</strong> {result.get('response_time', 0):.2f}s</div>
                        <div><strong>Labels:</strong> {result.get('labels_found', 0)}/{result.get('data_points_sent', 0)}</div>
                    </div>
"""
            else:
                error_msg = result.get("error", "Unknown error")
                html += f"""
                    <div class="error-message">{error_msg}</div>
"""
            
            html += """
                </div>
"""
        
        html += """
            </div>
        </div>
"""
    
    html += f"""
        <div class="timestamp">
            Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML
    html_path = output_dir / "dashboard.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return html_path


async def main():
    """Main test runner"""
    
    print("\n🚀 Starting Railway SVG Template Comprehensive Test...\n")
    
    # Run tests
    results, output_dir = await run_svg_tests()
    
    # Save results JSON
    results_path = output_dir / "test_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "successful": sum(1 for r in results if r.get("success")),
            "failed": sum(1 for r in results if not r.get("success")),
            "results": results
        }, f, indent=2)
    
    # Generate dashboard
    dashboard_path = generate_dashboard(results, output_dir)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    total = len(results)
    successful = sum(1 for r in results if r.get("success"))
    failed = total - successful
    
    print(f"Total Tests: {total}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    if total > 0:
        print(f"Success Rate: {(successful/total*100):.1f}%")
    else:
        print("Success Rate: N/A (no tests completed)")
    
    if successful > 0:
        response_times = [r.get("response_time", 0) for r in results if r.get("success")]
        print(f"Avg Response Time: {sum(response_times)/len(response_times):.2f}s")
    
    print(f"\n📁 Output Directory: {output_dir}")
    print(f"📄 Results JSON: {results_path}")
    print(f"🌐 Dashboard: {dashboard_path}")
    
    return output_dir


if __name__ == "__main__":
    output = asyncio.run(main())
    print(f"\n✨ Test complete! Open dashboard: {output}/dashboard.html")