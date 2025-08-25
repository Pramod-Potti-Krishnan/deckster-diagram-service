"""
Diagram validator for testing diagram outputs.

Validates diagram responses for correctness and quality.
"""

import re
from typing import Dict, Any, List, Optional
import json
from datetime import datetime


class DiagramValidator:
    """Validate diagram generation outputs"""
    
    def __init__(self):
        self.required_response_fields = [
            "diagram_id",
            "metadata"
        ]
        
        self.required_metadata_fields = [
            "generation_method",
            "generation_time_ms"
        ]
        
        self.valid_generation_methods = [
            "svg_template",
            "mermaid",
            "python_chart",
            "custom"
        ]
    
    def validate_diagram_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a complete diagram response"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "quality_score": 1.0
        }
        
        # Check required fields
        for field in self.required_response_fields:
            if field not in response:
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["quality_score"] -= 0.2
        
        # Validate content or URL present
        if "content" not in response and "url" not in response:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Neither content nor URL provided")
            validation_result["quality_score"] -= 0.3
        
        # Validate diagram_id format
        if "diagram_id" in response:
            if not self._validate_diagram_id(response["diagram_id"]):
                validation_result["warnings"].append("Invalid diagram_id format")
                validation_result["quality_score"] -= 0.1
        
        # Validate metadata
        if "metadata" in response:
            metadata_validation = self._validate_metadata(response["metadata"])
            validation_result["errors"].extend(metadata_validation["errors"])
            validation_result["warnings"].extend(metadata_validation["warnings"])
            validation_result["quality_score"] *= metadata_validation["quality_factor"]
        
        # Validate content if present
        if "content" in response:
            content_validation = self._validate_content(
                response["content"],
                response.get("metadata", {}).get("generation_method")
            )
            validation_result["errors"].extend(content_validation["errors"])
            validation_result["warnings"].extend(content_validation["warnings"])
            validation_result["quality_score"] *= content_validation["quality_factor"]
        
        # Validate URL if present
        if "url" in response:
            url_validation = self._validate_url(response["url"])
            if not url_validation["is_valid"]:
                validation_result["warnings"].append(url_validation["error"])
                validation_result["quality_score"] -= 0.1
        
        # Update is_valid based on errors
        validation_result["is_valid"] = len(validation_result["errors"]) == 0
        
        # Ensure quality score is between 0 and 1
        validation_result["quality_score"] = max(0, min(1, validation_result["quality_score"]))
        
        return validation_result
    
    def _validate_diagram_id(self, diagram_id: str) -> bool:
        """Validate diagram ID format"""
        # Should be UUID-like or specific format
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        custom_pattern = r'^diag-[a-zA-Z0-9]{6,}$'
        
        return (
            re.match(uuid_pattern, diagram_id.lower()) is not None or
            re.match(custom_pattern, diagram_id) is not None
        )
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata structure"""
        result = {
            "errors": [],
            "warnings": [],
            "quality_factor": 1.0
        }
        
        # Check required metadata fields
        for field in self.required_metadata_fields:
            if field not in metadata:
                result["errors"].append(f"Missing metadata field: {field}")
                result["quality_factor"] -= 0.1
        
        # Validate generation method
        if "generation_method" in metadata:
            if metadata["generation_method"] not in self.valid_generation_methods:
                result["warnings"].append(f"Unknown generation method: {metadata['generation_method']}")
                result["quality_factor"] -= 0.05
        
        # Validate generation time
        if "generation_time_ms" in metadata:
            gen_time = metadata["generation_time_ms"]
            if not isinstance(gen_time, (int, float)) or gen_time < 0:
                result["errors"].append("Invalid generation_time_ms")
                result["quality_factor"] -= 0.1
            elif gen_time > 10000:
                result["warnings"].append(f"Slow generation time: {gen_time}ms")
                result["quality_factor"] -= 0.05
        
        # Check for quality score
        if "quality_score" in metadata:
            score = metadata["quality_score"]
            if not isinstance(score, (int, float)) or score < 0 or score > 1:
                result["warnings"].append(f"Invalid quality_score: {score}")
        
        # Check cache hit
        if "cache_hit" in metadata:
            if not isinstance(metadata["cache_hit"], bool):
                result["warnings"].append("cache_hit should be boolean")
        
        return result
    
    def _validate_content(self, content: str, generation_method: Optional[str]) -> Dict[str, Any]:
        """Validate diagram content"""
        result = {
            "errors": [],
            "warnings": [],
            "quality_factor": 1.0
        }
        
        if not content:
            result["errors"].append("Empty content")
            result["quality_factor"] = 0
            return result
        
        # Check content based on generation method
        if generation_method == "svg_template" or generation_method == "python_chart":
            # Should be SVG
            if not self._is_valid_svg(content):
                result["errors"].append("Invalid SVG content")
                result["quality_factor"] -= 0.3
            else:
                svg_quality = self._assess_svg_quality(content)
                result["quality_factor"] *= svg_quality["factor"]
                result["warnings"].extend(svg_quality["warnings"])
        
        elif generation_method == "mermaid":
            # Should be Mermaid syntax or SVG
            if not self._is_valid_mermaid(content) and not self._is_valid_svg(content):
                result["errors"].append("Invalid Mermaid/SVG content")
                result["quality_factor"] -= 0.3
        
        # Check for potential security issues
        security_check = self._check_content_security(content)
        if not security_check["is_safe"]:
            result["errors"].extend(security_check["issues"])
            result["quality_factor"] *= 0.5
        
        return result
    
    def _is_valid_svg(self, content: str) -> bool:
        """Check if content is valid SVG"""
        content_lower = content.lower().strip()
        return (
            content_lower.startswith("<svg") and
            content_lower.endswith("</svg>") and
            "xmlns" in content_lower
        )
    
    def _is_valid_mermaid(self, content: str) -> bool:
        """Check if content is valid Mermaid syntax"""
        mermaid_keywords = [
            "graph", "flowchart", "sequenceDiagram", "gantt",
            "pie", "journey", "gitGraph", "erDiagram"
        ]
        
        content_lower = content.lower().strip()
        return any(keyword in content_lower for keyword in mermaid_keywords)
    
    def _assess_svg_quality(self, svg_content: str) -> Dict[str, Any]:
        """Assess SVG quality"""
        result = {
            "factor": 1.0,
            "warnings": []
        }
        
        # Check for viewBox
        if "viewBox" not in svg_content:
            result["warnings"].append("SVG missing viewBox attribute")
            result["factor"] -= 0.05
        
        # Check for title or aria-label
        if "<title>" not in svg_content and 'aria-label' not in svg_content:
            result["warnings"].append("SVG missing accessibility attributes")
            result["factor"] -= 0.05
        
        # Check size
        if len(svg_content) > 1000000:  # 1MB
            result["warnings"].append("SVG content very large")
            result["factor"] -= 0.1
        
        # Check for proper structure
        element_counts = {
            "rect": svg_content.count("<rect"),
            "circle": svg_content.count("<circle"),
            "path": svg_content.count("<path"),
            "text": svg_content.count("<text"),
            "g": svg_content.count("<g")
        }
        
        total_elements = sum(element_counts.values())
        if total_elements == 0:
            result["warnings"].append("SVG has no visible elements")
            result["factor"] -= 0.2
        elif total_elements > 1000:
            result["warnings"].append(f"SVG has many elements: {total_elements}")
            result["factor"] -= 0.05
        
        return result
    
    def _validate_url(self, url: str) -> Dict[str, Any]:
        """Validate URL format"""
        result = {"is_valid": True, "error": None}
        
        # Basic URL validation
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        
        if not re.match(url_pattern, url):
            result["is_valid"] = False
            result["error"] = f"Invalid URL format: {url}"
        
        # Check for Supabase storage URL pattern
        if "supabase" in url.lower() and "/storage/" not in url:
            result["error"] = "Supabase URL missing storage path"
        
        return result
    
    def _check_content_security(self, content: str) -> Dict[str, Any]:
        """Check content for security issues"""
        result = {
            "is_safe": True,
            "issues": []
        }
        
        # Check for script tags
        if "<script" in content.lower():
            result["is_safe"] = False
            result["issues"].append("Content contains script tags")
        
        # Check for event handlers
        dangerous_patterns = [
            r'on\w+\s*=',  # onclick, onload, etc.
            r'javascript:',
            r'data:.*script'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                result["is_safe"] = False
                result["issues"].append(f"Content contains dangerous pattern: {pattern}")
        
        # Check for external references
        if "http://" in content and "localhost" not in content:
            result["issues"].append("Content contains non-HTTPS external references")
        
        return result
    
    def validate_batch_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of diagram responses"""
        batch_result = {
            "total": len(responses),
            "valid": 0,
            "invalid": 0,
            "warnings_count": 0,
            "average_quality": 0,
            "details": []
        }
        
        total_quality = 0
        
        for response in responses:
            validation = self.validate_diagram_response(response)
            
            if validation["is_valid"]:
                batch_result["valid"] += 1
            else:
                batch_result["invalid"] += 1
            
            batch_result["warnings_count"] += len(validation["warnings"])
            total_quality += validation["quality_score"]
            
            batch_result["details"].append({
                "diagram_id": response.get("diagram_id", "unknown"),
                "is_valid": validation["is_valid"],
                "quality_score": validation["quality_score"],
                "errors": validation["errors"],
                "warnings": validation["warnings"]
            })
        
        if responses:
            batch_result["average_quality"] = total_quality / len(responses)
        
        return batch_result
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a human-readable validation report"""
        report = []
        report.append("=== Diagram Validation Report ===")
        report.append(f"Generated: {datetime.utcnow().isoformat()}")
        report.append("")
        
        if "total" in validation_results:
            # Batch report
            report.append(f"Total Diagrams: {validation_results['total']}")
            report.append(f"Valid: {validation_results['valid']}")
            report.append(f"Invalid: {validation_results['invalid']}")
            report.append(f"Average Quality: {validation_results['average_quality']:.2f}")
            report.append(f"Total Warnings: {validation_results['warnings_count']}")
            
            if validation_results.get("details"):
                report.append("\nDetails:")
                for detail in validation_results["details"][:10]:  # First 10
                    report.append(f"  - {detail['diagram_id']}: {'✓' if detail['is_valid'] else '✗'} (Quality: {detail['quality_score']:.2f})")
                    if detail["errors"]:
                        report.append(f"    Errors: {', '.join(detail['errors'])}")
        else:
            # Single diagram report
            report.append(f"Valid: {'Yes' if validation_results['is_valid'] else 'No'}")
            report.append(f"Quality Score: {validation_results['quality_score']:.2f}")
            
            if validation_results["errors"]:
                report.append("\nErrors:")
                for error in validation_results["errors"]:
                    report.append(f"  - {error}")
            
            if validation_results["warnings"]:
                report.append("\nWarnings:")
                for warning in validation_results["warnings"]:
                    report.append(f"  - {warning}")
        
        return "\n".join(report)


if __name__ == "__main__":
    # Test the validator
    validator = DiagramValidator()
    
    # Test valid response
    valid_response = {
        "diagram_id": "diag-123456",
        "content": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>',
        "url": "https://example.supabase.co/storage/v1/object/public/diagrams/test.svg",
        "metadata": {
            "generation_method": "svg_template",
            "generation_time_ms": 150,
            "quality_score": 0.95,
            "cache_hit": False
        }
    }
    
    result = validator.validate_diagram_response(valid_response)
    print("Valid Response Test:")
    print(validator.generate_validation_report(result))
    
    # Test invalid response
    invalid_response = {
        "content": "not valid svg",
        "metadata": {
            "generation_method": "invalid_method"
        }
    }
    
    result = validator.validate_diagram_response(invalid_response)
    print("\nInvalid Response Test:")
    print(validator.generate_validation_report(result))