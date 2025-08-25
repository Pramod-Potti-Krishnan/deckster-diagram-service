#!/usr/bin/env python3
"""
Test All 7 Mermaid Diagram Types with New Playbook
==================================================

Tests the refactored Mermaid generation with complete examples.
"""

import asyncio
import json
import websockets
import ssl
from datetime import datetime
from pathlib import Path
import webbrowser
import time

# Test cases for all 7 Mermaid types using CORRECT names
MERMAID_V3_TEST_CASES = [
    {
        "name": "Authentication Flowchart",
        "diagram_type": "flowchart",  # Correct Mermaid name
        "content": """Create a user authentication flow:
        User enters credentials -> Validate email format -> 
        Check user exists in database -> Verify password -> 
        If valid: Generate JWT token and redirect to dashboard
        If invalid: Show error and return to login"""
    },
    {
        "name": "E-commerce Database",
        "diagram_type": "erDiagram",  # Correct Mermaid name (was entity_relationship)
        "content": """Design database for online store:
        Customer entity: id, name, email, registration_date
        Product entity: id, name, price, stock
        Order entity: id, customer_id, order_date, total
        OrderItem entity: id, order_id, product_id, quantity
        
        Relationships:
        - Customer places many Orders
        - Order contains many OrderItems
        - Product appears in many OrderItems"""
    },
    {
        "name": "Shopping Journey",
        "diagram_type": "journey",  # Correct Mermaid name (was user_journey)
        "content": """Customer shopping experience:
        Browse products (satisfaction: 4)
        Search for specific item (satisfaction: 5)
        Add to cart (satisfaction: 4)
        Apply discount code (satisfaction: 2 - hard to find)
        Checkout process (satisfaction: 3 - too many steps)
        Receive confirmation (satisfaction: 5)
        Track delivery (satisfaction: 4)
        Receive product (satisfaction: 5)"""
    },
    {
        "name": "Project Development",
        "diagram_type": "gantt",  # Correct Mermaid name
        "content": """Software project timeline:
        Week 1-2: Requirements gathering and analysis
        Week 2-3: System design and architecture
        Week 3-5: Backend development
        Week 4-6: Frontend development
        Week 6-7: Integration and testing
        Week 7-8: Bug fixes and optimization
        Week 8: Deployment and go-live"""
    },
    {
        "name": "Risk Matrix",
        "diagram_type": "quadrantChart",  # Correct Mermaid name (was quadrant)
        "content": """Project risk assessment:
        High Impact, High Probability: Data breach, Budget overrun
        High Impact, Low Probability: Natural disaster, Total system failure
        Low Impact, High Probability: Minor bugs, Documentation delays
        Low Impact, Low Probability: Printer failure, Coffee shortage
        
        Plot risks based on their impact (0-1) and probability (0-1)"""
    },
    {
        "name": "Company History",
        "diagram_type": "timeline",  # Correct Mermaid name
        "content": """Tech startup evolution:
        2019: Company founded by 2 engineers
        2020 Q1: First prototype launched
        2020 Q3: Seed funding of $1M
        2021: Reached 10,000 users
        2022 Q2: Series A funding of $10M
        2022 Q4: International expansion
        2023: Reached 100,000 users
        2024: IPO announcement"""
    },
    {
        "name": "Sprint Board",
        "diagram_type": "kanban",  # Correct Mermaid name
        "content": """Current sprint tasks:
        
        Backlog:
        - Research new features (assigned: Alice)
        - Update documentation (assigned: Bob)
        
        In Progress:
        - Fix login bug (assigned: Charlie, priority: high)
        - Implement API endpoint (assigned: David)
        
        Testing:
        - User registration flow (assigned: Eve)
        
        Done:
        - Database migration
        - Setup CI/CD pipeline"""
    }
]


async def test_diagram(test_case: dict, index: int) -> dict:
    """Test a single diagram generation"""
    
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = f"mermaid-v3-test-{datetime.now().timestamp()}-{index}"
    full_url = f"{url}?session_id={session_id}&user_id=test-v3"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    result = {
        "name": test_case["name"],
        "diagram_type": test_case["diagram_type"],
        "success": False,
        "mermaid_code": None,
        "error": None,
        "response_time": 0,
        "metadata": {}
    }
    
    start_time = time.time()
    
    try:
        async with websockets.connect(full_url, ssl=ssl_context, ping_timeout=30) as ws:
            # Skip welcome
            await ws.recv()
            
            # Send request
            request = {
                "type": "diagram_request",
                "correlation_id": f"v3-test-{index}",
                "data": {
                    "diagram_type": test_case["diagram_type"],
                    "content": test_case["content"],
                    "theme": {
                        "primaryColor": "#3B82F6",
                        "backgroundColor": "#ffffff"
                    }
                }
            }
            
            await ws.send(json.dumps(request))
            
            # Wait for response
            for _ in range(3):
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=20.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "diagram_response":
                        payload = data.get("payload", {})
                        result["success"] = True
                        
                        # Extract Mermaid code
                        if payload.get("mermaid"):
                            result["mermaid_code"] = payload["mermaid"].get("code")
                        elif payload.get("metadata", {}).get("mermaid_code"):
                            result["mermaid_code"] = payload["metadata"]["mermaid_code"]
                        
                        result["metadata"] = payload.get("metadata", {})
                        result["output_type"] = payload.get("output_type")
                        break
                        
                    elif data.get("type") == "error_response":
                        result["error"] = data.get("payload", {}).get("error_message")
                        break
                        
                except asyncio.TimeoutError:
                    result["error"] = "Timeout"
                    break
                    
    except Exception as e:
        result["error"] = str(e)
    
    result["response_time"] = round((time.time() - start_time) * 1000)
    return result


