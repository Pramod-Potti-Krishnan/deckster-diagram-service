#!/usr/bin/env python3
"""
Test script to verify hub_spoke diagrams have white background
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from models import DiagramRequest, DiagramTheme, DataPoint
from models.request_models import ColorScheme
from agents.svg_agent import SVGAgent
from config.settings import Settings


async def test_hub_spoke_background():
    """Test hub_spoke diagrams with both color schemes"""
    print("\n" + "=" * 60)
    print("Testing Hub & Spoke Background (Should be White)")
    print("=" * 60)
    
    # Initialize settings and agent
    settings = Settings()
    svg_agent = SVGAgent(settings)
    await svg_agent.initialize()
    
    # Create output directory
    output_dir = "hub_spoke_background_test"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test cases
    test_cases = [
        {
            "name": "Hub Spoke 4 - Monochromatic",
            "diagram_type": "hub_spoke_4",
            "color_scheme": ColorScheme.MONOCHROMATIC,
            "primary_color": "#dc2626"
        },
        {
            "name": "Hub Spoke 4 - Complementary",
            "diagram_type": "hub_spoke_4",
            "color_scheme": ColorScheme.COMPLEMENTARY,
            "primary_color": "#dc2626"
        },
        {
            "name": "Hub Spoke 6 - Monochromatic",
            "diagram_type": "hub_spoke_6",
            "color_scheme": ColorScheme.MONOCHROMATIC,
            "primary_color": "#2563eb"
        },
        {
            "name": "Hub Spoke 6 - Complementary",
            "diagram_type": "hub_spoke_6",
            "color_scheme": ColorScheme.COMPLEMENTARY,
            "primary_color": "#2563eb"
        }
    ]
    
    # Data points for hub_spoke_4
    data_points_4 = [
        DataPoint(label="Core"),
        DataPoint(label="Node 1"),
        DataPoint(label="Node 2"),
        DataPoint(label="Node 3"),
        DataPoint(label="Node 4")
    ]
    
    # Data points for hub_spoke_6
    data_points_6 = [
        DataPoint(label="Core"),
        DataPoint(label="Node 1"),
        DataPoint(label="Node 2"),
        DataPoint(label="Node 3"),
        DataPoint(label="Node 4"),
        DataPoint(label="Node 5"),
        DataPoint(label="Node 6")
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        
        # Select appropriate data points
        data_points = data_points_4 if "4" in test_case['diagram_type'] else data_points_6
        
        request = DiagramRequest(
            content="Test content",
            diagram_type=test_case['diagram_type'],
            theme=DiagramTheme(
                primaryColor=test_case['primary_color'],
                colorScheme=test_case['color_scheme'],
                useSmartTheming=True
            ),
            data_points=data_points
        )
        
        try:
            result = await svg_agent.generate(request)
            
            # Save SVG
            filename = f"{test_case['diagram_type']}_{test_case['color_scheme'].value}.svg"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                f.write(result['content'])
            
            # Check for white background
            svg_content = result['content']
            has_white_bg = 'fill="#ffffff"' in svg_content or 'fill="white"' in svg_content
            has_colored_bg = 'fill="#fafafa"' in svg_content or 'fill="url(#bg_pattern)' in svg_content
            
            if has_white_bg and not has_colored_bg:
                print(f"  ✅ White background confirmed")
            else:
                print(f"  ⚠️  Background might not be white")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"Results saved to: {output_dir}/")
    print("=" * 60)
    
    await svg_agent.shutdown()


async def main():
    await test_hub_spoke_background()


if __name__ == "__main__":
    asyncio.run(main())