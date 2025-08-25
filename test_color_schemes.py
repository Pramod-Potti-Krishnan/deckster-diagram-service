#!/usr/bin/env python3
"""
Test script for monochromatic and complementary color schemes
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from models import DiagramRequest, DiagramTheme, DataPoint
from models.request_models import ColorScheme
from agents.svg_agent import SVGAgent
from config.settings import Settings


async def test_color_schemes():
    """Test both monochromatic and complementary color schemes"""
    print("\n" + "=" * 60)
    print("Testing Color Schemes (Monochromatic vs Complementary)")
    print("=" * 60)
    
    # Initialize settings and agent
    settings = Settings()
    svg_agent = SVGAgent(settings)
    await svg_agent.initialize()
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"color_scheme_test_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test cases comparing both schemes
    test_cases = [
        {
            "diagram_type": "matrix_2x2",
            "primary_color": "#2563eb",  # Blue
            "data_points": [
                DataPoint(label="High/High"),
                DataPoint(label="Low/High"),
                DataPoint(label="Low/Low"),
                DataPoint(label="High/Low")
            ]
        },
        {
            "diagram_type": "hub_spoke_4",
            "primary_color": "#dc2626",  # Red
            "data_points": [
                DataPoint(label="Core"),
                DataPoint(label="Node 1"),
                DataPoint(label="Node 2"),
                DataPoint(label="Node 3"),
                DataPoint(label="Node 4")
            ]
        },
        {
            "diagram_type": "pyramid_3_level",
            "primary_color": "#16a34a",  # Green
            "data_points": [
                DataPoint(label="Top"),
                DataPoint(label="Middle"),
                DataPoint(label="Bottom")
            ]
        },
        {
            "diagram_type": "venn_2_circle",
            "primary_color": "#7c3aed",  # Purple
            "data_points": [
                DataPoint(label="Set A", value=45),
                DataPoint(label="Set B", value=45),
                DataPoint(label="Overlap", value=10)
            ]
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['diagram_type']} with {test_case['primary_color']}")
        
        # Test monochromatic scheme
        mono_request = DiagramRequest(
            content="Test content",
            diagram_type=test_case['diagram_type'],
            theme=DiagramTheme(
                primaryColor=test_case['primary_color'],
                colorScheme=ColorScheme.MONOCHROMATIC,
                useSmartTheming=True
            ),
            data_points=test_case['data_points']
        )
        
        # Test complementary scheme
        comp_request = DiagramRequest(
            content="Test content",
            diagram_type=test_case['diagram_type'],
            theme=DiagramTheme(
                primaryColor=test_case['primary_color'],
                colorScheme=ColorScheme.COMPLEMENTARY,
                useSmartTheming=True
            ),
            data_points=test_case['data_points']
        )
        
        try:
            # Generate monochromatic version
            mono_result = await svg_agent.generate(mono_request)
            mono_filename = f"{test_case['diagram_type']}_monochromatic.svg"
            mono_path = os.path.join(output_dir, mono_filename)
            with open(mono_path, 'w') as f:
                f.write(mono_result['content'])
            print(f"  ✅ Monochromatic generated: {mono_filename}")
            
            # Generate complementary version
            comp_result = await svg_agent.generate(comp_request)
            comp_filename = f"{test_case['diagram_type']}_complementary.svg"
            comp_path = os.path.join(output_dir, comp_filename)
            with open(comp_path, 'w') as f:
                f.write(comp_result['content'])
            print(f"  ✅ Complementary generated: {comp_filename}")
            
            results.append({
                "diagram_type": test_case['diagram_type'],
                "primary_color": test_case['primary_color'],
                "mono_file": mono_filename,
                "comp_file": comp_filename,
                "success": True
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({
                "diagram_type": test_case['diagram_type'],
                "error": str(e),
                "success": False
            })
    
    # Generate comparison HTML viewer
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Color Scheme Comparison</title>
    <style>
        body {
            font-family: 'Inter', -apple-system, system-ui, sans-serif;
            padding: 20px;
            background: #f8fafc;
            margin: 0;
        }
        h1 {
            color: #1e293b;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #64748b;
            margin-bottom: 40px;
        }
        .comparison-grid {
            display: grid;
            gap: 40px;
        }
        .comparison-row {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .row-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid #e2e8f0;
        }
        .diagram-type {
            font-size: 20px;
            font-weight: 600;
            color: #1e293b;
            flex: 1;
        }
        .color-chip {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            border: 2px solid #e2e8f0;
        }
        .diagrams {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .diagram-container {
            text-align: center;
        }
        .scheme-label {
            font-size: 14px;
            font-weight: 600;
            color: #475569;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .diagram-wrapper {
            background: #f8fafc;
            border-radius: 8px;
            padding: 16px;
            border: 1px solid #e2e8f0;
        }
        .diagram-wrapper img {
            width: 100%;
            height: auto;
            display: block;
        }
        .monochromatic .scheme-label {
            color: #2563eb;
        }
        .complementary .scheme-label {
            color: #dc2626;
        }
    </style>
</head>
<body>
    <h1>Color Scheme Comparison</h1>
    <p class="subtitle">Monochromatic (single color variations) vs Complementary (multiple colors)</p>
    
    <div class="comparison-grid">
"""
    
    for result in results:
        if result['success']:
            html_content += f"""
        <div class="comparison-row">
            <div class="row-header">
                <div class="diagram-type">{result['diagram_type'].replace('_', ' ').title()}</div>
                <div class="color-chip" style="background: {result['primary_color']};"></div>
            </div>
            <div class="diagrams">
                <div class="diagram-container monochromatic">
                    <div class="scheme-label">Monochromatic</div>
                    <div class="diagram-wrapper">
                        <img src="{result['mono_file']}" alt="Monochromatic">
                    </div>
                </div>
                <div class="diagram-container complementary">
                    <div class="scheme-label">Complementary</div>
                    <div class="diagram-wrapper">
                        <img src="{result['comp_file']}" alt="Complementary">
                    </div>
                </div>
            </div>
        </div>
"""
    
    html_content += """
    </div>
</body>
</html>
"""
    
    # Save HTML viewer
    viewer_path = os.path.join(output_dir, "comparison.html")
    with open(viewer_path, 'w') as f:
        f.write(html_content)
    
    # Print summary
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    print(f"\n" + "=" * 60)
    print(f"Summary: {success_count}/{total_count} diagram types tested successfully")
    print(f"Results saved to: {output_dir}/")
    print(f"Open {viewer_path} to compare color schemes")
    print("=" * 60)
    
    await svg_agent.shutdown()
    
    return success_count == total_count


async def main():
    """Run the test"""
    success = await test_color_schemes()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())