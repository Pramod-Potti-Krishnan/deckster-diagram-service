#!/usr/bin/env python3
"""
Test Railway deployment for all Mermaid diagram types
Generates HTML viewer with rendered diagrams
"""

import asyncio
import json
import websockets
import ssl
import os
from datetime import datetime
from pathlib import Path

async def test_mermaid_diagram(session_id, diagram_type, content, description):
    """Test a single Mermaid diagram type"""
    
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    full_url = f"{url}?session_id={session_id}&user_id=test"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
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
            
            # Get responses (skip status updates)
            data = None
            for _ in range(10):  # Try up to 10 messages
                response = await asyncio.wait_for(ws.recv(), timeout=30.0)
                msg = json.loads(response)
                
                # Skip status updates
                if msg.get("type") == "status_update":
                    continue
                    
                # Process diagram response
                if msg.get("type") == "diagram_response":
                    data = msg
                    break
                    
                # Handle error response
                if msg.get("type") == "error_response":
                    data = msg
                    break
            
            if data and data.get("type") == "diagram_response":
                payload = data.get("payload", {})
                
                # Extract Mermaid code or SVG
                result = {
                    "type": diagram_type,
                    "description": description,
                    "success": True,
                    "content": payload.get("content", ""),
                    "metadata": payload.get("metadata", {}),
                    "mermaid_code": None,
                    "svg": None
                }
                
                # Check if we got Mermaid code in metadata
                metadata = payload.get("metadata", {})
                if "mermaid_code" in metadata:
                    result["mermaid_code"] = metadata["mermaid_code"]
                
                # Check if we got SVG with embedded Mermaid
                content = payload.get("content", "")
                if content.startswith("<svg"):
                    result["svg"] = content
                    
                    # Try to extract Mermaid code from embedded JSON
                    if "application/mermaid+json" in content:
                        import re
                        json_match = re.search(r'<script type="application/mermaid\+json">({.*?})</script>', content, re.DOTALL)
                        if json_match:
                            try:
                                mermaid_data = json.loads(json_match.group(1))
                                if "code" in mermaid_data:
                                    result["mermaid_code"] = mermaid_data["code"]
                            except:
                                pass
                
                return result
                
            elif data.get("type") == "error_response":
                return {
                    "type": diagram_type,
                    "description": description,
                    "success": False,
                    "error": data.get("payload", {}).get("error_message", "Unknown error")
                }
            else:
                return {
                    "type": diagram_type,
                    "description": description,
                    "success": False,
                    "error": "Unexpected response type"
                }
                
    except asyncio.TimeoutError:
        return {
            "type": diagram_type,
            "description": description,
            "success": False,
            "error": "Timeout waiting for response"
        }
    except Exception as e:
        return {
            "type": diagram_type,
            "description": description,
            "success": False,
            "error": str(e)
        }

async def test_all_mermaid_types():
    """Test all 7 Mermaid diagram types"""
    
    print("Testing Railway Mermaid Deployment")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test cases for all 7 Mermaid types
    test_cases = [
        ("flowchart", 
         "Create a flowchart showing: User Login -> Validate Credentials -> Success/Failure -> Dashboard/Error Page",
         "Process Flow Diagram"),
        
        ("erDiagram",
         "Create an ER diagram with: User entity (id, name, email), Order entity (id, user_id, total, status), Product entity (id, name, price). User has many Orders, Order has many Products",
         "Entity Relationship Diagram"),
        
        ("journey",
         "Show a customer journey for online shopping: Browse Products (satisfaction 4), Add to Cart (satisfaction 5), Checkout Process (satisfaction 3), Payment (satisfaction 2), Order Confirmation (satisfaction 5)",
         "User Journey Map"),
        
        ("gantt",
         "Create a project timeline: Planning (Week 1-2), Design (Week 2-3), Development (Week 3-6), Testing (Week 5-7), Deployment (Week 7)",
         "Gantt Chart Timeline"),
        
        ("quadrantChart",
         "Create a risk assessment matrix with quadrants for Impact vs Probability. High Impact/High Probability: System Outage. Low Impact/High Probability: Minor Bugs. High Impact/Low Probability: Data Breach. Low Impact/Low Probability: UI Issues",
         "Quadrant Chart Matrix"),
        
        ("timeline",
         "Show company milestones: 2020 Q1 - Company Founded, 2020 Q3 - First Product Launch, 2021 Q1 - Series A Funding, 2021 Q4 - 100k Users, 2022 Q2 - International Expansion, 2023 Q1 - IPO",
         "Timeline Diagram"),
        
        ("kanban",
         "Create a development board with columns: Backlog (Feature A, Feature B), In Progress (Bug Fix, Feature C), Code Review (Feature D), Testing (Feature E), Done (Feature F, Feature G)",
         "Kanban Board")
    ]
    
    session_id = f"mermaid-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results = []
    
    for diagram_type, content, description in test_cases:
        print(f"Testing {diagram_type}...")
        result = await test_mermaid_diagram(session_id, diagram_type, content, description)
        results.append(result)
        
        if result["success"]:
            print(f"  ✅ SUCCESS")
            if result.get("mermaid_code"):
                print(f"     Generated Mermaid code ({len(result['mermaid_code'])} chars)")
            if result.get("svg"):
                print(f"     Rendered to SVG ({len(result['svg'])} chars)")
        else:
            print(f"  ❌ FAILED: {result.get('error')}")
        print()
    
    return results

