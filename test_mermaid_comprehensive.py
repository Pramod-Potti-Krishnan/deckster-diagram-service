#!/usr/bin/env python3
"""
Comprehensive Mermaid Test - Test all diagram types from playbook
Tests all 9 Mermaid diagram types defined in the playbook via Railway API
"""

import asyncio
import json
import websockets
import ssl
from datetime import datetime
import os
from pathlib import Path

# Comprehensive test cases for all Mermaid types in playbook
MERMAID_TEST_CASES = [
    # 1. FLOWCHART
    {
        "diagram_type": "flowchart",
        "name": "User Authentication Flow",
        "content": """User Authentication Process:
        1. User enters credentials (username and password)
        2. System validates format (email format, password strength)
        3. If format invalid, show error and return to step 1
        4. Query database for user credentials
        5. If user not found, show "Invalid credentials" error
        6. If found, verify password hash
        7. If password incorrect, increment failed attempts and check lockout
        8. If locked out, show lockout message
        9. If password correct, generate JWT token
        10. Set session cookie and redirect to dashboard
        11. Log authentication event"""
    },
    
    # 2. CLASS DIAGRAM
    {
        "diagram_type": "class_diagram", 
        "name": "E-commerce System Classes",
        "content": """Design an object-oriented e-commerce system with these classes:
        - User class with properties: id, email, password, role and methods: login(), logout(), updateProfile()
        - Product class with properties: id, name, price, stock, category and methods: updateStock(), applyDiscount()
        - ShoppingCart class with properties: items[], total and methods: addItem(), removeItem(), calculateTotal()
        - Order class with properties: id, userId, items[], status, total and methods: processPayment(), shipOrder(), cancelOrder()
        - Payment class with properties: orderId, amount, method, status and methods: authorize(), capture(), refund()
        - User has one ShoppingCart, ShoppingCart contains many Products, Order belongs to User, Payment belongs to Order"""
    },
    
    # 3. ENTITY RELATIONSHIP
    {
        "diagram_type": "entity_relationship",
        "name": "University Database Schema", 
        "content": """University database with these entities and relationships:
        - Student entity: studentId (PK), firstName, lastName, email, enrollmentDate, major
        - Course entity: courseId (PK), courseName, credits, department, instructor
        - Enrollment entity: enrollmentId (PK), studentId (FK), courseId (FK), semester, grade
        - Professor entity: professorId (PK), firstName, lastName, department, email, office
        - Department entity: deptId (PK), deptName, building, budget
        Relationships: 
        - Student enrolls in many Courses (many-to-many through Enrollment)
        - Professor teaches many Courses (one-to-many)
        - Course belongs to one Department (many-to-one)
        - Department has many Professors (one-to-many)"""
    },
    
    # 4. USER JOURNEY
    {
        "diagram_type": "user_journey",
        "name": "Online Shopping Journey",
        "content": """Customer journey for purchasing a laptop online:
        1. Awareness stage: User sees social media ad for laptop sale (satisfaction: 3/5)
        2. Research stage: User visits website, compares 5 different laptop models (satisfaction: 4/5)
        3. Consideration: User reads reviews, watches video demos (satisfaction: 4/5)  
        4. Decision: User adds laptop to cart but sees high shipping cost (satisfaction: 2/5)
        5. Action: User finds promo code for free shipping and completes purchase (satisfaction: 5/5)
        6. Delivery: User receives laptop in 3 days with good packaging (satisfaction: 5/5)
        7. Setup: User follows setup guide but has driver issues (satisfaction: 2/5)
        8. Support: User contacts support chat and gets help within 5 minutes (satisfaction: 5/5)
        9. Satisfaction: User writes positive review and recommends to friends (satisfaction: 5/5)"""
    },
    
    # 5. GANTT CHART
    {
        "diagram_type": "gantt",
        "name": "Software Development Timeline",
        "content": """Project timeline for mobile app development (3 months):
        Week 1-2: Requirements gathering and analysis
        Week 2-3: UI/UX design mockups and prototypes
        Week 3-4: Technical architecture design
        Week 4-6: Backend API development
        Week 5-8: Frontend mobile app development
        Week 7-8: Database design and implementation
        Week 8-9: Integration of frontend with backend
        Week 9-10: Unit testing and bug fixes
        Week 10-11: User acceptance testing
        Week 11-12: Performance optimization
        Week 12: Deployment preparation and go-live
        Critical path: Requirements → Architecture → Backend → Integration → Testing → Deployment"""
    },
    
    # 6. QUADRANT CHART
    {
        "diagram_type": "quadrant",
        "name": "Risk Assessment Matrix",
        "content": """Risk assessment for IT project with Impact (Low to High) on Y-axis and Probability (Low to High) on X-axis:
        Quadrant 1 (High Impact, High Probability): 
        - Data breach from cyberattack
        - Key developer leaving project
        - Major scope creep
        Quadrant 2 (High Impact, Low Probability):
        - Complete system failure
        - Natural disaster affecting data center
        - Regulatory compliance changes
        Quadrant 3 (Low Impact, High Probability):
        - Minor bugs in non-critical features
        - Slight schedule delays
        - Team communication issues
        Quadrant 4 (Low Impact, Low Probability):
        - Printer malfunction
        - Office Wi-Fi issues
        - Coffee machine breakdown"""
    },
    
    # 7. TIMELINE
    {
        "diagram_type": "timeline",
        "name": "Company Growth History",
        "content": """Tech startup evolution from 2018 to 2024:
        2018 Q1: Company founded in garage by 2 co-founders
        2018 Q3: First prototype developed
        2018 Q4: Seed funding of $500K raised
        2019 Q2: Beta launch with 100 users
        2019 Q4: Series A funding of $5M, team grows to 15
        2020 Q1: Product officially launches
        2020 Q3: 10,000 active users milestone
        2021 Q1: Series B funding of $20M
        2021 Q3: International expansion to Europe
        2022 Q1: 100,000 users, 50 employees
        2022 Q4: Acquired competitor for $10M
        2023 Q2: Launched enterprise version
        2023 Q4: Series C funding of $50M
        2024 Q1: IPO announcement, valued at $500M"""
    },
    
    # 8. KANBAN BOARD
    {
        "diagram_type": "kanban",
        "name": "Sprint Development Board",
        "content": """Current sprint kanban board status:
        Backlog column:
        - Implement user notifications system
        - Add export to PDF feature
        - Optimize database queries
        
        To Do column:
        - Fix login page CSS issues
        - Write unit tests for payment module
        - Update API documentation
        
        In Progress column:
        - Develop user dashboard (assigned to: John, 60% complete)
        - Integrate third-party analytics (assigned to: Sarah, 30% complete)
        - Refactor authentication service (assigned to: Mike, 80% complete)
        
        Testing column:
        - Shopping cart functionality (tested by: QA team)
        - Email verification flow (tested by: Lisa)
        
        Done column:
        - Setup CI/CD pipeline
        - Migrate to new database server
        - Implement two-factor authentication
        - Fix critical security vulnerability"""
    },
    
    # 9. ARCHITECTURE DIAGRAM
    {
        "diagram_type": "architecture",
        "name": "Microservices Architecture",
        "content": """Cloud-based microservices architecture for e-commerce platform:
        
        Frontend Layer:
        - React Web Application
        - React Native Mobile Apps (iOS/Android)
        - Admin Dashboard (Angular)
        
        API Gateway Layer:
        - Kong API Gateway for routing and rate limiting
        - Authentication/Authorization service
        
        Microservices Layer:
        - User Service (Node.js): Handles user accounts and profiles
        - Product Service (Python/Django): Manages product catalog
        - Order Service (Java/Spring): Processes orders and transactions
        - Payment Service (Go): Handles payment processing
        - Notification Service (Node.js): Email and push notifications
        - Search Service (Elasticsearch): Product search and filtering
        
        Data Layer:
        - PostgreSQL for user and order data
        - MongoDB for product catalog
        - Redis for caching and sessions
        - S3 for media storage
        
        Infrastructure:
        - Kubernetes for container orchestration
        - Docker containers for each service
        - AWS cloud hosting
        - CloudFlare CDN
        
        All services communicate via REST APIs and message queues (RabbitMQ)"""
    }
]


