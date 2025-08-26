# SVG Diagram Generation API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [WebSocket Connection](#websocket-connection)
4. [Request Format](#request-format)
5. [Color Theming & Spatial Intelligence](#color-theming--spatial-intelligence)
6. [Available Diagram Types](#available-diagram-types)
7. [Response Format](#response-format)
8. [Code Examples](#code-examples)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Deckster Diagram Service is a WebSocket-based API that generates professional SVG diagrams with intelligent color theming and spatial color assignment. The service operates as a black box - you send structured data, it returns beautiful, production-ready SVG diagrams.

### Key Features
- **25+ Diagram Types**: Matrices, pyramids, Venn diagrams, hub & spoke, and more
- **Intelligent Color Theming**: Automatic color generation with spatial awareness
- **WCAG-Compliant Contrast**: Automatic text color adjustment for readability
- **Real-time Generation**: WebSocket-based for instant feedback
- **Zero Configuration**: Works out of the box with sensible defaults

---

## Quick Start

```javascript
// Connect to the WebSocket
const ws = new WebSocket('wss://deckster-diagram-service-production.up.railway.app/ws');

// Send a diagram request after connection
ws.onopen = () => {
  ws.send(JSON.stringify({
    message_id: "unique-123",
    type: "diagram_request",
    payload: {
      diagram_type: "matrix_2x2",
      data_points: [
        { label: "High Impact / High Effort" },
        { label: "High Impact / Low Effort" },
        { label: "Low Impact / Low Effort" },
        { label: "Low Impact / High Effort" }
      ],
      theme: {
        primaryColor: "#3b82f6",
        colorScheme: "monochromatic"
      }
    }
  }));
};

// Handle response
ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  if (response.type === "diagram_response") {
    // response.payload.content contains the complete SVG
    document.getElementById('diagram').innerHTML = response.payload.content;
  }
};
```

---

## WebSocket Connection

### Endpoints

**Production (Railway)**
```
wss://deckster-diagram-service-production.up.railway.app/ws
```

**Local Development**
```
ws://localhost:8080/ws
```

### Connection Flow

1. **Connect**: Establish WebSocket connection
2. **Acknowledgment**: Server sends `connection_ack` message
3. **Request**: Send diagram generation request
4. **Response**: Receive generated SVG or error message
5. **Keep Alive**: Connection remains open for multiple requests

### Connection Acknowledgment

Upon successful connection:
```json
{
  "type": "connection_ack",
  "timestamp": "2024-08-24T12:00:00Z"
}
```

---

## Request Format

### Message Structure

```typescript
interface DiagramRequest {
  message_id: string;           // Unique identifier for tracking
  type: "diagram_request";      // Must be exactly this value
  payload: {
    // Required fields
    diagram_type: string;        // Type of diagram (see Available Types)
    data_points: DataPoint[];    // Array of data points for the diagram
    
    // Optional fields
    content?: string;            // Additional context or title
    theme?: ThemeConfiguration;  // Color and styling options
    method?: "svg_template";     // Force SVG template generation
  }
}

interface DataPoint {
  label: string;                 // Text to display
  value?: number;                // Optional numeric value
  description?: string;          // Optional additional text
}
```

### Theme Configuration

```typescript
interface ThemeConfiguration {
  // Primary color (hex format required)
  primaryColor: string;          // e.g., "#3b82f6"
  
  // Color scheme selection
  colorScheme: "monochromatic" | "complementary";
  
  // Optional colors (auto-generated if not provided)
  secondaryColor?: string;       // For complementary scheme
  accentColor?: string;          // For additional contrast
  
  // Smart features (recommended to leave as default)
  useSmartTheming?: boolean;     // Default: true - enables all smart features
}
```

---

## Color Theming & Spatial Intelligence

### Color Schemes

#### 1. Monochromatic Scheme
Uses variations of a single color with intelligent spatial assignment.

```json
{
  "primaryColor": "#10b981",
  "colorScheme": "monochromatic"
}
```

**Features:**
- Generates 7-10 variations of the primary color
- Applies spatial intelligence based on diagram type
- Professional, cohesive appearance
- Perfect for reports and presentations

#### 2. Complementary Scheme
Uses multiple colors based on color theory relationships.

```json
{
  "primaryColor": "#3b82f6",
  "colorScheme": "complementary",
  "secondaryColor": "#f59e0b",  // Optional
  "accentColor": "#10b981"      // Optional
}
```

**Features:**
- Auto-generates missing colors using color wheel
- Secondary: Complementary (opposite) color
- Accent: Triadic (120° apart) color
- Better for distinguishing categories

### Spatial Color Assignment

The API automatically applies spatial color relationships:

#### Matrix Diagrams (2x2, 3x3)
- **2D Gradient Algorithm**: Colors vary along both X and Y axes
- X-axis: Controls lightness (left to right: light to dark)
- Y-axis: Controls saturation (top to bottom: vivid to muted)
- Creates logical visual flow across quadrants

#### Pyramid Diagrams
- **Vertical Gradient**: Dark base to light peak
- Creates natural hierarchy through luminance
- Foundation appears heavier, peak appears lighter

#### Hub & Spoke Diagrams
- **Radial Progression**: Hub is darkest
- Spokes use variations within ±30° of primary hue
- Maintains color family coherence

#### Venn Diagrams
- **Intersection Blending**: Overlaps are darkened
- Ensures proper text contrast in all regions
- Uses color mixing algorithms

#### Honeycomb Patterns
- **Distance-based Coloring**: Center to edge progression
- Adjacent cells have smooth transitions
- Creates natural clustering effect

---

## Available Diagram Types

### Complete List with Required Data Points

| Diagram Type | Data Points Required | Description |
|-------------|---------------------|-------------|
| **Matrices** |
| `matrix_2x2` | 4 | 2x2 grid with quadrants |
| `matrix_3x3` | 9 | 3x3 grid |
| `swot_matrix` | 4 | SWOT analysis layout |
| **Hub & Spoke** |
| `hub_spoke_4` | 5 | Central hub + 4 nodes |
| `hub_spoke_6` | 7 | Central hub + 6 nodes |
| **Process Flows** |
| `process_flow_3` | 3 | Linear 3-step process |
| `process_flow_4` | 4 | Linear 4-step process |
| `process_flow_5` | 5 | Linear 5-step process |
| **Pyramids** |
| `pyramid_3_level` | 3 | 3-tier hierarchy |
| `pyramid_4_level` | 4 | 4-tier hierarchy |
| `pyramid_5_level` | 5 | 5-tier hierarchy |
| **Cycles** |
| `cycle_3_step` | 3 | Circular 3-step flow |
| `cycle_4_step` | 4 | Circular 4-step flow |
| `cycle_5_step` | 5 | Circular 5-step flow |
| **Funnels** |
| `funnel_3_stage` | 3 | 3-stage funnel |
| `funnel_4_stage` | 4 | 4-stage funnel |
| `funnel_5_stage` | 5 | 5-stage funnel |
| **Venn Diagrams** |
| `venn_2_circle` | 3 | 2 sets + intersection |
| `venn_3_circle` | 7 | 3 sets + 4 intersections |
| **Honeycombs** |
| `honeycomb_3_cell` | 3 | 3 hexagonal cells |
| `honeycomb_5_cell` | 5 | 5 hexagonal cells |
| `honeycomb_7_cell` | 7 | 7 hexagonal cells |
| **Special** |
| `gears_3` | 3 | Interconnected gears |
| `fishbone_4_bone` | 5 | Cause-effect diagram |
| `timeline_horizontal` | 4-6 | Horizontal timeline |
| `roadmap_quarterly_4` | 4 | Quarterly roadmap |

---

## Response Format

### Success Response

```json
{
  "message_id": "unique-123",
  "type": "diagram_response",
  "payload": {
    "status": "success",
    "content": "<svg xmlns='...' >...</svg>",  // Complete SVG content
    "metadata": {
      "diagram_type": "matrix_2x2",
      "generation_method": "svg_template",
      "theme_applied": {
        "primaryColor": "#3b82f6",
        "colorScheme": "monochromatic",
        "colors_generated": 4,
        "spatial_algorithm": "2d_gradient"
      },
      "processing_time_ms": 45
    }
  },
  "timestamp": "2024-08-24T12:00:00Z"
}
```

### Error Response

```json
{
  "message_id": "unique-123",
  "type": "error_response",
  "payload": {
    "error_code": "INVALID_DIAGRAM_TYPE",
    "error_message": "Diagram type 'unknown' is not supported",
    "suggestions": ["matrix_2x2", "hub_spoke_4", "pyramid_3_level"]
  },
  "timestamp": "2024-08-24T12:00:00Z"
}
```

---

## Code Examples

### JavaScript/TypeScript (Complete Client)

```typescript
class DiagramClient {
  private ws: WebSocket | null = null;
  private pendingRequests = new Map();
  
  async connect(url = 'wss://deckster-diagram-service-production.up.railway.app/ws') {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(url);
      
      this.ws.onopen = () => {
        console.log('Connected to diagram service');
        resolve(true);
      };
      
      this.ws.onmessage = (event) => {
        const response = JSON.parse(event.data);
        
        if (response.type === 'connection_ack') {
          return;
        }
        
        const handler = this.pendingRequests.get(response.message_id);
        if (handler) {
          handler(response);
          this.pendingRequests.delete(response.message_id);
        }
      };
      
      this.ws.onerror = reject;
    });
  }
  
  async generateDiagram(config: {
    type: string;
    labels: string[];
    primaryColor?: string;
    colorScheme?: 'monochromatic' | 'complementary';
  }): Promise<string> {
    return new Promise((resolve, reject) => {
      const messageId = `req-${Date.now()}-${Math.random()}`;
      
      const request = {
        message_id: messageId,
        type: "diagram_request",
        payload: {
          diagram_type: config.type,
          data_points: config.labels.map(label => ({ label })),
          theme: {
            primaryColor: config.primaryColor || "#3b82f6",
            colorScheme: config.colorScheme || "monochromatic",
            useSmartTheming: true
          },
          method: "svg_template"  // Force SVG template generation
        }
      };
      
      this.pendingRequests.set(messageId, (response) => {
        if (response.type === 'diagram_response') {
          resolve(response.payload.content);
        } else if (response.type === 'error_response') {
          reject(new Error(response.payload.error_message));
        }
      });
      
      this.ws?.send(JSON.stringify(request));
    });
  }
  
  disconnect() {
    this.ws?.close();
  }
}

// Usage Example
async function createDiagrams() {
  const client = new DiagramClient();
  await client.connect();
  
  // Matrix with 2D gradient spatial coloring
  const matrixSvg = await client.generateDiagram({
    type: 'matrix_2x2',
    labels: [
      'High Priority / High Impact',
      'Low Priority / High Impact',
      'Low Priority / Low Impact',
      'High Priority / Low Impact'
    ],
    primaryColor: '#10b981',
    colorScheme: 'monochromatic'
  });
  
  // Pyramid with vertical gradient
  const pyramidSvg = await client.generateDiagram({
    type: 'pyramid_5_level',
    labels: ['Foundation', 'Infrastructure', 'Platform', 'Services', 'Applications'],
    primaryColor: '#3b82f6',
    colorScheme: 'monochromatic'
  });
  
  // Hub & Spoke with radial colors
  const hubSpokeSvg = await client.generateDiagram({
    type: 'hub_spoke_4',
    labels: ['Core System', 'Module A', 'Module B', 'Module C', 'Module D'],
    primaryColor: '#f59e0b',
    colorScheme: 'monochromatic'
  });
  
  document.getElementById('matrix').innerHTML = matrixSvg;
  document.getElementById('pyramid').innerHTML = pyramidSvg;
  document.getElementById('hubspoke').innerHTML = hubSpokeSvg;
  
  client.disconnect();
}

createDiagrams();
```

### Python (Async Client)

```python
import asyncio
import json
import websockets
import ssl
from typing import List, Optional, Dict, Any
from uuid import uuid4

class DiagramService:
    def __init__(self, url: str = 'wss://deckster-diagram-service-production.up.railway.app/ws'):
        self.url = url
        # Create SSL context for secure connections
        self.ssl_context = ssl.create_default_context()
        
    async def generate_diagram(
        self,
        diagram_type: str,
        labels: List[str],
        primary_color: str = "#3b82f6",
        color_scheme: str = "monochromatic",
        secondary_color: Optional[str] = None,
        accent_color: Optional[str] = None
    ) -> str:
        """
        Generate an SVG diagram with spatial color intelligence.
        
        Args:
            diagram_type: Type of diagram (e.g., 'matrix_2x2', 'pyramid_3_level')
            labels: List of labels for diagram elements
            primary_color: Primary hex color
            color_scheme: Either 'monochromatic' or 'complementary'
            secondary_color: Optional secondary color for complementary scheme
            accent_color: Optional accent color for complementary scheme
            
        Returns:
            SVG content as string
        """
        async with websockets.connect(self.url, ssl=self.ssl_context) as websocket:
            # Wait for connection acknowledgment
            ack = await websocket.recv()
            ack_data = json.loads(ack)
            assert ack_data['type'] == 'connection_ack'
            
            # Prepare request
            message_id = str(uuid4())
            request = {
                "message_id": message_id,
                "type": "diagram_request",
                "payload": {
                    "diagram_type": diagram_type,
                    "data_points": [{"label": label} for label in labels],
                    "theme": {
                        "primaryColor": primary_color,
                        "colorScheme": color_scheme,
                        "useSmartTheming": True
                    },
                    "method": "svg_template"
                }
            }
            
            # Add optional colors if provided
            if secondary_color and color_scheme == "complementary":
                request["payload"]["theme"]["secondaryColor"] = secondary_color
            if accent_color and color_scheme == "complementary":
                request["payload"]["theme"]["accentColor"] = accent_color
            
            # Send request
            await websocket.send(json.dumps(request))
            
            # Wait for response
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get("message_id") == message_id:
                    if data["type"] == "diagram_response":
                        return data["payload"]["content"]
                    elif data["type"] == "error_response":
                        raise Exception(f"Error: {data['payload']['error_message']}")

# Example usage
async def main():
    service = DiagramService()
    
    # Example 1: Matrix with 2D gradient spatial coloring
    matrix_svg = await service.generate_diagram(
        diagram_type="matrix_2x2",
        labels=[
            "High Risk / High Reward",
            "Low Risk / High Reward",
            "Low Risk / Low Reward",
            "High Risk / Low Reward"
        ],
        primary_color="#10b981",
        color_scheme="monochromatic"
    )
    with open("matrix.svg", "w") as f:
        f.write(matrix_svg)
    print("✅ Matrix diagram saved to matrix.svg")
    
    # Example 2: Pyramid with vertical gradient
    pyramid_svg = await service.generate_diagram(
        diagram_type="pyramid_5_level",
        labels=["Foundation", "Layer 2", "Layer 3", "Layer 4", "Peak"],
        primary_color="#8b5cf6",
        color_scheme="monochromatic"
    )
    with open("pyramid.svg", "w") as f:
        f.write(pyramid_svg)
    print("✅ Pyramid diagram saved to pyramid.svg")
    
    # Example 3: Venn with intersection blending
    venn_svg = await service.generate_diagram(
        diagram_type="venn_2_circle",
        labels=["Frontend Skills", "Backend Skills", "Full Stack"],
        primary_color="#dc2626",
        color_scheme="monochromatic"
    )
    with open("venn.svg", "w") as f:
        f.write(venn_svg)
    print("✅ Venn diagram saved to venn.svg")
    
    # Example 4: Hub & Spoke with complementary colors
    hub_svg = await service.generate_diagram(
        diagram_type="hub_spoke_4",
        labels=["Central Hub", "North", "East", "South", "West"],
        primary_color="#f59e0b",
        secondary_color="#3b82f6",
        accent_color="#10b981",
        color_scheme="complementary"
    )
    with open("hub_spoke.svg", "w") as f:
        f.write(hub_svg)
    print("✅ Hub & Spoke diagram saved to hub_spoke.svg")

if __name__ == "__main__":
    asyncio.run(main())
```

### cURL with websocat

```bash
# Install websocat first: brew install websocat (macOS) or cargo install websocat

# Simple monochromatic matrix
echo '{
  "message_id": "test-001",
  "type": "diagram_request",
  "payload": {
    "diagram_type": "matrix_2x2",
    "data_points": [
      {"label": "Q1"}, {"label": "Q2"}, 
      {"label": "Q3"}, {"label": "Q4"}
    ],
    "theme": {
      "primaryColor": "#10b981",
      "colorScheme": "monochromatic"
    }
  }
}' | websocat wss://deckster-diagram-service-production.up.railway.app/ws

# Pyramid with custom labels
echo '{
  "message_id": "test-002",
  "type": "diagram_request",
  "payload": {
    "diagram_type": "pyramid_3_level",
    "data_points": [
      {"label": "Strategic"},
      {"label": "Tactical"},
      {"label": "Operational"}
    ],
    "theme": {
      "primaryColor": "#7c3aed",
      "colorScheme": "monochromatic"
    },
    "method": "svg_template"
  }
}' | websocat wss://deckster-diagram-service-production.up.railway.app/ws
```

---

## Advanced Features

### 1. Automatic Text Contrast (WCAG Compliant)
- Text automatically switches between black (#000000) and white (#ffffff)
- Based on background luminance calculation
- Ensures minimum contrast ratio of 4.5:1
- No configuration needed

### 2. Spatial Color Intelligence
- **2D Gradients**: Matrix diagrams use X/Y axis variations
- **Vertical Gradients**: Pyramids transition from dark to light
- **Radial Progression**: Hub & spoke maintains hue family
- **Intersection Blending**: Venn overlaps are properly darkened

### 3. Smart Border Matching
- Borders automatically match fill colors
- Creates seamless, modern appearance
- Reduces visual clutter

### 4. Element-Specific Coloring
Each diagram type has custom color assignment logic:
- Matrix quadrants: 2D gradient based on position
- Pyramid levels: Progressive lightness from base to peak
- Hub & spoke: Hub is darkest, spokes vary within color family
- Venn circles: Transparent with darkened intersections

### 5. No Configuration Required
Default settings work perfectly for most use cases:
- Only required field: `diagram_type` and `data_points`
- Primary color defaults to professional blue (#3b82f6)
- Color scheme defaults to monochromatic
- Smart theming enabled by default

---

## Troubleshooting

### Common Issues and Solutions

#### 1. WebSocket Connection Failed
```
Error: WebSocket connection failed
```
**Solution**: Ensure you're using the correct endpoint with `/ws` suffix:
- Correct: `wss://deckster-diagram-service-production.up.railway.app/ws`
- Wrong: `wss://deckster-diagram-service-production.up.railway.app`

#### 2. Invalid Diagram Type
```json
{
  "error_code": "INVALID_DIAGRAM_TYPE",
  "error_message": "Diagram type 'matrix_4x4' is not supported"
}
```
**Solution**: Check the Available Diagram Types section for valid options.

#### 3. Wrong Number of Data Points
```json
{
  "error_code": "INVALID_DATA_POINTS",
  "error_message": "matrix_2x2 requires exactly 4 data points, got 3"
}
```
**Solution**: Provide exactly the required number of labels for the diagram type.

#### 4. Invalid Color Format
```json
{
  "error_code": "INVALID_COLOR",
  "error_message": "Color must be in hex format (#RRGGBB)"
}
```
**Solution**: Use hex format with # prefix (e.g., "#3b82f6", not "rgb(59,130,246)").

#### 5. SSL Certificate Issues (Python)
```python
ssl.SSLCertVerificationError: certificate verify failed
```
**Solution**: For development only, bypass SSL verification:
```python
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
```

### Rate Limits
- **Requests per minute**: 100 per IP
- **Concurrent connections**: 10 per IP
- **Message size limit**: 100KB
- **Connection timeout**: 5 minutes of inactivity

### Debug Mode
Include `debug: true` in your request for detailed processing information:
```json
{
  "message_id": "debug-001",
  "type": "diagram_request",
  "payload": {
    "diagram_type": "matrix_2x2",
    "data_points": [...],
    "debug": true
  }
}
```

---

## Changelog

### Version 3.0.0 (Current - August 2024)
- ✨ **Spatial Color Intelligence**: 2D gradients, vertical gradients, radial progression
- 🎨 **Enhanced Text Contrast**: WCAG-compliant automatic text color selection
- 🔧 **Fixed Color Duplication**: Unique colors for all elements
- 🌈 **Improved Hub & Spoke**: Spokes stay within primary color family
- 🔄 **Venn Intersection Fix**: Proper darkening for text visibility
- 📝 **Message Format Update**: New `message_id` and `payload` structure

### Version 2.0.0
- Added monochromatic and complementary color schemes
- Implemented smart theming with automatic color generation
- Added gradient removal and seamless borders
- Added 25 SVG template diagram types

### Version 1.0.0
- Initial release with basic diagram generation
- WebSocket-based API
- Basic color theming

---

## Support

For issues or feature requests:
- GitHub: [https://github.com/Pramod-Potti-Krishnan/deckster-diagram-service](https://github.com/Pramod-Potti-Krishnan/deckster-diagram-service)
- Production API: [https://deckster-diagram-service-production.up.railway.app](https://deckster-diagram-service-production.up.railway.app)

---

*Last updated: August 2024 | API Version: 3.0.0*