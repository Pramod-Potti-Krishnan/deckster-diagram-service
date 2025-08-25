#!/usr/bin/env python3
"""
Mermaid Generation Demo - Visual Test
Shows actual Mermaid code generation and rendering
"""

import asyncio
import json
import websockets
import ssl
from datetime import datetime
from pathlib import Path
import webbrowser

# Focus on diagram types that are working
DEMO_CASES = [
    {
        "name": "Login Flow",
        "diagram_type": "flowchart",
        "content": "User enters email and password -> Validate credentials -> If valid: Generate JWT token -> Store in cookie -> Redirect to dashboard. If invalid: Show error -> Return to login"
    },
    {
        "name": "User Management System",
        "diagram_type": "class_diagram",
        "content": "User class with id, email, name, role. Methods: login(), logout(), updateProfile(). Role class with id, name, permissions[]. User has one Role. Permission class with id, action, resource."
    },
    {
        "name": "Customer Journey",
        "diagram_type": "user_journey",
        "content": "Customer discovers product on social media (happiness 4/5) -> Visits website (3/5) -> Compares prices (2/5) -> Reads reviews (4/5) -> Adds to cart (3/5) -> Applies discount code (5/5) -> Completes purchase (5/5) -> Receives product (5/5)"
    },
    {
        "name": "Risk Matrix",
        "diagram_type": "quadrant",
        "content": "High Impact High Probability: Data breach, Server downtime. High Impact Low Probability: Natural disaster, Total system failure. Low Impact High Probability: Minor bugs, Slow response times. Low Impact Low Probability: Printer issues, Coffee shortage"
    }
]

async def test_diagram(case, index):
    """Test single diagram generation"""
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = f"demo-{datetime.now().timestamp()}-{index}"
    full_url = f"{url}?session_id={session_id}&user_id=demo"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    result = {
        "name": case["name"],
        "diagram_type": case["diagram_type"],
        "success": False,
        "mermaid_code": None,
        "metadata": {}
    }
    
    try:
        async with websockets.connect(full_url, ssl=ssl_context) as ws:
            # Skip welcome message
            await ws.recv()
            
            # Send request
            request = {
                "type": "diagram_request",
                "correlation_id": f"demo-{index}",
                "data": {
                    "diagram_type": case["diagram_type"],
                    "content": case["content"],
                    "theme": {
                        "primaryColor": "#3B82F6",
                        "backgroundColor": "#ffffff",
                        "textColor": "#1F2937"
                    }
                }
            }
            
            await ws.send(json.dumps(request))
            
            # Wait for response
            for _ in range(5):
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "diagram_response":
                        payload = data.get("payload", {})
                        result["success"] = True
                        
                        # Extract Mermaid code from various possible locations
                        if payload.get("mermaid"):
                            result["mermaid_code"] = payload["mermaid"].get("code")
                        elif payload.get("metadata", {}).get("mermaid_code"):
                            result["mermaid_code"] = payload["metadata"]["mermaid_code"]
                        
                        result["metadata"] = payload.get("metadata", {})
                        break
                        
                except asyncio.TimeoutError:
                    result["error"] = "Timeout"
                    break
                    
    except Exception as e:
        result["error"] = str(e)
    
    return result

