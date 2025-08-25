#!/usr/bin/env python3
"""
Comprehensive Mermaid Diagram Testing with Failure Analysis
===========================================================

Tests ALL Mermaid diagram types supported by the system with:
- Generous timeouts to handle network latency
- Detailed failure analysis
- Visual HTML output with rendered diagrams
- Diagnostic information for troubleshooting
"""

import asyncio
import json
import websockets
import ssl
from datetime import datetime
from pathlib import Path
import webbrowser
from typing import Dict, List, Any, Optional
import time

# All 15 Mermaid diagram types with appropriate test content
MERMAID_TEST_CASES = [
    {
        "name": "Process Flow",
        "diagram_type": "flowchart",
        "content": """Create a flowchart showing a user authentication process:
        1. User enters email and password
        2. System validates email format
        3. If invalid format, show error and return to step 1
        4. Query database for user account
        5. If account not found, show "Account does not exist" error
        6. If account exists, verify password hash
        7. If password incorrect, increment failed attempts
        8. If failed attempts > 3, lock account for 15 minutes
        9. If password correct, generate JWT token
        10. Store token in secure cookie
        11. Redirect to dashboard"""
    },
    {
        "name": "UML Class Diagram",
        "diagram_type": "class_diagram",
        "content": """Design a class diagram for an e-commerce system:
        
        User class:
        - Properties: userId (int), email (string), firstName (string), lastName (string)
        - Methods: login(), logout(), updateProfile(), getOrders()
        
        Product class:
        - Properties: productId (int), name (string), price (decimal), stock (int)
        - Methods: updateStock(), applyDiscount(), checkAvailability()
        
        Order class:
        - Properties: orderId (int), userId (int), orderDate (date), total (decimal)
        - Methods: processPayment(), sendConfirmation(), cancelOrder()
        
        ShoppingCart class:
        - Properties: cartId (int), userId (int), items (array)
        - Methods: addItem(), removeItem(), checkout()
        
        Relationships:
        - User has one ShoppingCart
        - User has many Orders
        - Order contains many Products
        - ShoppingCart contains many Products"""
    },
    {
        "name": "Database Schema",
        "diagram_type": "entity_relationship",
        "content": """Create an ER diagram for a university database:
        
        Student entity:
        - studentId (PK), firstName, lastName, email, major, gpa
        
        Course entity:
        - courseId (PK), courseName, courseCode, credits, department
        
        Professor entity:
        - professorId (PK), firstName, lastName, department, office
        
        Enrollment entity:
        - enrollmentId (PK), studentId (FK), courseId (FK), semester, grade
        
        Department entity:
        - deptId (PK), deptName, building, budget
        
        Relationships:
        - Students enroll in many Courses (many-to-many through Enrollment)
        - Professors teach many Courses (one-to-many)
        - Courses belong to one Department (many-to-one)
        - Departments have many Professors (one-to-many)"""
    },
    {
        "name": "Customer Experience Journey",
        "diagram_type": "user_journey",
        "content": """Map a customer's journey buying a laptop online:
        
        1. Awareness (3/5): Sees Instagram ad for laptop sale
        2. Browse (4/5): Visits website, searches for laptops
        3. Research (4/5): Compares 5 models, reads reviews
        4. Decision (5/5): Finds perfect laptop with good reviews
        5. Cart (3/5): Adds to cart, sees shipping cost
        6. Discount (2/5): Searches for promo codes, frustration
        7. Success (5/5): Finds 20% off code through email signup
        8. Checkout (4/5): Enters payment details
        9. Confirmation (5/5): Receives order confirmation
        10. Delivery (3/5): Waits 3 days, package delayed
        11. Unboxing (5/5): Perfect condition
        12. Setup (3/5): Some driver issues
        13. Support (5/5): Chat support helps quickly
        14. Satisfaction (5/5): Writes positive review"""
    },
    {
        "name": "Project Timeline",
        "diagram_type": "gantt",
        "content": """Create a Gantt chart for a 3-month mobile app project:
        
        Week 1-2: Requirements Gathering
        Week 2-3: UI/UX Design (overlaps with requirements)
        Week 3-4: Technical Architecture
        Week 4-6: Backend Development
        Week 5-8: Frontend Development (starts week into backend)
        Week 8-9: Testing Phase
        Week 9-10: Bug Fixes
        Week 10-11: Performance Optimization
        Week 11-12: Deployment and Launch
        
        Critical milestones:
        - Week 2: Requirements approved
        - Week 4: Design finalized
        - Week 8: Alpha version ready
        - Week 10: Beta testing complete
        - Week 12: Production launch"""
    },
    {
        "name": "Risk Assessment",
        "diagram_type": "quadrant",
        "content": """Create a risk quadrant chart with Impact (Low to High) and Probability (Low to High):
        
        High Impact, High Probability (Critical):
        - Data breach from cyber attack
        - Key team member resignation
        - Major scope creep
        - Budget overrun by 30%
        
        High Impact, Low Probability (Major):
        - Complete system failure
        - Natural disaster
        - Vendor bankruptcy
        - Technology obsolescence
        
        Low Impact, High Probability (Minor):
        - Minor bugs in features
        - Small schedule delays
        - Documentation delays
        - Team conflicts
        
        Low Impact, Low Probability (Negligible):
        - Office equipment failure
        - Parking issues
        - Coffee machine breakdown
        - Minor version conflicts"""
    },
    {
        "name": "Company Evolution",
        "diagram_type": "timeline",
        "content": """Show tech startup growth from 2018 to 2024:
        
        2018 Q1: Company founded by 2 Stanford graduates
        2018 Q3: First prototype developed
        2018 Q4: Seed funding $500K raised
        
        2019 Q2: Beta launch with 100 users
        2019 Q4: Series A funding $5M
        
        2020 Q2: COVID causes remote work boom, growth spikes
        2020 Q4: First profitable quarter
        
        2021 Q2: European expansion
        2021 Q4: 100,000 users milestone
        
        2022 Q2: Mobile apps launched
        2022 Q4: Series C $50M at $500M valuation
        
        2023 Q2: AI features launched
        2023 Q4: Revenue exceeds $100M
        
        2024 Q1: IPO announcement
        2024 Q2: Public trading at $2B valuation"""
    },
    {
        "name": "Sprint Board",
        "diagram_type": "kanban",
        "content": """Current sprint kanban board:
        
        BACKLOG:
        - Implement OAuth authentication
        - Add multi-language support
        - Create admin dashboard
        
        TO DO:
        - Fix shopping cart bug
        - Add email notifications
        - Implement recommendation engine
        
        IN PROGRESS:
        - Develop user profile page (John, 60% done)
        - Integrate inventory system (Sarah, 40% done)
        
        IN REVIEW:
        - Mobile responsive design (awaiting approval)
        - Search improvements (testing)
        
        TESTING:
        - Order tracking feature (5 tests passed, 2 failed)
        
        DONE:
        - Setup CI/CD pipeline
        - Migrate to PostgreSQL
        - Implement 2FA"""
    },
    {
        "name": "System Architecture",
        "diagram_type": "architecture",
        "content": """Microservices architecture for e-commerce:
        
        Frontend Layer:
        - React Web App
        - React Native Mobile
        - Admin Dashboard (Vue.js)
        
        API Gateway:
        - Kong Gateway
        - Rate limiting
        - Authentication
        
        Microservices:
        - User Service (Node.js): Authentication, profiles
        - Product Service (Python): Catalog, inventory
        - Order Service (Java): Processing, fulfillment
        - Payment Service (Go): Transactions, refunds
        - Notification Service (Node.js): Email, SMS
        
        Data Layer:
        - PostgreSQL: Users, orders
        - MongoDB: Products, reviews
        - Redis: Cache, sessions
        - S3: Media storage
        
        Infrastructure:
        - Kubernetes orchestration
        - AWS hosting
        - CloudFlare CDN"""
    },
    {
        "name": "API Sequence",
        "diagram_type": "sequence",
        "content": """User login sequence with 2FA:
        
        1. User submits email and password to Frontend
        2. Frontend sends credentials to API Gateway
        3. API Gateway forwards to Auth Service
        4. Auth Service queries User Database
        5. Database returns user record
        6. Auth Service validates password hash
        7. Auth Service generates 2FA code
        8. Auth Service sends code via SMS Service
        9. SMS Service confirms delivery
        10. Auth Service returns "2FA required" to Frontend
        11. User enters 2FA code
        12. Frontend sends code to Auth Service
        13. Auth Service validates code
        14. Auth Service generates JWT token
        15. Auth Service returns token to Frontend
        16. Frontend stores token and redirects to dashboard"""
    },
    {
        "name": "Budget Distribution",
        "diagram_type": "pie_chart",
        "content": """Q4 2024 IT budget allocation:
        
        - Infrastructure & Cloud: 35%
        - Development Team Salaries: 30%
        - Software Licenses: 15%
        - Security & Compliance: 10%
        - Training & Conferences: 5%
        - Hardware & Equipment: 3%
        - Miscellaneous: 2%"""
    },
    {
        "name": "User Journey Map",
        "diagram_type": "journey_map",
        "content": """New user onboarding journey:
        
        Step 1: User lands on homepage (Excitement: High)
        Step 2: Clicks "Sign Up" button (Curiosity: High)
        Step 3: Fills registration form (Effort: Medium)
        Step 4: Email verification required (Friction: Medium)
        Step 5: Checks email and clicks link (Relief: Medium)
        Step 6: Profile setup wizard starts (Interest: High)
        Step 7: Adds personal information (Effort: Low)
        Step 8: Chooses preferences (Engagement: High)
        Step 9: Tutorial walkthrough (Learning: High)
        Step 10: First feature usage (Success: High)
        Step 11: Invites team members (Advocacy: High)"""
    },
    {
        "name": "Concept Mind Map",
        "diagram_type": "mind_map",
        "content": """Digital Marketing Strategy mind map:
        
        Central: Digital Marketing
        
        Branch 1: Content Marketing
        - Blog posts
        - Video content
        - Infographics
        - Podcasts
        
        Branch 2: Social Media
        - Facebook ads
        - Instagram stories
        - LinkedIn articles
        - Twitter engagement
        
        Branch 3: SEO
        - Keyword research
        - On-page optimization
        - Link building
        - Technical SEO
        
        Branch 4: Email Marketing
        - Newsletter
        - Drip campaigns
        - Segmentation
        - A/B testing
        
        Branch 5: Analytics
        - Google Analytics
        - Conversion tracking
        - ROI measurement
        - User behavior"""
    },
    {
        "name": "Network Topology",
        "diagram_type": "network",
        "content": """Corporate network diagram:
        
        Internet Gateway connects to:
        - Firewall (primary defense)
        
        Firewall connects to:
        - DMZ with Web Server and Mail Server
        - Core Switch
        
        Core Switch connects to:
        - Database Server (isolated)
        - Application Servers (cluster of 3)
        - Department Switches (3 branches)
        
        Department Switch 1: HR (20 workstations)
        Department Switch 2: Engineering (50 workstations)
        Department Switch 3: Sales (30 workstations)
        
        Each department also has:
        - Wireless Access Point
        - Network Printer
        - File Server"""
    },
    {
        "name": "Learning Concept Map",
        "diagram_type": "concept_map",
        "content": """Machine Learning concepts and relationships:
        
        Machine Learning (root concept)
        
        Connects to Supervised Learning:
        - Uses labeled data
        - Includes Classification (predicts categories)
        - Includes Regression (predicts values)
        - Examples: Decision Trees, SVM, Neural Networks
        
        Connects to Unsupervised Learning:
        - Uses unlabeled data
        - Includes Clustering (groups similar data)
        - Includes Dimensionality Reduction
        - Examples: K-means, PCA, Autoencoders
        
        Connects to Reinforcement Learning:
        - Uses rewards and penalties
        - Agent learns from environment
        - Examples: Q-learning, Policy Gradient
        
        All connect to Deep Learning:
        - Multiple neural network layers
        - Includes CNNs for images
        - Includes RNNs for sequences
        - Includes Transformers for NLP"""
    }
]


