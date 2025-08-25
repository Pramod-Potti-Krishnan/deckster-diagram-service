"""
Unified Playbook - Semantic routing engine with Gemini

Uses Gemini for intelligent routing decisions based on content semantics.
Falls back to rule-based routing if AI is unavailable.
"""

from typing import Dict, List, Any, Optional
import os
import json
import asyncio

from models import DiagramRequest, GenerationStrategy, GenerationMethod
from config import SUPPORTED_DIAGRAM_TYPES, METHOD_PRIORITIES
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Import Gemini only if available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not installed. Falling back to rule-based routing.")


class UnifiedPlaybook:
    """
    Unified playbook for diagram generation routing
    
    Uses Gemini for semantic routing to intelligently determine
    the best generation method based on content analysis.
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            settings.templates_dir
        )
        
        # Build routing rules for fallback
        self.routing_rules = self._build_routing_rules()
        
        # Cache for template availability
        self.template_cache: Dict[str, bool] = {}
        
        # Initialize Gemini if available and configured
        self.gemini_client = None
        self.use_semantic_routing = False
        
        if (GEMINI_AVAILABLE and 
            settings.enable_semantic_routing and 
            settings.google_api_key):
            try:
                genai.configure(api_key=settings.google_api_key)
                self.gemini_client = genai.GenerativeModel(settings.gemini_model)
                self.use_semantic_routing = True
                logger.info(f"Initialized Gemini ({settings.gemini_model}) for semantic routing")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.use_semantic_routing = False
    
    async def initialize(self):
        """Initialize playbook and scan templates"""
        logger.info("Initializing Unified Playbook...")
        
        # Scan templates directory
        self._scan_templates()
        
        logger.info(f"Found {len(self.template_cache)} SVG templates")
        
        if self.use_semantic_routing:
            logger.info("Semantic routing enabled with Gemini")
        else:
            logger.info("Using rule-based routing")
        
        logger.info("Unified Playbook initialized")
    
    def _scan_templates(self):
        """Scan templates directory for available SVG templates"""
        if os.path.exists(self.templates_dir):
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.svg'):
                    template_name = filename[:-4]  # Remove .svg extension
                    self.template_cache[template_name] = True
                    logger.debug(f"Found template: {template_name}")
    
    def _build_routing_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Build routing rules for diagram types
        
        Returns:
            Dictionary mapping diagram types to routing information
        """
        
        rules = {}
        
        # Build rules from supported types
        for method, types in SUPPORTED_DIAGRAM_TYPES.items():
            for diagram_type in types:
                if diagram_type not in rules:
                    rules[diagram_type] = {
                        "primary": None,
                        "methods": [],
                        "confidence": {}
                    }
                
                # Add method to available methods
                rules[diagram_type]["methods"].append(method)
                
                # Set confidence based on priority
                priority = METHOD_PRIORITIES.get(method, 99)
                confidence = 1.0 - (priority * 0.2)  # Higher priority = higher confidence
                rules[diagram_type]["confidence"][method] = max(0.2, confidence)
                
                # Set primary method (lowest priority number)
                if rules[diagram_type]["primary"] is None:
                    rules[diagram_type]["primary"] = method
                else:
                    current_priority = METHOD_PRIORITIES.get(
                        rules[diagram_type]["primary"], 99
                    )
                    if priority < current_priority:
                        rules[diagram_type]["primary"] = method
        
        return rules
    
    async def get_strategy(self, request: DiagramRequest) -> GenerationStrategy:
        """
        Get generation strategy for request
        
        Args:
            request: Diagram generation request
            
        Returns:
            Generation strategy with method and fallbacks
        """
        
        # Try semantic routing first if available
        if self.use_semantic_routing:
            try:
                strategy = await self._semantic_route(request)
                if strategy:
                    return strategy
            except Exception as e:
                logger.warning(f"Semantic routing failed, falling back to rules: {e}")
        
        # Fall back to rule-based routing
        return await self._rule_based_route(request)
    
    async def _semantic_route(self, request: DiagramRequest) -> Optional[GenerationStrategy]:
        """
        Use Gemini for semantic routing
        
        Args:
            request: Diagram generation request
            
        Returns:
            Generation strategy or None if failed
        """
        
        try:
            # Prepare context about available methods
            available_templates = list(self.template_cache.keys())
            
            # Create prompt for Gemini
            prompt = f"""
            You are a diagram routing expert. Analyze the following request and determine the best generation method.
            
            Request:
            - Diagram Type: {request.diagram_type}
            - Content: {request.content[:500]}  # Limit content length
            - Data Points Count: {len(request.data_points) if request.data_points else 'Not specified'}
            - Theme: {json.dumps(request.theme.dict(), indent=2)}
            
            Available Methods:
            1. SVG_TEMPLATE: Fast, high-quality pre-built templates. Best for standard diagrams.
               Available templates: {', '.join(available_templates)}
            
            2. MERMAID: Flexible, code-based generation. Good for flowcharts, sequences, mindmaps.
               Supports: flowchart, sequence, gantt, pie_chart, journey_map, mind_map
            
            3. PYTHON_CHART: Matplotlib/Plotly based. Best for data visualizations.
               Supports: pie_chart, bar_chart, line_chart, scatter_plot, funnel
            
            Based on the content and requirements, provide a JSON response with:
            {{
                "primary_method": "SVG_TEMPLATE" | "MERMAID" | "PYTHON_CHART",
                "confidence": 0.0 to 1.0,
                "reasoning": "Brief explanation",
                "fallback_order": ["method1", "method2"],
                "quality_estimate": "high" | "medium" | "acceptable",
                "estimated_time_ms": integer
            }}
            
            Consider:
            - If an SVG template exists for {request.diagram_type}, prefer it for quality
            - For data-heavy content with numbers/percentages, consider PYTHON_CHART
            - For process flows and relationships, consider MERMAID
            - Match the diagram type to the best-suited method
            
            Return ONLY valid JSON, no additional text.
            """
            
            # Get response from Gemini
            response = await asyncio.to_thread(
                self.gemini_client.generate_content, 
                prompt
            )
            
            # Parse response
            response_text = response.text.strip()
            # Clean up response if wrapped in markdown
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            routing_decision = json.loads(response_text.strip())
            
            # Convert to GenerationStrategy
            # Map string to enum value
            method_map = {
                "SVG_TEMPLATE": GenerationMethod.SVG_TEMPLATE,
                "MERMAID": GenerationMethod.MERMAID,
                "PYTHON_CHART": GenerationMethod.PYTHON_CHART,
                "svg_template": GenerationMethod.SVG_TEMPLATE,
                "mermaid": GenerationMethod.MERMAID,
                "python_chart": GenerationMethod.PYTHON_CHART
            }
            
            primary_method = method_map.get(
                routing_decision["primary_method"],
                GenerationMethod.SVG_TEMPLATE
            )
            
            fallback_chain = [
                method_map.get(method, GenerationMethod.MERMAID)
                for method in routing_decision.get("fallback_order", [])
                if method != routing_decision["primary_method"]
            ]
            
            strategy = GenerationStrategy(
                method=primary_method,
                confidence=routing_decision["confidence"],
                reasoning=f"[Gemini] {routing_decision['reasoning']}",
                fallback_chain=fallback_chain,
                estimated_time_ms=routing_decision.get("estimated_time_ms", 1000),
                quality_estimate=routing_decision.get("quality_estimate", "medium")
            )
            
            logger.info(f"Semantic routing selected: {primary_method} (confidence: {strategy.confidence})")
            return strategy
            
        except Exception as e:
            logger.error(f"Semantic routing error: {e}")
            return None
    
    async def _rule_based_route(self, request: DiagramRequest) -> GenerationStrategy:
        """
        Fall back to rule-based routing
        
        Args:
            request: Diagram generation request
            
        Returns:
            Generation strategy
        """
        
        diagram_type = request.diagram_type.lower().replace(' ', '_')
        
        # Check if we have rules for this type
        if diagram_type in self.routing_rules:
            rules = self.routing_rules[diagram_type]
            
            # Check template availability for SVG
            if rules["primary"] == "svg_template":
                if not self._has_template(diagram_type):
                    # No template, use next best method
                    logger.info(f"No SVG template for {diagram_type}, using fallback")
                    rules = self._adjust_for_missing_template(rules)
            
            # Build strategy
            primary_method = GenerationMethod(rules["primary"])
            confidence = rules["confidence"].get(rules["primary"], 0.5)
            
            # Build fallback chain
            fallback_chain = []
            for method in rules["methods"]:
                if method != rules["primary"]:
                    fallback_chain.append(GenerationMethod(method))
            
            # Sort fallback chain by priority
            fallback_chain.sort(
                key=lambda m: METHOD_PRIORITIES.get(m.value, 99)
            )
            
            strategy = GenerationStrategy(
                method=primary_method,
                confidence=confidence,
                reasoning=self._generate_reasoning(diagram_type, primary_method),
                fallback_chain=fallback_chain,
                estimated_time_ms=self._estimate_time(primary_method),
                quality_estimate=self._estimate_quality(primary_method, confidence)
            )
            
            return strategy
        
        # Unknown type - try to infer
        return await self._infer_strategy(request)
    
    def _has_template(self, diagram_type: str) -> bool:
        """Check if SVG template exists"""
        return self.template_cache.get(diagram_type, False)
    
    def _adjust_for_missing_template(self, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust rules when SVG template is missing"""
        adjusted = rules.copy()
        
        # Remove svg_template from methods
        if "svg_template" in adjusted["methods"]:
            adjusted["methods"].remove("svg_template")
        
        # Set new primary (next best method)
        if adjusted["methods"]:
            # Sort by priority
            adjusted["methods"].sort(
                key=lambda m: METHOD_PRIORITIES.get(m, 99)
            )
            adjusted["primary"] = adjusted["methods"][0]
        
        return adjusted
    
    async def _infer_strategy(self, request: DiagramRequest) -> GenerationStrategy:
        """
        Infer strategy for unknown diagram types
        
        Args:
            request: Diagram request
            
        Returns:
            Inferred generation strategy
        """
        
        logger.info(f"Inferring strategy for unknown type: {request.diagram_type}")
        
        # Analyze content to determine best method
        content_lower = request.content.lower()
        
        # Check for chart-like patterns
        if any(word in content_lower for word in ["percentage", "value", "data", "number"]):
            # Likely a data visualization
            return GenerationStrategy(
                method=GenerationMethod.PYTHON_CHART,
                confidence=0.6,
                reasoning="Content suggests data visualization",
                fallback_chain=[GenerationMethod.MERMAID],
                estimated_time_ms=2000,
                quality_estimate="medium"
            )
        
        # Check for flow-like patterns
        if any(word in content_lower for word in ["step", "flow", "process", "then"]):
            # Likely a flow diagram
            return GenerationStrategy(
                method=GenerationMethod.MERMAID,
                confidence=0.7,
                reasoning="Content suggests flow or process",
                fallback_chain=[GenerationMethod.PYTHON_CHART],
                estimated_time_ms=1000,
                quality_estimate="medium"
            )
        
        # Default to Mermaid as most flexible
        return GenerationStrategy(
            method=GenerationMethod.MERMAID,
            confidence=0.5,
            reasoning="Default fallback for unknown type",
            fallback_chain=[GenerationMethod.PYTHON_CHART],
            estimated_time_ms=1500,
            quality_estimate="acceptable"
        )
    
    def _generate_reasoning(self, diagram_type: str, method: GenerationMethod) -> str:
        """Generate reasoning for method selection"""
        
        if method == GenerationMethod.SVG_TEMPLATE:
            return f"SVG template available for {diagram_type} with high quality"
        elif method == GenerationMethod.MERMAID:
            return f"Mermaid supports {diagram_type} with good flexibility"
        elif method == GenerationMethod.PYTHON_CHART:
            return f"Python charting for {diagram_type} with full customization"
        else:
            return f"Selected {method} for {diagram_type}"
    
    def _estimate_time(self, method: GenerationMethod) -> int:
        """Estimate generation time in milliseconds"""
        
        estimates = {
            GenerationMethod.SVG_TEMPLATE: 200,
            GenerationMethod.MERMAID: 800,
            GenerationMethod.PYTHON_CHART: 2000,
            GenerationMethod.CUSTOM: 3000
        }
        return estimates.get(method, 1000)
    
    def _estimate_quality(self, method: GenerationMethod, confidence: float) -> str:
        """Estimate output quality"""
        
        if method == GenerationMethod.SVG_TEMPLATE and confidence > 0.8:
            return "high"
        elif confidence > 0.6:
            return "medium"
        else:
            return "acceptable"