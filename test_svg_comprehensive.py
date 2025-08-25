"""
Comprehensive test for ALL SVG diagram templates
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

# Comprehensive test cases for ALL available SVG templates
TEST_CASES = [
    # Pyramids
    {"name": "3-Level Pyramid", "diagram_type": "pyramid_3_level", "content": "Strategic levels", 
     "data_points": [{"label": "Foundation", "value": 40}, {"label": "Core", "value": 35}, {"label": "Peak", "value": 25}]},
    {"name": "4-Level Pyramid", "diagram_type": "pyramid_4_level", "content": "Organizational hierarchy",
     "data_points": [{"label": "Base", "value": 40}, {"label": "Middle", "value": 30}, {"label": "Upper", "value": 20}, {"label": "Top", "value": 10}]},
    {"name": "5-Level Pyramid", "diagram_type": "pyramid_5_level", "content": "Maslow's hierarchy",
     "data_points": [{"label": "Physiological", "value": 30}, {"label": "Safety", "value": 25}, {"label": "Love", "value": 20}, {"label": "Esteem", "value": 15}, {"label": "Self-actualization", "value": 10}]},
    
    # Cycles
    {"name": "3-Step Cycle", "diagram_type": "cycle_3_step", "content": "Development cycle",
     "data_points": [{"label": "Plan", "value": 33}, {"label": "Do", "value": 34}, {"label": "Check", "value": 33}]},
    {"name": "4-Step Cycle", "diagram_type": "cycle_4_step", "content": "PDCA cycle",
     "data_points": [{"label": "Plan", "value": 25}, {"label": "Do", "value": 25}, {"label": "Check", "value": 25}, {"label": "Act", "value": 25}]},
    {"name": "5-Step Cycle", "diagram_type": "cycle_5_step", "content": "DMAIC process",
     "data_points": [{"label": "Define", "value": 20}, {"label": "Measure", "value": 20}, {"label": "Analyze", "value": 20}, {"label": "Improve", "value": 20}, {"label": "Control", "value": 20}]},
    
    # Venn Diagrams
    {"name": "2-Circle Venn", "diagram_type": "venn_2_circle", "content": "Overlapping concepts",
     "data_points": [{"label": "Set A", "value": 50}, {"label": "Set B", "value": 50}]},
    {"name": "3-Circle Venn", "diagram_type": "venn_3_circle", "content": "Triple overlap",
     "data_points": [{"label": "Area 1", "value": 33}, {"label": "Area 2", "value": 33}, {"label": "Area 3", "value": 34}]},
    
    # Funnels
    {"name": "3-Stage Funnel", "diagram_type": "funnel_3_stage", "content": "Sales pipeline",
     "data_points": [{"label": "Leads", "value": 1000}, {"label": "Prospects", "value": 300}, {"label": "Customers", "value": 50}]},
    {"name": "4-Stage Funnel", "diagram_type": "funnel_4_stage", "content": "AIDA model",
     "data_points": [{"label": "Awareness", "value": 1000}, {"label": "Interest", "value": 500}, {"label": "Decision", "value": 200}, {"label": "Action", "value": 50}]},
    {"name": "5-Stage Funnel", "diagram_type": "funnel_5_stage", "content": "Customer journey",
     "data_points": [{"label": "Awareness", "value": 10000}, {"label": "Consideration", "value": 5000}, {"label": "Evaluation", "value": 2000}, {"label": "Purchase", "value": 500}, {"label": "Loyalty", "value": 100}]},
    
    # Matrices
    {"name": "2x2 Matrix", "diagram_type": "matrix_2x2", "content": "Priority matrix",
     "data_points": [{"label": "High-High", "value": 25}, {"label": "High-Low", "value": 25}, {"label": "Low-High", "value": 25}, {"label": "Low-Low", "value": 25}]},
    {"name": "3x3 Matrix", "diagram_type": "matrix_3x3", "content": "Risk assessment",
     "data_points": [{"label": "Cell 1", "value": 11}, {"label": "Cell 2", "value": 11}, {"label": "Cell 3", "value": 11}, 
                     {"label": "Cell 4", "value": 11}, {"label": "Cell 5", "value": 12}, {"label": "Cell 6", "value": 11},
                     {"label": "Cell 7", "value": 11}, {"label": "Cell 8", "value": 11}, {"label": "Cell 9", "value": 11}]},
    {"name": "SWOT Matrix", "diagram_type": "swot_matrix", "content": "SWOT analysis",
     "data_points": [{"label": "Strengths", "value": 25}, {"label": "Weaknesses", "value": 25}, {"label": "Opportunities", "value": 25}, {"label": "Threats", "value": 25}]},
    
    # Hub and Spoke
    {"name": "Hub-Spoke 4", "diagram_type": "hub_spoke_4", "content": "Central system",
     "data_points": [{"label": "Hub", "value": 40}, {"label": "Spoke 1", "value": 15}, {"label": "Spoke 2", "value": 15}, {"label": "Spoke 3", "value": 15}, {"label": "Spoke 4", "value": 15}]},
    {"name": "Hub-Spoke 6", "diagram_type": "hub_spoke_6", "content": "Network topology",
     "data_points": [{"label": "Central", "value": 30}, {"label": "Node 1", "value": 12}, {"label": "Node 2", "value": 12}, {"label": "Node 3", "value": 12}, {"label": "Node 4", "value": 12}, {"label": "Node 5", "value": 11}, {"label": "Node 6", "value": 11}]},
    
    # Honeycombs
    {"name": "3-Cell Honeycomb", "diagram_type": "honeycomb_3", "content": "Core components",
     "data_points": [{"label": "Component A", "value": 33}, {"label": "Component B", "value": 33}, {"label": "Component C", "value": 34}]},
    {"name": "5-Cell Honeycomb", "diagram_type": "honeycomb_5", "content": "Team structure",
     "data_points": [{"label": "Team 1", "value": 20}, {"label": "Team 2", "value": 20}, {"label": "Team 3", "value": 20}, {"label": "Team 4", "value": 20}, {"label": "Team 5", "value": 20}]},
    {"name": "7-Cell Honeycomb", "diagram_type": "honeycomb_7", "content": "Service mesh",
     "data_points": [{"label": "Service A", "value": 14}, {"label": "Service B", "value": 14}, {"label": "Service C", "value": 14}, {"label": "Service D", "value": 14}, {"label": "Service E", "value": 15}, {"label": "Service F", "value": 15}, {"label": "Service G", "value": 14}]},
    
    # Process Flows
    {"name": "3-Step Process", "diagram_type": "process_flow_3", "content": "Simple workflow",
     "data_points": [{"label": "Input", "value": 33}, {"label": "Process", "value": 34}, {"label": "Output", "value": 33}]},
    {"name": "5-Step Process", "diagram_type": "process_flow_5", "content": "Production line",
     "data_points": [{"label": "Raw Material", "value": 20}, {"label": "Processing", "value": 20}, {"label": "Assembly", "value": 20}, {"label": "Testing", "value": 20}, {"label": "Packaging", "value": 20}]},
    
    # Others
    {"name": "Fishbone Diagram", "diagram_type": "fishbone_4_bone", "content": "Root cause analysis",
     "data_points": [{"label": "People", "value": 25}, {"label": "Process", "value": 25}, {"label": "Equipment", "value": 25}, {"label": "Materials", "value": 25}]},
    {"name": "Gears System", "diagram_type": "gears_3", "content": "Interconnected systems",
     "data_points": [{"label": "Engine", "value": 40}, {"label": "Transmission", "value": 30}, {"label": "Output", "value": 30}]},
    {"name": "Timeline", "diagram_type": "timeline_horizontal", "content": "Project milestones",
     "data_points": [{"label": "Q1", "value": 25}, {"label": "Q2", "value": 25}, {"label": "Q3", "value": 25}, {"label": "Q4", "value": 25}]},
    {"name": "Roadmap", "diagram_type": "roadmap_quarterly_4", "content": "Product roadmap",
     "data_points": [{"label": "Q1 2024", "value": 25}, {"label": "Q2 2024", "value": 25}, {"label": "Q3 2024", "value": 25}, {"label": "Q4 2024", "value": 25}]}
]

async def test_all_svg_templates():
    """Test ALL available SVG templates"""
    
    # Initialize settings and agent
    settings = Settings()
    svg_agent = SVGAgent(settings)
    await svg_agent.initialize()
    
    print(f"\n🚀 Comprehensive SVG Template Testing")
    print(f"=" * 60)
    print(f"Templates available: {len(svg_agent.template_cache)}")
    print(f"Test cases prepared: {len(TEST_CASES)}")
    print(f"=" * 60)
    
    results = []
    successful = 0
    failed = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] 📊 Testing: {test_case['name']}")
        print(f"         Type: {test_case['diagram_type']}")
        
        try:
            # Check if template is supported
            if not await svg_agent.supports(test_case['diagram_type']):
                print(f"         ❌ Template not found")
                failed += 1
                results.append({
                    "name": test_case['name'],
                    "type": test_case['diagram_type'],
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
                
                if '<svg' in svg_content and '</svg>' in svg_content:
                    successful += 1
                    
                    # Check for label replacements
                    labels_found = 0
                    if test_case.get('data_points'):
                        labels_found = sum(
                            1 for dp in test_case['data_points'] 
                            if dp['label'] in svg_content
                        )
                    
                    print(f"         ✅ Success! Size: {len(svg_content)} chars")
                    print(f"         📝 Labels: {labels_found}/{len(test_case.get('data_points', []))}")
                    
                    results.append({
                        "name": test_case['name'],
                        "type": test_case['diagram_type'],
                        "status": "success",
                        "size": len(svg_content),
                        "labels_found": labels_found,
                        "labels_total": len(test_case.get('data_points', []))
                    })
                    
                    # Save individual SVG
                    output_dir = f"svg_comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    os.makedirs(output_dir, exist_ok=True)
                    
                    svg_file = os.path.join(output_dir, f"{test_case['diagram_type']}.svg")
                    with open(svg_file, "w") as f:
                        f.write(svg_content)
                else:
                    print(f"         ⚠️  Invalid SVG structure")
                    failed += 1
                    results.append({
                        "name": test_case['name'],
                        "type": test_case['diagram_type'],
                        "status": "failed",
                        "error": "Invalid SVG structure"
                    })
            else:
                print(f"         ❌ No content in result")
                failed += 1
                results.append({
                    "name": test_case['name'],
                    "type": test_case['diagram_type'],
                    "status": "failed",
                    "error": "No content in result"
                })
                
        except Exception as e:
            print(f"         ❌ Error: {str(e)}")
            failed += 1
            results.append({
                "name": test_case['name'],
                "type": test_case['diagram_type'],
                "status": "failed",
                "error": str(e)
            })
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📈 COMPREHENSIVE TEST SUMMARY")
    print(f"=" * 60)
    print(f"Total templates tested: {len(TEST_CASES)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"Success rate: {(successful/len(TEST_CASES)*100):.1f}%")
    
    # Save detailed results
    output_dir = f"svg_comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "test_results.json"), "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(TEST_CASES),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/len(TEST_CASES)*100):.1f}%",
            "results": results
        }, f, indent=2)
    
    print(f"\n📁 Results saved to: {output_dir}/")
    
    # Generate HTML dashboard
    if successful > 0:
        html_content = await generate_html_dashboard(TEST_CASES, svg_agent, results, output_dir)
        html_path = os.path.join(output_dir, "dashboard.html")
        with open(html_path, "w") as f:
            f.write(html_content)
        print(f"🌐 HTML dashboard saved to: {html_path}")
    
    return successful, failed

async def generate_html_dashboard(test_cases, svg_agent, results, output_dir):
    """Generate comprehensive HTML dashboard"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SVG Template Test Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .stats {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-around;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .stat {
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .categories {
            margin-bottom: 40px;
        }
        .category {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .category-title {
            font-size: 1.5em;
            color: #333;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .diagram-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        .diagram-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e0e0e0;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .diagram-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        .diagram-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .diagram-name {
            font-weight: bold;
            color: #333;
        }
        .diagram-type {
            font-size: 0.85em;
            color: #666;
            font-family: monospace;
            background: #e8e8e8;
            padding: 2px 8px;
            border-radius: 4px;
        }
        .svg-container {
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 250px;
            max-height: 400px;
            overflow: auto;
        }
        .svg-container svg {
            max-width: 100%;
            height: auto;
        }
        .status-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }
        .status-success {
            background: #4caf50;
            color: white;
        }
        .status-failed {
            background: #f44336;
            color: white;
        }
        .error-message {
            color: #f44336;
            font-size: 0.9em;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 SVG Template Test Dashboard</h1>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">""" + str(len(test_cases)) + """</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #4caf50;">""" + str(sum(1 for r in results if r['status'] == 'success')) + """</div>
                <div class="stat-label">Successful</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #f44336;">""" + str(sum(1 for r in results if r['status'] == 'failed')) + """</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat">
                <div class="stat-value">""" + f"{(sum(1 for r in results if r['status'] == 'success')/len(results)*100):.1f}" + """%</div>
                <div class="stat-label">Success Rate</div>
            </div>
        </div>
        
        <div class="categories">
"""
    
    # Group test cases by category
    categories = {
        "Pyramids": ["pyramid_3_level", "pyramid_4_level", "pyramid_5_level"],
        "Cycles": ["cycle_3_step", "cycle_4_step", "cycle_5_step"],
        "Venn Diagrams": ["venn_2_circle", "venn_3_circle"],
        "Funnels": ["funnel_3_stage", "funnel_4_stage", "funnel_5_stage"],
        "Matrices": ["matrix_2x2", "matrix_3x3", "swot_matrix"],
        "Hub & Spoke": ["hub_spoke_4", "hub_spoke_6"],
        "Honeycombs": ["honeycomb_3", "honeycomb_5", "honeycomb_7"],
        "Process Flows": ["process_flow_3", "process_flow_5"],
        "Specialized": ["fishbone_4_bone", "gears_3", "timeline_horizontal", "roadmap_quarterly_4"]
    }
    
    for category_name, diagram_types in categories.items():
        category_tests = [tc for tc in test_cases if tc['diagram_type'] in diagram_types]
        if not category_tests:
            continue
            
        html += f"""
            <div class="category">
                <div class="category-title">{category_name}</div>
                <div class="diagram-grid">
"""
        
        for test_case in category_tests:
            result = next((r for r in results if r['type'] == test_case['diagram_type']), None)
            status = result['status'] if result else 'failed'
            
            try:
                # Generate SVG for display
                request = DiagramRequest(
                    diagram_type=test_case['diagram_type'],
                    content=test_case['content'],
                    data_points=test_case.get('data_points', []),
                    theme=DiagramTheme()
                )
                
                if await svg_agent.supports(test_case['diagram_type']):
                    svg_result = await svg_agent.generate(request)
                    svg_content = svg_result.get('content', '')
                    
                    html += f"""
                    <div class="diagram-card">
                        <div class="diagram-header">
                            <span class="diagram-name">{test_case['name']}</span>
                            <span class="status-badge status-{status}">{status.upper()}</span>
                        </div>
                        <div class="diagram-type">{test_case['diagram_type']}</div>
                        <div class="svg-container">
                            {svg_content}
                        </div>
"""
                    if result and status == 'success':
                        html += f"""
                        <div style="margin-top: 10px; font-size: 0.85em; color: #666;">
                            Labels: {result.get('labels_found', 0)}/{result.get('labels_total', 0)} | 
                            Size: {result.get('size', 0)} chars
                        </div>
"""
                    html += """
                    </div>
"""
                else:
                    html += f"""
                    <div class="diagram-card">
                        <div class="diagram-header">
                            <span class="diagram-name">{test_case['name']}</span>
                            <span class="status-badge status-failed">FAILED</span>
                        </div>
                        <div class="diagram-type">{test_case['diagram_type']}</div>
                        <div class="error-message">Template not found</div>
                    </div>
"""
            except Exception as e:
                html += f"""
                    <div class="diagram-card">
                        <div class="diagram-header">
                            <span class="diagram-name">{test_case['name']}</span>
                            <span class="status-badge status-failed">ERROR</span>
                        </div>
                        <div class="diagram-type">{test_case['diagram_type']}</div>
                        <div class="error-message">{str(e)}</div>
                    </div>
"""
        
        html += """
                </div>
            </div>
"""
    
    html += f"""
        </div>
        <div style="text-align: center; color: white; margin-top: 30px; font-size: 0.9em;">
            Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
    
    return html

if __name__ == "__main__":
    successful, failed = asyncio.run(test_all_svg_templates())
    sys.exit(0 if failed == 0 else 1)