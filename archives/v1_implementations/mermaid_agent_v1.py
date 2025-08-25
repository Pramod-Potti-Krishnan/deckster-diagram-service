"""
Mermaid Diagram Agent

Generates diagrams using Mermaid syntax.
"""

from typing import Dict, Any, List
import json
import os

from models import DiagramRequest
from .base_agent import BaseAgent
from utils.logger import setup_logger
from utils.mermaid_renderer import render_mermaid_to_svg
from utils.llm_mermaid_generator import generate_mermaid_with_llm

logger = setup_logger(__name__)


class MermaidAgent(BaseAgent):
    """
    Agent for Mermaid-based diagram generation
    
    Generates Mermaid code and returns it for client-side rendering.
    """
    
    def __init__(self, settings):
        super().__init__(settings)
        self.settings = settings  # Store settings for LLM access
        self.supported_types = [
            "flowchart", "sequence", "gantt", "pie_chart",
            "journey_map", "mind_map", "architecture",
            "network", "concept_map", "state_diagram"
        ]
        # Check if server-side rendering is enabled
        self.server_side_rendering = os.getenv("MERMAID_SERVER_RENDER", "true").lower() == "true"
        logger.info(f"Mermaid server-side rendering: {self.server_side_rendering}")
        
        # Log LLM status
        if settings.enable_llm_mermaid and settings.google_api_key:
            logger.info(f"LLM Mermaid generation enabled with model: {settings.gemini_model}")
        else:
            logger.info("LLM Mermaid generation disabled, using templates")
    
    async def supports(self, diagram_type: str) -> bool:
        """Check if diagram type is supported"""
        return diagram_type in self.supported_types
    
    async def generate(self, request: DiagramRequest) -> Dict[str, Any]:
        """Generate Mermaid diagram code"""
        
        # Validate request
        self.validate_request(request)
        
        # Extract data points
        data_points = self.extract_data_points(request)
        
        # PRIMARY: Always try LLM generation first
        mermaid_code = None
        generation_method_suffix = ""
        llm_attempted = False
        llm_failure_reason = None
        
        # Check if LLM is available
        if not self.settings.google_api_key:
            llm_failure_reason = "No Google API key configured"
            logger.warning(f"LLM generation not available: {llm_failure_reason}")
        elif not self.settings.enable_llm_mermaid:
            llm_failure_reason = "LLM generation disabled in settings"
            logger.info(f"LLM generation skipped: {llm_failure_reason}")
        else:
            # PRIMARY METHOD: Attempt LLM generation
            llm_attempted = True
            logger.info(f"🚀 Starting LLM generation for {request.diagram_type} (PRIMARY method)")
            logger.debug(f"Content length: {len(request.content)} chars")
            
            try:
                mermaid_code = await generate_mermaid_with_llm(
                    self.settings,
                    request.diagram_type,
                    request.content,
                    data_points,
                    request.theme.dict()
                )
                
                if mermaid_code:
                    generation_method_suffix = "_llm"
                    logger.info(f"✅ Successfully generated {request.diagram_type} with LLM (PRIMARY)")
                    logger.debug(f"LLM generated {len(mermaid_code)} chars of Mermaid code")
                else:
                    llm_failure_reason = "LLM returned empty result"
                    logger.warning(f"⚠️ LLM generation returned no code for {request.diagram_type}")
            except Exception as e:
                llm_failure_reason = str(e)
                logger.error(f"❌ LLM generation failed: {e}")
        
        # FALLBACK: Use template-based generation only if LLM failed
        if not mermaid_code:
            logger.info(f"📋 Falling back to template generation for {request.diagram_type}")
            if llm_failure_reason:
                logger.info(f"   Reason: {llm_failure_reason}")
            
            mermaid_code = self._generate_mermaid_code(
                request.diagram_type,
                data_points,
                request.theme.dict()
            )
            generation_method_suffix = "_template"
            logger.info(f"✅ Generated {request.diagram_type} with template (FALLBACK)")
        
        # Render SVG based on configuration
        if self.server_side_rendering:
            try:
                # Try server-side rendering with Mermaid CLI
                svg_content = await render_mermaid_to_svg(
                    mermaid_code,
                    request.theme.dict(),
                    fallback_to_placeholder=True
                )
                generation_method = f"mermaid_server{generation_method_suffix}"
                logger.info(f"Successfully rendered {request.diagram_type} on server")
            except Exception as e:
                logger.warning(f"Server-side rendering failed, using placeholder: {e}")
                # Fallback to placeholder
                svg_content = self._wrap_mermaid_code(mermaid_code, request.theme.dict())
                generation_method = f"mermaid_placeholder{generation_method_suffix}"
        else:
            # Use placeholder for client-side rendering
            svg_content = self._wrap_mermaid_code(mermaid_code, request.theme.dict())
            generation_method = f"mermaid_client{generation_method_suffix}"
        
        return {
            "content": svg_content,
            "content_type": "svg",
            "diagram_type": request.diagram_type,
            "metadata": {
                "generation_method": generation_method,
                "mermaid_code": mermaid_code,
                "server_rendered": self.server_side_rendering and generation_method.startswith("mermaid_server"),
                "cache_hit": False,
                "llm_attempted": llm_attempted,
                "llm_used": "_llm" in generation_method,
                "llm_failure_reason": llm_failure_reason if not mermaid_code or "_template" in generation_method else None
            }
        }
    
    def _generate_mermaid_code(
        self,
        diagram_type: str,
        data_points: List[Dict[str, Any]],
        theme: Dict[str, Any]
    ) -> str:
        """
        Generate Mermaid code for diagram
        
        Args:
            diagram_type: Type of diagram
            data_points: Data for the diagram
            theme: Theme configuration
            
        Returns:
            Mermaid code string
        """
        
        if diagram_type == "flowchart":
            return self._generate_flowchart(data_points)
        elif diagram_type == "sequence":
            return self._generate_sequence(data_points)
        elif diagram_type == "pie_chart":
            return self._generate_pie_chart(data_points)
        elif diagram_type == "gantt":
            return self._generate_gantt(data_points)
        elif diagram_type == "journey_map":
            return self._generate_journey(data_points)
        elif diagram_type == "mind_map":
            return self._generate_mindmap(data_points)
        elif diagram_type == "state_diagram":
            return self._generate_state_diagram(data_points)
        else:
            # Default to flowchart
            return self._generate_flowchart(data_points)
    
    def _generate_flowchart(self, data_points: List[Dict[str, Any]]) -> str:
        """Generate flowchart Mermaid code"""
        
        lines = ["flowchart TD"]
        
        for i, point in enumerate(data_points):
            label = point.get("label", f"Step {i+1}")
            node_id = f"node{i}"
            
            # Add node
            lines.append(f"    {node_id}[{label}]")
            
            # Add connection to next node
            if i < len(data_points) - 1:
                next_id = f"node{i+1}"
                lines.append(f"    {node_id} --> {next_id}")
        
        return "\n".join(lines)
    
    def _generate_sequence(self, data_points: List[Dict[str, Any]]) -> str:
        """Generate sequence diagram Mermaid code"""
        
        lines = ["sequenceDiagram"]
        
        # Assume pairs of interactions
        for i in range(0, len(data_points), 2):
            if i + 1 < len(data_points):
                actor1 = data_points[i].get("label", f"Actor{i+1}")
                actor2 = data_points[i+1].get("label", f"Actor{i+2}")
                lines.append(f"    {actor1}->>+{actor2}: Message")
                lines.append(f"    {actor2}-->>-{actor1}: Response")
        
        return "\n".join(lines)
    
    def _generate_pie_chart(self, data_points: List[Dict[str, Any]]) -> str:
        """Generate pie chart Mermaid code"""
        
        lines = ['pie title Distribution']
        
        for point in data_points:
            label = point.get("label", "Item")
            value = point.get("value", 1)
            lines.append(f'    "{label}" : {value}')
        
        return "\n".join(lines)
    
    def _generate_gantt(self, data_points: List[Dict[str, Any]]) -> str:
        """Generate Gantt chart Mermaid code"""
        
        lines = [
            "gantt",
            "    title Project Timeline",
            "    dateFormat YYYY-MM-DD"
        ]
        
        for i, point in enumerate(data_points):
            label = point.get("label", f"Task {i+1}")
            lines.append(f"    {label} :a{i}, 2024-01-0{i+1}, 7d")
        
        return "\n".join(lines)
    
    def _generate_journey(self, data_points: List[Dict[str, Any]]) -> str:
        """Generate journey map Mermaid code"""
        
        lines = ["journey", "    title User Journey"]
        
        for point in data_points:
            label = point.get("label", "Step")
            lines.append(f"    {label}: 5: User")
        
        return "\n".join(lines)
    
    def _generate_mindmap(self, data_points: List[Dict[str, Any]]) -> str:
        """Generate mindmap Mermaid code"""
        
        lines = ["mindmap", "  root((Central))"]
        
        for point in data_points:
            label = point.get("label", "Branch")
            lines.append(f"    {label}")
        
        return "\n".join(lines)
    
    def _generate_state_diagram(self, data_points: List[Dict[str, Any]]) -> str:
        """Generate state diagram Mermaid code"""
        
        lines = ["stateDiagram-v2"]
        
        for i, point in enumerate(data_points):
            label = point.get("label", f"State{i+1}")
            
            if i == 0:
                lines.append(f"    [*] --> {label}")
            else:
                prev_label = data_points[i-1].get("label", f"State{i}")
                lines.append(f"    {prev_label} --> {label}")
            
            if i == len(data_points) - 1:
                lines.append(f"    {label} --> [*]")
        
        return "\n".join(lines)
    
    def _wrap_mermaid_code(self, mermaid_code: str, theme: Dict[str, Any]) -> str:
        """
        Wrap Mermaid code in SVG container
        
        For client-side rendering, we return a special SVG that contains
        the Mermaid code as metadata.
        """
        
        # Create a placeholder SVG with Mermaid code embedded
        svg_template = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
    <defs>
        <style>
            .mermaid-placeholder {{
                font-family: {theme.get('fontFamily', 'sans-serif')};
                fill: {theme.get('textColor', '#333')};
            }}
        </style>
        <script type="application/mermaid+json">{{
            "code": {json.dumps(mermaid_code)},
            "theme": "default",
            "themeVariables": {{
                "primaryColor": "{theme.get('primaryColor', '#3B82F6')}",
                "primaryTextColor": "{theme.get('textColor', '#fff')}",
                "primaryBorderColor": "{theme.get('secondaryColor', '#60A5FA')}",
                "lineColor": "{theme.get('secondaryColor', '#60A5FA')}",
                "background": "{theme.get('backgroundColor', '#fff')}"
            }}
        }}</script>
    </defs>
    <rect width="800" height="600" fill="{theme.get('backgroundColor', '#fff')}"/>
    <text x="400" y="300" text-anchor="middle" class="mermaid-placeholder">
        [Mermaid Diagram - Render on Client]
    </text>
</svg>'''
        
        return svg_template