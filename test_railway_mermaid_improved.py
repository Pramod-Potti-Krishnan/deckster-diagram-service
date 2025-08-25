#!/usr/bin/env python3
"""
Improved Railway Mermaid Test with Fixes
=========================================
- Simpler flowchart prompts without styling
- Extended timeout for Gantt charts
- Retry logic for failed diagrams
- Better error handling and logging
"""

import asyncio
import json
import websockets
import ssl
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

async def test_mermaid_with_retry(
    session_id: str,
    diagram_type: str,
    content: str,
    description: str,
    max_retries: int = 2,
    timeout: int = 30
) -> Dict[str, Any]:
    """Test a Mermaid diagram with retry logic"""
    
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    full_url = f"{url}?session_id={session_id}&user_id=test"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            
            async with websockets.connect(full_url, ssl=ssl_context, ping_timeout=20) as ws:
                # Skip welcome message
                await ws.recv()
                
                # Send diagram request
                request = {
                    "type": "diagram_request",
                    "correlation_id": f"test-{diagram_type}-{attempt}",
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
                
                # Get responses with appropriate timeout
                data = None
                for _ in range(15):  # Try more messages for complex diagrams
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=timeout)
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
                    except asyncio.TimeoutError:
                        if attempt < max_retries - 1:
                            print(f"  ⏱️  Timeout on attempt {attempt + 1}, retrying...")
                            break
                        else:
                            raise
                
                elapsed = time.time() - start_time
                
                if data and data.get("type") == "diagram_response":
                    payload = data.get("payload", {})
                    
                    result = {
                        "type": diagram_type,
                        "description": description,
                        "success": True,
                        "content": payload.get("content", ""),
                        "metadata": payload.get("metadata", {}),
                        "mermaid_code": None,
                        "svg": None,
                        "elapsed_time": elapsed,
                        "attempts": attempt + 1
                    }
                    
                    # Extract Mermaid code
                    metadata = payload.get("metadata", {})
                    if "mermaid_code" in metadata:
                        result["mermaid_code"] = metadata["mermaid_code"]
                    
                    # Check for SVG
                    content = payload.get("content", "")
                    if content.startswith("<svg"):
                        result["svg"] = content
                        
                        # Try to extract embedded Mermaid code
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
                    
                elif data and data.get("type") == "error_response":
                    if attempt < max_retries - 1:
                        print(f"  ⚠️  Error on attempt {attempt + 1}: {data.get('payload', {}).get('error_message', 'Unknown')}")
                        await asyncio.sleep(2)  # Wait before retry
                        continue
                    else:
                        return {
                            "type": diagram_type,
                            "description": description,
                            "success": False,
                            "error": data.get("payload", {}).get("error_message", "Unknown error"),
                            "elapsed_time": elapsed,
                            "attempts": attempt + 1
                        }
                        
        except asyncio.TimeoutError:
            if attempt < max_retries - 1:
                print(f"  ⏱️  Timeout on attempt {attempt + 1}/{max_retries}")
                await asyncio.sleep(2)
                continue
            else:
                return {
                    "type": diagram_type,
                    "description": description,
                    "success": False,
                    "error": f"Timeout after {max_retries} attempts ({timeout}s each)",
                    "attempts": max_retries
                }
        except Exception as e:
            return {
                "type": diagram_type,
                "description": description,
                "success": False,
                "error": str(e),
                "attempts": attempt + 1
            }
    
    return {
        "type": diagram_type,
        "description": description,
        "success": False,
        "error": "Failed after all retry attempts",
        "attempts": max_retries
    }