class DiagramTestResult:
    """Store test results for a single diagram"""
    
    def __init__(self, test_case: Dict[str, Any]):
        self.name = test_case["name"]
        self.diagram_type = test_case["diagram_type"]
        self.content = test_case["content"]
        self.success = False
        self.mermaid_code = None
        self.output_type = None
        self.error = None
        self.error_stage = None  # 'connection', 'timeout', 'generation', 'rendering'
        self.response_time_ms = None
        self.metadata = {}
        self.raw_response = None
        self.attempts = 0
        self.warnings = []


async def test_single_diagram(test_case: Dict[str, Any], index: int, timeout: int = 20) -> DiagramTestResult:
    """Test a single diagram with generous timeout and error tracking"""
    
    result = DiagramTestResult(test_case)
    start_time = time.time()
    
    # Railway WebSocket URL
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = f"comprehensive-test-{datetime.now().timestamp()}-{index}"
    user_id = "test-comprehensive"
    full_url = f"{url}?session_id={session_id}&user_id={user_id}"
    
    # SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        # Attempt connection
        result.attempts += 1
        async with websockets.connect(full_url, ssl=ssl_context, ping_timeout=30) as websocket:
            # Receive welcome message
            try:
                welcome = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            except asyncio.TimeoutError:
                result.error = "Timeout waiting for welcome message"
                result.error_stage = "connection"
                return result
            
            # Prepare request
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
            
            # Send request
            await websocket.send(json.dumps(request))
            
            # Wait for response with generous timeout
            response_received = False
            for attempt in range(3):  # Try up to 3 times to receive response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "diagram_response":
                        payload = response_data.get("payload", {})
                        result.raw_response = payload
                        result.success = True
                        response_received = True
                        
                        # Extract output type
                        result.output_type = payload.get("output_type", "unknown")
                        
                        # Extract Mermaid code from various possible locations
                        if payload.get("mermaid"):
                            result.mermaid_code = payload["mermaid"].get("code")
                        elif payload.get("metadata", {}).get("mermaid_code"):
                            result.mermaid_code = payload["metadata"]["mermaid_code"]
                        
                        # Extract metadata
                        result.metadata = payload.get("metadata", {})
                        
                        # Check for rendering info
                        rendering = payload.get("rendering", {})
                        if rendering.get("render_error"):
                            result.warnings.append(f"Render error: {rendering['render_error']}")
                        
                        break
                        
                    elif response_data.get("type") == "error_response":
                        result.error = response_data.get("payload", {}).get("error_message", "Unknown error")
                        result.error_stage = "generation"
                        break
                        
                    elif response_data.get("type") == "status_update":
                        # Log status but continue waiting
                        status = response_data.get("payload", {}).get("status")
                        if status:
                            result.warnings.append(f"Status: {status}")
                        
                except asyncio.TimeoutError:
                    if attempt == 2:  # Last attempt
                        result.error = f"Timeout after {timeout}s (attempt {attempt + 1})"
                        result.error_stage = "timeout"
                    else:
                        result.warnings.append(f"Timeout attempt {attempt + 1}, retrying...")
                        await asyncio.sleep(1)  # Brief pause before retry
                        
            if not response_received and not result.error:
                result.error = "No valid response received"
                result.error_stage = "generation"
                
    except websockets.exceptions.WebSocketException as e:
        result.error = f"WebSocket error: {str(e)}"
        result.error_stage = "connection"
    except Exception as e:
        result.error = f"Unexpected error: {str(e)}"
        result.error_stage = "connection"
    
    # Calculate response time
    result.response_time_ms = int((time.time() - start_time) * 1000)
    
    return result


