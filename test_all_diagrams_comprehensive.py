#!/usr/bin/env python3
"""
Comprehensive Test - All Mermaid and SVG Diagrams
==================================================
Tests all supported diagram types from Railway API.
"""

import asyncio
import json
import websockets
import ssl
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

async def test_diagram(
    session_id: str,
    diagram_type: str,
    content: str,
    description: str,
    category: str
) -> Dict[str, Any]:
    """Test a single diagram generation"""
    
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    full_url = f"{url}?session_id={session_id}&user_id=test"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        start_time = time.time()
        
        async with websockets.connect(full_url, ssl=ssl_context, ping_timeout=20) as ws:
            # Skip welcome message
            await ws.recv()
            
            # Send diagram request
            request = {
                "type": "diagram_request",
                "correlation_id": f"test-{diagram_type}",
                "data": {
                    "diagram_type": diagram_type,
                    "content": content,
                    "theme": {
                        "primaryColor": "#3B82F6",
                        "secondaryColor": "#60A5FA",
                        "accentColor": "#8B5CF6"
                    }
                }
            }
            
            await ws.send(json.dumps(request))
            
            # Get response
            data = None
            timeout = 20 if diagram_type == "gantt" else 15
            
            for i in range(10):
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=timeout)
                    msg = json.loads(response)
                    
                    if msg.get("type") == "status_update":
                        continue
                    
                    if msg.get("type") == "diagram_response":
                        data = msg
                        break
                    elif msg.get("type") == "error_response":
                        data = msg
                        break
                except asyncio.TimeoutError:
                    continue
            
            elapsed = time.time() - start_time
            
            if data and data.get("type") == "diagram_response":
                payload = data.get("payload", {})
                metadata = payload.get("metadata", {})
                
                result = {
                    "type": diagram_type,
                    "description": description,
                    "category": category,
                    "success": True,
                    "content": payload.get("content", ""),
                    "content_type": payload.get("content_type", ""),
                    "mermaid_code": metadata.get("mermaid_code"),
                    "elapsed_time": elapsed
                }
                
                # Determine if it's SVG or Mermaid
                if payload.get("content", "").startswith("<svg"):
                    result["is_svg"] = True
                    result["is_mermaid"] = "mermaid_code" in metadata
                else:
                    result["is_svg"] = False
                    result["is_mermaid"] = True
                
                return result
            else:
                error_msg = "Unknown error"
                if data and data.get("type") == "error_response":
                    error_msg = data.get("payload", {}).get("error_message", "Unknown error")
                
                return {
                    "type": diagram_type,
                    "description": description,
                    "category": category,
                    "success": False,
                    "error": error_msg,
                    "elapsed_time": elapsed
                }
                
    except Exception as e:
        return {
            "type": diagram_type,
            "description": description,
            "category": category,
            "success": False,
            "error": str(e),
            "elapsed_time": 0
        }

