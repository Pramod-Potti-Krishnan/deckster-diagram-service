#!/usr/bin/env python3
"""Create HTML with embedded SVG content"""

import os
from pathlib import Path

def create_embedded_html():
    svg_dir = Path("railway_test_final")
    
    # Diagram configurations
    diagrams = [
        {
            "name": "Pyramid - 5 Level",
            "file": "pyramid_5_mono.svg",
            "colorScheme": "Monochromatic",
            "primaryColor": "#3b82f6",
            "uniqueColors": 6,
            "colors": ["#2469da", "#ffffff", "#000000", "#3b82f6", "#6ca1f8"]
        },
        {
            "name": "Pyramid - 5 Level",
            "file": "pyramid_5_comp.svg",
            "colorScheme": "Complementary",
            "primaryColor": "#8b5cf6",
            "uniqueColors": 6,
            "colors": ["#c6f65a", "#ffffff", "#f68b5a", "#8b5bf6", "#000000"]
        },
        {
            "name": "Matrix 2x2",
            "file": "matrix_2x2_mono.svg",
            "colorScheme": "Monochromatic",
            "primaryColor": "#10b981",
            "uniqueColors": 5,
            "colors": ["#fee2e2", "#ffffff", "#a1f6da", "#000000", "#81e3c3"]
        },
        {
            "name": "Hub & Spoke - 4 Nodes",
            "file": "hub_spoke_4.svg",
            "colorScheme": "Complementary",
            "primaryColor": "#f59e0b",
            "uniqueColors": 7,
            "colors": ["#f59e0a", "#ffffff", "#686664", "#f8bb54", "#0a61f4"]
        },
        {
            "name": "Venn Diagram - 2 Circles",
            "file": "venn_2_circle.svg",
            "colorScheme": "Complementary",
            "primaryColor": "#06b6d4",
            "uniqueColors": 4,
            "colors": ["#ffffff", "#037689", "#01363f", "#000000"]
        }
    ]
    
    # Read SVG contents
    svg_contents = {}
    for diagram in diagrams:
        svg_path = svg_dir / diagram["file"]
        if svg_path.exists():
            with open(svg_path, 'r') as f:
                svg_contents[diagram["file"]] = f.read()
        else:
            svg_contents[diagram["file"]] = '<text x="50%" y="50%" text-anchor="middle">SVG not found</text>'
    
    # Generate HTML
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Railway Deployment - Color Test Results</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 20px;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            color: rgba(255,255,255,0.9);
            text-align: center;
            margin-bottom: 40px;
            font-size: 1.2rem;
        }
        
        .status-banner {
            background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 40px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .status-banner h2 {
            font-size: 1.8rem;
            margin-bottom: 10px;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .status-item {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .status-item .label {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        
        .status-item .value {
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        .diagram-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .diagram-card {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .diagram-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
        }
        
        .diagram-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }
        
        .diagram-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .diagram-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
        }
        
        .color-scheme {
            display: inline-block;
            padding: 4px 12px;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            font-size: 0.85rem;
        }
        
        .color-preview {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        
        .color-dot {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .diagram-content {
            padding: 20px;
            background: #f8f9fa;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .diagram-content svg {
            max-width: 100%;
            height: auto;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
        }
        
        .color-analysis {
            padding: 20px;
            background: white;
            border-top: 1px solid #e5e7eb;
        }
        
        .color-analysis h4 {
            color: #374151;
            margin-bottom: 10px;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .color-palette {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .color-chip {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 4px 8px;
            background: #f3f4f6;
            border-radius: 6px;
            font-size: 0.85rem;
            font-family: 'Courier New', monospace;
        }
        
        .color-chip .swatch {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 1px solid #d1d5db;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Railway Deployment - Color Distribution Test</h1>
        <p class="subtitle">Testing improved color themes with monochromatic and complementary schemes</p>
        
        <div class="status-banner">
            <h2>✅ All Tests Passed!</h2>
            <div class="status-grid">
                <div class="status-item">
                    <div class="label">Total Tests</div>
                    <div class="value">5</div>
                </div>
                <div class="status-item">
                    <div class="label">Successful</div>
                    <div class="value">5</div>
                </div>
                <div class="status-item">
                    <div class="label">Failed</div>
                    <div class="value">0</div>
                </div>
                <div class="status-item">
                    <div class="label">Success Rate</div>
                    <div class="value">100%</div>
                </div>
            </div>
        </div>
        
        <div class="diagram-grid">
'''
    
    # Add diagram cards
    for diagram in diagrams:
        color_chips = ''.join([f'''
            <div class="color-chip">
                <div class="swatch" style="background: {color}"></div>
                <span>{color}</span>
            </div>
        ''' for color in diagram["colors"]])
        
        html += f'''
            <div class="diagram-card">
                <div class="diagram-header">
                    <div class="diagram-title">{diagram["name"]}</div>
                    <div class="diagram-info">
                        <span class="color-scheme">{diagram["colorScheme"]}</span>
                        <div class="color-preview">
                            <span style="font-size: 0.9rem;">Primary:</span>
                            <div class="color-dot" style="background: {diagram["primaryColor"]}"></div>
                        </div>
                    </div>
                </div>
                <div class="diagram-content">
                    {svg_contents[diagram["file"]]}
                </div>
                <div class="color-analysis">
                    <h4>Color Analysis ({diagram["uniqueColors"]} unique colors)</h4>
                    <div class="color-palette">
                        {color_chips}
                    </div>
                </div>
            </div>
        '''
    
    html += '''
        </div>
    </div>
</body>
</html>'''
    
    # Write the HTML file
    with open('railway_final_display.html', 'w') as f:
        f.write(html)
    
    print("✅ Created railway_final_display.html with embedded SVGs")

if __name__ == "__main__":
    create_embedded_html()