"""
LLM-based Mermaid Diagram Generator

Uses Google Gemini to generate syntactically correct Mermaid diagrams
based on the Mermaid playbook context and user requirements.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
import logging
import sys
import os

# Import from local playbooks
from playbooks.mermaid_playbook import (
    get_diagram_spec,
    get_syntax_patterns,
    get_construction_rules,
    get_escape_rules,
    get_diagram_examples
)

# Import request analyzer for rich context extraction
from utils.request_analyzer import RequestAnalyzer

logger = logging.getLogger(__name__)

# Import Gemini only if available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not installed. LLM generation disabled.")


class LLMMermaidGenerator:
    """
    Generate Mermaid diagrams using LLM with playbook context.
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.gemini_client = None
        self.enabled = False
        self.request_analyzer = RequestAnalyzer()  # Initialize request analyzer
        
        # Initialize Gemini if available and configured
        if (GEMINI_AVAILABLE and 
            settings.google_api_key and
            getattr(settings, 'enable_llm_mermaid', True)):
            try:
                genai.configure(api_key=settings.google_api_key)
                
                # Configure generation parameters
                generation_config = {
                    "temperature": settings.llm_temperature,
                    "max_output_tokens": settings.llm_max_tokens,
                }
                
                self.gemini_client = genai.GenerativeModel(
                    settings.gemini_model or "gemini-2.0-flash-lite",
                    generation_config=generation_config
                )
                self.enabled = True
                logger.info(f"LLM Mermaid generator initialized with {settings.gemini_model}")
                logger.info(f"  Temperature: {settings.llm_temperature}, Max tokens: {settings.llm_max_tokens}")
                
                if settings.llm_debug_mode:
                    logger.setLevel(logging.DEBUG)
                    logger.debug(f"LLM Debug mode enabled")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini for Mermaid generation: {e}")
                self.enabled = False
    
    async def generate(
        self,
        diagram_type: str,
        content: str,
        data_points: List[Dict[str, Any]],
        theme: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate Mermaid code using LLM with playbook context.
        
        Args:
            diagram_type: Type of diagram to generate
            content: User's content/requirements
            data_points: Structured data for the diagram
            theme: Theme configuration
            
        Returns:
            Generated Mermaid code or None if failed
        """
        
        if not self.enabled or not self.gemini_client:
            return None
        
        try:
            # Analyze the user's content to extract structured data
            if self.settings.enable_request_analysis:
                content_analysis = self.request_analyzer.analyze(content, diagram_type)
                key_phrases = self.request_analyzer.extract_key_phrases(content)
                
                if self.settings.llm_debug_mode:
                    logger.debug(f"Content analysis for {diagram_type}:")
                    logger.debug(f"  Extracted entities: {content_analysis.get('entities', [])}")
                    logger.debug(f"  Key phrases: {key_phrases}")
            else:
                content_analysis = {}
                key_phrases = []
            
            # Get playbook context for this diagram type
            playbook_context = self._build_playbook_context(diagram_type)
            
            if self.settings.llm_debug_mode:
                logger.debug(f"Playbook context loaded: {playbook_context.get('name', 'Unknown')}")
                logger.debug(f"  Examples available: {list(playbook_context.get('examples', {}).keys())}")
            
            # Build the prompt with rich context
            prompt = self._build_prompt(
                diagram_type,
                content,
                data_points,
                theme,
                playbook_context,
                content_analysis,
                key_phrases
            )
            
            if self.settings.llm_debug_mode:
                logger.debug(f"Generated prompt length: {len(prompt)} chars")
                logger.debug(f"First 500 chars of prompt: {prompt[:500]}...")
            
            # Generate with Gemini
            logger.info(f"Sending request to {self.settings.gemini_model}...")
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                prompt
            )
            
            if self.settings.llm_debug_mode:
                logger.debug(f"LLM response received, length: {len(response.text)} chars")
                logger.debug(f"First 200 chars: {response.text[:200]}...")
            
            # Extract and clean the Mermaid code
            mermaid_code = self._extract_mermaid_code(response.text)
            
            if self.settings.llm_debug_mode:
                logger.debug(f"Extracted Mermaid code length: {len(mermaid_code)} chars")
                logger.debug(f"First line: {mermaid_code.split(chr(10))[0] if mermaid_code else 'Empty'}")
            
            # Validate the generated code
            if self._validate_mermaid_code(mermaid_code, diagram_type):
                logger.info(f"✅ Successfully generated valid {diagram_type} diagram with LLM")
                return mermaid_code
            else:
                logger.warning(f"⚠️ LLM generated invalid Mermaid code for {diagram_type}")
                if self.settings.llm_debug_mode:
                    logger.debug(f"Invalid code: {mermaid_code[:500] if mermaid_code else 'Empty'}")
                return None
                
        except Exception as e:
            logger.error(f"LLM Mermaid generation failed: {e}")
            return None
    
    def _build_playbook_context(self, diagram_type: str) -> Dict[str, Any]:
        """
        Build comprehensive playbook context for the diagram type.
        
        Args:
            diagram_type: Type of diagram
            
        Returns:
            Dictionary with playbook information
        """
        
        spec = get_diagram_spec(diagram_type)
        if not spec:
            return {}
        
        return {
            "name": spec.get("name", diagram_type),
            "mermaid_type": spec.get("mermaid_type", diagram_type),
            "when_to_use": spec.get("when_to_use", []),
            "syntax_patterns": get_syntax_patterns(diagram_type),
            "construction_rules": get_construction_rules(diagram_type),
            "escape_rules": get_escape_rules(diagram_type),
            "examples": get_diagram_examples(diagram_type)
        }
    
    def _build_prompt(
        self,
        diagram_type: str,
        content: str,
        data_points: List[Dict[str, Any]],
        theme: Dict[str, Any],
        playbook_context: Dict[str, Any],
        content_analysis: Dict[str, Any],
        key_phrases: List[str]
    ) -> str:
        """
        Build detailed prompt for LLM with rich context.
        
        Args:
            diagram_type: Type of diagram to generate
            content: User's content/requirements
            data_points: Structured data
            theme: Theme configuration
            playbook_context: Playbook information for this diagram type
            content_analysis: Extracted structured data from content
            key_phrases: Important phrases to preserve
            
        Returns:
            Complete prompt for LLM
        """
        
        # Format syntax patterns for clarity
        syntax_str = json.dumps(playbook_context.get("syntax_patterns", {}), indent=2)
        
        # Format construction rules
        rules_str = "\n".join(playbook_context.get("construction_rules", []))
        
        # Format escape rules
        escape_str = json.dumps(playbook_context.get("escape_rules", {}), indent=2)
        
        # Get examples
        examples = playbook_context.get("examples", {})
        basic_example = examples.get("basic", "")
        complete_example = examples.get("complete", basic_example)
        
        # Format data points
        data_str = json.dumps(data_points, indent=2) if data_points else "No structured data provided"
        
        # Format extracted context from content analysis
        analysis_str = self._format_content_analysis(content_analysis, diagram_type)
        
        # Format key phrases
        key_phrases_str = "\n".join(f"- {phrase}" for phrase in key_phrases) if key_phrases else "No specific phrases identified"
        
        prompt = f"""You are a Mermaid diagram expert. Generate a syntactically correct Mermaid {diagram_type} diagram.

DIAGRAM TYPE: {playbook_context.get('name', diagram_type)}
MERMAID TYPE: {playbook_context.get('mermaid_type', diagram_type)}

USER REQUIREMENTS:
{content}

EXTRACTED CONTEXT:
{analysis_str}

KEY PHRASES TO PRESERVE:
{key_phrases_str}

DATA POINTS:
{data_str}

SYNTAX PATTERNS:
{syntax_str}

CONSTRUCTION RULES:
{rules_str}

ESCAPE RULES:
{escape_str}

BASIC EXAMPLE:
```mermaid
{basic_example}
```

COMPLETE EXAMPLE:
```mermaid
{complete_example}
```

IMPORTANT INSTRUCTIONS:
1. Generate ONLY the Mermaid code, no explanations or markdown wrappers
2. Start with the correct diagram type declaration: {playbook_context.get('mermaid_type', diagram_type)}
3. Follow the exact syntax patterns provided above
4. Apply all construction rules in order
5. Use proper escaping for special characters as defined in escape rules
6. Ensure all node IDs are unique and alphanumeric
7. Make the diagram meaningful based on the user's content and extracted context
8. Use appropriate shapes and connections for the diagram type
9. Include ALL entities, relationships, and data from the extracted context
10. Preserve the key phrases exactly as identified
11. For flowcharts: use the flow direction and include all decisions
12. For sequences: include all actors and interactions
13. For Gantt: include all tasks, dates, and dependencies
14. For pie charts: use all segments with their values/percentages
15. For mind maps: include the central topic and all branches
16. For state diagrams: include all states, transitions, and conditions
17. DO NOT include ```mermaid``` tags or any other markdown

Generate the Mermaid code now:"""
        
        return prompt
    
    def _format_content_analysis(self, analysis: Dict[str, Any], diagram_type: str) -> str:
        """
        Format the content analysis into a readable string for the LLM.
        
        Args:
            analysis: Content analysis dictionary
            diagram_type: Type of diagram
            
        Returns:
            Formatted analysis string
        """
        
        lines = []
        
        # Format based on diagram type specifics
        if diagram_type == "flowchart":
            if analysis.get('nodes'):
                lines.append(f"Nodes/Steps: {', '.join(analysis['nodes'])}")
            if analysis.get('decisions'):
                lines.append(f"Decision Points: {', '.join(analysis['decisions'])}")
            if analysis.get('flow_direction'):
                lines.append(f"Flow Direction: {analysis['flow_direction']}")
                
        elif diagram_type == "sequence":
            if analysis.get('actors'):
                lines.append(f"Actors/Services: {', '.join(analysis['actors'])}")
            if analysis.get('interactions'):
                lines.append("Interactions:")
                for interaction in analysis['interactions']:
                    lines.append(f"  - {interaction}")
                    
        elif diagram_type == "gantt":
            if analysis.get('tasks'):
                lines.append(f"Tasks: {', '.join(analysis['tasks'])}")
            if analysis.get('dates'):
                lines.append("Date Ranges:")
                for date_range in analysis['dates']:
                    lines.append(f"  - {date_range}")
            if analysis.get('durations'):
                lines.append("Durations:")
                for duration in analysis['durations']:
                    lines.append(f"  - {duration}")
            if analysis.get('dependencies'):
                lines.append(f"Dependencies: {', '.join(analysis['dependencies'])}")
                
        elif diagram_type == "pie_chart":
            if analysis.get('segments'):
                lines.append("Segments:")
                for segment in analysis['segments']:
                    lines.append(f"  - {segment['label']}: {segment['value']}")
                    
        elif diagram_type == "mind_map":
            if analysis.get('central_topic'):
                lines.append(f"Central Topic: {analysis['central_topic']}")
            if analysis.get('branches'):
                lines.append(f"Main Branches: {', '.join(analysis['branches'])}")
            if analysis.get('sub_branches'):
                lines.append("Sub-branches:")
                for parent, children in analysis['sub_branches'].items():
                    lines.append(f"  - {parent}: {', '.join(children)}")
                    
        elif diagram_type == "state_diagram":
            if analysis.get('initial_state'):
                lines.append(f"Initial State: {analysis['initial_state']}")
            if analysis.get('states'):
                lines.append(f"States: {', '.join(analysis['states'])}")
            if analysis.get('transitions'):
                lines.append("Transitions:")
                for transition in analysis['transitions']:
                    lines.append(f"  - {transition}")
            if analysis.get('final_states'):
                lines.append(f"Final States: {', '.join(analysis['final_states'])}")
                
        elif diagram_type == "journey_map":
            if analysis.get('stages'):
                lines.append(f"Journey Stages: {' -> '.join(analysis['stages'])}")
            if analysis.get('actors'):
                lines.append(f"Actors: {', '.join(analysis['actors'])}")
                
        elif diagram_type == "architecture":
            if analysis.get('layers'):
                lines.append(f"Layers: {', '.join(analysis['layers'])}")
            if analysis.get('services'):
                lines.append(f"Services/Components: {', '.join(analysis['services'])}")
            if analysis.get('technologies'):
                lines.append(f"Technologies: {', '.join(analysis['technologies'])}")
                
        elif diagram_type == "network":
            if analysis.get('devices'):
                lines.append(f"Network Devices: {', '.join(analysis['devices'])}")
            if analysis.get('connections'):
                lines.append("Connections:")
                for conn in analysis['connections']:
                    lines.append(f"  - {conn}")
                    
        elif diagram_type == "concept_map":
            if analysis.get('main_concept'):
                lines.append(f"Main Concept: {analysis['main_concept']}")
            if analysis.get('concepts'):
                lines.append(f"Concepts: {', '.join(analysis['concepts'])}")
            if analysis.get('relationships'):
                lines.append("Relationships:")
                for rel in analysis['relationships']:
                    if isinstance(rel, dict):
                        lines.append(f"  - {rel.get('from', '')} -> {rel.get('to', '')} ({rel.get('type', '')})")
                    else:
                        lines.append(f"  - {rel}")
        
        # Add generic information if available
        if analysis.get('entities') and diagram_type not in ['flowchart', 'sequence', 'mind_map']:
            lines.append(f"Entities: {', '.join(analysis['entities'])}")
        if analysis.get('relationships') and diagram_type not in ['concept_map']:
            lines.append("Relationships:")
            for rel in analysis['relationships']:
                if isinstance(rel, tuple) and len(rel) == 2:
                    lines.append(f"  - {rel[0]} -> {rel[1]}")
        if analysis.get('values'):
            lines.append(f"Values: {', '.join(str(v) for v in analysis['values'])}")
        
        return "\n".join(lines) if lines else "No specific context extracted"
    
    def _extract_mermaid_code(self, response_text: str) -> str:
        """
        Extract and clean Mermaid code from LLM response.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Cleaned Mermaid code
        """
        
        # Remove markdown code blocks if present
        text = response_text.strip()
        
        # Remove ```mermaid wrapper if present
        if text.startswith("```mermaid"):
            text = text[10:]
        elif text.startswith("```"):
            text = text[3:]
        
        # Remove closing ``` if present
        if text.endswith("```"):
            text = text[:-3]
        
        # Clean up any remaining wrapper text
        lines = text.strip().split('\n')
        
        # Find the actual start of Mermaid code
        mermaid_start = -1
        mermaid_keywords = [
            'flowchart', 'graph', 'sequenceDiagram', 'classDiagram',
            'stateDiagram', 'erDiagram', 'journey', 'gantt',
            'pie', 'quadrantChart', 'requirementDiagram', 'gitGraph',
            'mindmap', 'timeline', 'kanban', 'architecture-beta'
        ]
        
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            if any(line_lower.startswith(keyword.lower()) for keyword in mermaid_keywords):
                mermaid_start = i
                break
        
        if mermaid_start >= 0:
            lines = lines[mermaid_start:]
        
        return '\n'.join(lines).strip()
    
    def _validate_mermaid_code(self, code: str, diagram_type: str) -> bool:
        """
        Basic validation of generated Mermaid code.
        
        Args:
            code: Generated Mermaid code
            diagram_type: Expected diagram type
            
        Returns:
            True if code appears valid
        """
        
        if not code:
            return False
        
        # Get the expected Mermaid type
        spec = get_diagram_spec(diagram_type)
        if not spec:
            return False
        
        expected_type = spec.get("mermaid_type", "")
        
        # Check if code starts with correct diagram type
        first_line = code.split('\n')[0].strip().lower()
        
        # Handle special cases
        if expected_type == "journey":
            return first_line.startswith("journey")
        elif expected_type == "gantt":
            return first_line.startswith("gantt")
        elif expected_type == "erDiagram":
            return first_line.startswith("erdiagram")
        elif expected_type == "classDiagram":
            return first_line.startswith("classdiagram")
        elif expected_type == "sequenceDiagram":
            return first_line.startswith("sequencediagram")
        elif expected_type == "stateDiagram-v2":
            return first_line.startswith("statediagram")
        elif expected_type == "flowchart":
            return first_line.startswith("flowchart") or first_line.startswith("graph")
        elif expected_type == "quadrantChart":
            return first_line.startswith("quadrantchart")
        elif expected_type == "timeline":
            return first_line.startswith("timeline")
        elif expected_type == "kanban":
            return first_line.startswith("kanban")
        elif expected_type == "architecture-beta":
            return first_line.startswith("architecture-beta")
        elif expected_type == "pie":
            return first_line.startswith("pie")
        else:
            # Generic check
            return len(code.split('\n')) > 1


async def generate_mermaid_with_llm(
    settings,
    diagram_type: str,
    content: str,
    data_points: List[Dict[str, Any]],
    theme: Dict[str, Any]
) -> Optional[str]:
    """
    Convenience function to generate Mermaid code with LLM.
    
    Args:
        settings: Application settings
        diagram_type: Type of diagram
        content: User requirements
        data_points: Structured data
        theme: Theme configuration
        
    Returns:
        Generated Mermaid code or None
    """
    
    generator = LLMMermaidGenerator(settings)
    return await generator.generate(diagram_type, content, data_points, theme)