async def run_all_tests():
    """Run tests for all diagram types"""
    
    print(f"{Colors.BOLD}🚀 Comprehensive Diagram Test - All Types{Colors.RESET}")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Service: deckster-diagram-service-production.up.railway.app")
    print()
    
    # All diagram types - Mermaid and SVG
    test_cases = [
        # === MERMAID DIAGRAMS ===
        {
            "type": "flowchart",
            "content": "Create a user authentication flow: Login -> Validate Credentials -> Success: Dashboard, Failure: Error Message -> Retry",
            "description": "User Authentication Flow",
            "category": "Mermaid"
        },
        {
            "type": "erDiagram",
            "content": "Create database schema for e-commerce: Customer (id, name, email), Product (id, name, price, stock), Order (id, customer_id, date, total), OrderItem (order_id, product_id, quantity, price)",
            "description": "E-commerce Database Schema",
            "category": "Mermaid"
        },
        {
            "type": "journey",
            "content": "Customer support journey: Contact Support (3/5), Wait in Queue (2/5), Talk to Agent (4/5), Problem Resolved (5/5), Follow-up Survey (4/5)",
            "description": "Customer Support Journey",
            "category": "Mermaid"
        },
        {
            "type": "gantt",
            "content": "Q1 2024 Product Launch: January: Market Research and Planning, February: Design and Prototyping, March: Development Sprint 1, April: Development Sprint 2, May: Testing and QA, June: Launch Preparation and Go-Live",
            "description": "Product Launch Timeline",
            "category": "Mermaid"
        },
        {
            "type": "quadrantChart",
            "content": "Feature Priority Matrix. X-axis: Business Value (Low to High). Y-axis: Technical Complexity (Low to High). Features: AI Chat (high value, high complexity), Dark Mode (low value, low complexity), API v2 (high value, medium complexity), Code Refactor (medium value, high complexity)",
            "description": "Feature Priority Matrix",
            "category": "Mermaid"
        },
        {
            "type": "timeline",
            "content": "Startup Journey: 2019: Idea Conception, 2020: MVP Development, 2021: Seed Funding $500k, 2022: Product Launch, 2023: Series A $5M, 2024: International Expansion",
            "description": "Startup Growth Timeline",
            "category": "Mermaid"
        },
        {
            "type": "kanban",
            "content": "Sprint Board: Backlog (User Auth, Payment Integration, Analytics), In Progress (API Development, UI Redesign), Code Review (Database Optimization), Testing (Mobile App), Done (Landing Page, Documentation)",
            "description": "Development Sprint Board",
            "category": "Mermaid"
        },
        
        # === SVG DIAGRAMS ===
        {
            "type": "pyramid",
            "content": "Maslow's Hierarchy: Self-Actualization (achieving potential), Esteem (respect and recognition), Love and Belonging (relationships), Safety (security and health), Physiological (food and shelter)",
            "description": "Maslow's Hierarchy Pyramid",
            "category": "SVG"
        },
        {
            "type": "funnel",
            "content": "Sales Funnel: Website Visitors (10,000), Leads (2,000), Qualified Leads (500), Opportunities (100), Customers (25)",
            "description": "Sales Conversion Funnel",
            "category": "SVG"
        },
        {
            "type": "cycle",
            "content": "Software Development Lifecycle: Planning -> Design -> Development -> Testing -> Deployment -> Maintenance",
            "description": "SDLC Cycle",
            "category": "SVG"
        },
        {
            "type": "venn",
            "content": "Skills Overlap: Frontend (React, CSS, JavaScript), Backend (Python, Django, PostgreSQL), Overlap (API Design, Git, Testing)",
            "description": "Full-Stack Skills Venn",
            "category": "SVG"
        },
        {
            "type": "matrix",
            "content": "SWOT Analysis: Strengths (Strong Team, Good Funding), Weaknesses (Limited Marketing, Tech Debt), Opportunities (Growing Market, AI Integration), Threats (Competition, Economic Downturn)",
            "description": "SWOT Analysis Matrix",
            "category": "SVG"
        },
        {
            "type": "honeycomb",
            "content": "Core Values: Innovation, Integrity, Collaboration, Excellence, Customer Focus, Sustainability, Diversity",
            "description": "Company Core Values",
            "category": "SVG"
        },
        {
            "type": "hub_spoke",
            "content": "Microservices Architecture: API Gateway (center), Services: Auth Service, User Service, Payment Service, Notification Service, Analytics Service, Storage Service",
            "description": "Microservices Architecture",
            "category": "SVG"
        },
        {
            "type": "fishbone",
            "content": "Website Slow Performance: People (Lack of Training), Process (No Optimization), Technology (Old Servers, Unoptimized Code), Environment (High Traffic, Network Issues)",
            "description": "Performance Issue Analysis",
            "category": "SVG"
        },
        {
            "type": "roadmap",
            "content": "2024 Product Roadmap: Q1 (Core Features, Bug Fixes), Q2 (Mobile App, API v2), Q3 (AI Features, Analytics), Q4 (Enterprise Features, Scale)",
            "description": "Annual Product Roadmap",
            "category": "SVG"
        },
        {
            "type": "process_flow",
            "content": "Order Processing: Receive Order -> Validate Payment -> Check Inventory -> Pack Items -> Ship -> Send Tracking -> Deliver",
            "description": "Order Fulfillment Process",
            "category": "SVG"
        },
        {
            "type": "gears",
            "content": "System Components: Frontend (User Interface), Backend (Business Logic), Database (Data Storage)",
            "description": "System Architecture Gears",
            "category": "SVG"
        }
    ]
    
    session_id = f"comprehensive-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results = []
    
    # Test each diagram
    mermaid_count = sum(1 for tc in test_cases if tc["category"] == "Mermaid")
    svg_count = sum(1 for tc in test_cases if tc["category"] == "SVG")
    
    print(f"Testing {len(test_cases)} diagrams: {mermaid_count} Mermaid, {svg_count} SVG")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        category_color = Colors.BLUE if test_case["category"] == "Mermaid" else Colors.YELLOW
        print(f"{category_color}[{i}/{len(test_cases)}] {test_case['category']}: {test_case['description']}{Colors.RESET}", end=" ")
        
        result = await test_diagram(
            session_id,
            test_case["type"],
            test_case["content"],
            test_case["description"],
            test_case["category"]
        )
        
        results.append(result)
        
        if result["success"]:
            print(f"{Colors.GREEN}✅ ({result['elapsed_time']:.1f}s){Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ {result.get('error', 'Failed')}{Colors.RESET}")
        
        await asyncio.sleep(0.5)
    
    return results

