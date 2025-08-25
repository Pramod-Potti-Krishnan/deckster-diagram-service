#!/usr/bin/env python3
"""
Monitor Railway deployment for updates
Tests if the new code has been deployed
"""

import asyncio
import json
import websockets
import ssl
from datetime import datetime
import time

async def check_deployment_version():
    """Check if deployment has new code by testing diagram types"""
    
    url = "wss://deckster-diagram-service-production.up.railway.app/ws"
    session_id = f"monitor-{int(time.time())}"
    full_url = f"{url}?session_id={session_id}&user_id=test"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Test types that should work with new code
    test_cases = [
        ("flowchart", "Simple flow: Start -> Process -> End", True),  # Should always work
        ("erDiagram", "User entity with id and name", True),          # New name format
        ("journey", "User journey: Browse -> Buy", True),             # New name format
        ("quadrantChart", "Risk matrix with items", True),            # New name format
    ]
    
    results = []
    
    for diagram_type, content, should_work in test_cases:
        try:
            async with websockets.connect(full_url, ssl=ssl_context, ping_timeout=10) as ws:
                # Skip welcome
                await ws.recv()
                
                # Send request
                request = {
                    "type": "diagram_request",
                    "correlation_id": f"test-{diagram_type}",
                    "data": {
                        "diagram_type": diagram_type,
                        "content": content,
                        "theme": {"primaryColor": "#3B82F6"}
                    }
                }
                
                await ws.send(json.dumps(request))
                
                # Get response
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    success = data.get("type") == "diagram_response"
                    results.append({
                        "type": diagram_type,
                        "success": success,
                        "expected": should_work
                    })
                    
                except asyncio.TimeoutError:
                    results.append({
                        "type": diagram_type,
                        "success": False,
                        "expected": should_work
                    })
                    
        except Exception as e:
            results.append({
                "type": diagram_type,
                "success": False,
                "expected": should_work,
                "error": str(e)
            })
    
    return results

async def monitor_loop():
    """Monitor deployment status continuously"""
    
    print("Railway Deployment Monitor")
    print("=" * 60)
    print("Monitoring for deployment of new code...")
    print("Looking for: erDiagram, journey, quadrantChart support")
    print("=" * 60)
    print()
    
    last_status = None
    check_count = 0
    
    while True:
        check_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"[{timestamp}] Check #{check_count}")
        
        try:
            results = await check_deployment_version()
            
            # Calculate success rate
            working = sum(1 for r in results if r["success"])
            total = len(results)
            
            # Check if new code is deployed
            new_types_working = sum(1 for r in results 
                                  if r["type"] in ["erDiagram", "journey", "quadrantChart"] 
                                  and r["success"])
            
            status = f"{working}/{total} working"
            
            # Detailed results
            for result in results:
                icon = "✅" if result["success"] else "❌"
                print(f"  {icon} {result['type']}: {'Working' if result['success'] else 'Failed'}")
            
            print(f"  Summary: {status}")
            
            # Check if deployment updated
            if new_types_working >= 2:  # At least 2 of the new types work
                print()
                print("🎉 NEW CODE DETECTED! 🎉")
                print("The Railway deployment has been updated with the latest code!")
                print(f"New diagram types working: {new_types_working}/3")
                print()
                print("You can now run the full test suite:")
                print("  python test_mermaid_v3.py")
                break
            else:
                print(f"  Status: Old code still deployed (new types: {new_types_working}/3)")
                print()
            
            # Different status than before
            if status != last_status:
                print(f"  ⚠️ Status changed: {last_status} -> {status}")
                last_status = status
            
        except Exception as e:
            print(f"  Error checking deployment: {e}")
        
        # Wait before next check
        print(f"  Waiting 30 seconds before next check...")
        await asyncio.sleep(30)

async def single_check():
    """Do a single deployment check"""
    
    print("Railway Deployment Status Check")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = await check_deployment_version()
    
    # Show results
    print("Test Results:")
    for result in results:
        icon = "✅" if result["success"] else "❌"
        status = "Working" if result["success"] else "Failed"
        print(f"  {icon} {result['type']}: {status}")
    
    # Analysis
    working = sum(1 for r in results if r["success"])
    total = len(results)
    new_types_working = sum(1 for r in results 
                          if r["type"] in ["erDiagram", "journey", "quadrantChart"] 
                          and r["success"])
    
    print()
    print(f"Summary: {working}/{total} diagram types working")
    
    if new_types_working >= 2:
        print("✅ NEW CODE IS DEPLOYED!")
        print(f"   New diagram types working: {new_types_working}/3")
    else:
        print("⏳ OLD CODE STILL DEPLOYED")
        print(f"   New diagram types working: {new_types_working}/3")
        print("   Waiting for Railway to redeploy from GitHub...")
    
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Single check mode
        asyncio.run(single_check())
    else:
        # Continuous monitoring
        print("Starting continuous monitoring...")
        print("Press Ctrl+C to stop")
        print()
        try:
            asyncio.run(monitor_loop())
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")