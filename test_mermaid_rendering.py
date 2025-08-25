#!/usr/bin/env python3
"""
Test if generated Mermaid code can be rendered
"""

import asyncio
from utils.mermaid_renderer import render_mermaid_to_svg

test_codes = [
    {
        "name": "Flowchart",
        "code": """flowchart TD
    N1["User enters credentials"]
    N2["Validate format"]
    N3["Check database"]
    N4["Verify password"]
    N5["Generate token"]
    N6["Set cookie"]
    N7["Redirect to dashboard"]

    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
    N5 --> N6
    N6 --> N7"""
    },
    {
        "name": "Class Diagram",
        "code": """classDiagram
    class User {
        +String id
        +String name
        +String email
        +login() void
        +logout() void
    }

    class Product {
        +String id
        +String name
        +double price
        +int stock
    }

    User "1" --> "*" Product : has"""
    },
    {
        "name": "Timeline",
        "code": """timeline
    title Company History Timeline

    section Key Milestones
        2020-03 : Founded
        2020-12 : First product launched
        2021-06 : Series A funding secured
        2022-03 : Reached 100 employees
        2023-03 : IPO"""
    }
]

async def test_rendering():
    print("Testing Mermaid code rendering...")
    print("=" * 60)
    
    for test in test_codes:
        print(f"\nTesting: {test['name']}")
        print("-" * 40)
        
        try:
            svg = await render_mermaid_to_svg(
                test["code"],
                {"primaryColor": "#3B82F6"},
                fallback_to_placeholder=False
            )
            
            if svg and svg.startswith("<svg"):
                print(f"✅ Successfully rendered to SVG")
                print(f"   SVG size: {len(svg)} chars")
            else:
                print(f"❌ Failed to render - got: {svg[:100] if svg else 'None'}")
                
        except Exception as e:
            print(f"❌ Rendering failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_rendering())