def create_comprehensive_viewer(results: List[Dict[str, Any]]) -> str:
    """Create HTML viewer with all diagrams"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(f"comprehensive_test_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    
    # Calculate statistics
    mermaid_results = [r for r in results if r["category"] == "Mermaid"]
    svg_results = [r for r in results if r["category"] == "SVG"]
    
    mermaid_success = sum(1 for r in mermaid_results if r["success"])
    svg_success = sum(1 for r in svg_results if r["success"])
    
    html_content = create_html_content(results, mermaid_success, svg_success, len(mermaid_results), len(svg_results))
    
    # Save HTML file
    html_file = output_dir / "all_diagrams.html"
    html_file.write_text(html_content)
    
    return str(html_file)

def create_html_content(results, mermaid_success, svg_success, mermaid_total, svg_total):
    """Generate the HTML content"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Diagrams - Mermaid & SVG Comprehensive Test</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        {get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Comprehensive Diagram Test Results</h1>
        <p class="subtitle">All Mermaid and SVG diagram types from Railway API</p>
        
        {get_stats_section(mermaid_success, svg_success, mermaid_total, svg_total)}
        
        {get_mermaid_section(results)}
        
        {get_svg_section(results)}
        
        <div class="footer">
            <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Using Mermaid v11 with optimized theme from Visualization Guide</p>
        </div>
    </div>
    
    <script>
        {get_mermaid_config()}
    </script>
</body>
</html>"""

def get_css_styles():
    """Return CSS styles"""
    return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        h1 {
            color: white;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            color: white;
            text-align: center;
            font-size: 1.2em;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #1f2937;
        }
        
        .stat-label {
            color: #6b7280;
            margin-top: 5px;
        }
        
        .section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 3px solid #3B82F6;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 1.8em;
            color: #1f2937;
            font-weight: bold;
        }
        
        .badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            color: white;
        }
        
        .badge.mermaid {
            background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
        }
        
        .badge.svg {
            background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
        }
        
        .diagrams-grid {
            display: grid;
            gap: 30px;
        }
        
        .diagram-card {
            background: #f9fafb;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e5e7eb;
        }
        
        .diagram-header {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            padding: 15px 20px;
            border-bottom: 1px solid #d1d5db;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .diagram-title {
            font-weight: 600;
            color: #1f2937;
        }
        
        .diagram-type {
            font-size: 0.85em;
            color: #6b7280;
            background: white;
            padding: 4px 8px;
            border-radius: 4px;
        }
        
        .diagram-content {
            padding: 30px;
            background: white;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow-x: auto;
        }
        
        .mermaid-wrapper, .svg-wrapper {
            width: 100%;
        }
        
        .mermaid {
            display: flex;
            justify-content: center;
        }
        
        .gantt-wrapper .mermaid {
            min-width: 900px;
        }
        
        .svg-wrapper svg {
            max-width: 100%;
            height: auto;
        }
        
        .error-box {
            background: #fee2e2;
            color: #991b1b;
            padding: 20px;
            border-radius: 6px;
            border: 1px solid #fca5a5;
        }
        
        .performance-info {
            background: #f0f9ff;
            padding: 10px 15px;
            border-top: 1px solid #e0f2fe;
            color: #0369a1;
            font-size: 0.9em;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
        }
        
        .footer p {
            margin: 5px 0;
            opacity: 0.9;
        }
    """