def analyze_failures(results: List[DiagramTestResult]) -> Dict[str, Any]:
    """Analyze failure patterns across all tests"""
    
    analysis = {
        "total_tests": len(results),
        "successful": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "success_rate": 0,
        "failures_by_stage": {},
        "failures_by_type": {},
        "average_response_time_ms": 0,
        "timeout_failures": [],
        "generation_failures": [],
        "rendering_warnings": [],
        "unsupported_types": []
    }
    
    # Calculate success rate
    if analysis["total_tests"] > 0:
        analysis["success_rate"] = round(analysis["successful"] / analysis["total_tests"] * 100, 1)
    
    # Analyze failures
    response_times = []
    for result in results:
        if result.response_time_ms:
            response_times.append(result.response_time_ms)
        
        if not result.success:
            # Track by stage
            stage = result.error_stage or "unknown"
            analysis["failures_by_stage"][stage] = analysis["failures_by_stage"].get(stage, 0) + 1
            
            # Track by diagram type
            analysis["failures_by_type"][result.diagram_type] = analysis["failures_by_type"].get(result.diagram_type, 0) + 1
            
            # Categorize failures
            if result.error_stage == "timeout":
                analysis["timeout_failures"].append(result.diagram_type)
            elif result.error_stage == "generation":
                analysis["generation_failures"].append({
                    "type": result.diagram_type,
                    "error": result.error
                })
                
                # Check for unsupported type indicators
                if result.error and ("not supported" in result.error.lower() or 
                                    "unsupported" in result.error.lower() or
                                    "failed" in result.error.lower()):
                    analysis["unsupported_types"].append(result.diagram_type)
        
        # Check for rendering warnings even in successful cases
        if result.warnings:
            for warning in result.warnings:
                if "render" in warning.lower():
                    analysis["rendering_warnings"].append({
                        "type": result.diagram_type,
                        "warning": warning
                    })
    
    # Calculate average response time
    if response_times:
        analysis["average_response_time_ms"] = round(sum(response_times) / len(response_times))
    
    return analysis


