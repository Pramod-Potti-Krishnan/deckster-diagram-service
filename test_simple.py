#!/usr/bin/env python3
"""Simple test for SVG generation with color theming"""

import asyncio
from agents.svg_agent import SVGAgent
from models.request_models import DiagramRequest, DiagramTheme, ColorScheme
from config.settings import Settings

async def test_diagrams():
    # Create agent with settings
    settings = Settings()
    agent = SVGAgent(settings)

    # Test request with monochromatic theme
    request = DiagramRequest(
        diagram_type="pyramid",
        labels=["Foundation", "Layer 2", "Layer 3", "Layer 4", "Top"],
        content="Hierarchical structure with 5 levels",
        theme=DiagramTheme(
            primaryColor="#3b82f6",
            colorScheme=ColorScheme.MONOCHROMATIC
        )
    )

    try:
        result = await agent.generate(request)
        if result.status == "success":
            print("✓ Pyramid generated successfully")
            
            # Check for color variety
            import re
            fill_colors = re.findall(r'fill="(#[0-9a-fA-F]{6})"', result.svg)
            unique_fills = list(set(fill_colors))
            print(f"  Unique colors: {len(unique_fills)}")
            print(f"  Colors: {unique_fills[:10]}")
            
            # Save to file
            with open("test_pyramid_mono.svg", "w") as f:
                f.write(result.svg)
            print("  Saved to test_pyramid_mono.svg")
        else:
            print(f"✗ Error: {result.message}")
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()

    # Test with complementary theme
    request2 = DiagramRequest(
        diagram_type="matrix_2x2",
        labels=["Q1", "Q2", "Q3", "Q4"],
        content="2x2 Matrix",
        theme=DiagramTheme(
            primaryColor="#10b981",
            colorScheme=ColorScheme.COMPLEMENTARY
        )
    )

    try:
        result = await agent.generate(request2)
        if result.status == "success":
            print("\n✓ Matrix 2x2 generated successfully")
            
            # Check for color variety
            import re
            fill_colors = re.findall(r'fill="(#[0-9a-fA-F]{6})"', result.svg)
            unique_fills = list(set(fill_colors))
            print(f"  Unique colors: {len(unique_fills)}")
            print(f"  Colors: {unique_fills[:10]}")
            
            # Save to file
            with open("test_matrix_comp.svg", "w") as f:
                f.write(result.svg)
            print("  Saved to test_matrix_comp.svg")
        else:
            print(f"✗ Error: {result.message}")
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_diagrams())