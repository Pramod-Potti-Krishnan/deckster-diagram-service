#!/usr/bin/env python3
"""
Quick Railway test with 3 diagrams for demonstration
"""

import asyncio
import json
import websockets
import ssl
from datetime import datetime
from pathlib import Path
import webbrowser

# Quick test with 3 diagram types
TEST_CASES = [
    {
        "name": "User Login Flow",
        "diagram_type": "flowchart",
        "content": "User login process: User enters credentials -> System validates -> If valid, generate token -> Set session -> Redirect to dashboard. If invalid, show error -> Return to login"
    },
    {
        "name": "System Classes",
        "diagram_type": "class_diagram", 
        "content": "User class with properties: id, name, email and methods: login(), logout(). Product class with: id, name, price. User has many Products."
    },
    {
        "name": "Project Timeline",
        "diagram_type": "gantt",
        "content": "Project: Week 1-2: Planning, Week 3-4: Design, Week 5-6: Development, Week 7: Testing, Week 8: Deployment"
    }
]

async def test_diagram(test_case, index):
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = f"quick-test-{index}"
    full_url = f"{url}?session_id={session_id}&user_id=test"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    result = {
        "name": test_case["name"],
        "diagram_type": test_case["diagram_type"],
        "success": False,
        "mermaid_code": None,
        "output_type": None,
        "metadata": {}
    }
    
    try:
        async with websockets.connect(full_url, ssl=ssl_context) as ws:
            await ws.recv()  # Welcome
            
            request = {
                "type": "diagram_request",
                "correlation_id": f"test-{index}",
                "data": {
                    "diagram_type": test_case["diagram_type"],
                    "content": test_case["content"],
                    "theme": {"primaryColor": "#3B82F6"}
                }
            }
            
            await ws.send(json.dumps(request))
            
            for _ in range(5):
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "diagram_response":
                        payload = data.get("payload", {})
                        result["success"] = True
                        result["output_type"] = payload.get("output_type", "unknown")
                        
                        if payload.get("mermaid"):
                            result["mermaid_code"] = payload["mermaid"].get("code")
                        elif payload.get("metadata", {}).get("mermaid_code"):
                            result["mermaid_code"] = payload["metadata"]["mermaid_code"]
                        
                        result["metadata"] = payload.get("metadata", {})
                        break
                except asyncio.TimeoutError:
                    break
    except Exception as e:
        result["error"] = str(e)
    
    return result

def create_html(results):
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Railway Mermaid Test</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; text-align: center; }}
        .diagram {{ background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #3B82F6; }}
        .title {{ font-size: 1.2em; font-weight: bold; }}
        .type {{ background: #3B82F6; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; }}
        .content {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .code {{ background: #1f2937; color: #e5e7eb; padding: 15px; border-radius: 4px; overflow: auto; }}
        .code pre {{ margin: 0; font-size: 0.9em; white-space: pre-wrap; }}
        .render {{ background: #f9fafb; padding: 20px; border-radius: 4px; min-height: 300px; display: flex; align-items: center; justify-content: center; }}
        .mermaid {{ max-width: 100%; }}
        .error {{ color: red; text-align: center; padding: 20px; }}
        .success {{ color: green; }}
        .failed {{ color: red; }}
    </style>
</head>
<body>
    <h1>🎨 Railway Mermaid Test Results</h1>
"""
    
    for i, r in enumerate(results, 1):
        status = "✅" if r["success"] else "❌"
        html += f"""
    <div class="diagram">
        <div class="header">
            <span class="title">{i}. {r['name']} {status}</span>
            <span class="type">{r['diagram_type']}</span>
        </div>
        <div class="content">
            <div class="code">
                <h3 style="color: white; margin-top: 0;">Mermaid Code:</h3>
                <pre>{r.get('mermaid_code', 'No code generated')}</pre>
            </div>
            <div class="render">
"""
        
        if r.get("mermaid_code"):
            html += f"""
                <div class="mermaid">
{r['mermaid_code']}
                </div>
"""
        else:
            html += '<div class="error">No diagram to render</div>'
        
        html += """
            </div>
        </div>
    </div>
"""
    
    html += """
    <script>mermaid.initialize({ startOnLoad: true });</script>
</body>
</html>
"""
    
    output_dir = Path(f"railway_quick_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_dir.mkdir(exist_ok=True)
    html_path = output_dir / "results.html"
    
    with open(html_path, 'w') as f:
        f.write(html)
    
    return str(html_path.absolute())

async def main():
    print("\n🚀 Quick Railway Mermaid Test")
    print("=" * 50)
    
    results = []
    for i, test in enumerate(TEST_CASES, 1):
        print(f"[{i}/3] Testing {test['name']}...")
        result = await test_diagram(test, i)
        results.append(result)
        print(f"  {'✅' if result['success'] else '❌'} {result.get('output_type', 'failed')}")
    
    html_path = create_html(results)
    print(f"\n📄 Opening results: {html_path}")
    webbrowser.open(f'file://{html_path}')
    
    print("\n✨ Test complete! Check your browser for visual results.")

if __name__ == "__main__":
    asyncio.run(main())