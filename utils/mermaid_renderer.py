"""
Mermaid Renderer Module

Renders Mermaid diagrams to SVG using the Mermaid CLI.
"""

import asyncio
import tempfile
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import subprocess

from utils.logger import setup_logger

logger = setup_logger(__name__)


class MermaidRenderer:
    """Renders Mermaid diagrams to SVG format"""
    
    def __init__(self):
        self.mmdc_path = "mmdc"  # Assumes mmdc is in PATH
        self._check_mermaid_cli()
    
    def _check_mermaid_cli(self):
        """Check if Mermaid CLI is available"""
        try:
            result = subprocess.run(
                [self.mmdc_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"Mermaid CLI found: {result.stdout.strip()}")
            else:
                logger.warning("Mermaid CLI not found or not working properly")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"Mermaid CLI check failed: {e}")
            logger.warning("Mermaid diagrams will use placeholder SVG")
    
    async def render_to_svg(
        self,
        mermaid_code: str,
        theme: Optional[Dict[str, Any]] = None,
        width: int = 800,
        height: int = 600
    ) -> str:
        """
        Render Mermaid code to SVG
        
        Args:
            mermaid_code: Mermaid diagram code
            theme: Theme configuration
            width: SVG width
            height: SVG height
            
        Returns:
            SVG string
        """
        
        # Create temporary directory for files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write Mermaid code to temp file
            input_file = temp_path / "diagram.mmd"
            output_file = temp_path / "output.svg"
            config_file = temp_path / "config.json"
            
            # Write Mermaid code
            input_file.write_text(mermaid_code)
            
            # Create Mermaid config with theme
            config = self._create_mermaid_config(theme)
            config_file.write_text(json.dumps(config, indent=2))
            
            # Build mmdc command with puppeteer config
            cmd = [
                self.mmdc_path,
                "-i", str(input_file),
                "-o", str(output_file),
                "-c", str(config_file),
                "-b", "transparent",
                "-w", str(width),
                "-H", str(height),
                "--puppeteerConfigFile", str(self._create_puppeteer_config(temp_path))
            ]
            
            try:
                # Run mmdc command
                result = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(),
                    timeout=30  # 30 second timeout
                )
                
                if result.returncode != 0:
                    error_msg = stderr.decode() if stderr else "Unknown error"
                    logger.error(f"Mermaid CLI error: {error_msg}")
                    raise RuntimeError(f"Mermaid rendering failed: {error_msg}")
                
                # Read the generated SVG
                if output_file.exists():
                    svg_content = output_file.read_text()
                    return self._clean_svg(svg_content)
                else:
                    raise RuntimeError("Mermaid CLI did not generate output file")
                    
            except asyncio.TimeoutError:
                logger.error("Mermaid rendering timeout")
                raise RuntimeError("Mermaid rendering timeout after 30 seconds")
            except Exception as e:
                logger.error(f"Mermaid rendering error: {e}")
                raise
    
    def _create_puppeteer_config(self, temp_path: Path) -> Path:
        """
        Create Puppeteer configuration file
        
        Args:
            temp_path: Temporary directory path
            
        Returns:
            Path to puppeteer config file
        """
        puppeteer_config = {
            "executablePath": os.getenv("PUPPETEER_EXECUTABLE_PATH", "/usr/bin/chromium"),
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--single-process",
                "--disable-gpu"
            ]
        }
        
        config_file = temp_path / "puppeteer-config.json"
        config_file.write_text(json.dumps(puppeteer_config, indent=2))
        return config_file
    
    def _create_mermaid_config(self, theme: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Create Mermaid configuration with theme
        
        Args:
            theme: Theme configuration
            
        Returns:
            Mermaid config dict
        """
        
        if not theme:
            theme = {}
        
        # Map theme to Mermaid config
        config = {
            "theme": "default",
            "themeVariables": {
                "primaryColor": theme.get("primaryColor", "#3B82F6"),
                "primaryTextColor": theme.get("textColor", "#1F2937"),
                "primaryBorderColor": theme.get("secondaryColor", "#60A5FA"),
                "lineColor": theme.get("secondaryColor", "#60A5FA"),
                "secondaryColor": theme.get("secondaryColor", "#60A5FA"),
                "background": theme.get("backgroundColor", "#FFFFFF"),
                "mainBkg": theme.get("primaryColor", "#3B82F6"),
                "secondBkg": theme.get("secondaryColor", "#60A5FA"),
                "tertiaryColor": "#F3F4F6",
                "fontFamily": theme.get("fontFamily", "Inter, system-ui, sans-serif"),
                "fontSize": "16px"
            }
        }
        
        return config
    
    def _clean_svg(self, svg_content: str) -> str:
        """
        Clean and optimize SVG output
        
        Args:
            svg_content: Raw SVG from Mermaid CLI
            
        Returns:
            Cleaned SVG string
        """
        
        # Remove unnecessary whitespace
        lines = svg_content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines if line.strip()]
        
        # Join back together
        cleaned_svg = '\n'.join(cleaned_lines)
        
        # Ensure SVG has proper XML declaration
        if not cleaned_svg.startswith('<?xml'):
            cleaned_svg = '<?xml version="1.0" encoding="UTF-8"?>\n' + cleaned_svg
        
        return cleaned_svg
    
    def create_placeholder_svg(
        self,
        mermaid_code: str,
        theme: Optional[Dict[str, Any]] = None,
        width: int = 800,
        height: int = 600,
        error_message: Optional[str] = None
    ) -> str:
        """
        Create a placeholder SVG when rendering fails
        
        Args:
            mermaid_code: Original Mermaid code
            theme: Theme configuration
            width: SVG width
            height: SVG height
            error_message: Optional error message to display
            
        Returns:
            Placeholder SVG string
        """
        
        if not theme:
            theme = {}
        
        message = error_message or "[Mermaid Diagram - Render on Client]"
        
        svg_template = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <defs>
        <style>
            .mermaid-placeholder {{
                font-family: {theme.get('fontFamily', 'Inter, system-ui, sans-serif')};
                fill: {theme.get('textColor', '#1F2937')};
            }}
            .error-text {{
                fill: #EF4444;
                font-size: 14px;
            }}
        </style>
        <script type="application/mermaid+json">{{
            "code": {json.dumps(mermaid_code)},
            "theme": "default",
            "themeVariables": {{
                "primaryColor": "{theme.get('primaryColor', '#3B82F6')}",
                "primaryTextColor": "{theme.get('textColor', '#1F2937')}",
                "primaryBorderColor": "{theme.get('secondaryColor', '#60A5FA')}",
                "lineColor": "{theme.get('secondaryColor', '#60A5FA')}",
                "background": "{theme.get('backgroundColor', '#FFFFFF')}"
            }}
        }}</script>
    </defs>
    <rect width="{width}" height="{height}" fill="{theme.get('backgroundColor', '#FFFFFF')}"/>
    <text x="{width/2}" y="{height/2}" text-anchor="middle" class="mermaid-placeholder">
        {message}
    </text>
    {f'<text x="{width/2}" y="{height/2 + 30}" text-anchor="middle" class="error-text">{error_message}</text>' if error_message else ''}
</svg>'''
        
        return svg_template


# Singleton instance
_renderer_instance = None


async def get_mermaid_renderer() -> MermaidRenderer:
    """Get or create the singleton Mermaid renderer"""
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = MermaidRenderer()
    return _renderer_instance


async def render_mermaid_to_svg(
    mermaid_code: str,
    theme: Optional[Dict[str, Any]] = None,
    fallback_to_placeholder: bool = True
) -> str:
    """
    Convenience function to render Mermaid to SVG
    
    Args:
        mermaid_code: Mermaid diagram code
        theme: Theme configuration
        fallback_to_placeholder: If True, return placeholder on error
        
    Returns:
        SVG string (rendered or placeholder)
    """
    
    renderer = await get_mermaid_renderer()
    
    try:
        # Try to render with Mermaid CLI
        svg = await renderer.render_to_svg(mermaid_code, theme)
        logger.info("Mermaid diagram rendered successfully")
        return svg
    except Exception as e:
        logger.error(f"Failed to render Mermaid diagram: {e}")
        
        if fallback_to_placeholder:
            # Return placeholder SVG with embedded Mermaid code
            return renderer.create_placeholder_svg(
                mermaid_code,
                theme,
                error_message=f"Server-side rendering failed: {str(e)}"
            )
        else:
            raise