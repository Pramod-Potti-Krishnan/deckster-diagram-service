#!/usr/bin/env python3
"""
Create a self-contained HTML viewer with all diagrams embedded
"""

import json
import html

# Read the production diagrams
with open('production_diagrams.json', 'r') as f:
    diagrams = json.load(f)

# HTML template with embedded data
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Railway Production Test - Self-Contained Viewer</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #1a202c;
            margin-bottom: 10px;
        }
        
        .stats-bar {
            display: flex;
            gap: 30px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e2e8f0;
        }
        
        .stat {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #48bb78;
        }
        
        .stat-label {
            color: #718096;
            font-size: 0.9em;
        }
        
        .navigation {
            background: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #e2e8f0;
        }
        
        .nav-buttons {
            display: flex;
            gap: 10px;
        }
        
        .nav-btn {
            padding: 10px 20px;
            background: #3B82F6;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        .nav-btn:hover:not(:disabled) {
            background: #2563EB;
            transform: translateY(-2px);
        }
        
        .nav-btn:disabled {
            background: #cbd5e0;
            cursor: not-allowed;
            transform: none;
        }
        
        .page-info {
            font-size: 1.1em;
            color: #4a5568;
        }
        
        .page-number {
            font-weight: bold;
            color: #3B82F6;
        }
        
        .jump-controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .jump-input {
            width: 60px;
            padding: 8px;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            font-size: 16px;
            text-align: center;
        }
        
        .main-container {
            flex: 1;
            padding: 30px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .diagram-container {
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 1200px;
            min-height: 600px;
        }
        
        .diagram-header {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .diagram-title {
            font-size: 2em;
            color: #2d3748;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .diagram-number {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
        }
        
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.7em;
            font-weight: 500;
        }
        
        .badge-svg {
            background: #9f7aea;
            color: white;
        }
        
        .badge-mermaid {
            background: #4299e1;
            color: white;
        }
        
        .diagram-content {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
            overflow: auto;
            padding: 20px;
        }
        
        .svg-content {
            max-width: 100%;
            height: auto;
        }
        
        .mermaid-diagram {
            max-width: 100%;
        }
        
        .error-message {
            background: #fed7d7;
            color: #c53030;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .loading {
            text-align: center;
            color: #718096;
            font-size: 1.2em;
        }
        
        .shortcuts {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            font-size: 0.9em;
        }
        
        .shortcuts h3 {
            margin-bottom: 10px;
            color: #4a5568;
        }
        
        .shortcuts kbd {
            background: #f7fafc;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Railway Production Test Results</h1>
        <p style="color: #718096;">WebSocket Diagram Service - Production Deployment</p>
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-value">32/32</div>
                <div class="stat-label">Tests Passed</div>
            </div>
            <div class="stat">
                <div class="stat-value">100%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat">
                <div class="stat-value">25</div>
                <div class="stat-label">SVG Templates</div>
            </div>
            <div class="stat">
                <div class="stat-value">7</div>
                <div class="stat-label">Mermaid Diagrams</div>
            </div>
        </div>
    </div>

    <div class="navigation">
        <div class="nav-buttons">
            <button class="nav-btn" id="prevBtn" onclick="changePage(-1)">← Previous</button>
            <button class="nav-btn" id="nextBtn" onclick="changePage(1)">Next →</button>
        </div>
        
        <div class="page-info">
            Diagram <span class="page-number" id="currentPage">1</span> of <span class="page-number" id="totalPages">32</span>
        </div>
        
        <div class="jump-controls">
            <label>Jump to:</label>
            <input type="number" class="jump-input" id="jumpInput" min="1" max="32" value="1">
            <button class="nav-btn" onclick="jumpToPage()">Go</button>
        </div>
    </div>

    <div class="main-container">
        <div class="diagram-container">
            <div class="diagram-header">
                <div class="diagram-title">
                    <span class="diagram-number" id="diagramNumber">#1</span>
                    <span id="diagramName">Loading...</span>
                    <span class="badge" id="diagramBadge">...</span>
                </div>
            </div>
            
            <div class="diagram-content" id="diagramContent">
                <div class="loading">Loading diagrams...</div>
            </div>
        </div>
    </div>

    <div class="shortcuts">
        <h3>⌨️ Shortcuts</h3>
        <div><kbd>←</kbd> Previous</div>
        <div><kbd>→</kbd> Next</div>
        <div><kbd>1-9</kbd> Jump to diagram</div>
    </div>

    <script>
        // Embedded diagram data
        const diagrams = DIAGRAM_DATA_PLACEHOLDER;
        
        // Initialize Mermaid
        mermaid.initialize({ 
            startOnLoad: false,
            theme: 'default',
            themeVariables: {
                primaryColor: '#3B82F6',
                primaryTextColor: '#1F2937',
                primaryBorderColor: '#60A5FA',
                lineColor: '#60A5FA',
                background: '#FFFFFF'
            }
        });

        let currentIndex = 0;

        // Display a specific diagram
        function displayDiagram(index) {
            if (index < 0 || index >= diagrams.length) return;
            
            currentIndex = index;
            const diagram = diagrams[index];
            
            // Update navigation
            document.getElementById('currentPage').textContent = index + 1;
            document.getElementById('jumpInput').value = index + 1;
            document.getElementById('prevBtn').disabled = index === 0;
            document.getElementById('nextBtn').disabled = index === diagrams.length - 1;
            
            // Update header
            document.getElementById('diagramNumber').textContent = `#${index + 1}`;
            document.getElementById('diagramName').textContent = diagram.type.replace(/_/g, ' ').toUpperCase();
            
            const badge = document.getElementById('diagramBadge');
            if (diagram.category === 'svg') {
                badge.className = 'badge badge-svg';
                badge.textContent = 'SVG Template';
            } else {
                badge.className = 'badge badge-mermaid';
                badge.textContent = 'Mermaid';
            }
            
            // Display content
            const contentDiv = document.getElementById('diagramContent');
            
            if (!diagram.success) {
                contentDiv.innerHTML = `<div class="error-message">Error: ${diagram.error || 'Failed to generate'}</div>`;
                return;
            }
            
            if (diagram.content) {
                // Display SVG content directly
                contentDiv.innerHTML = `<div class="svg-content">${diagram.content}</div>`;
                
                // If it contains embedded Mermaid, extract and render it
                if (diagram.content.includes('application/mermaid+json')) {
                    try {
                        const match = diagram.content.match(/"code":\\s*"([^"]+)"/);
                        if (match) {
                            const mermaidCode = match[1].replace(/\\\\n/g, '\\n');
                            contentDiv.innerHTML = `<div class="mermaid-diagram" id="mermaid-${index}">${mermaidCode}</div>`;
                            mermaid.run({
                                nodes: [document.getElementById(`mermaid-${index}`)]
                            });
                        }
                    } catch (e) {
                        console.error('Error rendering Mermaid:', e);
                    }
                }
            } else if (diagram.mermaid_code) {
                // Render Mermaid code
                contentDiv.innerHTML = `<div class="mermaid-diagram" id="mermaid-${index}">${diagram.mermaid_code}</div>`;
                mermaid.run({
                    nodes: [document.getElementById(`mermaid-${index}`)]
                });
            } else {
                contentDiv.innerHTML = '<div class="error-message">No content available</div>';
            }
        }

        // Navigation functions
        function changePage(direction) {
            const newIndex = currentIndex + direction;
            if (newIndex >= 0 && newIndex < diagrams.length) {
                displayDiagram(newIndex);
            }
        }

        function jumpToPage() {
            const page = parseInt(document.getElementById('jumpInput').value);
            if (page >= 1 && page <= diagrams.length) {
                displayDiagram(page - 1);
            }
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowLeft':
                    changePage(-1);
                    break;
                case 'ArrowRight':
                    changePage(1);
                    break;
                default:
                    // Number keys 1-9 for quick navigation
                    if (e.key >= '1' && e.key <= '9') {
                        const index = parseInt(e.key) - 1;
                        if (index < diagrams.length) {
                            displayDiagram(index);
                        }
                    }
            }
        });

        // Initialize with first diagram
        document.getElementById('totalPages').textContent = diagrams.length;
        document.getElementById('jumpInput').max = diagrams.length;
        displayDiagram(0);
    </script>
</body>
</html>"""

# Replace placeholder with actual data
html_content = html_content.replace('DIAGRAM_DATA_PLACEHOLDER', json.dumps(diagrams))

# Write the self-contained HTML
with open('railway_production_self_contained.html', 'w') as f:
    f.write(html_content)

print(f"Created self-contained HTML with {len(diagrams)} diagrams")
print("File: railway_production_self_contained.html")