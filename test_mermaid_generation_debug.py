#!/usr/bin/env python3
"""
Debug Mermaid generation to see what code is being produced
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
from config import Settings
from agents.mermaid_agent import MermaidAgent
from models import DiagramRequest, DiagramTheme
from playbooks.mermaid_playbook import get_diagram_spec, get_syntax_patterns, get_construction_rules, get_diagram_examples

async def test_mermaid_generation_locally():
    """Test Mermaid generation locally to see what code is produced"""
    
    settings = Settings()
    
    # Test cases that are failing
    test_cases = [
        {
            "type": "flowchart",
            "content": "User login process: User enters credentials -> Validate format -> Check database -> Verify password -> Generate token -> Set cookie -> Redirect to dashboard"
        },
        {
            "type": "class_diagram",
            "content": "Create a User class with properties: id, name, email and methods: login(), logout(). Create a Product class with: id, name, price, stock. User has many Products."
        },
        {
            "type": "gantt",
            "content": "Project timeline: Week 1-2: Planning, Week 3-4: Design, Week 5-8: Development, Week 9-10: Testing, Week 11-12: Deployment"
        },
        {
            "type": "timeline",
            "content": "Company history: 2020 Q1: Founded, 2020 Q4: First product, 2021 Q2: Series A funding, 2022 Q1: 100 employees, 2023 Q1: IPO"
        },
        {
            "type": "architecture",
            "content": "Microservices: API Gateway connects to User Service, Product Service, Order Service. Each service has its own database. All services publish events to Message Queue."
        }
    ]
    
    print("=" * 80)
    print("MERMAID GENERATION DEBUG TEST")
    print("=" * 80)
    
    # Initialize agent
    agent = MermaidAgent(settings)
    
    for test in test_cases:
        print(f"\n\nTesting: {test['type']}")
        print("-" * 40)
        
        # Create request
        request = DiagramRequest(
            diagram_type=test["type"],
            content=test["content"],
            theme=DiagramTheme()
        )
        
        try:
            # Get playbook context
            spec = get_diagram_spec(test["type"])
            if not spec:
                print(f"  ❌ No playbook spec for {test['type']}")
                continue
                
            context = {
                "name": spec.get("name", test["type"]),
                "mermaid_type": spec.get("mermaid_type", test["type"]),
                "syntax_patterns": get_syntax_patterns(test["type"]),
                "construction_rules": get_construction_rules(test["type"]),
                "examples": get_diagram_examples(test["type"]),
                "escape_rules": spec.get("escape_rules", {})
            }
            
            # Build prompt
            prompt = agent._build_prompt(
                test["type"],
                test["content"],
                request.theme.dict(),
                context
            )
            
            print(f"  Prompt length: {len(prompt)} chars")
            print(f"  Has example: {'Yes' if context['examples'] else 'No'}")
            print(f"  Mermaid type: {context.get('mermaid_type', 'unknown')}")
            
            # Try to generate
            if agent.enabled and agent.model:
                print("  Generating with Gemini 2.5 Flash...")
                
                # Generate
                response = agent.model.generate_content(
                    prompt + "\n\nReturn a JSON object with: mermaid_code, confidence (0-1), entities_extracted (list), relationships_count (int), diagram_type_confirmed"
                )
                
                # Try to extract Mermaid code
                response_text = response.text
                print(f"\n  Response preview (first 500 chars):")
                print(f"  {response_text[:500]}...")
                
                # Try to parse JSON
                import json
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0]
                elif '{' in response_text:
                    start = response_text.index('{')
                    end = response_text.rindex('}') + 1
                    response_text = response_text[start:end]
                
                try:
                    output = json.loads(response_text)
                    mermaid_code = output.get('mermaid_code', '')
                    
                    print(f"\n  ✅ Generated Mermaid code:")
                    print("  " + "\n  ".join(mermaid_code.split('\n')[:10]))
                    
                    # Check if it starts correctly
                    expected_start = context.get('syntax_patterns', {}).get('diagram_start', test['type'])
                    if mermaid_code.strip().startswith(expected_start):
                        print(f"  ✅ Starts correctly with: {expected_start}")
                    else:
                        print(f"  ❌ Does NOT start with: {expected_start}")
                        print(f"     Actually starts with: {mermaid_code.split()[0] if mermaid_code else 'empty'}")
                        
                except json.JSONDecodeError as e:
                    print(f"  ❌ Failed to parse JSON: {e}")
                    print(f"     Raw response: {response_text[:200]}...")
            else:
                print("  ❌ Agent not enabled")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mermaid_generation_locally())