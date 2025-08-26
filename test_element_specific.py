# Test element-specific color application
import sys
sys.path.insert(0, '/private/tmp/deckster-diagram-service')

from utils.color_utils import MonochromaticTheme

# Create theme  
theme = MonochromaticTheme('#10b981')

# Original colors from matrix_2x2.svg template
svg_before_theme = '''<svg>
<rect id="q1_fill" x="410" y="160" fill="#dbeafe"/>
<rect id="q2_fill" x="160" y="160" fill="#fef3c7"/>
<rect id="q3_fill" x="160" y="310" fill="#fee2e2"/>
<rect id="q4_fill" x="410" y="310" fill="#dcfce7"/>
</svg>'''

print("Original SVG:")
print(svg_before_theme)

# Apply full theme (simulating what happens in the agent)
result = theme.apply_to_svg(svg_before_theme)

print("\nAfter theme.apply_to_svg():")
print(result)

# Extract colors
import re
for i in range(1, 5):
    match = re.search(rf'id="q{i}_fill"[^>]*fill="([^"]*)"', result)
    if match:
        print(f"  Q{i}: {match.group(1)}")

# Check for duplicates
colors = re.findall(r'fill="(#[^"]*)"', result)
print(f"\nAll colors: {colors}")
print(f"Unique colors: {set(colors)}")

q1_color = re.search(r'id="q1_fill"[^>]*fill="([^"]*)"', result).group(1)
q4_color = re.search(r'id="q4_fill"[^>]*fill="([^"]*)"', result).group(1)
print(f"\n❌ Q1 and Q4 same? {q1_color == q4_color} (Q1: {q1_color}, Q4: {q4_color})")
