import sys
import os
import asyncio
sys.path.insert(0, '/private/tmp/deckster-diagram-service')

from models.request_models import DiagramRequest, ColorScheme
from agents.svg_agent import SVGAgent
from config import Settings

async def test():
    settings = Settings()
    agent = SVGAgent(settings)
    await agent.initialize()
    
    # Create request for Matrix with monochromatic theme
    request_data = {
        "content": "Test matrix",
        "diagram_type": "matrix_2x2",
        "data": [
            {"label": "Priority matrix with monochromatic theme"},
            {"label": "Low / High"},
            {"label": "Low / Low"},
            {"label": "High / Low"}
        ],
        "theme": {
            "primaryColor": "#10b981",
            "useSmartTheming": True,
            "colorScheme": "monochromatic"
        }
    }
    
    request = DiagramRequest(**request_data)
    result = await agent.generate(request)
    
    # Check the colors in the result
    import re
    svg_content = result['content']
    
    # Find all quadrant colors
    print("Quadrant colors:")
    for i in range(1, 5):
        match = re.search(rf'id="q{i}_fill"[^>]*fill="([^"]*)"', svg_content)
        if match:
            print(f"  Q{i}: {match.group(1)}")
    
    # Check for duplicates
    q1_match = re.search(r'id="q1_fill"[^>]*fill="([^"]*)"', svg_content)
    q4_match = re.search(r'id="q4_fill"[^>]*fill="([^"]*)"', svg_content)
    
    if q1_match and q4_match:
        q1_color = q1_match.group(1)
        q4_color = q4_match.group(1)
        
        if q1_color == q4_color:
            print(f"\n❌ ISSUE: Q1 and Q4 have the same color: {q1_color}")
        else:
            print(f"\n✅ SUCCESS: Q1 and Q4 have different colors")
            print(f"   Q1: {q1_color}, Q4: {q4_color}")
    
    # Save for inspection
    with open('test_debug_output.svg', 'w') as f:
        f.write(svg_content)
    print("\nSaved to test_debug_output.svg")

asyncio.run(test())