async def test_single_mermaid(websocket, test_case, index):
    """Test a single Mermaid diagram and return the result"""
    
    correlation_id = f"mermaid-test-{index}-{test_case['diagram_type']}"
    
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
    
    print(f"  Sending request for {test_case['name']}...")
    await websocket.send(json.dumps(request))
    
    # Collect response
    result = None
    for _ in range(15):  # Wait for up to 15 messages (Mermaid generation may take longer)
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
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
                    "name": test_case["name"]
                }
                break
            elif msg_type == "error_response":
                payload = response_data.get("payload", {})
                result = {
                    "success": False,
                    "error": payload.get("error_message", "Unknown error"),
                    "diagram_type": test_case["diagram_type"],
                    "name": test_case["name"]
                }
                break
                
        except asyncio.TimeoutError:
            result = {
                "success": False,
                "error": "Timeout waiting for response",
                "diagram_type": test_case["diagram_type"],
                "name": test_case["name"]
            }
            break
    
    return result


async def run_mermaid_tests():
    """Run all Mermaid tests and save results"""
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"mermaid_test_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    
    # Railway WebSocket URL
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = f"mermaid-test-{int(datetime.now().timestamp())}"
    user_id = "mermaid-test-user"
    full_url = f"{url}?session_id={session_id}&user_id={user_id}"
    
    print("=" * 80)
    print("COMPREHENSIVE MERMAID DIAGRAM TEST")
    print("=" * 80)
    print(f"Service URL: {url}")
    print(f"Output Directory: {output_dir}")
    print(f"Testing {len(MERMAID_TEST_CASES)} Mermaid diagram types")
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
            
            # Test each Mermaid diagram
            for i, test_case in enumerate(MERMAID_TEST_CASES, 1):
                print(f"\n[{i}/{len(MERMAID_TEST_CASES)}] Testing {test_case['diagram_type']}: {test_case['name']}")
                
                result = await test_single_mermaid(websocket, test_case, i)
                results.append(result)
                
                if result["success"]:
                    method = result['metadata'].get('generation_method', 'unknown')
                    llm_used = result['metadata'].get('llm_used', False)
                    print(f"  ✅ Success - Method: {method}, LLM: {llm_used}")
                    
                    # Save SVG content
                    if result.get("content"):
                        filename = f"{i:02d}_{test_case['diagram_type']}.svg"
                        filepath = output_dir / filename
                        
                        with open(filepath, "w") as f:
                            f.write(result["content"])
                        print(f"  💾 Saved to {filename}")
                        
                        result["saved_file"] = str(filepath)
                else:
                    print(f"  ❌ Failed: {result['error']}")
                
                # Small delay between tests
                await asyncio.sleep(1.0)
                
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
    
    return results, output_dir