def create_html_report(results: list) -> str:
    """Create HTML report with rendered diagrams"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    successful = sum(1 for r in results if r["success"])
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Mermaid V3 Test Results</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            margin: 0;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        h1 {{
            text-align: center;
            color: #1f2937;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            text-align: center;
            color: #6b7280;
            margin-bottom: 30px;
        }}
        
        .summary {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 40px;
            padding: 20px;
            background: #f9fafb;
            border-radius: 12px;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #3b82f6;
        }}
        
        .stat-label {{
            color: #6b7280;
            margin-top: 5px;
        }}
        
        .results {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
        }}
        
        .diagram-card {{
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .card-header {{
            background: #f9fafb;
            padding: 15px 20px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .card-title {{
            font-weight: 600;
            color: #1f2937;
        }}
        
        .badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge-success {{
            background: #10b981;
            color: white;
        }}
        
        .badge-error {{
            background: #ef4444;
            color: white;
        }}
        
        .badge-type {{
            background: #3b82f6;
            color: white;
            margin-left: 8px;
        }}
        
        .card-body {{
            padding: 20px;
        }}
        
        .mermaid-container {{
            background: #f9fafb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            min-height: 250px;
            overflow: auto;
        }}
        
        .code-block {{
            background: #1f2937;
            color: #e5e7eb;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.85em;
            overflow-x: auto;
            max-height: 200px;
            margin-bottom: 15px;
        }}
        
        .metadata {{
            display: flex;
            gap: 20px;
            font-size: 0.85em;
            color: #6b7280;
        }}
        
        .error-msg {{
            background: #fee2e2;
            color: #dc2626;
            padding: 10px;
            border-radius: 6px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Mermaid V3 Playbook Test Results</h1>
        <div class="subtitle">Testing all 7 Mermaid diagram types with complete examples - {timestamp}</div>
        
        <div class="summary">
            <div class="stat">
                <div class="stat-value">7</div>
                <div class="stat-label">Diagram Types</div>
            </div>
            <div class="stat">
                <div class="stat-value">{successful}</div>
                <div class="stat-label">Successful</div>
            </div>
            <div class="stat">
                <div class="stat-value">{round(successful/7*100)}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
        </div>
        
        <div class="results">
"""
    
    for result in results:
        status_badge = "badge-success" if result["success"] else "badge-error"
        status_text = "✓ Success" if result["success"] else "✗ Failed"
        
        html += f"""
            <div class="diagram-card">
                <div class="card-header">
                    <span class="card-title">{result['name']}</span>
                    <div>
                        <span class="badge {status_badge}">{status_text}</span>
                        <span class="badge badge-type">{result['diagram_type']}</span>
                    </div>
                </div>
                <div class="card-body">
"""
        
        if result["success"] and result.get("mermaid_code"):
            escaped_code = result["mermaid_code"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html += f"""
                    <div class="mermaid-container">
                        <div class="mermaid">
{result["mermaid_code"]}
                        </div>
                    </div>
                    <details>
                        <summary>View Mermaid Code</summary>
                        <pre class="code-block">{escaped_code}</pre>
                    </details>
"""
        else:
            html += f"""
                    <div class="error-msg">
                        Error: {result.get('error', 'Unknown error')}
                    </div>
"""
        
        html += f"""
                    <div class="metadata">
                        <span>Response: {result.get('response_time', 0)}ms</span>
                        <span>Type: {result.get('output_type', 'N/A')}</span>
"""
        
        if result.get("metadata", {}).get("llm_model"):
            html += f"<span>Model: {result['metadata']['llm_model']}</span>"
        
        html += """
                    </div>
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
    
    <script>
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'default',
            themeVariables: {
                primaryColor: '#3B82F6'
            }
        });
    </script>
</body>
</html>
"""
    
    # Save HTML
    output_dir = Path(f"mermaid_v3_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_dir.mkdir(exist_ok=True)
    html_path = output_dir / "results.html"
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return str(html_path.absolute())


async def main():
    """Run all tests"""
    
    print("\n" + "="*60)
    print("MERMAID V3 COMPREHENSIVE TEST")
    print("Testing with correct diagram type names and complete examples")
    print("="*60 + "\n")
    
    results = []
    
    for i, test_case in enumerate(MERMAID_V3_TEST_CASES, 1):
        print(f"[{i}/7] Testing {test_case['name']} ({test_case['diagram_type']})...")
        result = await test_diagram(test_case, i)
        results.append(result)
        
        if result["success"]:
            print(f"  ✅ Success - {result['response_time']}ms")
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown')}")
        
        # Small delay between tests
        if i < len(MERMAID_V3_TEST_CASES):
            await asyncio.sleep(2)
    
    # Generate report
    print("\nGenerating HTML report...")
    html_path = create_html_report(results)
    
    print(f"✅ Report saved: {html_path}")
    print("Opening in browser...")
    webbrowser.open(f'file://{html_path}')
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    print(f"\n{'='*60}")
    print(f"RESULTS: {successful}/7 diagrams generated successfully")
    
    if successful < 7:
        print("\nFailed diagrams:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['diagram_type']}: {r.get('error', 'Unknown')}")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())