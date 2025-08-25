"""
Test SVG diagram generation locally
"""

import asyncio
import json
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import DiagramRequest, DiagramTheme
from agents.svg_agent import SVGAgent
from config.settings import Settings

# Test configurations for different SVG templates
TEST_CASES = [
    {
        "name": "3-Level Pyramid",
        "diagram_type": "pyramid_3_level",
        "content": "Strategic pyramid with three levels: Foundation, Core Operations, Strategic Goals",
        "data_points": [
            {"label": "Foundation", "value": 40},
            {"label": "Core Operations", "value": 35},
            {"label": "Strategic Goals", "value": 25}
        ]
    },
    {
        "name": "3-Step Cycle",
        "diagram_type": "cycle_3_step",
        "content": "Product development cycle: Design, Build, Test",
        "data_points": [
            {"label": "Design", "value": 33},
            {"label": "Build", "value": 34},
            {"label": "Test", "value": 33}
        ]
    },
    {
        "name": "2-Circle Venn",
        "diagram_type": "venn_2_circle",
        "content": "Skills overlap: Technical Skills vs Soft Skills",
        "data_points": [
            {"label": "Technical Skills", "value": 45},
            {"label": "Soft Skills", "value": 55}
        ]
    },
    {
        "name": "4-Stage Funnel",
        "diagram_type": "funnel_4_stage",
        "content": "Sales funnel: Awareness, Interest, Decision, Action",
        "data_points": [
            {"label": "Awareness", "value": 1000},
            {"label": "Interest", "value": 500},
            {"label": "Decision", "value": 200},
            {"label": "Action", "value": 50}
        ]
    },
    {
        "name": "SWOT Matrix",
        "diagram_type": "swot_matrix",
        "content": "Business SWOT analysis",
        "data_points": [
            {"label": "Strengths", "value": 25},
            {"label": "Weaknesses", "value": 25},
            {"label": "Opportunities", "value": 25},
            {"label": "Threats", "value": 25}
        ]
    },
    {
        "name": "Hub and Spoke - 4 nodes",
        "diagram_type": "hub_spoke_4",
        "content": "Central hub with 4 connected nodes",
        "data_points": [
            {"label": "Central Hub", "value": 40},
            {"label": "Node 1", "value": 20},
            {"label": "Node 2", "value": 20},
            {"label": "Node 3", "value": 10},
            {"label": "Node 4", "value": 10}
        ]
    }
]

async def test_svg_generation():
    """Test SVG generation with multiple diagram types"""
    
    # Initialize settings and agent
    settings = Settings()
    svg_agent = SVGAgent(settings)
    await svg_agent.initialize()
    
    print(f"\n🚀 Testing SVG Diagram Generation")
    print(f"=" * 60)
    print(f"Found {len(svg_agent.template_cache)} templates loaded")
    print(f"Templates: {', '.join(svg_agent.template_cache.keys())}")
    print(f"=" * 60)
    
    results = []
    successful = 0
    failed = 0
    
    for test_case in TEST_CASES:
        print(f"\n📊 Testing: {test_case['name']}")
        print(f"   Type: {test_case['diagram_type']}")
        
        try:
            # Check if template is supported
            if not await svg_agent.supports(test_case['diagram_type']):
                print(f"   ❌ Template not found: {test_case['diagram_type']}")
                failed += 1
                results.append({
                    "name": test_case['name'],
                    "status": "failed",
                    "error": "Template not found"
                })
                continue
            
            # Create request
            request = DiagramRequest(
                diagram_type=test_case['diagram_type'],
                content=test_case['content'],
                data_points=test_case.get('data_points', []),
                theme=DiagramTheme()
            )
            
            # Generate diagram
            result = await svg_agent.generate(request)
            
            # Validate result
            if result and 'content' in result:
                svg_content = result['content']
                
                # Basic validation
                if '<svg' in svg_content and '</svg>' in svg_content:
                    print(f"   ✅ Success! Generated {len(svg_content)} characters")
                    successful += 1
                    
                    # Check for proper replacements
                    if test_case.get('data_points'):
                        labels_found = sum(
                            1 for dp in test_case['data_points'] 
                            if dp['label'] in svg_content
                        )
                        print(f"   📝 Found {labels_found}/{len(test_case['data_points'])} labels in SVG")
                    
                    results.append({
                        "name": test_case['name'],
                        "status": "success",
                        "size": len(svg_content),
                        "labels_found": labels_found if test_case.get('data_points') else 0
                    })
                else:
                    print(f"   ⚠️  Invalid SVG structure")
                    failed += 1
                    results.append({
                        "name": test_case['name'],
                        "status": "failed",
                        "error": "Invalid SVG structure"
                    })
            else:
                print(f"   ❌ No content in result")
                failed += 1
                results.append({
                    "name": test_case['name'],
                    "status": "failed",
                    "error": "No content in result"
                })
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            failed += 1
            results.append({
                "name": test_case['name'],
                "status": "failed",
                "error": str(e)
            })
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📈 TEST SUMMARY")
    print(f"=" * 60)
    print(f"Total tests: {len(TEST_CASES)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"Success rate: {(successful/len(TEST_CASES)*100):.1f}%")
    
    # Save detailed results
    output_dir = f"svg_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save summary
    with open(os.path.join(output_dir, "test_summary.json"), "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(TEST_CASES),
            "successful": successful,
            "failed": failed,
            "results": results
        }, f, indent=2)
    
    print(f"\n📁 Results saved to: {output_dir}/")
    
    # Generate HTML viewer for successful diagrams
    if successful > 0:
        html_content = await generate_html_viewer(TEST_CASES, svg_agent, output_dir)
        html_path = os.path.join(output_dir, "svg_viewer.html")
        with open(html_path, "w") as f:
            f.write(html_content)
        print(f"🌐 HTML viewer saved to: {html_path}")
    
    return successful == len(TEST_CASES)

async def generate_html_viewer(test_cases, svg_agent, output_dir):
    """Generate HTML to view all SVG diagrams"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SVG Diagram Test Results</title>
    <style>
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        h1 {
            color: white;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .diagram-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        .diagram-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        .diagram-title {
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .diagram-type {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
            font-family: monospace;
            background: #f5f5f5;
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
        }
        .svg-container {
            background: #fafafa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 300px;
        }
        .svg-container svg {
            max-width: 100%;
            height: auto;
        }
        .timestamp {
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>🎨 SVG Diagram Generation Test Results</h1>
    <div class="grid">
"""
    
    for test_case in test_cases:
        try:
            # Generate SVG for this test case
            request = DiagramRequest(
                diagram_type=test_case['diagram_type'],
                content=test_case['content'],
                data_points=test_case.get('data_points', []),
                theme=DiagramTheme()
            )
            
            if await svg_agent.supports(test_case['diagram_type']):
                result = await svg_agent.generate(request)
                svg_content = result.get('content', '')
                
                html += f"""
        <div class="diagram-card">
            <div class="diagram-title">{test_case['name']}</div>
            <div class="diagram-type">{test_case['diagram_type']}</div>
            <div class="svg-container">
                {svg_content}
            </div>
        </div>
"""
        except Exception as e:
            html += f"""
        <div class="diagram-card">
            <div class="diagram-title">{test_case['name']}</div>
            <div class="diagram-type">{test_case['diagram_type']}</div>
            <div class="svg-container">
                <p style="color: red;">Error: {str(e)}</p>
            </div>
        </div>
"""
    
    html += f"""
    </div>
    <div class="timestamp">Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</body>
</html>
"""
    
    return html

if __name__ == "__main__":
    success = asyncio.run(test_svg_generation())
    sys.exit(0 if success else 1)