def create_mermaid_html_viewer(results, output_dir):
    """Create HTML file to view all Mermaid test results"""
    
    # Calculate statistics
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    llm_successful = sum(1 for r in results if r["success"] and r.get("metadata", {}).get("llm_used"))
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagram Comprehensive Test Results</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1600px;
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
            color: #1F2937;
            border-bottom: 3px solid #3B82F6;
            padding-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .summary {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-label {{
            font-size: 12px;
            color: #6B7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #1F2937;
            margin-top: 5px;
        }}
        .diagram-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 30px;
        }}
        .diagram-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .diagram-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }}
        .diagram-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
        }}
        .diagram-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .diagram-type {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .diagram-content {{
            background: #f9fafb;
            padding: 20px;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: auto;
        }}
        .diagram-content svg {{
            max-width: 100%;
            height: auto;
        }}
        .metadata {{
            padding: 15px 20px;
            background: #fafafa;
            font-size: 13px;
            color: #6B7280;
            border-top: 1px solid #e5e7eb;
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
            font-weight: bold;
        }}
        .failure-badge {{
            color: #DC2626;
            font-weight: bold;
        }}
        .llm-badge {{
            background: #3B82F6;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            display: inline-block;
        }}
        .method-badge {{
            background: #10B981;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>
            <span>🎨</span>
            <span>Mermaid Diagram Comprehensive Test Results</span>
        </h1>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-label">Test Time</div>
                <div class="stat-value">{datetime.now().strftime("%H:%M:%S")}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Tests</div>
                <div class="stat-value">{len(results)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Successful</div>
                <div class="stat-value success-badge">{successful}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Failed</div>
                <div class="stat-value failure-badge">{failed}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">LLM Generated</div>
                <div class="stat-value" style="color: #3B82F6">{llm_successful}</div>
            </div>
        </div>
        
        <div class="diagram-grid">
"""
    
    # Add each diagram
    for i, result in enumerate(results, 1):
        html_content += f"""
        <div class="diagram-card">
            <div class="diagram-header">
                <div class="diagram-title">{i}. {result.get('name', result['diagram_type'])}</div>
                <div class="diagram-type">{result['diagram_type'].replace('_', ' ').title()}</div>
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
            method = metadata.get('generation_method', 'unknown')
            llm_used = metadata.get('llm_used', False)
            
            html_content += f"""
                <span class="method-badge">{method}</span>
                {' <span class="llm-badge">LLM</span>' if llm_used else ''}
                | <strong>Confidence:</strong> {metadata.get('confidence', 'N/A')}
                | <strong>Cached:</strong> {metadata.get('cache_hit', False)}
            """
        else:
            html_content += f"<strong>Error:</strong> {result.get('error', 'Unknown')}"
        
        html_content += """
            </div>
        </div>
        """
    
    html_content += """
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    html_path = output_dir / "mermaid_results.html"
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    return html_path


async def main():
    """Main test runner"""
    print("\nStarting comprehensive Mermaid diagram test...")
    
    # Run tests
    results, output_dir = await run_mermaid_tests()
    
    # Create HTML viewer
    html_path = create_mermaid_html_viewer(results, output_dir)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    llm_successful = sum(1 for r in results if r["success"] and r.get("metadata", {}).get("llm_used"))
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print(f"🤖 LLM Generated: {llm_successful}/{successful}")
    print(f"\n📁 Output Directory: {output_dir}")
    print(f"🌐 HTML Viewer: {html_path}")
    
    # Detailed breakdown
    print("\nDETAILED RESULTS:")
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        method = result.get("metadata", {}).get("generation_method", "failed") if result["success"] else "N/A"
        print(f"{status} {result['diagram_type']:20s} - {method:15s} - {result['name']}")
    
    return str(html_path)


if __name__ == "__main__":
    html_file = asyncio.run(main())
    print(f"\nTo view results, open: {html_file}")