async def run_improved_tests():
    """Run improved Mermaid tests with optimized prompts and timeouts"""
    
    print(f"{Colors.BOLD}Improved Railway Mermaid Test Suite{Colors.RESET}")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Service: deckster-diagram-service-production.up.railway.app")
    print()
    
    # Optimized test cases with simpler prompts
    test_cases = [
        {
            "type": "flowchart",
            "content": "Create a simple flowchart without any styling: Start -> Input Data -> Process Data -> Decision (Is Valid?) -> If Yes: Save to Database -> If No: Show Error -> End",
            "description": "Simple Process Flow",
            "timeout": 30,
            "retries": 2
        },
        {
            "type": "erDiagram",
            "content": "Create an ER diagram: User entity with id, name, email. Order entity with id, user_id, total. Product entity with id, name, price. User has many Orders. Order has many Products.",
            "description": "Database Schema",
            "timeout": 30,
            "retries": 2
        },
        {
            "type": "journey",
            "content": "Customer journey: Browse Products (4/5 satisfaction), Add to Cart (5/5), Checkout (3/5), Payment (2/5), Order Confirmation (5/5)",
            "description": "User Journey Map",
            "timeout": 30,
            "retries": 2
        },
        {
            "type": "gantt",
            "content": "Simple project timeline starting today: Week 1: Planning, Week 2-3: Design, Week 4-6: Development, Week 7: Testing, Week 8: Deployment",
            "description": "Project Timeline (Simple)",
            "timeout": 60,  # Extended timeout for Gantt
            "retries": 3     # More retries for Gantt
        },
        {
            "type": "quadrantChart",
            "content": "Create a priority matrix. X-axis: Impact (Low to High). Y-axis: Effort (Low to High). Items: Feature A (high impact, low effort), Bug Fix (low impact, low effort), Refactor (high impact, high effort), Documentation (low impact, high effort)",
            "description": "Priority Matrix",
            "timeout": 30,
            "retries": 2
        },
        {
            "type": "timeline",
            "content": "Company milestones: 2020: Founded, 2021: First Product, 2022: Series A Funding, 2023: 100k Users, 2024: International Expansion",
            "description": "Company Timeline",
            "timeout": 30,
            "retries": 2
        },
        {
            "type": "kanban",
            "content": "Development board with three columns. Backlog: Feature A, Feature B. In Progress: Bug Fix, Feature C. Done: Feature D, Feature E",
            "description": "Kanban Board",
            "timeout": 30,
            "retries": 2
        }
    ]
    
    session_id = f"improved-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results = []
    
    # Test each diagram type
    for i, test_case in enumerate(test_cases, 1):
        diagram_type = test_case["type"]
        print(f"{Colors.BLUE}[{i}/{len(test_cases)}] Testing {diagram_type}{Colors.RESET}")
        print(f"  Description: {test_case['description']}")
        print(f"  Timeout: {test_case['timeout']}s, Max retries: {test_case['retries']}")
        
        result = await test_mermaid_with_retry(
            session_id,
            diagram_type,
            test_case["content"],
            test_case["description"],
            max_retries=test_case["retries"],
            timeout=test_case["timeout"]
        )
        
        results.append(result)
        
        # Display result
        if result["success"]:
            elapsed = result.get("elapsed_time", 0)
            attempts = result.get("attempts", 1)
            code_len = len(result.get("mermaid_code", "")) if result.get("mermaid_code") else 0
            svg_len = len(result.get("svg", "")) if result.get("svg") else 0
            
            print(f"  {Colors.GREEN}✅ SUCCESS{Colors.RESET}")
            print(f"     Time: {elapsed:.2f}s (attempt {attempts})")
            if code_len > 0:
                print(f"     Mermaid code: {code_len} chars")
            if svg_len > 0:
                print(f"     SVG output: {svg_len} chars")
        else:
            error = result.get("error", "Unknown error")
            attempts = result.get("attempts", 1)
            print(f"  {Colors.RED}❌ FAILED{Colors.RESET}")
            print(f"     Error: {error}")
            print(f"     Attempts: {attempts}")
        
        print()
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    return results

