import sys
sys.path.insert(0, '/private/tmp/deckster-diagram-service')

from utils.color_utils import MonochromaticTheme

theme = MonochromaticTheme('#10b981')

# Check which original colors map to the duplicate
original_colors = ['#dbeafe', '#fef3c7', '#fee2e2', '#dcfce7']
print("Color mappings:")
for color in original_colors:
    if color in theme.color_map:
        print(f"  {color} -> {theme.color_map[color]}")
