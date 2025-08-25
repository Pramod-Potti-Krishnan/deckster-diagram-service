#!/usr/bin/env python3
"""
Create HTML viewer for already generated Railway test SVG files
"""

import os
from pathlib import Path
from datetime import datetime

def create_viewer():
    """Create HTML viewer for existing SVG files"""
    
    output_dir = Path("railway_test_output")
    
    # Find all SVG files
    svg_files = sorted(output_dir.glob("*.svg"))
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Railway Diagram Test Results</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #1F2937;
            border-bottom: 3px solid #3B82F6;
            padding-bottom: 10px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .diagram-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
            gap: 30px;
        }}
        .diagram-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .diagram-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e5e7eb;
        }}
        .diagram-title {{
            font-size: 18px;
            font-weight: 600;
            color: #1F2937;
        }}
        .diagram-type {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        .type-svg {{
            background: #10B981;
            color: white;
        }}
        .type-mermaid {{
            background: #3B82F6;
            color: white;
        }}
        .diagram-content {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 4px;
            padding: 20px;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: auto;
        }}
        .diagram-content svg {{
            max-width: 100%;
            height: auto;
        }}
        .metadata {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e5e7eb;
            font-size: 13px;
            color: #6B7280;
        }}
        .success-badge {{
            color: #10B981;
        }}
    </style>
</head>
<body>
    <h1>🚀 Railway Diagram Service - Test Results</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Test Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>SVG Files Found:</strong> <span class="success-badge">{len(svg_files)}</span></p>
        <p><strong>Output Directory:</strong> {output_dir.absolute()}</p>
    </div>
    
    <div class="diagram-grid">
"""
    
    # Add each SVG file
    for i, svg_file in enumerate(svg_files, 1):
        filename = svg_file.name
        
        # Try to determine type from filename
        if "cycle" in filename or "pyramid" in filename or "venn" in filename or "matrix" in filename:
            diagram_type = "SVG Template"
            type_class = "type-svg"
        else:
            diagram_type = "Mermaid/Chart"
            type_class = "type-mermaid"
        
        # Extract diagram name from filename
        diagram_name = filename[3:-4].replace('_', ' ').title() if filename[:2].isdigit() else filename[:-4].replace('_', ' ').title()
        
        # Read SVG content
        with open(svg_file, 'r') as f:
            svg_content = f.read()
        
        html_content += f"""
        <div class="diagram-card">
            <div class="diagram-header">
                <span class="diagram-title">{i}. {diagram_name}</span>
                <span class="diagram-type {type_class}">{diagram_type}</span>
            </div>
            <div class="diagram-content">
                {svg_content}
            </div>
            <div class="metadata">
                <strong>File:</strong> {filename}<br>
                <strong>Size:</strong> {svg_file.stat().st_size:,} bytes
            </div>
        </div>
        """
    
    html_content += """
    </div>
</body>
</html>
"""
    
    # Save HTML file
    html_path = output_dir / "results.html"
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    print(f"\n✅ HTML viewer created: {html_path}")
    return str(html_path)

if __name__ == "__main__":
    html_file = create_viewer()
    print(f"\nTo view results, open: {html_file}")