def get_stats_section(mermaid_success, svg_success, mermaid_total, svg_total):
    """Generate statistics section"""
    total_success = mermaid_success + svg_success
    total = mermaid_total + svg_total
    
    return f"""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-value">{total_success}/{total}</div>
                <div class="stat-label">Total Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{mermaid_success}/{mermaid_total}</div>
                <div class="stat-label">Mermaid Diagrams</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{svg_success}/{svg_total}</div>
                <div class="stat-label">SVG Diagrams</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{(total_success/total*100):.0f}%</div>
                <div class="stat-label">Overall Success</div>
            </div>
        </div>
    """

def get_mermaid_section(results):
    """Generate Mermaid diagrams section"""
    mermaid_results = [r for r in results if r["category"] == "Mermaid"]
    
    content = """
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">📊 Mermaid Diagrams</h2>
                <span class="badge mermaid">Rendered with v11</span>
            </div>
            <div class="diagrams-grid">
    """
    
    for result in mermaid_results:
        wrapper_class = "gantt-wrapper" if result["type"] == "gantt" else "mermaid-wrapper"
        
        if result["success"] and result.get("mermaid_code"):
            content += f"""
                <div class="diagram-card {wrapper_class}">
                    <div class="diagram-header">
                        <span class="diagram-title">{result['description']}</span>
                        <span class="diagram-type">{result['type']}</span>
                    </div>
                    <div class="diagram-content">
                        <div class="{wrapper_class}">
                            <div class="mermaid">
{result['mermaid_code']}
                            </div>
                        </div>
                    </div>
                    <div class="performance-info">
                        ⚡ Generated in {result['elapsed_time']:.2f}s
                    </div>
                </div>
            """
        elif result["success"] and result.get("content", "").startswith("<svg"):
            # Fallback to SVG if available
            content += f"""
                <div class="diagram-card">
                    <div class="diagram-header">
                        <span class="diagram-title">{result['description']}</span>
                        <span class="diagram-type">{result['type']} (SVG)</span>
                    </div>
                    <div class="diagram-content">
                        <div class="svg-wrapper">
                            {result['content']}
                        </div>
                    </div>
                    <div class="performance-info">
                        ⚡ Generated in {result['elapsed_time']:.2f}s
                    </div>
                </div>
            """
        else:
            content += f"""
                <div class="diagram-card">
                    <div class="diagram-header">
                        <span class="diagram-title">{result['description']}</span>
                        <span class="diagram-type">{result['type']}</span>
                    </div>
                    <div class="diagram-content">
                        <div class="error-box">
                            ❌ Generation failed: {result.get('error', 'Unknown error')}
                        </div>
                    </div>
                </div>
            """
    
    content += """
            </div>
        </div>
    """
    
    return content

def get_svg_section(results):
    """Generate SVG diagrams section"""
    svg_results = [r for r in results if r["category"] == "SVG"]
    
    content = """
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">🎨 SVG Diagrams</h2>
                <span class="badge svg">Template-based</span>
            </div>
            <div class="diagrams-grid">
    """
    
    for result in svg_results:
        if result["success"]:
            content += f"""
                <div class="diagram-card">
                    <div class="diagram-header">
                        <span class="diagram-title">{result['description']}</span>
                        <span class="diagram-type">{result['type']}</span>
                    </div>
                    <div class="diagram-content">
                        <div class="svg-wrapper">
                            {result.get('content', '')}
                        </div>
                    </div>
                    <div class="performance-info">
                        ⚡ Generated in {result['elapsed_time']:.2f}s
                    </div>
                </div>
            """
        else:
            content += f"""
                <div class="diagram-card">
                    <div class="diagram-header">
                        <span class="diagram-title">{result['description']}</span>
                        <span class="diagram-type">{result['type']}</span>
                    </div>
                    <div class="diagram-content">
                        <div class="error-box">
                            ❌ Generation failed: {result.get('error', 'Unknown error')}
                        </div>
                    </div>
                </div>
            """
    
    content += """
            </div>
        </div>
    """
    
    return content

