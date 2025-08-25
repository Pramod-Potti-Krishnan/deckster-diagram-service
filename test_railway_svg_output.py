#!/usr/bin/env python3
"""
Test Railway deployment - Generate and save SVG outputs
Tests both SVG templates and Mermaid LLM generation
"""

import asyncio
import json
import websockets
import ssl
from datetime import datetime
import os
from pathlib import Path

# Test cases
TEST_CASES = [
    # SVG Template tests
    {
        "type": "svg_template",
        "diagram_type": "cycle_3_step",
        "content": "Plan: Define objectives and strategies\\nExecute: Implement the plan\\nReview: Analyze results and improve",
        "expected_method": "svg_template"
    },
    {
        "type": "svg_template", 
        "diagram_type": "pyramid_3_level",
        "content": "Foundation: Core infrastructure and systems\\nMiddle Layer: Business services and APIs\\nTop: User-facing applications",
        "expected_method": "svg_template"
    },
    {
        "type": "svg_template",
        "diagram_type": "venn_2_circle",
        "content": "Frontend: React, Vue, CSS\\nBackend: Python, Node, Database\\nOverlap: Full Stack Development",
        "expected_method": "svg_template"
    },
    {
        "type": "svg_template",
        "diagram_type": "matrix_2x2",
        "content": "High Impact/High Effort: Strategic initiatives\\nHigh Impact/Low Effort: Quick wins\\nLow Impact/High Effort: Avoid\\nLow Impact/Low Effort: Fill-ins",
        "expected_method": "svg_template"
    },
    
    # Mermaid LLM tests
    {
        "type": "mermaid",
        "diagram_type": "flowchart",
        "content": "User Registration Process: User enters email -> Validate email format -> Check if email exists -> If new, create account -> Send verification email -> User clicks link -> Account activated -> Login enabled",
        "expected_method": "mermaid"
    },
    {
        "type": "mermaid",
        "diagram_type": "pie_chart", 
        "content": "Market Share Analysis: Apple has 45% of the smartphone market, Samsung holds 30%, Xiaomi has 15%, and Others make up the remaining 10%",
        "expected_method": "mermaid"
    },
    {
        "type": "mermaid",
        "diagram_type": "sequence",
        "content": "API Authentication Flow: Client sends login request to Auth Server, Auth Server validates credentials with Database, Database returns user data, Auth Server generates JWT token, Auth Server sends token to Client, Client uses token for API requests",
        "expected_method": "mermaid"
    },
    {
        "type": "mermaid",
        "diagram_type": "mind_map",
        "content": "Project Management with main branches: Planning (Requirements, Timeline, Budget), Execution (Development, Testing, Deployment), Monitoring (Performance, User Feedback, Analytics), Closing (Documentation, Lessons Learned)",
        "expected_method": "mermaid"
    }
]


async def test_single_diagram(websocket, test_case, index):
    """Test a single diagram and return the result"""
    
    correlation_id = f"test-{index}-{test_case['diagram_type']}"
    
    # Send request
    request = {
        "type": "diagram_request",
        "correlation_id": correlation_id,
        "data": {
            "diagram_type": test_case["diagram_type"],
            "content": test_case["content"],
            "theme": {
                "primaryColor": "#3B82F6",
                "backgroundColor": "#ffffff",
                "textColor": "#1F2937"
            }
        }
    }
    
    print(f"  Sending request for {test_case['diagram_type']}...")
    await websocket.send(json.dumps(request))
    
    # Collect response
    result = None
    for _ in range(10):  # Wait for up to 10 messages
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            response_data = json.loads(response)
            msg_type = response_data.get("type")
            
            if msg_type == "diagram_response":
                payload = response_data.get("payload", {})
                result = {
                    "success": True,
                    "content": payload.get("content"),
                    "url": payload.get("url"),
                    "metadata": payload.get("metadata", {}),
                    "diagram_type": test_case["diagram_type"],
                    "test_type": test_case["type"]
                }
                break
            elif msg_type == "error_response":
                payload = response_data.get("payload", {})
                result = {
                    "success": False,
                    "error": payload.get("error_message", "Unknown error"),
                    "diagram_type": test_case["diagram_type"],
                    "test_type": test_case["type"]
                }
                break
                
        except asyncio.TimeoutError:
            result = {
                "success": False,
                "error": "Timeout waiting for response",
                "diagram_type": test_case["diagram_type"],
                "test_type": test_case["type"]
            }
            break
    
    return result


