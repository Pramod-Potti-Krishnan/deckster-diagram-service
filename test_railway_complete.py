#!/usr/bin/env python3
"""
Complete Railway Mermaid Testing with Visual HTML Output
Tests Railway API and creates interactive HTML with rendered diagrams
"""

import asyncio
import json
import websockets
import ssl
from datetime import datetime
import os
from pathlib import Path
import webbrowser
from typing import Dict, List, Any

# Comprehensive test cases for all Mermaid types
TEST_CASES = [
    {
        "name": "User Authentication Flow",
        "diagram_type": "flowchart",
        "content": """User Authentication Process with multiple decision points:
        1. User enters email and password on login page
        2. System validates email format (must be valid email)
        3. If invalid format, show error "Invalid email format" and return to step 1
        4. System queries database for user account
        5. If account not found, show error "Account does not exist" 
        6. If account exists, verify password hash against stored hash
        7. If password incorrect, increment failed attempts counter
        8. If failed attempts > 3, lock account for 15 minutes
        9. If password correct, generate JWT authentication token
        10. Store token in secure cookie
        11. Log successful authentication event
        12. Redirect user to dashboard
        13. Show welcome message with username"""
    },
    {
        "name": "E-commerce System Architecture",
        "diagram_type": "class_diagram", 
        "content": """Design an e-commerce system with these classes:
        
        User class:
        - Properties: userId (int), email (string), passwordHash (string), firstName (string), lastName (string), createdAt (date)
        - Methods: login(), logout(), updateProfile(), resetPassword(), getOrders()
        
        Product class:
        - Properties: productId (int), name (string), description (string), price (decimal), stock (int), category (string), imageUrl (string)
        - Methods: updateStock(quantity), applyDiscount(percentage), checkAvailability(), getReviews()
        
        ShoppingCart class:
        - Properties: cartId (int), userId (int), items (array), subtotal (decimal), tax (decimal), total (decimal)
        - Methods: addItem(product, quantity), removeItem(productId), updateQuantity(productId, quantity), calculateTotal(), checkout()
        
        Order class:
        - Properties: orderId (int), userId (int), orderDate (date), status (string), items (array), shippingAddress (string), total (decimal)
        - Methods: processPayment(), updateStatus(status), sendConfirmation(), trackShipment(), cancelOrder()
        
        Payment class:
        - Properties: paymentId (int), orderId (int), amount (decimal), method (string), transactionId (string), status (string)
        - Methods: authorize(), capture(), refund(), validateCard()
        
        Relationships:
        - User has one ShoppingCart
        - User has many Orders
        - ShoppingCart contains many Products
        - Order contains many Products
        - Order has one Payment
        - Product belongs to Category"""
    },
    {
        "name": "University Database Schema",
        "diagram_type": "entity_relationship",
        "content": """University database with detailed entities:
        
        Student entity:
        - studentId (PK, INT)
        - firstName (VARCHAR)
        - lastName (VARCHAR)
        - email (VARCHAR, UNIQUE)
        - dateOfBirth (DATE)
        - enrollmentDate (DATE)
        - major (VARCHAR)
        - gpa (DECIMAL)
        - credits (INT)
        
        Course entity:
        - courseId (PK, INT)
        - courseName (VARCHAR)
        - courseCode (VARCHAR, UNIQUE)
        - credits (INT)
        - department (VARCHAR)
        - maxEnrollment (INT)
        - semester (VARCHAR)
        
        Professor entity:
        - professorId (PK, INT)
        - firstName (VARCHAR)
        - lastName (VARCHAR)
        - email (VARCHAR, UNIQUE)
        - department (VARCHAR)
        - office (VARCHAR)
        - tenure (BOOLEAN)
        
        Enrollment entity:
        - enrollmentId (PK, INT)
        - studentId (FK to Student)
        - courseId (FK to Course)
        - semester (VARCHAR)
        - year (INT)
        - grade (VARCHAR)
        - enrollmentDate (DATE)
        
        Department entity:
        - deptId (PK, INT)
        - deptName (VARCHAR)
        - building (VARCHAR)
        - budget (DECIMAL)
        - chairProfessorId (FK to Professor)
        
        Relationships:
        - Student enrolls in many Courses (many-to-many through Enrollment)
        - Professor teaches many Courses (one-to-many)
        - Course belongs to one Department (many-to-one)
        - Department has one chair Professor (one-to-one)
        - Department has many Professors (one-to-many)"""
    },
    {
        "name": "Customer Purchase Journey",
        "diagram_type": "user_journey",
        "content": """Online laptop purchase journey with satisfaction scores:
        
        1. Awareness (3/5 satisfaction): User sees Instagram ad for laptop sale, clicks through to website
        2. Initial Browse (4/5 satisfaction): Lands on homepage, uses search to find laptops, applies filters for price range $800-1200
        3. Product Research (4/5 satisfaction): Compares 5 different laptop models, reads specifications, watches embedded review videos
        4. Review Analysis (5/5 satisfaction): Reads 50+ customer reviews, checks ratings distribution, looks at verified purchase badges
        5. Cart Addition (3/5 satisfaction): Adds laptop to cart, sees shipping cost of $49, feels disappointed about extra cost
        6. Coupon Search (2/5 satisfaction): Searches for promo codes, tries 3 codes that don't work, frustration builds
        7. Success (5/5 satisfaction): Finds 20% off code plus free shipping through email signup
        8. Checkout (4/5 satisfaction): Enters payment details, uses saved address, selects express shipping
        9. Confirmation (5/5 satisfaction): Receives order confirmation, gets tracking number immediately
        10. Delivery Wait (3/5 satisfaction): Waits 3 days, checks tracking multiple times, package delayed by one day
        11. Unboxing (5/5 satisfaction): Receives laptop in perfect condition, good packaging, includes surprise gift
        12. Setup (2/5 satisfaction): Has trouble with initial Windows setup, drivers need updating
        13. Support (5/5 satisfaction): Uses chat support, agent helps within 5 minutes, problem resolved
        14. Satisfaction (5/5 satisfaction): Writes 5-star review, recommends to 3 friends, joins brand community"""
    },
    {
        "name": "Software Development Project",
        "diagram_type": "gantt",
        "content": """Mobile app development project timeline (3 months):
        
        Week 1-2: Requirements Gathering
        - Stakeholder interviews
        - User research
        - Competitive analysis
        - Requirements documentation
        
        Week 2-3: UI/UX Design
        - Wireframing
        - Mockup creation
        - Design system setup
        - Prototype development
        
        Week 3-4: Technical Architecture
        - Technology stack selection
        - Database design
        - API specification
        - Security planning
        
        Week 4-6: Backend Development
        - API development
        - Database implementation
        - Authentication system
        - Third-party integrations
        
        Week 5-8: Frontend Development
        - UI component building
        - State management
        - API integration
        - Responsive design
        
        Week 8-9: Testing Phase
        - Unit testing
        - Integration testing
        - User acceptance testing
        - Bug fixing
        
        Week 10-11: Performance Optimization
        - Load testing
        - Speed optimization
        - Memory optimization
        - Security audit
        
        Week 11-12: Deployment
        - Production setup
        - App store submission
        - Launch preparation
        - Go-live"""
    },
    {
        "name": "Company Growth Timeline",
        "diagram_type": "timeline",
        "content": """Tech startup evolution from 2018 to 2024:
        
        2018 Q1: Company founded by 2 Stanford graduates in Palo Alto garage
        2018 Q3: First working prototype of AI assistant developed
        2018 Q4: Seed funding of $500K raised from angel investors
        
        2019 Q1: Beta launch with 100 invited users
        2019 Q2: Reached 1,000 beta users
        2019 Q3: Product pivot based on user feedback
        2019 Q4: Series A funding of $5M led by Sequoia Capital
        
        2020 Q1: Official product launch
        2020 Q2: COVID-19 causes remote work boom, user growth spikes
        2020 Q3: Reached 10,000 active users
        2020 Q4: First profitable quarter
        
        2021 Q1: Series B funding of $20M
        2021 Q2: Opened European office in London
        2021 Q3: Launched enterprise version
        2021 Q4: 100,000 users milestone
        
        2022 Q1: Acquired competitor TechAssist for $10M
        2022 Q2: Launched mobile apps for iOS and Android
        2022 Q3: Opened Asia Pacific office in Singapore
        2022 Q4: Series C funding of $50M at $500M valuation
        
        2023 Q1: Reached 1 million users
        2023 Q2: Launched AI-powered features
        2023 Q3: Partnership with Microsoft
        2023 Q4: Revenue exceeds $100M annually
        
        2024 Q1: IPO announcement
        2024 Q2: Public trading begins at $2B valuation"""
    },
    {
        "name": "Sprint Development Board",
        "diagram_type": "kanban",
        "content": """Current sprint kanban board for e-commerce platform:
        
        BACKLOG:
        - Implement OAuth 2.0 authentication
        - Add multi-language support (Spanish, French, German)
        - Create admin dashboard for analytics
        - Optimize database queries for product search
        - Add wishlist functionality
        
        TO DO:
        - Fix shopping cart persistence bug (High Priority)
        - Add email notification for order status
        - Implement product recommendation engine
        - Update payment gateway to Stripe v3
        - Write unit tests for checkout flow
        
        IN PROGRESS:
        - Develop user profile page (Assigned: John, 60% complete, 3 days in progress)
        - Integrate inventory management system (Assigned: Sarah, 40% complete, 2 days in progress)
        - Refactor product catalog API (Assigned: Mike, 80% complete, 4 days in progress)
        - Implement real-time chat support (Assigned: Lisa, 30% complete, 1 day in progress)
        
        IN REVIEW:
        - Mobile responsive design updates (Reviewer: Team Lead, 2 comments to address)
        - Search functionality improvements (Reviewer: QA Team, testing in progress)
        - Customer review system (Reviewer: Product Owner, awaiting approval)
        
        TESTING:
        - Order tracking feature (QA: Emma, 5 test cases passed, 2 failed)
        - Discount code system (QA: David, regression testing)
        - Export orders to CSV (QA: Automated tests running)
        
        DONE:
        - Setup CI/CD pipeline with GitHub Actions
        - Migrate database to PostgreSQL 14
        - Implement two-factor authentication
        - Fix critical XSS vulnerability
        - Add product image zoom feature
        - Optimize homepage load time (reduced by 40%)"""
    },
    {
        "name": "Microservices Architecture",
        "diagram_type": "architecture",
        "content": """E-commerce platform microservices architecture:
        
        FRONTEND LAYER:
        - React Web Application (Customer Portal)
        - React Native Mobile Apps (iOS and Android)
        - Vue.js Admin Dashboard
        - Next.js Marketing Website
        
        API GATEWAY:
        - Kong API Gateway
        - Rate limiting and throttling
        - API key management
        - Request routing
        - Load balancing
        
        MICROSERVICES:
        - User Service (Node.js/Express): User authentication, profiles, preferences
        - Product Service (Python/FastAPI): Product catalog, inventory, pricing
        - Order Service (Java/Spring Boot): Order processing, fulfillment, tracking
        - Payment Service (Go): Payment processing, refunds, invoicing
        - Notification Service (Node.js): Email, SMS, push notifications
        - Search Service (Elasticsearch): Product search, filters, recommendations
        - Analytics Service (Python): User behavior, sales reports, insights
        - Review Service (Ruby/Rails): Product reviews, ratings, moderation
        
        DATA LAYER:
        - PostgreSQL: User data, orders, transactions
        - MongoDB: Product catalog, reviews
        - Redis: Session cache, temporary data
        - Elasticsearch: Search indices
        - S3: Product images, documents
        
        MESSAGE QUEUE:
        - RabbitMQ: Async communication between services
        - Apache Kafka: Event streaming, audit logs
        
        INFRASTRUCTURE:
        - Kubernetes: Container orchestration
        - Docker: Containerization
        - AWS: Cloud hosting
        - CloudFlare: CDN and DDoS protection
        - New Relic: Application monitoring
        - ELK Stack: Logging and monitoring"""
    },
    {
        "name": "Risk Assessment Matrix",
        "diagram_type": "quadrant",
        "content": """Project risk assessment with Impact (Low to High) and Probability (Low to High):
        
        HIGH IMPACT, HIGH PROBABILITY (Critical Risks):
        - Data breach from cyber attack
        - Key team member resignation
        - Major scope creep from client
        - Budget overrun by 30%
        - Missed regulatory deadline
        
        HIGH IMPACT, LOW PROBABILITY (Major Risks):
        - Complete system failure
        - Natural disaster affecting data center
        - Sudden regulatory changes
        - Main vendor bankruptcy
        - Technology becomes obsolete
        
        LOW IMPACT, HIGH PROBABILITY (Minor Risks):
        - Minor bugs in non-critical features
        - Small schedule delays (1-2 days)
        - Team communication issues
        - Documentation delays
        - Minor integration problems
        
        LOW IMPACT, LOW PROBABILITY (Negligible Risks):
        - Office printer malfunction
        - Coffee machine breakdown
        - Parking issues
        - Minor version control conflicts
        - Slow internet for one day"""
    }
]


