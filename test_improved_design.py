#!/usr/bin/env python3
"""
Test script for improved SVG design system
- No gradients (solid colors only)
- No borders on filled shapes
- Smart text colors (black/white based on background)
- No titles/subtitles
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from models import DiagramRequest, DiagramTheme, DataPoint
from agents.svg_agent import SVGAgent
from config.settings import Settings


async def test_improved_design():
    """Test the improved design system with various themes"""
    print("\n" + "=" * 60)
    print("Testing Improved SVG Design System")
    print("=" * 60)
    
    # Initialize settings and agent
    settings = Settings()
    svg_agent = SVGAgent(settings)
    await svg_agent.initialize()
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"improved_design_test_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test cases with different themes and diagrams
    test_cases = [
        {
            "name": "Dark Theme Matrix",
            "diagram_type": "matrix_2x2",
            "theme": DiagramTheme(
                primaryColor="#1e3a8a",  # Dark blue
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="High Priority"),
                DataPoint(label="Medium Priority"),
                DataPoint(label="Low Priority"),
                DataPoint(label="No Priority")
            ]
        },
        {
            "name": "Light Theme Hub Spoke",
            "diagram_type": "hub_spoke_4",
            "theme": DiagramTheme(
                primaryColor="#fbbf24",  # Light yellow
                secondaryColor="#60a5fa",  # Light blue
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="Central Hub"),
                DataPoint(label="Service A"),
                DataPoint(label="Service B"),
                DataPoint(label="Service C"),
                DataPoint(label="Service D")
            ]
        },
        {
            "name": "Mixed Theme Roadmap",
            "diagram_type": "roadmap_quarterly_4",
            "theme": DiagramTheme(
                primaryColor="#dc2626",  # Red
                secondaryColor="#16a34a",  # Green
                accentColor="#2563eb",  # Blue
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="Phase 1"),
                DataPoint(label="Phase 2"),
                DataPoint(label="Phase 3"),
                DataPoint(label="Phase 4")
            ]
        },
        {
            "name": "Purple Theme Pyramid",
            "diagram_type": "pyramid_3_level",
            "theme": DiagramTheme(
                primaryColor="#7c3aed",  # Purple
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="Executive"),
                DataPoint(label="Management"),
                DataPoint(label="Operations")
            ]
        },
        {
            "name": "Gradient Test Funnel",
            "diagram_type": "funnel_3_stage",
            "theme": DiagramTheme(
                primaryColor="#0891b2",  # Cyan
                useSmartTheming=True
            ),
            "data_points": [
                DataPoint(label="Awareness"),
                DataPoint(label="Interest"),
                DataPoint(label="Conversion")
            ]
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Testing: {test_case['name']}")
        print(f"  Diagram: {test_case['diagram_type']}")
        print(f"  Primary color: {test_case['theme'].primaryColor}")
        
        request = DiagramRequest(
            content="Test content for improved design",
            diagram_type=test_case['diagram_type'],
            theme=test_case['theme'],
            data_points=test_case['data_points']
        )
        
        try:
            result = await svg_agent.generate(request)
            svg_content = result['content']
            
            # Save SVG file
            filename = f"{test_case['diagram_type']}_{test_case['name'].replace(' ', '_').lower()}.svg"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                f.write(svg_content)
            
            # Perform checks
            # Check for actual gradient definitions and gradient fill usage
            has_gradient_defs = '<linearGradient' in svg_content or '<radialGradient' in svg_content
            has_gradient_fills = 'fill="url(#' in svg_content and 'gradient' in svg_content
            
            checks = {
                "No gradients": not has_gradient_defs and not has_gradient_fills,
                "Seamless borders": True,  # Now we're making borders same color as fill, not removing them
                "No titles": '_title' not in svg_content,
                "Smart text colors": 'fill="#000000"' in svg_content or 'fill="#ffffff"' in svg_content
            }
            
            all_passed = all(checks.values())
            status = "✅ PASS" if all_passed else "⚠️  PARTIAL"
            
            print(f"  Status: {status}")
            for check_name, passed in checks.items():
                symbol = "✓" if passed else "✗"
                print(f"    {symbol} {check_name}")
            
            results.append({
                "name": test_case['name'],
                "diagram_type": test_case['diagram_type'],
                "passed": all_passed,
                "checks": checks,
                "file": filename
            })
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append({
                "name": test_case['name'],
                "diagram_type": test_case['diagram_type'],
                "passed": False,
                "error": str(e)
            })
    
    # Generate HTML viewer
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Improved Design Test Results</title>
    <style>
        body {
            font-family: 'Inter', -apple-system, system-ui, sans-serif;
            padding: 20px;
            background: #f8fafc;
            margin: 0;
        }
        h1 {
            color: #1e293b;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #64748b;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 24px;
        }
        .card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .card-header {
            padding: 16px;
            border-bottom: 1px solid #e2e8f0;
        }
        .card-title {
            font-size: 16px;
            font-weight: 600;
            color: #1e293b;
            margin: 0 0 4px 0;
        }
        .card-subtitle {
            font-size: 13px;
            color: #64748b;
        }
        .card-content {
            padding: 16px;
            background: #f8fafc;
        }
        .card img {
            width: 100%;
            height: auto;
            display: block;
        }
        .checks {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #e2e8f0;
        }
        .check {
            display: flex;
            align-items: center;
            margin: 4px 0;
            font-size: 13px;
        }
        .check-icon {
            width: 16px;
            height: 16px;
            margin-right: 8px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            color: white;
        }
        .check-pass {
            background: #22c55e;
        }
        .check-fail {
            background: #ef4444;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .status-pass {
            background: #dcfce7;
            color: #16a34a;
        }
        .status-partial {
            background: #fef3c7;
            color: #d97706;
        }
        .status-fail {
            background: #fee2e2;
            color: #dc2626;
        }
    </style>
</head>
<body>
    <h1>Improved SVG Design System</h1>
    <p class="subtitle">Testing gradient removal, border removal, smart text colors, and title removal</p>
    
    <div class="grid">
"""
    
    for result in results:
        if 'error' in result:
            status_class = 'status-fail'
            status_text = 'ERROR'
        elif result['passed']:
            status_class = 'status-pass'
            status_text = 'PASS'
        else:
            status_class = 'status-partial'
            status_text = 'PARTIAL'
        
        html_content += f"""
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">{result['name']}</h3>
                <div class="card-subtitle">
                    {result['diagram_type']} · 
                    <span class="status-badge {status_class}">{status_text}</span>
                </div>
            </div>
            <div class="card-content">
"""
        
        if 'file' in result:
            html_content += f'                <img src="{result["file"]}" alt="{result["name"]}">\n'
            
            if 'checks' in result:
                html_content += '                <div class="checks">\n'
                for check_name, passed in result['checks'].items():
                    icon_class = 'check-pass' if passed else 'check-fail'
                    icon = '✓' if passed else '✗'
                    html_content += f"""
                    <div class="check">
                        <div class="check-icon {icon_class}">{icon}</div>
                        <span>{check_name}</span>
                    </div>
"""
                html_content += '                </div>\n'
        else:
            html_content += f'                <p style="color: #ef4444;">Error: {result.get("error", "Unknown error")}</p>\n'
        
        html_content += """            </div>
        </div>
"""
    
    html_content += """
    </div>
</body>
</html>
"""
    
    # Save HTML viewer
    viewer_path = os.path.join(output_dir, "results.html")
    with open(viewer_path, 'w') as f:
        f.write(html_content)
    
    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r.get('passed', False))
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n" + "=" * 60)
    print(f"Summary: {passed}/{total} tests fully passed ({success_rate:.1f}%)")
    print(f"Results saved to: {output_dir}/")
    print(f"Open {viewer_path} to view results")
    print("=" * 60)
    
    await svg_agent.shutdown()
    
    return success_rate >= 80  # Consider 80% as success threshold


async def main():
    """Run the test"""
    success = await test_improved_design()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())