async def run_tests():
    """Run all tests and save results"""
    
    # Create output directory
    output_dir = Path("railway_test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Railway WebSocket URL
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = f"test-{int(datetime.now().timestamp())}"
    user_id = "test-user"
    full_url = f"{url}?session_id={session_id}&user_id={user_id}"
    
    print("=" * 80)
    print("RAILWAY DEPLOYMENT TEST - SVG OUTPUT VERIFICATION")
    print("=" * 80)
    print(f"Service URL: {url}")
    print(f"Output Directory: {output_dir}")
    print(f"Testing {len(TEST_CASES)} diagrams")
    print("=" * 80)
    
    # SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    results = []
    
    try:
        async with websockets.connect(full_url, ssl=ssl_context) as websocket:
            print("✅ Connected to Railway WebSocket\n")
            
            # Receive welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"Welcome: {welcome_data.get('type')}\n")
            
            # Test each diagram
            for i, test_case in enumerate(TEST_CASES, 1):
                print(f"\n[{i}/{len(TEST_CASES)}] Testing {test_case['type']}: {test_case['diagram_type']}")
                
                result = await test_single_diagram(websocket, test_case, i)
                results.append(result)
                
                if result["success"]:
                    print(f"  ✅ Success - Method: {result['metadata'].get('generation_method', 'unknown')}")
                    
                    # Save SVG content
                    if result.get("content"):
                        filename = f"{i:02d}_{test_case['diagram_type']}.svg"
                        filepath = output_dir / filename
                        
                        # Extract SVG content (might be wrapped)
                        svg_content = result["content"]
                        
                        with open(filepath, "w") as f:
                            f.write(svg_content)
                        print(f"  💾 Saved to {filename}")
                        
                        result["saved_file"] = str(filepath)
                else:
                    print(f"  ❌ Failed: {result['error']}")
                
                # Small delay between tests
                await asyncio.sleep(0.5)
                
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
    
    return results, output_dir


def create_html_viewer(results, output_dir):
    """Create HTML file to view all generated diagrams"""
    
    # Add timestamp and counts
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(results)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Railway Diagram Test Results</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #1F2937;
            border-bottom: 3px solid #3B82F6;
            padding-bottom: 10px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .diagram-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
            gap: 30px;
        }}
        .diagram-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .diagram-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e5e7eb;
        }}
        .diagram-title {{
            font-size: 18px;
            font-weight: 600;
            color: #1F2937;
        }}
        .diagram-type {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        .type-svg_template {{
            background: #10B981;
            color: white;
        }}
        .type-mermaid {{
            background: #3B82F6;
            color: white;
        }}
        .diagram-content {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 4px;
            padding: 20px;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .diagram-content svg {{
            max-width: 100%;
            height: auto;
        }}
        .metadata {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e5e7eb;
            font-size: 13px;
            color: #6B7280;
        }}
        .error {{
            background: #FEE2E2;
            color: #DC2626;
            padding: 20px;
            border-radius: 4px;
            text-align: center;
        }}
        .success-badge {{
            color: #10B981;
        }}
        .failure-badge {{
            color: #DC2626;
        }}
    </style>
</head>
<body>
    <h1>🚀 Railway Diagram Service - Test Results</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Test Time:</strong> {timestamp}</p>
        <p><strong>Total Tests:</strong> {total}</p>
        <p><strong>Successful:</strong> <span class="success-badge">{successful}</span></p>
        <p><strong>Failed:</strong> <span class="failure-badge">{failed}</span></p>
    </div>
    
    <div class="diagram-grid">
"""
    
    # Add each diagram
    for i, result in enumerate(results, 1):
        type_class = f"type-{result['test_type']}"
        
        html_content += f"""
        <div class="diagram-card">
            <div class="diagram-header">
                <span class="diagram-title">{i}. {result['diagram_type'].replace('_', ' ').title()}</span>
                <span class="diagram-type {type_class}">{result['test_type'].upper()}</span>
            </div>
            <div class="diagram-content">
        """
        
        if result["success"] and result.get("saved_file"):
            # Read the SVG file
            svg_path = Path(result["saved_file"])
            if svg_path.exists():
                with open(svg_path, "r") as f:
                    svg_content = f.read()
                html_content += svg_content
            else:
                html_content += '<div class="error">SVG file not found</div>'
        else:
            error_msg = result.get("error", "Unknown error")
            html_content += f'<div class="error">Failed to generate: {error_msg}</div>'
        
        html_content += """
            </div>
            <div class="metadata">
        """
        
        if result["success"]:
            metadata = result.get("metadata", {})
            html_content += f"""
                <strong>Method:</strong> {metadata.get('generation_method', 'unknown')}<br>
                <strong>LLM Used:</strong> {metadata.get('llm_used', False)}<br>
                <strong>Confidence:</strong> {metadata.get('confidence', 'N/A')}
            """
        
        html_content += """
            </div>
        </div>
        """
    
    html_content += """
    </div>
</body>
</html>
"""
    
    # Save HTML file
    html_path = output_dir / "results.html"
    with open(html_path, "w") as f:
        f.write(html_content)
    
    return html_path


async def main():
    """Main test runner"""
    print("Starting Railway deployment test...")
    
    # Run tests
    results, output_dir = await run_tests()
    
    # Create HTML viewer
    html_path = create_html_viewer(results, output_dir)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print(f"\n📁 Output Directory: {output_dir}")
    print(f"🌐 HTML Viewer: {html_path}")
    
    return str(html_path)


if __name__ == "__main__":
    html_file = asyncio.run(main())
    print(f"\nTo view results, open: {html_file}")