def create_demo_html(results):
    """Create beautiful HTML demo page"""
    
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagram Generation Demo</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .results-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
        }}
        
        .diagram-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }}
        
        .diagram-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
        }}
        
        .card-header {{
            background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
            color: white;
            padding: 20px;
        }}
        
        .card-title {{
            font-size: 1.5em;
            margin-bottom: 5px;
        }}
        
        .card-type {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        
        .card-body {{
            padding: 30px;
            background: #f9fafb;
        }}
        
        .mermaid-container {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
        }}
        
        .mermaid {{
            max-width: 100%;
        }}
        
        .code-section {{
            margin-top: 20px;
        }}
        
        .code-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .code-label {{
            font-weight: 600;
            color: #4B5563;
        }}
        
        .copy-btn {{
            background: #3B82F6;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85em;
            transition: background 0.2s;
        }}
        
        .copy-btn:hover {{
            background: #2563EB;
        }}
        
        .code-block {{
            background: #1F2937;
            color: #E5E7EB;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'SF Mono', Monaco, Consolas, monospace;
            font-size: 0.9em;
            line-height: 1.5;
        }}
        
        .metadata {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #E5E7EB;
            display: flex;
            gap: 20px;
            font-size: 0.85em;
            color: #6B7280;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .meta-label {{
            font-weight: 600;
        }}
        
        .success-badge {{
            background: #10B981;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 20px;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Mermaid Diagram Generation Demo</h1>
            <p>Generated by Railway Diagram Service with Gemini 2.5 Flash</p>
            <p style="font-size: 0.9em; margin-top: 10px;">{timestamp}</p>
        </div>
        
        <div class="results-grid">
"""
    
    for i, result in enumerate(results, 1):
        if result["success"] and result.get("mermaid_code"):
            # Escape code for HTML
            escaped_code = result["mermaid_code"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            html += f"""
            <div class="diagram-card">
                <div class="card-header">
                    <div class="card-title">{result['name']}</div>
                    <span class="card-type">{result['diagram_type']}</span>
                </div>
                <div class="card-body">
                    <div class="mermaid-container">
                        <div class="mermaid">
{result['mermaid_code']}
                        </div>
                    </div>
                    
                    <div class="code-section">
                        <div class="code-header">
                            <span class="code-label">Mermaid Code</span>
                            <button class="copy-btn" onclick="copyCode(this, 'code-{i}')">Copy</button>
                        </div>
                        <pre class="code-block" id="code-{i}">{escaped_code}</pre>
                    </div>
                    
                    <div class="metadata">
                        <div class="meta-item">
                            <span class="meta-label">Method:</span>
                            <span>{result.get('metadata', {}).get('generation_method', 'N/A')}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Model:</span>
                            <span>{result.get('metadata', {}).get('llm_model', 'N/A')}</span>
                        </div>
                        <div class="meta-item">
                            <span class="success-badge">✓ Generated</span>
                        </div>
                    </div>
                </div>
            </div>
"""
    
    # Summary stats
    successful = sum(1 for r in results if r["success"])
    
    html += f"""
        </div>
        
        <div class="footer">
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(results)}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{successful}</div>
                    <div class="stat-label">Successful</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{round(successful/len(results)*100)}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
            </div>
            <p>✨ Powered by Gemini 2.5 Flash LLM</p>
        </div>
    </div>
    
    <script>
        // Initialize Mermaid
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            themeVariables: {{
                primaryColor: '#3B82F6',
                primaryTextColor: '#fff',
                primaryBorderColor: '#2563eb',
                lineColor: '#6b7280',
                secondaryColor: '#f3f4f6',
                background: '#ffffff',
                mainBkg: '#3B82F6',
                secondBkg: '#f3f4f6'
            }}
        }});
        
        // Copy code function
        function copyCode(button, codeId) {{
            const codeElement = document.getElementById(codeId);
            const text = codeElement.textContent;
            
            navigator.clipboard.writeText(text).then(() => {{
                const originalText = button.textContent;
                button.textContent = '✓ Copied!';
                setTimeout(() => {{
                    button.textContent = originalText;
                }}, 2000);
            }});
        }}
    </script>
</body>
</html>
"""
    
    # Save HTML
    output_dir = Path(f"mermaid_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_dir.mkdir(exist_ok=True)
    html_path = output_dir / "demo.html"
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return str(html_path.absolute())

async def main():
    """Run demo test"""
    print("\n" + "="*60)
    print("MERMAID GENERATION DEMO - VISUAL TEST")
    print("="*60)
    print(f"Testing {len(DEMO_CASES)} diagram types with Railway API")
    print("Using Gemini 2.5 Flash for LLM generation\n")
    
    results = []
    
    for i, case in enumerate(DEMO_CASES, 1):
        print(f"[{i}/{len(DEMO_CASES)}] Generating {case['name']}...")
        result = await test_diagram(case, i)
        results.append(result)
        
        if result["success"]:
            print(f"  ✅ Success - Generated {len(result.get('mermaid_code', ''))} chars")
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown')}")
        
        await asyncio.sleep(1)
    
    # Generate HTML
    print("\nGenerating visual demo page...")
    html_path = create_demo_html(results)
    
    print(f"✅ Demo page created: {html_path}")
    print("Opening in browser...")
    webbrowser.open(f'file://{html_path}')
    
    print("\n🎨 Check your browser to see the generated Mermaid diagrams!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())