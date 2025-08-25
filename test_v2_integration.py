#!/usr/bin/env python3
"""
Test V2 Integration - Verify v2 implementations are being used
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import components
from config.settings import Settings
from core import DiagramConductor
from models import DiagramRequest
from models.request_models import DiagramTheme

async def test_v2_integration():
    """Test that V2 implementations are properly integrated"""
    
    print("Testing V2 Integration")
    print("=" * 60)
    
    # Initialize settings
    settings = Settings()
    
    # Initialize conductor
    conductor = DiagramConductor(settings)
    await conductor.initialize()
    
    # Test diagram types that should work with V2
    test_cases = [
        ("flowchart", "Create a simple flow: Start -> Process -> End"),
        ("erDiagram", "User entity with id and name, Order entity with id and total"),
        ("journey", "User journey: Browse products, Add to cart, Checkout"),
        ("gantt", "Project timeline: Week 1 Planning, Week 2 Development"),
        ("quadrantChart", "Risk matrix with high risk items"),
        ("timeline", "Company history: 2020 Founded, 2021 Growth, 2022 IPO"),
        ("kanban", "Task board: Todo, In Progress, Done")
    ]
    
    results = []
    
    for diagram_type, content in test_cases:
        print(f"\nTesting {diagram_type}...")
        
        try:
            # Create request
            request = DiagramRequest(
                request_id=f"test-{diagram_type}",
                session_id="test-session",
                user_id="test-user",
                diagram_type=diagram_type,
                content=content,
                theme=DiagramTheme(primaryColor="#3B82F6")
            )
            
            # Generate diagram
            result = await conductor.generate(request)
            
            # Check result
            if result and "content" in result:
                success = True
                method = result.get("metadata", {}).get("generation_method", "unknown")
                print(f"  ✅ SUCCESS - Method: {method}")
                
                # Check if V2 is being used
                if "mermaid_llm_v2" in str(result.get("metadata", {})):
                    print(f"     Using V2 implementation!")
            else:
                success = False
                print(f"  ❌ FAILED")
            
            results.append({
                "type": diagram_type,
                "success": success
            })
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append({
                "type": diagram_type,
                "success": False,
                "error": str(e)
            })
    
    # Shutdown
    await conductor.shutdown()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    working = sum(1 for r in results if r["success"])
    total = len(results)
    print(f"Working: {working}/{total}")
    
    if working == total:
        print("✅ All diagram types working with V2!")
    else:
        print("⚠️ Some diagram types failed")
        for r in results:
            if not r["success"]:
                print(f"  - {r['type']}: Failed")

if __name__ == "__main__":
    asyncio.run(test_v2_integration())