async def test_railway_api(test_case: dict, index: int) -> dict:
    """Test a single diagram with Railway API"""
    
    # Railway WebSocket URL
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = f"test-{int(datetime.now().timestamp())}-{index}"
    user_id = "test-user"
    full_url = f"{url}?session_id={session_id}&user_id={user_id}"
    
    # SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    result = {
        "name": test_case["name"],
        "diagram_type": test_case["diagram_type"],
        "success": False,
        "mermaid_code": None,
        "output_type": None,
        "metadata": {},
        "error": None,
        "raw_response": None
    }
    
    try:
        async with websockets.connect(full_url, ssl=ssl_context) as websocket:
            # Receive welcome
            welcome = await websocket.recv()
            
            # Send request
            request = {
                "type": "diagram_request",
                "correlation_id": f"test-{index}",
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
            
            await websocket.send(json.dumps(request))
            
            # Wait for response
            for _ in range(10):
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "diagram_response":
                        payload = response_data.get("payload", {})
                        result["raw_response"] = payload
                        result["success"] = True
                        
                        # Extract based on new response format
                        result["output_type"] = payload.get("output_type", "unknown")
                        
                        # Get Mermaid code
                        if payload.get("mermaid"):
                            result["mermaid_code"] = payload["mermaid"].get("code")
                        elif payload.get("metadata", {}).get("mermaid_code"):
                            result["mermaid_code"] = payload["metadata"]["mermaid_code"]
                        
                        # Get metadata
                        result["metadata"] = payload.get("metadata", {})
                        
                        # Get rendering info
                        result["rendering"] = payload.get("rendering", {})
                        
                        break
                        
                    elif response_data.get("type") == "error_response":
                        result["error"] = response_data.get("payload", {}).get("error_message", "Unknown error")
                        break
                        
                except asyncio.TimeoutError:
                    result["error"] = "Timeout waiting for response"
                    break
                    
    except Exception as e:
        result["error"] = str(e)
    
    return result


def create_html_report(results: List[dict]) -> str:
    """Create interactive HTML report with Mermaid.js rendering"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"railway_mermaid_output_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    
    # Count statistics
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    has_mermaid = sum(1 for r in results if r.get("mermaid_code"))
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Railway Mermaid Test Results - {timestamp}</title>
    
    <!-- Mermaid.js for rendering -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
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
            opacity: 0.9;
            margin-top: 5px;
        }}
        
        .diagrams {{
            padding: 40px;
        }}
        
        .diagram-card {{
            margin-bottom: 60px;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .diagram-header {{
            background: #f9fafb;
            padding: 20px 30px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .diagram-title {{
            font-size: 1.4em;
            font-weight: 600;
            color: #1f2937;
        }}
        
        .diagram-type {{
            display: inline-block;
            padding: 6px 12px;
            background: #3B82F6;
            color: white;
            border-radius: 6px;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        .output-type {{
            display: inline-block;
            padding: 4px 10px;
            margin-left: 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .output-type.mermaid {{
            background: #10b981;
            color: white;
        }}
        
        .output-type.svg {{
            background: #f59e0b;
            color: white;
        }}
        
        .output-type.error {{
            background: #ef4444;
            color: white;
        }}
        
        .diagram-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            min-height: 400px;
        }}
        
        .code-section {{
            background: #1f2937;
            padding: 30px;
            overflow: auto;
        }}
        
        .code-section h3 {{
            color: #f9fafb;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .code-block {{
            background: #111827;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
        }}
        
        .code-block pre {{
            color: #e5e7eb;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
            font-size: 0.9em;
            line-height: 1.5;
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .render-section {{
            background: white;
            padding: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        
        .render-section h3 {{
            color: #1f2937;
            margin-bottom: 20px;
            font-size: 1.1em;
            text-align: center;
        }}
        
        .mermaid-container {{
            width: 100%;
            max-width: 100%;
            overflow: auto;
            padding: 20px;
            background: #f9fafb;
            border-radius: 8px;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .mermaid {{
            max-width: 100%;
        }}
        
        .error-message {{
            background: #fee2e2;
            color: #dc2626;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            width: 100%;
        }}
        
        .metadata-section {{
            background: #f9fafb;
            padding: 20px 30px;
            border-top: 1px solid #e5e7eb;
            font-size: 0.9em;
            color: #6b7280;
        }}
        
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .metadata-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .metadata-label {{
            font-weight: 600;
            color: #4b5563;
        }}
        
        .metadata-value {{
            color: #1f2937;
        }}
        
        .copy-button {{
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 6px 12px;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85em;
            transition: background 0.2s;
        }}
        
        .copy-button:hover {{
            background: #2563eb;
        }}
        
        .no-mermaid {{
            color: #6b7280;
            font-style: italic;
            text-align: center;
            padding: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Railway Mermaid Diagram Test Results</h1>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{successful}</div>
                    <div class="stat-label">Successful</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{has_mermaid}</div>
                    <div class="stat-label">With Mermaid Code</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{round(successful/total*100 if total > 0 else 0)}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
            </div>
        </div>
        
        <div class="diagrams">
"""
    
    # Add each diagram result
    for i, result in enumerate(results, 1):
        output_type = result.get("output_type", "unknown")
        output_class = "error" if not result["success"] else output_type
        
        html_content += f"""
            <div class="diagram-card">
                <div class="diagram-header">
                    <div>
                        <span class="diagram-title">{i}. {result['name']}</span>
                        <span class="output-type {output_class}">{output_type.upper()}</span>
                    </div>
                    <span class="diagram-type">{result['diagram_type']}</span>
                </div>
                
                <div class="diagram-content">
                    <div class="code-section">
                        <h3>Mermaid Code</h3>
                        <div class="code-block" style="position: relative;">
        """
        
        if result.get("mermaid_code"):
            # Escape the Mermaid code for HTML
            escaped_code = result["mermaid_code"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_content += f"""
                            <button class="copy-button" onclick="copyCode(this)">Copy</button>
                            <pre>{escaped_code}</pre>
            """
        else:
            html_content += """
                            <div class="no-mermaid">No Mermaid code generated</div>
            """
        
        html_content += """
                        </div>
                    </div>
                    
                    <div class="render-section">
                        <h3>Rendered Diagram</h3>
                        <div class="mermaid-container">
        """
        
        if result.get("mermaid_code") and result["success"]:
            # Create unique ID for this Mermaid diagram
            mermaid_id = f"mermaid-{i}"
            html_content += f"""
                            <div id="{mermaid_id}" class="mermaid">
{result["mermaid_code"]}
                            </div>
            """
        elif result.get("error"):
            html_content += f"""
                            <div class="error-message">
                                Error: {result["error"]}
                            </div>
            """
        else:
            html_content += """
                            <div class="no-mermaid">No diagram to render</div>
            """
        
        html_content += """
                        </div>
                    </div>
                </div>
        """
        
        # Add metadata section
        metadata = result.get("metadata", {})
        rendering = result.get("rendering", {})
        
        html_content += """
                <div class="metadata-section">
                    <div class="metadata-grid">
        """
        
        if metadata.get("generation_method"):
            html_content += f"""
                        <div class="metadata-item">
                            <span class="metadata-label">Method:</span>
                            <span class="metadata-value">{metadata.get('generation_method', 'N/A')}</span>
                        </div>
            """
        
        if metadata.get("llm_model"):
            html_content += f"""
                        <div class="metadata-item">
                            <span class="metadata-label">Model:</span>
                            <span class="metadata-value">{metadata.get('llm_model', 'N/A')}</span>
                        </div>
            """
        
        if metadata.get("confidence") is not None:
            html_content += f"""
                        <div class="metadata-item">
                            <span class="metadata-label">Confidence:</span>
                            <span class="metadata-value">{metadata.get('confidence', 'N/A')}</span>
                        </div>
            """
        
        if rendering:
            html_content += f"""
                        <div class="metadata-item">
                            <span class="metadata-label">Server Rendered:</span>
                            <span class="metadata-value">{rendering.get('server_rendered', False)}</span>
                        </div>
                        <div class="metadata-item">
                            <span class="metadata-label">Render Status:</span>
                            <span class="metadata-value">{rendering.get('render_status', 'N/A')}</span>
                        </div>
            """
        
        html_content += """
                    </div>
                </div>
            </div>
        """
    
    html_content += """
        </div>
    </div>
    
    <script>
        // Initialize Mermaid
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'default',
            themeVariables: {
                primaryColor: '#3B82F6',
                primaryTextColor: '#fff',
                primaryBorderColor: '#2563eb',
                lineColor: '#6b7280',
                secondaryColor: '#f3f4f6',
                tertiaryColor: '#e5e7eb'
            }
        });
        
        // Copy code function
        function copyCode(button) {
            const pre = button.nextElementSibling;
            const text = pre.textContent;
            navigator.clipboard.writeText(text).then(() => {
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
            });
        }
    </script>
</body>
</html>
"""
    
    # Save HTML file
    html_path = output_dir / "results.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(html_path.absolute())


async def main():
    """Main test runner"""
    print("\n" + "=" * 80)
    print("RAILWAY MERMAID COMPREHENSIVE TEST WITH VISUAL OUTPUT")
    print("=" * 80)
    print(f"Testing {len(TEST_CASES)} diagram types")
    print("Connecting to Railway API...")
    
    results = []
    
    # Test each case
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] Testing: {test_case['name']}")
        print(f"  Type: {test_case['diagram_type']}")
        
        result = await test_railway_api(test_case, i)
        results.append(result)
        
        if result["success"]:
            print(f"  ✅ Success - Output Type: {result.get('output_type', 'unknown')}")
            if result.get("mermaid_code"):
                print(f"  📝 Mermaid code: {len(result['mermaid_code'])} chars")
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    # Generate HTML report
    print("\n" + "=" * 80)
    print("Generating HTML report...")
    html_path = create_html_report(results)
    
    print(f"\n✅ HTML report generated: {html_path}")
    
    # Open in browser
    print("Opening in browser...")
    webbrowser.open(f'file://{html_path}')
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    has_mermaid = sum(1 for r in results if r.get("mermaid_code"))
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {successful}/{len(results)} ({round(successful/len(results)*100)}%)")
    print(f"With Mermaid Code: {has_mermaid}")
    print(f"\n📊 View the interactive results in your browser!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())