def create_improved_html_viewer(results):
    """Create an improved HTML viewer with better Mermaid.js configuration"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(f"railway_mermaid_improved_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    
    # Calculate statistics
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    failed = total - successful
    avg_time = sum(r.get("elapsed_time", 0) for r in results if r["success"]) / max(successful, 1)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Improved Mermaid Test Results</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #1a202c;
            border-bottom: 3px solid #3B82F6;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2d3748;
        }}
        
        .stat-label {{
            color: #718096;
            margin-top: 5px;
        }}
        
        .diagram-card {{
            background: white;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .diagram-header {{
            background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .status-badge.success {{
            background: #10b981;
        }}
        
        .status-badge.failed {{
            background: #ef4444;
        }}
        
        .diagram-content {{
            padding: 30px;
            background: #fafbfc;
            min-height: 300px;
        }}
        
        .mermaid-wrapper {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
            overflow-x: auto;
        }}
        
        .error-message {{
            color: #ef4444;
            padding: 20px;
            background: #fee;
            border-radius: 6px;
            border: 1px solid #fcc;
        }}
        
        .timing-info {{
            color: #64748b;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        pre {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Improved Mermaid Test Results</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{successful}/{total}</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{successful}</div>
                <div class="stat-label">✅ Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{failed}</div>
                <div class="stat-label">❌ Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{avg_time:.2f}s</div>
                <div class="stat-label">Avg Time</div>
            </div>
        </div>
"""
    
    # Add individual diagram results
    for i, result in enumerate(results):
        status_class = "success" if result["success"] else "failed"
        status_text = "Success" if result["success"] else "Failed"
        
        html_content += f"""
        <div class="diagram-card">
            <div class="diagram-header">
                <div>
                    <strong>{result['description']}</strong> ({result['type']})
                </div>
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
            <div class="diagram-content">
"""
        
        if result["success"]:
            if result.get("mermaid_code"):
                # Clean the Mermaid code - remove problematic styling
                mermaid_code = result["mermaid_code"]
                
                # Remove classDef and class lines for flowcharts
                if result["type"] == "flowchart" and "classDef" in mermaid_code:
                    lines = mermaid_code.split('\n')
                    filtered_lines = []
                    for line in lines:
                        if not line.strip().startswith('classDef') and not line.strip().startswith('class '):
                            filtered_lines.append(line)
                    mermaid_code = '\n'.join(filtered_lines)
                
                html_content += f"""
                <div class="mermaid-wrapper">
                    <div class="mermaid" id="mermaid-{i}">
{mermaid_code}
                    </div>
                </div>
                <div class="timing-info">
                    Generated in {result.get('elapsed_time', 0):.2f}s (Attempt {result.get('attempts', 1)})
                </div>
"""
            elif result.get("svg"):
                html_content += f"""
                <div class="mermaid-wrapper">
                    {result['svg']}
                </div>
                <div class="timing-info">
                    Generated in {result.get('elapsed_time', 0):.2f}s
                </div>
"""
        else:
            html_content += f"""
                <div class="error-message">
                    <strong>Error:</strong> {result.get('error', 'Unknown error')}<br>
                    <strong>Attempts:</strong> {result.get('attempts', 1)}
                </div>
"""
        
        html_content += """
            </div>
        </div>
"""
    
    # Add improved Mermaid initialization
    html_content += """
    </div>
    
    <script>
        // Initialize Mermaid with more permissive settings
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',  // Allow more flexibility
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            },
            themeVariables: {
                primaryColor: '#3B82F6',
                primaryTextColor: '#fff',
                primaryBorderColor: '#2563EB',
                lineColor: '#94A3B8',
                secondaryColor: '#60A5FA',
                tertiaryColor: '#DBEAFE'
            },
            er: {
                useMaxWidth: true
            },
            journey: {
                useMaxWidth: true
            },
            gantt: {
                useMaxWidth: true,
                numberSectionStyles: 4,
                fontSize: 12
            }
        });
        
        // Force re-render of Mermaid diagrams
        setTimeout(() => {
            mermaid.init();
        }, 100);
    </script>
</body>
</html>
"""
    
    # Save HTML file
    html_file = output_dir / "results.html"
    html_file.write_text(html_content)
    
    print(f"\n📁 Results saved to: {output_dir}")
    print(f"🌐 HTML viewer: {html_file}")
    
    return str(html_file)

async def main():
    """Main entry point"""
    
    # Run improved tests
    results = await run_improved_tests()
    
    # Create HTML viewer
    html_file = create_improved_html_viewer(results)
    
    # Print summary
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}FINAL SUMMARY{Colors.RESET}")
    print(f"Success Rate: {successful}/{total} ({(successful/total)*100:.1f}%)")
    
    if successful == total:
        print(f"{Colors.GREEN}🎉 All Mermaid diagrams generated successfully!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠️ Some diagrams failed:{Colors.RESET}")
        for r in results:
            if not r["success"]:
                print(f"  - {r['type']}: {r.get('error')}")
    
    print(f"\nView results: file://{html_file}")

if __name__ == "__main__":
    asyncio.run(main())