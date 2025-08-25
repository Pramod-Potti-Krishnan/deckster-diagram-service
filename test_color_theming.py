#!/usr/bin/env python3
"""
Test script for smart color theming system
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from models import DiagramRequest, DiagramTheme, DataPoint
from agents.svg_agent import SVGAgent
from utils.color_utils import SmartColorTheme, hex_to_rgb, rgb_to_hsl
from config.settings import Settings


async def test_color_utilities():
    """Test basic color utility functions"""
    print("\n=== Testing Color Utilities ===")
    
    from utils.color_utils import (
        hex_to_rgb, rgb_to_hex, rgb_to_hsl, hsl_to_rgb,
        adjust_lightness, adjust_saturation, generate_shades,
        get_complementary, get_analogous, get_triadic
    )
    
    # Test color conversions
    test_color = "#3b82f6"
    print(f"Test color: {test_color}")
    
    r, g, b = hex_to_rgb(test_color)
    print(f"RGB: ({r}, {g}, {b})")
    
    h, s, l = rgb_to_hsl(r, g, b)
    print(f"HSL: ({h:.1f}, {s:.1f}%, {l:.1f}%)")
    
    # Test color adjustments
    lighter = adjust_lightness(test_color, 20)
    darker = adjust_lightness(test_color, -20)
    print(f"Lighter: {lighter}")
    print(f"Darker: {darker}")
    
    # Test shade generation
    shades = generate_shades(test_color, 5)
    print(f"Shades: {shades}")
    
    # Test color harmony
    comp = get_complementary(test_color)
    print(f"Complementary: {comp}")
    
    analogous = get_analogous(test_color)
    print(f"Analogous: {analogous}")
    
    triadic = get_triadic(test_color)
    print(f"Triadic: {triadic}")
    
    return True


async def test_smart_theme():
    """Test SmartColorTheme class"""
    print("\n=== Testing Smart Theme Generation ===")
    
    # Test with just primary color
    theme1 = SmartColorTheme("#3b82f6")
    print("\nTheme with primary only (#3b82f6):")
    print(f"  Primary: {theme1.primary}")
    print(f"  Secondary (auto): {theme1.secondary}")
    print(f"  Accent (auto): {theme1.accent}")
    print(f"  Primary shades: {theme1.palette['primary']}")
    
    # Test with primary and secondary
    theme2 = SmartColorTheme("#3b82f6", "#22c55e")
    print("\nTheme with primary (#3b82f6) and secondary (#22c55e):")
    print(f"  Primary: {theme2.primary}")
    print(f"  Secondary: {theme2.secondary}")
    print(f"  Accent (auto): {theme2.accent}")
    
    # Test with all three colors
    theme3 = SmartColorTheme("#3b82f6", "#22c55e", "#f59e0b")
    print("\nTheme with all three colors:")
    print(f"  Primary: {theme3.primary}")
    print(f"  Secondary: {theme3.secondary}")
    print(f"  Accent: {theme3.accent}")
    
    # Test color mapping
    test_colors = ["#ffffff", "#3b82f6", "#22c55e", "#64748b", "#1e293b"]
    print("\nColor mapping examples:")
    for color in test_colors:
        mapped = theme1.color_map.get(color, color)
        print(f"  {color} -> {mapped}")
    
    return True


async def test_svg_theming():
    """Test SVG theming with actual templates"""
    print("\n=== Testing SVG Theming ===")
    
    # Initialize settings and agent
    settings = Settings()
    svg_agent = SVGAgent(settings)
    await svg_agent.initialize()
    
    # Test templates
    test_cases = [
        {
            "name": "Matrix 2x2 with Purple Theme",
            "diagram_type": "matrix_2x2",
            "theme": DiagramTheme(
                primaryColor="#8b5cf6",  # Purple
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="Urgent & Important"),
                DataPoint(label="Not Urgent & Important"),
                DataPoint(label="Not Urgent & Not Important"),
                DataPoint(label="Urgent & Not Important")
            ]
        },
        {
            "name": "Hub & Spoke with Green Theme",
            "diagram_type": "hub_spoke_4",
            "theme": DiagramTheme(
                primaryColor="#10b981",  # Green
                secondaryColor="#f59e0b",  # Orange
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="Core System"),
                DataPoint(label="Module A"),
                DataPoint(label="Module B"),
                DataPoint(label="Module C"),
                DataPoint(label="Module D")
            ]
        },
        {
            "name": "Roadmap with Custom Brand Colors",
            "diagram_type": "roadmap_quarterly_4",
            "theme": DiagramTheme(
                primaryColor="#e11d48",  # Rose
                secondaryColor="#0891b2",  # Cyan
                accentColor="#7c3aed",  # Violet
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="Q1 2024"),
                DataPoint(label="Q2 2024"),
                DataPoint(label="Q3 2024"),
                DataPoint(label="Q4 2024")
            ]
        },
        {
            "name": "Venn Diagram with Monochrome Theme",
            "diagram_type": "venn_2_circle",
            "theme": DiagramTheme(
                primaryColor="#374151",  # Gray
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="Set A", value=45),
                DataPoint(label="Set B", value=45),
                DataPoint(label="Intersection", value=10)
            ]
        }
    ]
    
    # Test each case
    results = []
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"  Diagram type: {test_case['diagram_type']}")
        print(f"  Primary color: {test_case['theme'].primaryColor}")
        
        request = DiagramRequest(
            content="Test content",
            diagram_type=test_case['diagram_type'],
            theme=test_case['theme'],
            data_points=test_case['data_points']
        )
        
        try:
            result = await svg_agent.generate(request)
            
            # Check if colors were replaced
            svg_content = result['content']
            
            # Extract theme that was used
            smart_theme = SmartColorTheme(
                test_case['theme'].primaryColor,
                test_case['theme'].secondaryColor,
                test_case['theme'].accentColor
            )
            
            # Check if any theme colors appear in the output
            theme_colors_found = []
            for color in smart_theme.palette['primary'][:3]:
                if color in svg_content:
                    theme_colors_found.append(color)
            
            if theme_colors_found:
                print(f"  ✅ Success - Theme colors applied: {theme_colors_found[:3]}")
                results.append(True)
            else:
                print(f"  ⚠️  Warning - No theme colors found in output")
                results.append(False)
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append(False)
    
    # Summary
    success_count = sum(results)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\n=== Summary ===")
    print(f"Tests passed: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    await svg_agent.shutdown()
    return success_rate == 100


async def test_theme_api_compatibility():
    """Test backward compatibility with existing API"""
    print("\n=== Testing API Backward Compatibility ===")
    
    settings = Settings()
    svg_agent = SVGAgent(settings)
    await svg_agent.initialize()
    
    # Test with old theme format (useSmartTheming defaults to True)
    old_theme = DiagramTheme(
        primaryColor="#3b82f6",
        backgroundColor="#ffffff",
        textColor="#1e293b"
    )
    
    request = DiagramRequest(
        content="Test content",
        diagram_type="matrix_2x2",
        theme=old_theme,
        data_points=[
            DataPoint(label="A"),
            DataPoint(label="B"),
            DataPoint(label="C"),
            DataPoint(label="D")
        ]
    )
    
    try:
        result = await svg_agent.generate(request)
        print("✅ Backward compatibility maintained")
    except Exception as e:
        print(f"❌ Backward compatibility broken: {e}")
        return False
    
    # Test with smart theming explicitly disabled
    basic_theme = DiagramTheme(
        primaryColor="#3b82f6",
        useSmartTheming=False
    )
    
    request.theme = basic_theme
    
    try:
        result = await svg_agent.generate(request)
        print("✅ Basic theming still works when disabled")
    except Exception as e:
        print(f"❌ Basic theming broken: {e}")
        return False
    
    await svg_agent.shutdown()
    return True


async def generate_themed_samples():
    """Generate sample SVGs with different themes for visual inspection"""
    print("\n=== Generating Themed Samples ===")
    
    settings = Settings()
    svg_agent = SVGAgent(settings)
    await svg_agent.initialize()
    
    output_dir = "themed_samples"
    os.makedirs(output_dir, exist_ok=True)
    
    themes = [
        ("default", DiagramTheme(primaryColor="#3b82f6")),
        ("purple", DiagramTheme(primaryColor="#8b5cf6")),
        ("green", DiagramTheme(primaryColor="#10b981")),
        ("rose", DiagramTheme(primaryColor="#e11d48")),
        ("monochrome", DiagramTheme(primaryColor="#374151")),
        ("brand", DiagramTheme(
            primaryColor="#ff6b6b",
            secondaryColor="#4ecdc4",
            accentColor="#ffe66d"
        ))
    ]
    
    diagrams = ["matrix_2x2", "hub_spoke_4", "venn_2_circle", "pyramid_3_level"]
    
    for diagram_type in diagrams:
        for theme_name, theme in themes:
            # Prepare data points based on diagram type
            if diagram_type == "venn_2_circle":
                data_points = [
                    DataPoint(label="Set A", value=45),
                    DataPoint(label="Set B", value=45),
                    DataPoint(label="Overlap", value=10)
                ]
            elif diagram_type == "hub_spoke_4":
                data_points = [
                    DataPoint(label="Core"),
                    DataPoint(label="Node 1"),
                    DataPoint(label="Node 2"),
                    DataPoint(label="Node 3"),
                    DataPoint(label="Node 4")
                ]
            else:
                data_points = [
                    DataPoint(label=f"Item {i+1}")
                    for i in range(4)
                ]
            
            request = DiagramRequest(
                content="Sample content",
                diagram_type=diagram_type,
                theme=theme,
                data_points=data_points
            )
            
            try:
                result = await svg_agent.generate(request)
                
                # Save SVG
                filename = f"{output_dir}/{diagram_type}_{theme_name}.svg"
                with open(filename, 'w') as f:
                    f.write(result['content'])
                
                print(f"✅ Generated: {filename}")
                
            except Exception as e:
                print(f"❌ Failed to generate {diagram_type} with {theme_name}: {e}")
    
    # Generate HTML viewer
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Themed SVG Samples</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background: #f5f5f5; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 8px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h3 { margin: 0 0 10px 0; font-size: 14px; color: #333; }
        .card img { width: 100%; height: auto; }
    </style>
</head>
<body>
    <h1>Themed SVG Samples</h1>
    <div class="grid">
"""
    
    for diagram_type in diagrams:
        for theme_name, _ in themes:
            filename = f"{diagram_type}_{theme_name}.svg"
            if os.path.exists(f"{output_dir}/{filename}"):
                html_content += f"""
        <div class="card">
            <h3>{diagram_type} - {theme_name}</h3>
            <img src="{filename}" alt="{diagram_type} {theme_name}">
        </div>
"""
    
    html_content += """
    </div>
</body>
</html>
"""
    
    with open(f"{output_dir}/index.html", 'w') as f:
        f.write(html_content)
    
    print(f"\n✅ Generated viewer at: {output_dir}/index.html")
    print("   Open this file in a browser to visually inspect the themed diagrams")
    
    await svg_agent.shutdown()
    return True


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Smart Color Theming System Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    tests = [
        ("Color Utilities", test_color_utilities),
        ("Smart Theme Generation", test_smart_theme),
        ("SVG Theming", test_svg_theming),
        ("API Compatibility", test_theme_api_compatibility),
        ("Sample Generation", generate_themed_samples)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if not result:
                all_passed = False
                print(f"\n❌ {test_name} test failed")
        except Exception as e:
            all_passed = False
            print(f"\n❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed successfully!")
    else:
        print("⚠️  Some tests failed. Please review the output above.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())