"""
Request Analyzer for Mermaid Diagram Generation

Analyzes user requests to extract structured data for LLM prompts.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RequestAnalyzer:
    """
    Analyzes user requests to extract entities, relationships, and data for diagram generation.
    """
    
    def __init__(self):
        # Patterns for extracting different types of information
        self.patterns = {
            'arrow': r'(?:->|→|=>|-->|==>|\|\|--|--\||<->|<-->)',
            'percentage': r'(\d+(?:\.\d+)?)\s*%',
            'currency': r'\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)',
            'date_range': r'(\w+\s+\d{1,2}(?:-\d{1,2})?(?:,?\s+\d{4})?)\s*(?:to|-)\s*(\w+\s+\d{1,2}(?:-\d{1,2})?(?:,?\s+\d{4})?)',
            'duration': r'(\d+(?:\.\d+)?)\s*(weeks?|days?|months?|hours?)',
            'entity': r'[A-Z][a-zA-Z\s]+(?:Service|System|Component|Layer|Database|Server|Client|Gateway|API|Module)',
            'state': r"(?:state|status|phase|stage)s?\s*[:=]\s*(['\"]?)([^'\"]+)\1",
            'relationship': r'(\w+)\s+(?:has|contains|includes|owns|manages|uses|connects to|depends on|triggers|calls|sends|receives)\s+(\w+)'
        }
    
    def analyze(self, content: str, diagram_type: str) -> Dict[str, Any]:
        """
        Analyze content based on diagram type and extract relevant information.
        
        Args:
            content: User's content/requirements
            diagram_type: Type of diagram being generated
            
        Returns:
            Dictionary with extracted information
        """
        analysis = {
            'entities': [],
            'relationships': [],
            'values': [],
            'temporal': [],
            'hierarchies': [],
            'states': [],
            'raw_content': content,
            'diagram_type': diagram_type
        }
        
        # Route to specific analyzer based on diagram type
        if diagram_type == 'flowchart':
            analysis.update(self._analyze_flowchart(content))
        elif diagram_type == 'sequence':
            analysis.update(self._analyze_sequence(content))
        elif diagram_type == 'gantt':
            analysis.update(self._analyze_gantt(content))
        elif diagram_type == 'pie_chart':
            analysis.update(self._analyze_pie_chart(content))
        elif diagram_type == 'mind_map':
            analysis.update(self._analyze_mind_map(content))
        elif diagram_type == 'state_diagram':
            analysis.update(self._analyze_state_diagram(content))
        elif diagram_type == 'journey_map':
            analysis.update(self._analyze_journey_map(content))
        elif diagram_type == 'architecture':
            analysis.update(self._analyze_architecture(content))
        elif diagram_type == 'network':
            analysis.update(self._analyze_network(content))
        elif diagram_type == 'concept_map':
            analysis.update(self._analyze_concept_map(content))
        else:
            # Generic analysis
            analysis.update(self._generic_analysis(content))
        
        return analysis
    
    def _analyze_flowchart(self, content: str) -> Dict[str, Any]:
        """Extract flowchart-specific information"""
        result = {
            'nodes': [],
            'edges': [],
            'decisions': [],
            'flow_direction': 'TD'  # Default top-down
        }
        
        # Extract arrow relationships
        arrow_pattern = re.compile(self.patterns['arrow'])
        parts = arrow_pattern.split(content)
        
        if len(parts) > 1:
            # Content has arrows, extract nodes and relationships
            for i, part in enumerate(parts):
                if part.strip():
                    result['nodes'].append(part.strip())
        
        # Look for decision points (if, when, check, validate)
        decision_keywords = r'\b(if|when|check|validate|verify|test|decision|choose)\b'
        if re.search(decision_keywords, content, re.IGNORECASE):
            decisions = re.findall(r'(?:if|when|check)\s+([^,\n]+)', content, re.IGNORECASE)
            result['decisions'] = decisions
        
        # Detect flow direction preferences
        if any(word in content.lower() for word in ['left to right', 'horizontal']):
            result['flow_direction'] = 'LR'
        elif any(word in content.lower() for word in ['bottom to top', 'upward']):
            result['flow_direction'] = 'BT'
        
        return result
    
    def _analyze_sequence(self, content: str) -> Dict[str, Any]:
        """Extract sequence diagram information"""
        result = {
            'actors': [],
            'messages': [],
            'interactions': []
        }
        
        # Extract entities that look like actors/services
        entities = re.findall(r'[A-Z][a-zA-Z\s]*(?:Service|Client|Server|User|System|API|Gateway|Database)', content)
        result['actors'] = list(set(entities))
        
        # Extract interaction verbs
        interaction_verbs = ['sends', 'receives', 'calls', 'returns', 'validates', 'confirms', 
                           'requests', 'responds', 'queries', 'fetches', 'processes', 'forwards']
        for verb in interaction_verbs:
            matches = re.findall(rf'(\w+)\s+{verb}\s+([^,\n]+)', content, re.IGNORECASE)
            result['interactions'].extend(matches)
        
        return result
    
    def _analyze_gantt(self, content: str) -> Dict[str, Any]:
        """Extract Gantt chart information"""
        result = {
            'tasks': [],
            'dates': [],
            'durations': [],
            'dependencies': []
        }
        
        # Extract date ranges
        date_matches = re.findall(self.patterns['date_range'], content)
        result['dates'] = date_matches
        
        # Extract durations
        duration_matches = re.findall(self.patterns['duration'], content)
        result['durations'] = duration_matches
        
        # Extract task names (usually before colons or dates)
        task_pattern = r'([A-Z][^:,\n]+)(?:\s*[:]\s*|\s+(?:from|starts?|begins?))'
        tasks = re.findall(task_pattern, content)
        result['tasks'] = [t.strip() for t in tasks]
        
        # Look for dependencies
        dep_keywords = ['after', 'following', 'depends on', 'requires', 'upon completion']
        for keyword in dep_keywords:
            deps = re.findall(rf'{keyword}\s+([^,\n]+)', content, re.IGNORECASE)
            result['dependencies'].extend(deps)
        
        return result
    
    def _analyze_pie_chart(self, content: str) -> Dict[str, Any]:
        """Extract pie chart information"""
        result = {
            'segments': [],
            'values': [],
            'percentages': []
        }
        
        # Extract percentages
        percentages = re.findall(self.patterns['percentage'], content)
        
        # Extract currency values
        currency = re.findall(self.patterns['currency'], content)
        
        # Extract label: value patterns
        label_value_pattern = r'([^:,\n]+):\s*(\d+(?:\.\d+)?%?|\$[\d,]+(?:\.\d+)?)'
        matches = re.findall(label_value_pattern, content)
        
        for match in matches:
            label, value = match
            result['segments'].append({
                'label': label.strip(),
                'value': value.strip()
            })
        
        # Also look for "X has Y%" or "X: Y%" patterns
        has_pattern = r'([^:,\n]+)\s+(?:has|is|represents?|accounts? for)\s+(\d+(?:\.\d+)?%?)'
        has_matches = re.findall(has_pattern, content, re.IGNORECASE)
        for match in has_matches:
            if not any(s['label'] == match[0].strip() for s in result['segments']):
                result['segments'].append({
                    'label': match[0].strip(),
                    'value': match[1].strip()
                })
        
        result['percentages'] = percentages
        result['values'] = currency
        
        return result
    
    def _analyze_mind_map(self, content: str) -> Dict[str, Any]:
        """Extract mind map information"""
        result = {
            'central_topic': '',
            'branches': [],
            'sub_branches': {},
            'hierarchy_levels': []
        }
        
        # Look for central topic (often after "Central" or at the beginning)
        central_match = re.search(r'(?:central|main|root|core)(?:\s+topic)?:\s*([^,\n]+)', content, re.IGNORECASE)
        if central_match:
            result['central_topic'] = central_match.group(1).strip()
        
        # Look for main branches
        branch_pattern = r'(?:branch|category|area|section)\s*\d*:\s*([^,\n]+)'
        branches = re.findall(branch_pattern, content, re.IGNORECASE)
        result['branches'] = branches
        
        # Look for hierarchical structures with colons or parentheses
        hier_pattern = r'([^:,\n]+):\s*\(([^)]+)\)'
        hierarchies = re.findall(hier_pattern, content)
        for parent, children in hierarchies:
            result['sub_branches'][parent.strip()] = [c.strip() for c in children.split(',')]
        
        return result
    
    def _analyze_state_diagram(self, content: str) -> Dict[str, Any]:
        """Extract state diagram information"""
        result = {
            'states': [],
            'transitions': [],
            'initial_state': '',
            'final_states': [],
            'conditions': []
        }
        
        # Extract states (often capitalized or in quotes)
        state_pattern = r"(?:state|status)\s*['\"]?([A-Za-z\s]+)['\"]?"
        states = re.findall(state_pattern, content, re.IGNORECASE)
        result['states'] = list(set(states))
        
        # Look for transitions
        transition_words = ['transitions? to', 'goes? to', 'moves? to', 'becomes?', 'changes? to', 'can go to']
        for word in transition_words:
            trans = re.findall(rf'([^,\n]+)\s+{word}\s+([^,\n]+)', content, re.IGNORECASE)
            result['transitions'].extend(trans)
        
        # Find initial state
        initial_match = re.search(r'(?:start|initial|begin)\s+(?:at|with|from|state)?\s*[:\s]*([^,\n]+)', content, re.IGNORECASE)
        if initial_match:
            result['initial_state'] = initial_match.group(1).strip()
        
        # Find final states
        final_pattern = r'(?:final|end|terminal)\s+(?:state|status)?s?\s*[:\s]*([^,\n]+)'
        finals = re.findall(final_pattern, content, re.IGNORECASE)
        result['final_states'] = finals
        
        return result
    
    def _analyze_journey_map(self, content: str) -> Dict[str, Any]:
        """Extract journey map information"""
        result = {
            'stages': [],
            'actors': [],
            'touchpoints': [],
            'emotions': []
        }
        
        # Extract stages (often with arrows or sequential markers)
        if '->' in content or '→' in content:
            parts = re.split(r'->|→', content)
            result['stages'] = [p.strip() for p in parts if p.strip()]
        
        # Look for numbered or lettered stages
        numbered_pattern = r'(?:\d+\.|\b[a-z]\))\s*([^,\n]+)'
        numbered = re.findall(numbered_pattern, content, re.IGNORECASE)
        if numbered and not result['stages']:
            result['stages'] = numbered
        
        # Extract actors/personas
        actor_keywords = ['user', 'customer', 'visitor', 'buyer', 'shopper', 'client']
        for keyword in actor_keywords:
            if keyword in content.lower():
                result['actors'].append(keyword.capitalize())
        
        return result
    
    def _analyze_architecture(self, content: str) -> Dict[str, Any]:
        """Extract architecture diagram information"""
        result = {
            'layers': [],
            'components': [],
            'services': [],
            'connections': [],
            'technologies': []
        }
        
        # Extract layers
        layer_keywords = ['layer', 'tier', 'level']
        for keyword in layer_keywords:
            layers = re.findall(rf'([^,\n]+)\s+{keyword}', content, re.IGNORECASE)
            result['layers'].extend(layers)
        
        # Extract services and components
        service_pattern = r'[A-Z][a-zA-Z\s]*(?:Service|Server|API|Gateway|Database|Cache|Queue|Storage)'
        services = re.findall(service_pattern, content)
        result['services'] = list(set(services))
        
        # Extract technology mentions
        tech_keywords = ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Kafka', 'RabbitMQ', 
                        'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Nginx', 'Apache']
        for tech in tech_keywords:
            if tech.lower() in content.lower():
                result['technologies'].append(tech)
        
        return result
    
    def _analyze_network(self, content: str) -> Dict[str, Any]:
        """Extract network topology information"""
        result = {
            'devices': [],
            'connections': [],
            'topology_type': 'hierarchical'
        }
        
        # Extract network devices
        device_keywords = ['router', 'switch', 'firewall', 'server', 'client', 'hub', 
                          'gateway', 'proxy', 'load balancer', 'internet', 'cloud']
        for device in device_keywords:
            if device in content.lower():
                result['devices'].append(device.capitalize())
        
        # Extract connections
        if '->' in content or '→' in content:
            parts = re.split(r'->|→', content)
            for i in range(len(parts) - 1):
                result['connections'].append((parts[i].strip(), parts[i+1].strip()))
        
        return result
    
    def _analyze_concept_map(self, content: str) -> Dict[str, Any]:
        """Extract concept map information"""
        result = {
            'concepts': [],
            'relationships': [],
            'main_concept': ''
        }
        
        # Look for main concept
        main_match = re.search(r'(?:main|primary|central)\s+concept:\s*([^,\n]+)', content, re.IGNORECASE)
        if main_match:
            result['main_concept'] = main_match.group(1).strip()
        
        # Extract relationships with arrows
        if '->' in content or '→' in content:
            parts = re.split(r'->|→', content)
            for i in range(len(parts) - 1):
                result['relationships'].append({
                    'from': parts[i].strip(),
                    'to': parts[i+1].strip(),
                    'type': 'leads to'
                })
        
        # Extract concepts (capitalized phrases)
        concept_pattern = r'[A-Z][a-zA-Z\s]+'
        concepts = re.findall(concept_pattern, content)
        result['concepts'] = list(set(concepts))
        
        return result
    
    def _generic_analysis(self, content: str) -> Dict[str, Any]:
        """Generic analysis for unknown diagram types"""
        result = {
            'entities': [],
            'relationships': [],
            'values': []
        }
        
        # Extract any entities (capitalized words/phrases)
        entities = re.findall(r'[A-Z][a-zA-Z\s]+', content)
        result['entities'] = list(set(entities))
        
        # Extract any arrow relationships
        if re.search(self.patterns['arrow'], content):
            parts = re.split(self.patterns['arrow'], content)
            result['relationships'] = [(parts[i].strip(), parts[i+1].strip()) 
                                      for i in range(len(parts)-1) if parts[i].strip()]
        
        # Extract any numerical values
        numbers = re.findall(r'\d+(?:\.\d+)?', content)
        result['values'] = numbers
        
        return result
    
    def extract_key_phrases(self, content: str) -> List[str]:
        """
        Extract key phrases that should be preserved in the diagram.
        
        Args:
            content: User's content
            
        Returns:
            List of key phrases
        """
        # Extract quoted phrases
        quoted = re.findall(r'["\']([^"\']+)["\']', content)
        
        # Extract capitalized phrases (likely important)
        capitalized = re.findall(r'[A-Z][a-zA-Z\s]+(?:[A-Z][a-zA-Z\s]+)*', content)
        
        # Combine and deduplicate
        key_phrases = list(set(quoted + capitalized))
        
        return [phrase.strip() for phrase in key_phrases if len(phrase.strip()) > 2]
    
    def suggest_diagram_type(self, content: str) -> str:
        """
        Suggest the best diagram type based on content analysis.
        
        Args:
            content: User's content
            
        Returns:
            Suggested diagram type
        """
        content_lower = content.lower()
        
        # Check for specific indicators
        if any(word in content_lower for word in ['flow', 'process', 'decision', 'if', 'then', 'validate']):
            return 'flowchart'
        elif any(word in content_lower for word in ['timeline', 'schedule', 'gantt', 'duration', 'deadline']):
            return 'gantt'
        elif any(word in content_lower for word in ['percentage', '%', 'distribution', 'breakdown', 'portion']):
            return 'pie_chart'
        elif any(word in content_lower for word in ['interaction', 'sends', 'receives', 'calls', 'api']):
            return 'sequence'
        elif any(word in content_lower for word in ['state', 'status', 'transition', 'phase']):
            return 'state_diagram'
        elif any(word in content_lower for word in ['journey', 'experience', 'touchpoint', 'customer']):
            return 'journey_map'
        elif any(word in content_lower for word in ['mind', 'branch', 'hierarchy', 'topic']):
            return 'mind_map'
        elif any(word in content_lower for word in ['architecture', 'layer', 'tier', 'service']):
            return 'architecture'
        elif any(word in content_lower for word in ['network', 'topology', 'router', 'firewall']):
            return 'network'
        elif any(word in content_lower for word in ['concept', 'relationship', 'connection']):
            return 'concept_map'
        else:
            return 'flowchart'  # Default


def analyze_request(content: str, diagram_type: str) -> Dict[str, Any]:
    """
    Convenience function to analyze a request.
    
    Args:
        content: User's content
        diagram_type: Type of diagram
        
    Returns:
        Analysis results
    """
    analyzer = RequestAnalyzer()
    return analyzer.analyze(content, diagram_type)