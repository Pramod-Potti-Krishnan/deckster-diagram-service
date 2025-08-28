#!/usr/bin/env python3
"""
Test text parsing logic directly
"""

from pathlib import Path
from types import SimpleNamespace
from agents.svg_agent import SVGAgent
from models import DiagramRequest

# Create minimal settings
settings = SimpleNamespace(
    templates_dir=Path("templates"),
    enable_smart_colors=True
)

# Create agent
agent = SVGAgent(settings)

# Test parsing logic
test_cases = [
    ("pyramid_3_level", "Strategic goals at top. Tactical initiatives in middle. Operational tasks at bottom."),
    ("cycle_3_step", "Plan phase. Execute phase. Review phase."),
    ("venn_2_circle", "Product features. Customer needs."),
]

for diagram_type, content in test_cases:
    print(f"\n{diagram_type}:")
    print(f"  Input: {content}")
    
    # Create request
    request = DiagramRequest(
        content=content,
        diagram_type=diagram_type,
        theme={"primaryColor": "#3B82F6"}
    )
    
    # Extract data points
    data_points = agent.extract_data_points(request)
    
    print(f"  Parsed into {len(data_points)} segments:")
    for i, dp in enumerate(data_points):
        print(f"    [{i+1}] {dp['label']}")