def create_html_viewer(results, reuse_dir=None):
    """Create an HTML file to view the generated diagrams"""
    
    if reuse_dir and Path(reuse_dir).exists():
        output_dir = Path(reuse_dir)
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(f"railway_mermaid_test_{timestamp}")
        output_dir.mkdir(exist_ok=True)
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Railway Mermaid Diagrams Test Results</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f7fa;
        }
        
        h1 {
            color: #1a202c;
            border-bottom: 3px solid #3B82F6;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        
        .summary {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .summary-item {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #3B82F6;
        }
        
        .summary-item.success {
            border-left-color: #10b981;
        }
        
        .summary-item.failed {
            border-left-color: #ef4444;
        }
        
        .diagram-container {
            background: white;
            margin-bottom: 30px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .diagram-header {
            background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .diagram-header h2 {
            margin: 0;
            font-size: 1.3em;
        }
        
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            background: rgba(255,255,255,0.2);
        }
        
        .status-badge.success {
            background: #10b981;
        }
        
        .status-badge.failed {
            background: #ef4444;
        }
        
        .diagram-content {
            padding: 30px;
            background: #fafbfc;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .mermaid-diagram {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            max-width: 100%;
            overflow-x: auto;
        }
        
        .error-message {
            color: #ef4444;
            padding: 20px;
            background: #fee;
            border-radius: 6px;
            border: 1px solid #fcc;
        }
        
        .code-section {
            background: #1e293b;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 6px;
            margin-top: 15px;
            overflow-x: auto;
        }
        
        .code-section pre {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            padding: 15px 20px 0;
            background: white;
        }
        
        .tab {
            padding: 8px 16px;
            background: #f1f5f9;
            border: none;
            border-radius: 6px 6px 0 0;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .tab.active {
            background: #fafbfc;
            font-weight: 600;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .metadata {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            margin-top: 15px;
            font-size: 0.9em;
            color: #64748b;
        }
    </style>
</head>
<body>
    <h1>🎨 Railway Mermaid Diagrams Test Results</h1>
    
    <div class="summary">
        <h2>Test Summary</h2>
        <p><strong>Timestamp:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        <p><strong>Deployment:</strong> Railway Production</p>
        <p><strong>Total Tests:</strong> """ + str(len(results)) + """</p>
        
        <div class="summary-grid">
"""
    
    # Add summary items
    for result in results:
        status_class = "success" if result["success"] else "failed"
        status_text = "✅ Success" if result["success"] else "❌ Failed"
        html_content += f"""
            <div class="summary-item {status_class}">
                <strong>{result['type']}</strong><br>
                {status_text}
            </div>
"""
    
    html_content += """
        </div>
    </div>
"""
    
    # Add individual diagram sections
    for i, result in enumerate(results):
        status_class = "success" if result["success"] else "failed"
        status_text = "Success" if result["success"] else "Failed"
        
        html_content += f"""
    <div class="diagram-container">
        <div class="diagram-header">
            <h2>{result['description']}</h2>
            <span class="status-badge {status_class}">{status_text}</span>
        </div>
"""
        
        if result["success"]:
            # Add tabs for viewing options
            html_content += f"""
        <div class="tabs">
            <button class="tab active" onclick="showTab('{i}', 'rendered')">Rendered Diagram</button>
            <button class="tab" onclick="showTab('{i}', 'code')">Mermaid Code</button>
            <button class="tab" onclick="showTab('{i}', 'metadata')">Metadata</button>
        </div>
"""
            
            # Rendered diagram tab
            html_content += f"""
        <div id="tab-{i}-rendered" class="tab-content active">
            <div class="diagram-content">
"""
            
            if result.get("mermaid_code"):
                # Render with Mermaid.js
                html_content += f"""
                <div class="mermaid-diagram">
                    <div class="mermaid" id="mermaid-{i}">
{result['mermaid_code']}
                    </div>
                </div>
"""
            elif result.get("svg"):
                # Display SVG directly
                html_content += f"""
                <div class="mermaid-diagram">
                    {result['svg']}
                </div>
"""
            
            html_content += """
            </div>
        </div>
"""
            
            # Code tab
            if result.get("mermaid_code"):
                html_content += f"""
        <div id="tab-{i}-code" class="tab-content">
            <div class="diagram-content">
                <div style="width: 100%;">
                    <div class="code-section">
                        <pre>{result['mermaid_code']}</pre>
                    </div>
                </div>
            </div>
        </div>
"""
            
            # Metadata tab
            html_content += f"""
        <div id="tab-{i}-metadata" class="tab-content">
            <div class="diagram-content">
                <div style="width: 100%;">
                    <div class="metadata">
                        <strong>Diagram Type:</strong> {result['type']}<br>
                        <strong>Generation Method:</strong> {result.get('metadata', {}).get('generation_method', 'N/A')}<br>
                        <strong>LLM Model:</strong> {result.get('metadata', {}).get('llm_model', 'N/A')}<br>
                        <strong>Server Rendered:</strong> {result.get('metadata', {}).get('server_rendered', 'N/A')}
                    </div>
                </div>
            </div>
        </div>
"""
            
        else:
            # Show error
            html_content += f"""
        <div class="diagram-content">
            <div class="error-message">
                <strong>Error:</strong> {result.get('error', 'Unknown error')}
            </div>
        </div>
"""
        
        html_content += """
    </div>
"""
    
    # Add JavaScript and close HTML
    html_content += """
    <script>
        // Initialize Mermaid
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'default',
            themeVariables: {
                primaryColor: '#3B82F6',
                primaryTextColor: '#fff',
                primaryBorderColor: '#2563EB',
                lineColor: '#94A3B8',
                secondaryColor: '#60A5FA',
                tertiaryColor: '#DBEAFE'
            }
        });
        
        // Tab switching function
        function showTab(diagramId, tabName) {
            // Hide all tabs for this diagram
            const tabs = document.querySelectorAll(`[id^="tab-${diagramId}-"]`);
            tabs.forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            const selectedTab = document.getElementById(`tab-${diagramId}-${tabName}`);
            if (selectedTab) {
                selectedTab.classList.add('active');
            }
            
            // Update tab buttons
            const buttons = document.querySelectorAll(`.diagram-container:nth-child(${parseInt(diagramId) + 3}) .tab`);
            buttons.forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent.toLowerCase().includes(tabName)) {
                    btn.classList.add('active');
                }
            });
        }
    </script>
</body>
</html>
"""
    
    # Save HTML file
    html_file = output_dir / "results.html"
    html_file.write_text(html_content)
    
    print(f"\n✅ HTML viewer created: {html_file}")
    return str(html_file)

async def main():
    """Main test function"""
    
    # Test all Mermaid types
    results = await test_all_mermaid_types()
    
    # Create HTML viewer (reuse existing directory if it exists)
    existing_dir = "railway_mermaid_test_20250817_223049"
    html_file = create_html_viewer(results, reuse_dir=existing_dir)
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print("=" * 60)
    print("FINAL SUMMARY")
    print(f"Successful: {successful}/{total}")
    
    if successful == total:
        print("🎉 All Mermaid diagram types working!")
    else:
        print("⚠️ Some diagram types failed:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['type']}: {r.get('error')}")
    
    print(f"\nView results in browser: file://{os.path.abspath(html_file)}")

if __name__ == "__main__":
    asyncio.run(main())