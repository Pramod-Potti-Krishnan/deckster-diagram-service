"""
Performance testing suite using Locust for Diagram Microservice v2.

This file tests WebSocket connections, diagram generation, and system load.
"""

from locust import User, task, between, events
from locust.exception import LocustError
import websocket
import json
import time
import random
import uuid
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketClient:
    """WebSocket client for Locust testing"""
    
    def __init__(self, host: str, user_id: str):
        self.host = host.replace("http://", "ws://").replace("https://", "wss://")
        self.user_id = user_id
        self.session_id = f"perf-test-{uuid.uuid4()}"
        self.ws = None
        self.connected = False
        self.request_times = {}
        
    def connect(self):
        """Establish WebSocket connection"""
        try:
            url = f"{self.host}/ws?session_id={self.session_id}&user_id={self.user_id}"
            self.ws = websocket.WebSocket()
            
            start_time = time.time()
            self.ws.connect(url)
            connection_time = int((time.time() - start_time) * 1000)
            
            # Receive welcome message
            welcome = json.loads(self.ws.recv())
            
            if welcome.get("type") == "connection_established":
                self.connected = True
                events.request.fire(
                    request_type="WebSocket",
                    name="connect",
                    response_time=connection_time,
                    response_length=len(json.dumps(welcome)),
                    exception=None,
                    context={}
                )
                return True
            else:
                raise Exception("Invalid welcome message")
                
        except Exception as e:
            events.request.fire(
                request_type="WebSocket",
                name="connect",
                response_time=0,
                response_length=0,
                exception=e,
                context={}
            )
            return False
    
    def send_diagram_request(self, diagram_type: str, content: str) -> Optional[Dict]:
        """Send diagram generation request"""
        if not self.connected:
            return None
        
        request_id = f"req-{uuid.uuid4()}"
        request = {
            "type": "diagram_request",
            "request_id": request_id,
            "data": {
                "diagram_type": diagram_type,
                "content": content,
                "theme": {
                    "primaryColor": "#3B82F6",
                    "secondaryColor": "#60A5FA"
                }
            }
        }
        
        try:
            start_time = time.time()
            self.request_times[request_id] = start_time
            
            # Send request
            self.ws.send(json.dumps(request))
            
            # Wait for response
            max_wait = 10  # seconds
            response_received = False
            response_data = None
            
            while time.time() - start_time < max_wait:
                try:
                    message = json.loads(self.ws.recv())
                    msg_type = message.get("type")
                    
                    if msg_type == "diagram_response" and message.get("request_id") == request_id:
                        response_time = int((time.time() - start_time) * 1000)
                        response_data = message.get("data", {})
                        
                        events.request.fire(
                            request_type="WebSocket",
                            name=f"generate_{diagram_type}",
                            response_time=response_time,
                            response_length=len(json.dumps(message)),
                            exception=None,
                            context={"diagram_type": diagram_type}
                        )
                        response_received = True
                        break
                    
                    elif msg_type == "error" and message.get("request_id") == request_id:
                        raise Exception(message.get("error", {}).get("message", "Unknown error"))
                        
                except websocket.WebSocketTimeoutException:
                    continue
            
            if not response_received:
                raise Exception("Response timeout")
            
            return response_data
            
        except Exception as e:
            events.request.fire(
                request_type="WebSocket",
                name=f"generate_{diagram_type}",
                response_time=0,
                response_length=0,
                exception=e,
                context={"diagram_type": diagram_type}
            )
            return None
    
    def send_ping(self):
        """Send ping message"""
        if not self.connected:
            return
        
        try:
            start_time = time.time()
            self.ws.send(json.dumps({"type": "ping"}))
            
            # Wait for pong
            message = json.loads(self.ws.recv())
            if message.get("type") == "pong":
                response_time = int((time.time() - start_time) * 1000)
                
                events.request.fire(
                    request_type="WebSocket",
                    name="ping",
                    response_time=response_time,
                    response_length=len(json.dumps(message)),
                    exception=None,
                    context={}
                )
        except Exception as e:
            events.request.fire(
                request_type="WebSocket",
                name="ping",
                response_time=0,
                response_length=0,
                exception=e,
                context={}
            )
    
    def disconnect(self):
        """Close WebSocket connection"""
        if self.ws:
            try:
                self.ws.close()
                self.connected = False
                events.request.fire(
                    request_type="WebSocket",
                    name="disconnect",
                    response_time=0,
                    response_length=0,
                    exception=None,
                    context={}
                )
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")