def get_mermaid_config():
    """Return optimized Mermaid configuration based on Visualization Guide"""
    return """
        // Optimized Mermaid configuration from Visualization Guide
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            },
            gantt: {
                useMaxWidth: true,
                numberSectionStyles: 4,
                fontSize: 12,
                topAxis: true,
                gridLineStartPadding: 350,
                leftPadding: 200,
                sectionFontSize: 14
            },
            journey: {
                useMaxWidth: true,
                leftMargin: 100
            },
            er: {
                useMaxWidth: true,
                layoutDirection: 'TB'
            },
            quadrantChart: {
                useMaxWidth: true
            },
            timeline: {
                useMaxWidth: true
            },
            themeVariables: {
                // Primary colors
                primaryColor: '#3B82F6',
                primaryTextColor: '#1f2937',
                primaryBorderColor: '#2563EB',
                lineColor: '#6b7280',
                secondaryColor: '#60A5FA',
                tertiaryColor: '#DBEAFE',
                
                // Task backgrounds for Gantt
                critBkgColor: '#ef4444',
                critBorderColor: '#dc2626',
                doneTaskBkgColor: '#9ca3af',
                doneTaskBorderColor: '#6b7280',
                activeTaskBkgColor: '#3B82F6',
                activeTaskBorderColor: '#2563EB',
                taskBkgColor: '#f3f4f6',
                taskBorderColor: '#9ca3af',
                
                // Text colors - Critical for readability
                taskTextColor: '#1f2937',
                taskTextDarkColor: '#ffffff',
                taskTextOutsideColor: '#1f2937',
                doneTaskTextColor: '#1f2937',
                activeTaskTextColor: '#ffffff',
                critTaskTextColor: '#ffffff',
                
                // Grid and timeline
                gridColor: '#9ca3af',
                todayLineColor: '#ef4444',
                excludeBkgColor: '#fafafa',
                
                // General text and colors
                textColor: '#1f2937',
                titleColor: '#1f2937',
                labelColor: '#1f2937',
                errorBkgColor: '#fecaca',
                errorTextColor: '#991b1b'
            }
        });
        
        // Force re-render after load
        setTimeout(() => {
            mermaid.init();
        }, 100);
    """

async def main():
    """Main entry point"""
    
    # Run all tests
    results = await run_all_tests()
    
    # Create HTML viewer
    html_file = create_comprehensive_viewer(results)
    
    # Print summary
    mermaid_results = [r for r in results if r["category"] == "Mermaid"]
    svg_results = [r for r in results if r["category"] == "SVG"]
    
    mermaid_success = sum(1 for r in mermaid_results if r["success"])
    svg_success = sum(1 for r in svg_results if r["success"])
    
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}FINAL SUMMARY{Colors.RESET}")
    print(f"Mermaid: {mermaid_success}/{len(mermaid_results)} successful")
    print(f"SVG: {svg_success}/{len(svg_results)} successful")
    print(f"Overall: {mermaid_success + svg_success}/{len(results)} ({((mermaid_success + svg_success)/len(results)*100):.0f}%)")
    
    if (mermaid_success + svg_success) == len(results):
        print(f"{Colors.GREEN}🎉 All diagrams generated successfully!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Failed diagrams:{Colors.RESET}")
        for r in results:
            if not r["success"]:
                print(f"  - {r['description']} ({r['type']}): {r.get('error')}")
    
    print(f"\n📁 Results saved to: {html_file}")
    print(f"Open in browser: file://{html_file}")

if __name__ == "__main__":
    asyncio.run(main())