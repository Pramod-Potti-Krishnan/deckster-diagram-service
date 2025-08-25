#!/usr/bin/env python3
"""
Test script to verify border refinement - borders should match fill colors
while preserving necessary lines like axes and connectors
"""

import asyncio
import os
import sys
from pathlib import Path
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from models import DiagramRequest, DiagramTheme, DataPoint
from agents.svg_agent import SVGAgent
from config.settings import Settings


async def test_border_refinement():
    """Test that borders match fill colors while preserving other lines"""
    print("\n" + "=" * 60)
    print("Testing Border Refinement (Borders = Fill Color)")
    print("=" * 60)
    
    # Initialize settings and agent
    settings = Settings()
    svg_agent = SVGAgent(settings)
    await svg_agent.initialize()
    
    # Test cases
    test_cases = [
        {
            "name": "Matrix with Axes",
            "diagram_type": "matrix_2x2",
            "theme": DiagramTheme(
                primaryColor="#2563eb",
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="High/High"),
                DataPoint(label="Low/High"),
                DataPoint(label="Low/Low"),
                DataPoint(label="High/Low")
            ]
        },
        {
            "name": "Hub & Spoke with Connectors",
            "diagram_type": "hub_spoke_4",
            "theme": DiagramTheme(
                primaryColor="#dc2626",
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="Hub"),
                DataPoint(label="Node 1"),
                DataPoint(label="Node 2"),
                DataPoint(label="Node 3"),
                DataPoint(label="Node 4")
            ]
        },
        {
            "name": "Process Flow with Arrows",
            "diagram_type": "process_flow_3",
            "theme": DiagramTheme(
                primaryColor="#16a34a",
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="Start"),
                DataPoint(label="Process"),
                DataPoint(label="End")
            ]
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"  Diagram: {test_case['diagram_type']}")
        
        request = DiagramRequest(
            content="Test content",
            diagram_type=test_case['diagram_type'],
            theme=test_case['theme'],
            data_points=test_case['data_points']
        )
        
        try:
            result = await svg_agent.generate(request)
            svg_content = result['content']
            
            # Check 1: Axes and connector lines should still exist
            has_lines = '<line' in svg_content
            has_paths = '<path' in svg_content and 'fill="none"' in svg_content
            has_connectors = has_lines or has_paths
            
            # Check 2: Find filled shapes with borders
            filled_shapes = re.findall(r'<(?:rect|circle|path|polygon)([^>]*fill="(#[0-9a-fA-F]{6})"[^>]*>)', svg_content)
            
            # Check 3: Verify borders match fills
            borders_match = True
            for shape_attrs, fill_color in filled_shapes:
                if 'stroke=' in shape_attrs:
                    stroke_match = re.search(r'stroke="([^"]*)"', shape_attrs)
                    if stroke_match:
                        stroke_color = stroke_match.group(1)
                        # Check if stroke matches fill (allowing for case differences)
                        if stroke_color.lower() != fill_color.lower():
                            # Check if it's a connector line (which should keep original color)
                            if 'fill="none"' not in shape_attrs:
                                borders_match = False
                                print(f"    ⚠️  Border mismatch: fill={fill_color}, stroke={stroke_color}")
            
            # Results
            print(f"  ✓ Has connector lines: {has_connectors}")
            print(f"  ✓ Borders match fills: {borders_match}")
            print(f"  ✓ Found {len(filled_shapes)} filled shapes")
            
            if not has_connectors and test_case['diagram_type'] in ['hub_spoke_4', 'process_flow_3']:
                print(f"  ❌ Missing expected connector lines!")
                all_passed = False
            
            if not borders_match:
                all_passed = False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_passed = False
    
    await svg_agent.shutdown()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Borders match fills, lines preserved.")
    else:
        print("⚠️  Some tests failed. Review output above.")
    print("=" * 60)
    
    return all_passed


async def main():
    """Run the test"""
    success = await test_border_refinement()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())