class DiagramUser(User):
    """Simulated user for diagram generation"""
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.user_id = f"load-test-user-{uuid.uuid4()}"
        
        # Diagram types and sample content
        self.diagram_types = [
            ("pyramid_3_level", "Foundation\nStructure\nPeak"),
            ("cycle_3_step", "Plan\nExecute\nReview"),
            ("venn_2_circle", "Set A: Items 1, 2, 3\nSet B: Items 3, 4, 5\nOverlap: Item 3"),
            ("matrix_2x2", "Q1: Important/Urgent\nQ2: Important/Not Urgent\nQ3: Not Important/Urgent\nQ4: Not Important/Not Urgent"),
            ("funnel", "Awareness: 1000\nInterest: 750\nDesire: 500\nAction: 250"),
            ("honeycomb_5", "Core\nNode 1\nNode 2\nNode 3\nNode 4"),
            ("timeline_horizontal", "2024 Q1: Planning\n2024 Q2: Development\n2024 Q3: Testing\n2024 Q4: Launch"),
            ("swot_matrix", "Strengths: Quality, Team\nWeaknesses: Resources\nOpportunities: Market\nThreats: Competition")
        ]
    
    def on_start(self):
        """Called when user starts"""
        self.client = WebSocketClient(self.host, self.user_id)
        if not self.client.connect():
            raise LocustError("Failed to connect WebSocket")
        logger.info(f"User {self.user_id} connected")
    
    def on_stop(self):
        """Called when user stops"""
        if self.client:
            self.client.disconnect()
        logger.info(f"User {self.user_id} disconnected")
    
    @task(10)
    def generate_random_diagram(self):
        """Generate a random diagram type"""
        diagram_type, content = random.choice(self.diagram_types)
        
        # Add some variation to content
        content += f"\n(Generated at {time.strftime('%Y-%m-%d %H:%M:%S')})"
        
        result = self.client.send_diagram_request(diagram_type, content)
        if result:
            logger.debug(f"Generated {diagram_type}: {result.get('diagram_id')}")
    
    @task(5)
    def generate_pyramid(self):
        """Generate pyramid diagram specifically"""
        levels = random.randint(3, 5)
        content = "\n".join([f"Level {i}" for i in range(1, levels + 1)])
        
        result = self.client.send_diagram_request(f"pyramid_{levels}_level", content)
        if result:
            logger.debug(f"Generated pyramid: {result.get('diagram_id')}")
    
    @task(3)
    def generate_complex_diagram(self):
        """Generate a complex diagram with more content"""
        # Generate a large flowchart
        nodes = []
        for i in range(10):
            nodes.append(f"Node {i}: Process step with detailed description")
        
        content = "\n".join(nodes)
        result = self.client.send_diagram_request("process_flow", content)
        if result:
            logger.debug(f"Generated complex diagram: {result.get('diagram_id')}")
    
    @task(2)
    def send_ping(self):
        """Send ping to keep connection alive"""
        self.client.send_ping()
    
    @task(1)
    def rapid_generation(self):
        """Simulate rapid diagram generation (stress test)"""
        for _ in range(3):
            diagram_type, content = random.choice(self.diagram_types[:3])
            self.client.send_diagram_request(diagram_type, content)
            time.sleep(0.5)


class AdminUser(User):
    """Simulated admin user checking metrics and health"""
    
    wait_time = between(10, 30)  # Less frequent checks
    
    @task(5)
    def check_health(self):
        """Check health endpoint"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure(f"Unhealthy status: {data.get('status')}")
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(3)
    def check_metrics(self):
        """Check metrics endpoint"""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code in [200, 404]:  # 404 if metrics disabled
                response.success()
            else:
                response.failure(f"Metrics check failed: {response.status_code}")
    
    @task(1)
    def check_root(self):
        """Check root endpoint"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("service") == "Diagram Microservice v2":
                    response.success()
                else:
                    response.failure("Invalid service response")
            else:
                response.failure(f"Root check failed: {response.status_code}")


# Event handlers for test lifecycle
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    logger.info(f"Starting load test against {environment.host}")
    logger.info(f"Users: {environment.parsed_options.num_users}")
    logger.info(f"Spawn rate: {environment.parsed_options.spawn_rate}")
    logger.info(f"Run time: {environment.parsed_options.run_time}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    logger.info("Load test completed")
    
    # Print summary statistics
    stats = environment.stats
    logger.info(f"Total requests: {stats.total.num_requests}")
    logger.info(f"Total failures: {stats.total.num_failures}")
    logger.info(f"Average response time: {stats.total.avg_response_time}ms")
    logger.info(f"Min response time: {stats.total.min_response_time}ms")
    logger.info(f"Max response time: {stats.total.max_response_time}ms")


# Custom command line arguments
@events.init_command_line_parser.add_listener
def init_parser(parser):
    """Add custom command line arguments"""
    parser.add_argument(
        '--scenario',
        type=str,
        default='mixed',
        choices=['mixed', 'websocket', 'http', 'stress'],
        help='Test scenario to run'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Test duration in seconds'
    )


# Scenario-based user selection
@events.init.add_listener
def on_init(environment, **kwargs):
    """Initialize test based on scenario"""
    scenario = environment.parsed_options.scenario
    
    if scenario == 'websocket':
        environment.user_classes = [DiagramUser]
    elif scenario == 'http':
        environment.user_classes = [AdminUser]
    elif scenario == 'stress':
        environment.user_classes = [DiagramUser]
        environment.parsed_options.num_users = 100
        environment.parsed_options.spawn_rate = 10
    else:  # mixed
        environment.user_classes = [DiagramUser, AdminUser]


if __name__ == "__main__":
    # Run Locust programmatically for testing
    import os
    from locust import run_single_user
    
    # Set test host
    host = os.environ.get("TEST_HOST", "http://localhost:8001")
    
    # Run single user test
    user = DiagramUser(environment={"host": host})
    run_single_user(user)