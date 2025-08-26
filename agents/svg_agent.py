"""
SVG Template Agent

Handles diagram generation using pre-built SVG templates.
"""

import os
import re
from typing import Dict, Any, List, Optional
from xml.etree import ElementTree as ET

from models import DiagramRequest
from models.response_models import OutputType
from models.request_models import ColorScheme
from .base_agent import BaseAgent
from utils.logger import setup_logger
from utils.color_utils import SmartColorTheme, MonochromaticTheme, get_contrast_color, extract_colors_from_svg

logger = setup_logger(__name__)


class SVGAgent(BaseAgent):
    """
    Agent for SVG template-based diagram generation
    
    Uses pre-built SVG templates with text and color replacements.
    """
    
    def __init__(self, settings):
        super().__init__(settings)
        self.templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            settings.templates_dir
        )
        self.template_cache: Dict[str, str] = {}
    
    async def initialize(self):
        """Initialize SVG agent and load templates"""
        await super().initialize()
        
        # Scan and cache templates
        self._load_templates()
        
        logger.info(f"SVG Agent initialized with {len(self.template_cache)} templates")
    
    def _load_templates(self):
        """Load SVG templates into cache"""
        if not os.path.exists(self.templates_dir):
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.svg'):
                template_name = filename[:-4]
                template_path = os.path.join(self.templates_dir, filename)
                
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        self.template_cache[template_name] = f.read()
                        self.supported_types.append(template_name)
                except Exception as e:
                    logger.error(f"Error loading template {filename}: {e}")
    
    async def supports(self, diagram_type: str) -> bool:
        """Check if diagram type is supported"""
        return diagram_type in self.template_cache
    
    async def generate(self, request: DiagramRequest) -> Dict[str, Any]:
        """Generate diagram using SVG template"""
        
        # Validate request
        self.validate_request(request)
        
        # Get template
        template = self.template_cache.get(request.diagram_type)
        if not template:
            raise ValueError(f"No template found for {request.diagram_type}")
        
        # Extract data points
        data_points = self.extract_data_points(request)
        
        # Apply replacements with template type context
        svg_content = self._apply_replacements(
            template,
            data_points,
            request.theme.dict(),
            request.diagram_type  # Pass template type for specific replacements
        )
        
        # Apply theme
        print(f"DEBUG: useSmartTheming = {request.theme.useSmartTheming}")
        if request.theme.useSmartTheming:
            # Use intelligent color theming based on selected scheme
            if request.theme.colorScheme == ColorScheme.MONOCHROMATIC:
                # Use monochromatic theme (single color variations)
                theme = MonochromaticTheme(request.theme.primaryColor)
            else:
                # Use complementary theme (multiple colors)
                theme = SmartColorTheme(
                    request.theme.primaryColor,
                    request.theme.secondaryColor,
                    request.theme.accentColor,
                    color_scheme="complementary"
                )
            
            svg_content = theme.apply_to_svg(svg_content)
            
            # Apply additional processing for better design
            svg_content = self._remove_gradients(svg_content, theme)
            svg_content = self._remove_borders(svg_content)
            svg_content = self._remove_titles(svg_content)
            
            # Apply element-specific colors BEFORE text colors to ensure correct contrast
            print(f"DEBUG: About to apply final element colors for {request.diagram_type}")
            svg_content = self._apply_final_element_colors(svg_content, theme, request.diagram_type)
            print(f"DEBUG: Finished applying final element colors")
            
            # Apply smart text colors AFTER final background colors for proper contrast
            svg_content = self._apply_smart_text_colors(svg_content)
        else:
            # Use basic theme replacement
            svg_content = self.apply_theme(svg_content, request.theme.dict())
        
        return {
            # Old format (backward compatibility)
            "content": svg_content,
            "content_type": "svg",
            "diagram_type": request.diagram_type,
            
            # V2 format indicators
            "output_type": OutputType.SVG.value,
            "svg": {
                "content": svg_content,
                "is_placeholder": False
            },
            "rendering": {
                "server_rendered": True,
                "render_method": "template",
                "render_status": "success"
            },
            
            # Metadata (works for both formats)
            "metadata": {
                "generation_method": "svg_template",
                "template_used": request.diagram_type,
                "elements_modified": len(data_points),
                "cache_hit": False,
                "server_rendered": True
            }
        }
    
    def _apply_replacements(
        self,
        template: str,
        data_points: List[Dict[str, Any]],
        theme: Dict[str, Any],
        template_type: str = None
    ) -> str:
        """
        Apply text replacements to template
        
        Args:
            template: SVG template content
            data_points: Data points to insert
            theme: Theme configuration
            template_type: Specific template type for targeted replacements
            
        Returns:
            Modified SVG content
        """
        
        svg_content = template
        
        # Get template-specific placeholders
        placeholders = self._get_template_placeholders(template_type)
        
        # Replace each placeholder with corresponding data point
        for i, point in enumerate(data_points):
            if i < len(placeholders):
                placeholder = placeholders[i]
                label = point.get("label", "")
                
                if placeholder and label:
                    # Handle split text (e.g., "Central\nHub" in tspan elements)
                    if "\n" in placeholder:
                        # Replace both the split version and the continuous version
                        parts = placeholder.split("\n")
                        # Try replacing as continuous text first
                        continuous = "".join(parts)
                        if continuous in svg_content:
                            svg_content = svg_content.replace(continuous, label)
                        # Then try replacing parts separately if they appear on different lines
                        for part in parts:
                            if part in svg_content:
                                # Only replace if it's the exact part (avoid partial replacements)
                                svg_content = svg_content.replace(f">{part}<", f">{label}<")
                    else:
                        # Simple replacement for non-split text
                        svg_content = svg_content.replace(placeholder, label)
        
        return svg_content
    
    def _remove_gradients(self, svg_content: str, theme) -> str:
        """Replace gradient fills with solid colors from theme"""
        import re
        
        # First, replace all gradient fill references with solid colors
        # Pattern to match any fill that references a gradient
        gradient_fill_pattern = r'fill="url\(#[^)]+\)"'
        
        # Counter for varying colors
        color_index = 0
        
        def replace_gradient_fill(match):
            nonlocal color_index
            # Cycle through different theme colors for variety
            if color_index % 4 == 0:
                color = theme.palette['primary'][min(2, len(theme.palette['primary'])-1)]
            elif color_index % 4 == 1:
                color = theme.palette['secondary'][min(2, len(theme.palette['secondary'])-1)]
            elif color_index % 4 == 2:
                color = theme.palette['accent'][min(1, len(theme.palette['accent'])-1)]
            else:
                color = theme.palette['primary'][min(1, len(theme.palette['primary'])-1)]
            color_index += 1
            return f'fill="{color}"'
        
        svg_content = re.sub(gradient_fill_pattern, replace_gradient_fill, svg_content)
        
        # Remove gradient definitions from defs section
        # Pattern to remove linearGradient and radialGradient elements
        svg_content = re.sub(r'<linearGradient[^>]*>.*?</linearGradient>', '', svg_content, flags=re.DOTALL)
        svg_content = re.sub(r'<radialGradient[^>]*>.*?</radialGradient>', '', svg_content, flags=re.DOTALL)
        
        # Clean up empty defs sections
        svg_content = re.sub(r'<defs>\s*</defs>', '', svg_content)
        
        return svg_content
    
    def _remove_borders(self, svg_content: str) -> str:
        """Make borders same color as fill for filled shapes"""
        import re
        
        # Find all elements with both fill and stroke
        # Pattern to match elements with fill color
        element_pattern = r'(<(?:rect|circle|path|polygon|ellipse)[^>]*fill="(#[0-9a-fA-F]{6})"[^>]*>)'
        
        def update_stroke(match):
            element = match.group(1)
            fill_color = match.group(2)
            
            # If element has a stroke attribute, replace it with fill color
            # Otherwise leave element unchanged (for lines, axes, etc.)
            if 'stroke=' in element:
                # Replace stroke color with fill color
                element = re.sub(r'stroke="[^"]*"', f'stroke="{fill_color}"', element)
            
            return element
        
        # Process elements that have fill colors
        svg_content = re.sub(element_pattern, update_stroke, svg_content)
        
        # Also handle reverse order (stroke before fill)
        element_pattern2 = r'(<(?:rect|circle|path|polygon|ellipse)[^>]*stroke="[^"]*"[^>]*fill="(#[0-9a-fA-F]{6})"[^>]*>)'
        
        def update_stroke2(match):
            element = match.group(1)
            fill_color = match.group(2)
            # Replace stroke color with fill color
            element = re.sub(r'stroke="[^"]*"', f'stroke="{fill_color}"', element)
            return element
        
        svg_content = re.sub(element_pattern2, update_stroke2, svg_content)
        
        return svg_content
    
    def _remove_titles(self, svg_content: str) -> str:
        """Remove title and subtitle text elements"""
        import re
        
        # Remove title elements and their content
        # Pattern to match title text elements
        title_pattern = r'<text[^>]*id="[^"]*_title"[^>]*>.*?</text>\s*'
        svg_content = re.sub(title_pattern, '', svg_content, flags=re.DOTALL)
        
        # Remove subtitles (usually the text element right after title)
        # Pattern for text elements that appear to be subtitles
        subtitle_patterns = [
            r'<text[^>]*y="[789]\d"[^>]*font-size="1[234]"[^>]*>.*?</text>\s*',  # Small text near top
            r'<text[^>]*>.*?(?:Quarterly Milestones|Impact vs Effort|Analysis).*?</text>\s*',  # Common subtitles
        ]
        
        for pattern in subtitle_patterns:
            svg_content = re.sub(pattern, '', svg_content, flags=re.DOTALL)
        
        return svg_content
    
    def _apply_smart_text_colors(self, svg_content: str) -> str:
        """Apply black or white text color based on background luminance"""
        import re
        
        # Extract all unique fill colors from the SVG
        fill_colors = extract_colors_from_svg(svg_content)
        
        # Build a map of element IDs to their fill colors
        # Pattern to find elements with both id and fill
        element_pattern = r'<(?:rect|circle|path|polygon)[^>]*id="([^"]+)"[^>]*fill="(#[0-9a-fA-F]{6})"'
        elements = re.findall(element_pattern, svg_content)
        
        # Also check reverse order (fill before id)
        element_pattern2 = r'<(?:rect|circle|path|polygon)[^>]*fill="(#[0-9a-fA-F]{6})"[^>]*id="([^"]+)"'
        elements2 = re.findall(element_pattern2, svg_content)
        
        # Create mapping of element IDs to colors
        element_colors = {}
        for elem_id, color in elements:
            element_colors[elem_id] = color
        for color, elem_id in elements2:
            element_colors[elem_id] = color
        
        # Find text elements and determine their background
        text_pattern = r'(<text[^>]*>)'
        
        def replace_text_color(match):
            text_tag = match.group(1)
            
            # Try to determine background color based on position or parent
            # Default to white background if can't determine
            bg_color = "#ffffff"
            
            # Extract position from text element
            x_match = re.search(r'x="(\d+)"', text_tag)
            y_match = re.search(r'y="(\d+)"', text_tag)
            
            if x_match and y_match:
                x, y = int(x_match.group(1)), int(y_match.group(1))
                
                # Look for containing elements based on position
                # This is a simplified approach - checking common patterns
                for elem_id, color in element_colors.items():
                    # Check if this text might be inside this element
                    # (This is a heuristic - proper XML parsing would be better)
                    
                    # Extract text element ID if present
                    text_id_match = re.search(r'id="([^"]+)"', text_tag)
                    if text_id_match:
                        text_id = text_id_match.group(1)
                        
                        # Check various matching patterns
                        # 1. Direct match: q1_fill -> q1_text
                        if elem_id.replace('_fill', '_text') == text_id:
                            bg_color = color
                            break
                        # 2. Quadrant pattern: q1_fill -> quadrant_1
                        if elem_id.startswith('q') and '_fill' in elem_id:
                            quad_num = elem_id[1:].replace('_fill', '')
                            if f'quadrant_{quad_num}' == text_id:
                                bg_color = color
                                break
                        # 3. Spoke pattern: spoke_1_fill -> spoke_1_text
                        if elem_id.startswith('spoke_') and elem_id.endswith('_fill'):
                            if elem_id.replace('_fill', '_text') == text_id:
                                bg_color = color
                                break
                        # 4. Hub pattern: hub_fill -> hub_text
                        if elem_id == 'hub_fill' and text_id == 'hub_text':
                            bg_color = color
                            break
                        # 5. Generic pattern: remove _fill suffix
                        if elem_id.endswith('_fill'):
                            base_id = elem_id[:-5]  # Remove '_fill'
                            if base_id in text_id or text_id.startswith(base_id):
                                bg_color = color
                                break
            
            # Get contrast color
            text_color = get_contrast_color(bg_color)
            
            # Replace or add fill attribute
            if 'fill=' in text_tag:
                text_tag = re.sub(r'fill="[^"]*"', f'fill="{text_color}"', text_tag)
            else:
                text_tag = text_tag[:-1] + f' fill="{text_color}">'
            
            return text_tag
        
        svg_content = re.sub(text_pattern, replace_text_color, svg_content)
        
        return svg_content
    
    def _apply_final_element_colors(self, svg_content: str, theme, diagram_type: str) -> str:
        """Apply element-specific colors using spatial relationships"""
        import re
        from utils.color_utils import (
            generate_2d_gradient, generate_radial_colors, 
            blend_colors, interpolate_color, hex_to_rgb, rgb_to_hsl, hsl_to_rgb, rgb_to_hex
        )
        
        logger.info(f"Applying spatial color assignment for {diagram_type}")
        
        # Get primary color from theme
        primary_color = theme.primary if hasattr(theme, 'primary') else "#10b981"
        
        # Matrix 2x2: Use 2D gradient for logical color transitions
        if diagram_type == "matrix_2x2" and 'id="q1_fill"' in svg_content:
            logger.info("Applying 2D gradient for matrix")
            
            # Generate 2x2 gradient
            gradient = generate_2d_gradient(primary_color, 2, 2)
            
            # Map to quadrants (top-left, top-right, bottom-left, bottom-right)
            colors = [
                gradient[0][1],  # Q1 (top-right): vivid dark
                gradient[0][0],  # Q2 (top-left): vivid light
                gradient[1][0],  # Q3 (bottom-left): muted light
                gradient[1][1],  # Q4 (bottom-right): muted dark
            ]
            
            logger.info(f"Matrix gradient colors: {colors}")
            
            for i, color in enumerate(colors, 1):
                logger.info(f"Applying {color} to Q{i}")
                # Replace both fill and stroke
                svg_content = re.sub(
                    rf'(id="q{i}_fill"[^>]*)(fill=")[^"]*(")',
                    rf'\1\2{color}\3',
                    svg_content,
                    flags=re.DOTALL
                )
                svg_content = re.sub(
                    rf'(id="q{i}_fill"[^>]*)(stroke=")[^"]*(")',
                    rf'\1\2{color}\3',
                    svg_content,
                    flags=re.DOTALL
                )
        
        # Hub & Spoke: Use radial/circular color progression
        elif diagram_type.startswith("hub_spoke") and 'id="hub_fill"' in svg_content:
            logger.info("Applying radial colors for hub & spoke")
            
            # Extract number of spokes from diagram_type (e.g., hub_spoke_4)
            num_spokes = 4  # default
            if '_' in diagram_type:
                try:
                    num_spokes = int(diagram_type.split('_')[-1])
                except:
                    pass
            
            # Generate radial colors
            radial_colors = generate_radial_colors(primary_color, num_spokes)
            logger.info(f"Radial colors: {radial_colors}")
            
            # Apply hub color
            if 'hub' in radial_colors:
                svg_content = re.sub(
                    r'(id="hub_fill"[^>]*)(fill=")[^"]*(")',
                    rf'\1\2{radial_colors["hub"]}\3',
                    svg_content,
                    flags=re.DOTALL
                )
                svg_content = re.sub(
                    r'(id="hub_fill"[^>]*)(stroke=")[^"]*(")',
                    rf'\1\2{radial_colors["hub"]}\3',
                    svg_content,
                    flags=re.DOTALL
                )
            
            # Apply spoke colors
            for i in range(1, num_spokes + 1):
                if f'spoke_{i}' in radial_colors:
                    color = radial_colors[f'spoke_{i}']
                    svg_content = re.sub(
                        rf'(id="spoke_{i}_fill"[^>]*)(fill=")[^"]*(")',
                        rf'\1\2{color}\3',
                        svg_content,
                        flags=re.DOTALL
                    )
                    svg_content = re.sub(
                        rf'(id="spoke_{i}_fill"[^>]*)(stroke=")[^"]*(")',
                        rf'\1\2{color}\3',
                        svg_content,
                        flags=re.DOTALL
                    )
        
        # Pyramid: Use vertical gradient (dark to light from bottom to top)
        elif "pyramid" in diagram_type and 'id="level_' in svg_content:
            logger.info("Applying vertical gradient for pyramid")
            
            # Extract number of levels
            num_levels = 5  # default
            if '_' in diagram_type:
                for part in diagram_type.split('_'):
                    if part.isdigit():
                        num_levels = int(part)
                        break
            
            # Generate gradient colors from dark (bottom) to light (top)
            colors = []
            for i in range(num_levels):
                factor = i / max(1, num_levels - 1)
                # Generate gradient manually
                lightness_factor = 0.25 + (factor * 0.55)  # 25% to 80% lightness
                r, g, b = hex_to_rgb(primary_color)
                h, s, l = rgb_to_hsl(r, g, b)
                new_l = lightness_factor * 100
                # Adjust saturation for better visual distinction
                new_s = s - (factor * 20)  # Slightly reduce saturation toward top
                new_s = max(30, new_s)
                r, g, b = hsl_to_rgb(h, new_s, new_l)
                colors.append(rgb_to_hex(r, g, b))
            
            logger.info(f"Pyramid gradient colors: {colors}")
            
            # Apply colors to levels
            for i, color in enumerate(colors, 1):
                svg_content = re.sub(
                    rf'(id="level_{i}"[^>]*)(fill=")[^"]*(")',
                    rf'\1\2{color}\3',
                    svg_content,
                    flags=re.DOTALL
                )
        
        # Venn Diagram: Fix intersection text contrast
        elif "venn" in diagram_type:
            logger.info("Applying Venn diagram colors with proper intersection")
            
            # Find circle colors first
            circle1_match = re.search(r'id="circle_1"[^>]*fill="([^"]*)"', svg_content)
            circle2_match = re.search(r'id="circle_2"[^>]*fill="([^"]*)"', svg_content)
            
            if circle1_match and circle2_match:
                color1 = circle1_match.group(1)
                color2 = circle2_match.group(1)
                
                # Generate darker intersection color
                intersection_color = blend_colors(color1, color2)
                logger.info(f"Blending {color1} and {color2} to get {intersection_color}")
                
                # Apply to intersection/overlap elements
                intersection_patterns = [
                    r'(id="intersection[^"]*"[^>]*)(fill=")[^"]*(")',
                    r'(id="overlap[^"]*"[^>]*)(fill=")[^"]*(")',
                    r'(class="intersection[^"]*"[^>]*)(fill=")[^"]*(")',
                ]
                
                for pattern in intersection_patterns:
                    svg_content = re.sub(
                        pattern,
                        rf'\1\2{intersection_color}\3',
                        svg_content,
                        flags=re.DOTALL
                    )
        
        return svg_content
    
    def _get_template_placeholders(self, template_type: str) -> List[str]:
        """Get specific placeholders for each template type"""
        
        TEMPLATE_PLACEHOLDERS = {
            # Matrices
            "matrix_2x2": ["High / High", "Low / High", "Low / Low", "High / Low"],
            "matrix_3x3": [
                "Cell 1", "Cell 2", "Cell 3",  # Row 1
                "Cell 4", "Cell 5", "Cell 6",  # Row 2
                "Cell 7", "Cell 8", "Cell 9"   # Row 3
            ],
            
            # Hub & Spoke
            "hub_spoke_4": ["Central", "Node 1", "Node 2", "Node 3", "Node 4"],
            "hub_spoke_6": ["Central", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", "Node 6"],
            
            # Process Flows
            "process_flow_3": ["Input", "Process", "Output"],
            "process_flow_5": ["Input", "Process", "Transform", "Validate", "Output"],
            
            # Gears
            "gears_3": ["Process", "System", "Output"],
            
            # Roadmap
            "roadmap_quarterly_4": ["Q1", "Q2", "Q3", "Q4"],
            
            # Venn (with intersections)
            "venn_2_circle": ["Set A", "Set B", "A ∩ B"],
            "venn_3_circle": ["Set A", "Set B", "Set C", 
                              "A ∩ B", "A ∩ C", "B ∩ C", "A∩B∩C"],
            
            # Honeycombs - using the actual text from templates
            "honeycomb_3": ["Core", "Cell 2", "Cell 3"],
            "honeycomb_5": ["Core", "Cell 2", "Cell 3", "Cell 4", "Cell 5"],
            "honeycomb_7": ["Core", "Cell 2", "Cell 3", "Cell 4", 
                            "Cell 5", "Cell 6", "Cell 7"],
            
            # Timeline
            "timeline_horizontal": ["Event 1", "Event 2", "Event 3", "Event 4"],
            
            # Pyramids (correct order from template)
            "pyramid_3_level": ["Peak Level", "Core Level", "Foundation Level"],
            "pyramid_4_level": ["Vision", "Strategy", "Development", "Foundation"],
            "pyramid_5_level": ["Vision", "Strategy", "Planning", "Implementation", "Foundation"],
            
            # Cycles (keep existing working patterns)
            "cycle_3_step": ["Step 1", "Step 2", "Step 3"],
            "cycle_4_step": ["Step 1", "Step 2", "Step 3", "Step 4"],
            "cycle_5_step": ["Define", "Measure", "Analyze", "Improve", "Control"],
            
            # Funnels (keep existing working patterns)
            "funnel_3_stage": ["Stage 1", "Stage 2", "Stage 3"],
            "funnel_4_stage": ["Stage 1", "Stage 2", "Stage 3", "Stage 4"],
            "funnel_5_stage": ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5"],
            
            # SWOT Matrix
            "swot_matrix": ["Strengths", "Weaknesses", "Opportunities", "Threats"],
            
            # Fishbone
            "fishbone_4_bone": ["Cause 1", "Cause 2", "Cause 3", "Cause 4"]
        }
        
        # Return template-specific placeholders or fall back to generic patterns
        if template_type in TEMPLATE_PLACEHOLDERS:
            return TEMPLATE_PLACEHOLDERS[template_type]
        
        # Generic fallback for unknown templates
        return [f"Item {i+1}" for i in range(10)]
    