def create_comprehensive_html_report(results: List[DiagramTestResult], analysis: Dict[str, Any]) -> str:
    """Create detailed HTML report with visual rendering and failure analysis"""
    
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Mermaid Testing Report</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f0f2f5;
            padding: 0;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 20px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: -30px auto 40px;
            padding: 0 20px;
        }}
        
        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .summary-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .summary-label {{
            font-size: 0.9em;
            color: #6b7280;
            margin-top: 8px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 0 20px 40px;
        }}
        
        .section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #1f2937;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }}
        
        .failure-analysis {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .analysis-box {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #ef4444;
        }}
        
        .analysis-box h3 {{
            color: #dc2626;
            margin-bottom: 10px;
        }}
        
        .diagram-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        
        .diagram-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .diagram-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        
        .card-header {{
            padding: 20px;
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .card-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: #1f2937;
        }}
        
        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .status-success {{
            background: #10b981;
            color: white;
        }}
        
        .status-failed {{
            background: #ef4444;
            color: white;
        }}
        
        .status-warning {{
            background: #f59e0b;
            color: white;
        }}
        
        .card-body {{
            padding: 20px;
        }}
        
        .mermaid-container {{
            background: #f9fafb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            min-height: 200px;
            max-height: 400px;
            overflow: auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .mermaid {{
            max-width: 100%;
        }}
        
        .error-box {{
            background: #fee2e2;
            color: #dc2626;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }}
        
        .warning-box {{
            background: #fef3c7;
            color: #d97706;
            padding: 10px;
            border-radius: 6px;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        
        .code-block {{
            background: #1f2937;
            color: #e5e7eb;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'SF Mono', Monaco, Consolas, monospace;
            font-size: 0.85em;
            line-height: 1.5;
            margin-bottom: 15px;
            max-height: 300px;
            position: relative;
        }}
        
        .copy-btn {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: #3b82f6;
            color: white;
            border: none;
            padding: 4px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
        }}
        
        .copy-btn:hover {{
            background: #2563eb;
        }}
        
        .metadata {{
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            font-size: 0.85em;
            color: #6b7280;
        }}
        
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}
        
        .meta-item {{
            display: flex;
            justify-content: space-between;
        }}
        
        .meta-label {{
            font-weight: 600;
            color: #4b5563;
        }}
        
        .filter-buttons {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 8px 16px;
            border: 1px solid #e5e7eb;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .filter-btn:hover {{
            background: #f9fafb;
        }}
        
        .filter-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        
        .hidden {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔬 Comprehensive Mermaid Testing Report</h1>
        <p>Testing all {len(results)} Mermaid diagram types with Gemini 2.5 Flash</p>
        <p style="font-size: 0.9em; margin-top: 10px;">{timestamp}</p>
    </div>
    
    <div class="summary-grid">
        <div class="summary-card">
            <div class="summary-value">{analysis['total_tests']}</div>
            <div class="summary-label">Total Tests</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">{analysis['successful']}</div>
            <div class="summary-label">Successful</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">{analysis['failed']}</div>
            <div class="summary-label">Failed</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">{analysis['success_rate']}%</div>
            <div class="summary-label">Success Rate</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">{analysis['average_response_time_ms']}ms</div>
            <div class="summary-label">Avg Response</div>
        </div>
    </div>
    
    <div class="container">
"""
    
    # Add failure analysis section if there are failures
    if analysis['failed'] > 0:
        html += """
        <div class="section">
            <h2 class="section-title">📊 Failure Analysis</h2>
            <div class="failure-analysis">
"""
        
        # Failures by stage
        if analysis['failures_by_stage']:
            html += """
                <div class="analysis-box">
                    <h3>Failures by Stage</h3>
                    <ul>
"""
            for stage, count in analysis['failures_by_stage'].items():
                html += f"<li><strong>{stage}:</strong> {count} failures</li>"
            html += """
                    </ul>
                </div>
"""
        
        # Timeout failures
        if analysis['timeout_failures']:
            html += """
                <div class="analysis-box">
                    <h3>Timeout Failures</h3>
                    <p>Diagrams that exceeded 20s timeout:</p>
                    <ul>
"""
            for dtype in analysis['timeout_failures']:
                html += f"<li>{dtype}</li>"
            html += """
                    </ul>
                </div>
"""
        
        # Unsupported types
        if analysis['unsupported_types']:
            html += """
                <div class="analysis-box">
                    <h3>Possibly Unsupported Types</h3>
                    <p>These diagram types may not be fully supported:</p>
                    <ul>
"""
            for dtype in set(analysis['unsupported_types']):
                html += f"<li>{dtype}</li>"
            html += """
                    </ul>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
    
    # Add filter buttons
    html += """
        <div class="section">
            <h2 class="section-title">📈 Diagram Results</h2>
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterDiagrams('all')">All ({0})</button>
                <button class="filter-btn" onclick="filterDiagrams('success')">✅ Successful ({1})</button>
                <button class="filter-btn" onclick="filterDiagrams('failed')">❌ Failed ({2})</button>
            </div>
            <div class="diagram-grid" id="diagram-grid">
""".format(len(results), analysis['successful'], analysis['failed'])
    
    # Add each diagram result
    for i, result in enumerate(results, 1):
        status_class = "status-success" if result.success else "status-failed"
        status_text = "Success" if result.success else "Failed"
        filter_class = "success" if result.success else "failed"
        
        html += f"""
            <div class="diagram-card {filter_class}" data-status="{filter_class}">
                <div class="card-header">
                    <div class="card-title">{i}. {result.name}</div>
                    <div>
                        <span class="status-badge {status_class}">{status_text}</span>
                        <span class="status-badge" style="background: #6366f1; color: white; margin-left: 8px;">
                            {result.diagram_type}
                        </span>
                    </div>
                </div>
                <div class="card-body">
"""
        
        if result.success and result.mermaid_code:
            # Successful diagram with Mermaid code
            escaped_code = result.mermaid_code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            html += f"""
                    <div class="mermaid-container">
                        <div class="mermaid">
{result.mermaid_code}
                        </div>
                    </div>
                    
                    <div class="code-block">
                        <button class="copy-btn" onclick="copyCode(this, 'code-{i}')">Copy</button>
                        <pre id="code-{i}">{escaped_code}</pre>
                    </div>
"""
            
            # Add warnings if any
            if result.warnings:
                html += '<div class="warning-box">⚠️ Warnings: ' + ', '.join(result.warnings) + '</div>'
            
        else:
            # Failed diagram
            html += f"""
                    <div class="error-box">
                        <strong>Error Stage:</strong> {result.error_stage or 'Unknown'}<br>
                        <strong>Error:</strong> {result.error or 'No error message'}
                    </div>
"""
            
            if result.warnings:
                html += '<div class="warning-box">⚠️ ' + ', '.join(result.warnings) + '</div>'
        
        # Add metadata
        html += f"""
                    <div class="metadata">
                        <div class="meta-grid">
                            <div class="meta-item">
                                <span class="meta-label">Response Time:</span>
                                <span>{result.response_time_ms}ms</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Output Type:</span>
                                <span>{result.output_type or 'N/A'}</span>
                            </div>
"""
        
        if result.metadata:
            if result.metadata.get('generation_method'):
                html += f"""
                            <div class="meta-item">
                                <span class="meta-label">Method:</span>
                                <span>{result.metadata['generation_method']}</span>
                            </div>
"""
            if result.metadata.get('llm_model'):
                html += f"""
                            <div class="meta-item">
                                <span class="meta-label">Model:</span>
                                <span>{result.metadata['llm_model']}</span>
                            </div>
"""
        
        html += """
                        </div>
                    </div>
                </div>
            </div>
"""
    
    html += """
            </div>
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
                secondaryColor: '#f3f4f6'
            },
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true
            }
        });
        
        // Copy code function
        function copyCode(button, codeId) {
            const codeElement = document.getElementById(codeId);
            const text = codeElement.textContent;
            
            navigator.clipboard.writeText(text).then(() => {
                const originalText = button.textContent;
                button.textContent = '✓ Copied!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
            });
        }
        
        // Filter diagrams
        function filterDiagrams(status) {
            const cards = document.querySelectorAll('.diagram-card');
            const buttons = document.querySelectorAll('.filter-btn');
            
            // Update button states
            buttons.forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent.toLowerCase().includes(status) || 
                    (status === 'all' && btn.textContent.startsWith('All'))) {
                    btn.classList.add('active');
                }
            });
            
            // Show/hide cards
            cards.forEach(card => {
                if (status === 'all') {
                    card.classList.remove('hidden');
                } else if (card.dataset.status === status) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        }
    </script>
</body>
</html>
"""
    
    # Save HTML file
    output_dir = Path(f"mermaid_comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_dir.mkdir(exist_ok=True)
    html_path = output_dir / "report.html"
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Also save analysis as JSON
    analysis_path = output_dir / "analysis.json"
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    return str(html_path.absolute())


async def main():
    """Run comprehensive Mermaid testing"""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE MERMAID DIAGRAM TESTING")
    print("="*80)
    print(f"Testing {len(MERMAID_TEST_CASES)} Mermaid diagram types")
    print("Using Gemini 2.5 Flash for LLM generation")
    print("Timeout: 20 seconds per diagram")
    print("Delay between tests: 3 seconds\n")
    
    results = []
    
    # Test each diagram type
    for i, test_case in enumerate(MERMAID_TEST_CASES, 1):
        print(f"[{i}/{len(MERMAID_TEST_CASES)}] Testing: {test_case['name']} ({test_case['diagram_type']})")
        
        # Run test with generous timeout
        result = await test_single_diagram(test_case, i, timeout=20)
        results.append(result)
        
        # Print result
        if result.success:
            code_length = len(result.mermaid_code) if result.mermaid_code else 0
            print(f"  ✅ Success - {code_length} chars, {result.response_time_ms}ms")
        else:
            print(f"  ❌ Failed - {result.error_stage}: {result.error}")
            if result.warnings:
                print(f"     Warnings: {', '.join(result.warnings)}")
        
        # Generous delay between tests to avoid rate limiting
        if i < len(MERMAID_TEST_CASES):
            print("  ⏳ Waiting 3 seconds before next test...")
            await asyncio.sleep(3)
    
    # Analyze failures
    print("\n" + "="*80)
    print("ANALYZING RESULTS...")
    analysis = analyze_failures(results)
    
    # Print analysis summary
    print(f"\n📊 SUMMARY:")
    print(f"  Total Tests: {analysis['total_tests']}")
    print(f"  Successful: {analysis['successful']} ({analysis['success_rate']}%)")
    print(f"  Failed: {analysis['failed']}")
    print(f"  Average Response Time: {analysis['average_response_time_ms']}ms")
    
    if analysis['failures_by_stage']:
        print(f"\n❌ FAILURES BY STAGE:")
        for stage, count in analysis['failures_by_stage'].items():
            print(f"  {stage}: {count}")
    
    if analysis['unsupported_types']:
        print(f"\n⚠️  POSSIBLY UNSUPPORTED TYPES:")
        for dtype in set(analysis['unsupported_types']):
            print(f"  - {dtype}")
    
    # Generate HTML report
    print("\n" + "="*80)
    print("Generating comprehensive HTML report...")
    html_path = create_comprehensive_html_report(results, analysis)
    
    print(f"✅ Report generated: {html_path}")
    print("Opening in browser...")
    webbrowser.open(f'file://{html_path}')
    
    print("\n🎨 Check your browser for the visual report with:")
    print("  - Rendered Mermaid diagrams")
    print("  - Detailed failure analysis")
    print("  - Filter by success/failure status")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())