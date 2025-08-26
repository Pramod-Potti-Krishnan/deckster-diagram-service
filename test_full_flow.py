import sys
import os
sys.path.insert(0, '/private/tmp/deckster-diagram-service')

from utils.color_utils import MonochromaticTheme

# Create theme
theme = MonochromaticTheme('#10b981')

# Test SVG content (simplified version of actual template)
svg_content = '''<svg>
<rect id="q1_fill" x="410" y="160" fill="#3b82f6"/>
<rect id="q2_fill" x="160" y="160" fill="#60a5fa"/>
<rect id="q3_fill" x="160" y="310" fill="#dbeafe"/>
<rect id="q4_fill" x="410" y="310" fill="#3b82f6"/>
</svg>'''

print("Original SVG:")
print(svg_content)

# Apply full theme (this is what happens in real usage)
result = theme.apply_to_svg(svg_content)

print("\nAfter apply_to_svg:")
print(result)

# Extract fill colors
import re
fills = re.findall(r'id="q\d_fill"[^>]*fill="([^"]*)"', result)
print("\nFill colors after full theme:")
for i, color in enumerate(fills, 1):
    print(f"  Q{i}: {color}")

print("\nAre Q1 and Q4 different?", fills[0] != fills[3] if len(fills) == 4 else "N/A")
