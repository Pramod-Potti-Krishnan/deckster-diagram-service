#!/usr/bin/env python3
"""
Final Railway Mermaid Test - All 7 Types
=========================================
Quick test of all Mermaid diagram types with the latest fixes.
"""

import asyncio
import json
import websockets
import ssl
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

async def test_single_diagram(
    session_id: str,
    diagram_type: str,
    content: str,
    description: str
) -> Dict[str, Any]:
    """Test a single Mermaid diagram"""
    
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
                        "secondaryColor": "#60A5FA"
                    }
                }
            }
            
            await ws.send(json.dumps(request))
            
            # Get response with timeout
            data = None
            timeout = 15  # 15 seconds for all types
            
            # Keep reading messages until we get the final response
            for i in range(10):
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=timeout)
                    msg = json.loads(response)
                    
                    # Skip status updates
                    if msg.get("type") == "status_update":
                        continue
                    
                    if msg.get("type") == "diagram_response":
                        data = msg
                        break
                    elif msg.get("type") == "error_response":
                        data = msg
                        break
                except asyncio.TimeoutError:
                    if i == 9:  # Last attempt
                        print(f" (timeout after {i+1} attempts)")
                    continue
            
            elapsed = time.time() - start_time
            
            if data and data.get("type") == "diagram_response":
                payload = data.get("payload", {})
                metadata = payload.get("metadata", {})
                
                return {
                    "type": diagram_type,
                    "description": description,
                    "success": True,
                    "has_mermaid": "mermaid_code" in metadata,
                    "has_svg": payload.get("content", "").startswith("<svg"),
                    "elapsed_time": elapsed
                }
            else:
                error_msg = "Unknown error"
                if data and data.get("type") == "error_response":
                    error_msg = data.get("payload", {}).get("error_message", "Unknown error")
                    
                return {
                    "type": diagram_type,
                    "description": description,
                    "success": False,
                    "error": error_msg,
                    "elapsed_time": elapsed
                }
                    
    except Exception as e:
        return {
            "type": diagram_type,
            "description": description,
            "success": False,
            "error": str(e),
            "elapsed_time": 0
        }

async def run_all_tests():
    """Run tests for all 7 Mermaid types"""
    
    print(f"{Colors.BOLD}🚀 Railway Mermaid Test - All 7 Types{Colors.RESET}")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Service: deckster-diagram-service-production.up.railway.app")
    print()
    
    # All 7 Mermaid diagram types
    test_cases = [
        {
            "type": "flowchart",
            "content": "Create a simple flowchart: Start -> Process -> Decision -> End",
            "description": "Flowchart"
        },
        {
            "type": "erDiagram",
            "content": "Create an ER diagram with User and Order entities",
            "description": "ER Diagram"
        },
        {
            "type": "journey",
            "content": "Customer journey: Browse -> Add to Cart -> Checkout -> Confirm",
            "description": "User Journey"
        },
        {
            "type": "gantt",
            "content": "Project timeline: Planning (Week 1), Design (Week 2-3), Development (Week 4-6), Testing (Week 7)",
            "description": "Gantt Chart"
        },
        {
            "type": "quadrantChart",
            "content": "Priority matrix with 4 items in different quadrants",
            "description": "Quadrant Chart"
        },
        {
            "type": "timeline",
            "content": "Company milestones: 2020 Founded, 2021 First Product, 2022 Funding, 2023 Expansion",
            "description": "Timeline"
        },
        {
            "type": "kanban",
            "content": "Development board: Backlog (2 items), In Progress (2 items), Done (2 items)",
            "description": "Kanban Board"
        }
    ]
    
    session_id = f"final-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results = []
    
    # Test each type
    for i, test_case in enumerate(test_cases, 1):
        print(f"{Colors.BLUE}[{i}/7] Testing {test_case['description']}...{Colors.RESET}", end=" ")
        
        result = await test_single_diagram(
            session_id,
            test_case["type"],
            test_case["content"],
            test_case["description"]
        )
        
        results.append(result)
        
        if result["success"]:
            print(f"{Colors.GREEN}✅ ({result['elapsed_time']:.1f}s){Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ {result.get('error', 'Failed')}{Colors.RESET}")
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    return results

def save_results(results):
    """Save results to HTML file"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(f"railway_final_test_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    
    # Calculate stats
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Railway Mermaid Test Results</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f7fa;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a202c;
            border-bottom: 3px solid #3B82F6;
            padding-bottom: 10px;
        }}
        .summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }}
        .summary h2 {{
            margin: 0;
            font-size: 2.5em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            background: #f3f4f6;
            font-weight: 600;
        }}
        .success {{
            color: #10b981;
            font-weight: 600;
        }}
        .failed {{
            color: #ef4444;
            font-weight: 600;
        }}
        .time {{
            color: #6b7280;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Railway Mermaid Test Results</h1>
        
        <div class="summary">
            <h2>{successful}/{total}</h2>
            <p>Diagrams Generated Successfully</p>
            <p>{(successful/total*100):.0f}% Success Rate</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Diagram Type</th>
                    <th>Status</th>
                    <th>Time</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for result in results:
        status_class = "success" if result["success"] else "failed"
        status_text = "✅ Success" if result["success"] else "❌ Failed"
        time_text = f"{result.get('elapsed_time', 0):.1f}s" if result["success"] else "-"
        
        details = ""
        if result["success"]:
            if result.get("has_mermaid"):
                details += "📝 Mermaid "
            if result.get("has_svg"):
                details += "🎨 SVG"
        else:
            details = result.get("error", "Unknown error")
        
        html_content += f"""
                <tr>
                    <td><strong>{result['description']}</strong></td>
                    <td class="{status_class}">{status_text}</td>
                    <td class="time">{time_text}</td>
                    <td>{details}</td>
                </tr>
"""
    
    html_content += """
            </tbody>
        </table>
        
        <p style="margin-top: 30px; color: #6b7280; text-align: center;">
            Generated at {timestamp}
        </p>
    </div>
</body>
</html>
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Save HTML
    html_file = output_dir / "results.html"
    html_file.write_text(html_content)
    
    return str(html_file)

async def main():
    """Main entry point"""
    
    # Run tests
    results = await run_all_tests()
    
    # Save results
    html_file = save_results(results)
    
    # Print summary
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}SUMMARY{Colors.RESET}")
    print(f"Success Rate: {successful}/{total} ({(successful/total)*100:.0f}%)")
    
    if successful == total:
        print(f"{Colors.GREEN}🎉 All diagrams generated successfully!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠️ Some diagrams failed:{Colors.RESET}")
        for r in results:
            if not r["success"]:
                print(f"  - {r['description']}: {r.get('error')}")
    
    print(f"\n📁 Results saved to: {html_file}")
    print(f"Open in browser: file://{html_file}")

if __name__ == "__main__":
    asyncio.run(main())