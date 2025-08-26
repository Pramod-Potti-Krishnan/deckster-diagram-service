import sys
import os
sys.path.insert(0, '/private/tmp/deckster-diagram-service')

from utils.color_utils import MonochromaticTheme

# Create theme
theme = MonochromaticTheme('#10b981')

# Test SVG content
svg_content = '''<svg>
<rect id="q1_fill" x="410" y="160" fill="#81e3c3"/>
<rect id="q2_fill" x="160" y="160" fill="#a1f6da"/>
<rect id="q3_fill" x="160" y="310" fill="#fee2e2"/>
<rect id="q4_fill" x="410" y="310" fill="#81e3c3"/>
</svg>'''

print("Original SVG:")
print(svg_content)

print("\nPalette primary colors:", theme.palette['primary'][:5])

# Apply element-specific colors
result = theme._apply_element_specific_colors(svg_content)

print("\nAfter element-specific colors:")
print(result)

# Extract fill colors
import re
fills = re.findall(r'id="q\d_fill"[^>]*fill="([^"]*)"', result)
print("\nFill colors after fix:")
for i, color in enumerate(fills, 1):
    print(f"  Q{i}: {color}")

print("\nAre Q1 and Q4 different?", fills[0] != fills[3] if len(fills) == 4 else "N/A")
