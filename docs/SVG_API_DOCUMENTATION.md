# SVG Diagram Generation API Documentation

## Table of Contents
1. [Quick Start](#quick-start)
2. [API Endpoint](#api-endpoint)
3. [Request Format](#request-format)
4. [Color Theming](#color-theming)
5. [Available Diagram Types](#available-diagram-types)
6. [Code Examples](#code-examples)
7. [Response Format](#response-format)
8. [Advanced Features](#advanced-features)

---

## Quick Start

Connect to the WebSocket endpoint and send a diagram generation request:

```javascript
const ws = new WebSocket('wss://deckster-diagram-service-production.up.railway.app');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: "generate_diagram",
    request_id: "unique-id-123",
    data: {
      content: "Your content here",
      diagram_type: "matrix_2x2",
      theme: {
        primaryColor: "#3b82f6",
        colorScheme: "monochromatic"
      },
      data_points: [
        { label: "High Priority" },
        { label: "Medium Priority" },
        { label: "Low Priority" },
        { label: "No Priority" }
      ]
    }
  }));
};
```

---

## API Endpoint

### Production (Railway)
```
wss://deckster-diagram-service-production.up.railway.app
```

### Local Development
```
ws://localhost:8080
```

---

## Request Format

### WebSocket Message Structure

```typescript
interface WebSocketMessage {
  type: "generate_diagram" | "status_update" | "error";
  request_id: string;  // Unique identifier for the request
  data: DiagramRequest | StatusUpdate | ErrorResponse;
  timestamp?: string;  // ISO 8601 format
}
```

### Diagram Request

```typescript
interface DiagramRequest {
  // Required fields
  content: string;           // Text content for the diagram
  diagram_type: string;      // Type of diagram (see Available Diagram Types)
  
  // Optional fields
  data_points?: DataPoint[]; // Structured data for the diagram
  theme?: DiagramTheme;      // Visual customization
  constraints?: Constraints; // Size and layout preferences
  session_id?: string;       // For tracking user sessions
  user_id?: string;         // User identification
}
```

### Data Point Structure

```typescript
interface DataPoint {
  label: string;           // Text label for the element
  value?: number;         // Optional numeric value
  description?: string;   // Additional description
  metadata?: object;      // Custom metadata
}
```

---

## Color Theming

### Theme Configuration

```typescript
interface DiagramTheme {
  // Color configuration
  primaryColor: string;      // Main color (hex format: #RRGGBB)
  secondaryColor?: string;   // Secondary color (auto-generated if not provided)
  accentColor?: string;      // Accent color (auto-generated if not provided)
  
  // Color scheme selection
  colorScheme: "monochromatic" | "complementary";  // Default: "complementary"
  
  // Additional styling
  backgroundColor?: string;  // Background color (default: #FFFFFF)
  textColor?: string;       // Text color (auto-calculated for contrast)
  fontFamily?: string;      // Font family (default: "Inter, sans-serif")
  style?: string;           // Style preset: "professional" | "playful" | "minimal" | "bold"
  useSmartTheming?: boolean; // Enable intelligent theming (default: true)
}
```

### Color Scheme Options

#### 1. Monochromatic Scheme
Uses different shades and tints of a single color for a cohesive, professional look.

**Example:**
```json
{
  "primaryColor": "#2563eb",
  "colorScheme": "monochromatic"
}
```
- Generates 7 shades from light to dark
- Creates muted variations for subtle contrast
- Perfect for formal presentations and reports
- Maintains visual harmony

#### 2. Complementary Scheme
Uses multiple colors based on color theory for vibrant, distinctive elements.

**Example:**
```json
{
  "primaryColor": "#2563eb",
  "secondaryColor": "#f59e0b",
  "accentColor": "#10b981",
  "colorScheme": "complementary"
}
```
- Auto-generates missing colors using color wheel relationships
- Secondary: Complementary color (opposite on wheel) if not provided
- Accent: Triadic color (120° apart) if not provided
- Better for distinguishing different data categories

### Smart Theming Features

When `useSmartTheming` is enabled (default):
- **No gradients**: Flat, modern design with solid colors
- **Seamless borders**: Borders match fill colors for clean appearance
- **Smart text colors**: Automatic black/white text based on background luminance
- **No titles**: Clean, content-focused diagrams without redundant labels

---

## Available Diagram Types

### 1. Matrices

#### `matrix_2x2` - 2x2 Matrix
**Data Points:** 4 labels (quadrants)
```json
{
  "diagram_type": "matrix_2x2",
  "data_points": [
    { "label": "High / High" },
    { "label": "Low / High" },
    { "label": "Low / Low" },
    { "label": "High / Low" }
  ]
}
```

#### `matrix_3x3` - 3x3 Matrix
**Data Points:** 9 labels (cells)
```json
{
  "diagram_type": "matrix_3x3",
  "data_points": [
    { "label": "Cell 1" }, { "label": "Cell 2" }, { "label": "Cell 3" },
    { "label": "Cell 4" }, { "label": "Cell 5" }, { "label": "Cell 6" },
    { "label": "Cell 7" }, { "label": "Cell 8" }, { "label": "Cell 9" }
  ]
}
```

#### `swot_matrix` - SWOT Analysis
**Data Points:** 4 labels
```json
{
  "diagram_type": "swot_matrix",
  "data_points": [
    { "label": "Strengths" },
    { "label": "Weaknesses" },
    { "label": "Opportunities" },
    { "label": "Threats" }
  ]
}
```

### 2. Hub & Spoke

#### `hub_spoke_4` - 4 Nodes
**Data Points:** 5 labels (1 hub + 4 nodes)
```json
{
  "diagram_type": "hub_spoke_4",
  "data_points": [
    { "label": "Central Hub" },
    { "label": "Node 1" },
    { "label": "Node 2" },
    { "label": "Node 3" },
    { "label": "Node 4" }
  ]
}
```

#### `hub_spoke_6` - 6 Nodes
**Data Points:** 7 labels (1 hub + 6 nodes)

### 3. Process Flows

#### `process_flow_3` - 3 Steps
**Data Points:** 3 labels
```json
{
  "diagram_type": "process_flow_3",
  "data_points": [
    { "label": "Input" },
    { "label": "Process" },
    { "label": "Output" }
  ]
}
```

#### `process_flow_5` - 5 Steps
**Data Points:** 5 labels

### 4. Pyramids

#### `pyramid_3_level` - 3 Levels
**Data Points:** 3 labels (top to bottom)
```json
{
  "diagram_type": "pyramid_3_level",
  "data_points": [
    { "label": "Peak Level" },
    { "label": "Core Level" },
    { "label": "Foundation Level" }
  ]
}
```

#### `pyramid_4_level` - 4 Levels
#### `pyramid_5_level` - 5 Levels

### 5. Cycles

#### `cycle_3_step` - 3 Steps
#### `cycle_4_step` - 4 Steps
#### `cycle_5_step` - 5 Steps

### 6. Funnels

#### `funnel_3_stage` - 3 Stages
#### `funnel_4_stage` - 4 Stages
#### `funnel_5_stage` - 5 Stages

### 7. Venn Diagrams

#### `venn_2_circle` - 2 Circles
**Data Points:** 3 labels (2 sets + intersection)
```json
{
  "diagram_type": "venn_2_circle",
  "data_points": [
    { "label": "Set A", "value": 45 },
    { "label": "Set B", "value": 45 },
    { "label": "Intersection", "value": 10 }
  ]
}
```

#### `venn_3_circle` - 3 Circles
**Data Points:** 7 labels (3 sets + 4 intersections)

### 8. Honeycombs

#### `honeycomb_3` - 3 Cells
#### `honeycomb_5` - 5 Cells
#### `honeycomb_7` - 7 Cells

### 9. Other Diagrams

#### `gears_3` - 3 Interconnected Gears
#### `fishbone_4_bone` - Fishbone/Cause-Effect Diagram
#### `timeline_horizontal` - Horizontal Timeline
#### `roadmap_quarterly_4` - Quarterly Roadmap

---

## Code Examples

### JavaScript/TypeScript

```typescript
class DiagramGenerator {
  private ws: WebSocket;
  
  constructor(url: string = 'wss://deckster-diagram-service-production.up.railway.app') {
    this.ws = new WebSocket(url);
    this.setupHandlers();
  }
  
  private setupHandlers() {
    this.ws.onopen = () => console.log('Connected');
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    this.ws.onerror = (error) => console.error('Error:', error);
  }
  
  generateDiagram(config: {
    type: string;
    labels: string[];
    primaryColor: string;
    scheme?: 'monochromatic' | 'complementary';
  }) {
    const request = {
      type: "generate_diagram",
      request_id: `req-${Date.now()}`,
      data: {
        content: config.labels.join('\n'),
        diagram_type: config.type,
        theme: {
          primaryColor: config.primaryColor,
          colorScheme: config.scheme || 'complementary',
          useSmartTheming: true
        },
        data_points: config.labels.map(label => ({ label }))
      }
    };
    
    this.ws.send(JSON.stringify(request));
  }
  
  private handleMessage(message: any) {
    switch(message.type) {
      case 'diagram_response':
        console.log('Diagram generated:', message.data.svg_url);
        break;
      case 'status_update':
        console.log('Status:', message.data.message);
        break;
      case 'error':
        console.error('Error:', message.data.error);
        break;
    }
  }
}

// Usage
const generator = new DiagramGenerator();

// Monochromatic theme example
generator.generateDiagram({
  type: 'matrix_2x2',
  labels: ['Urgent & Important', 'Not Urgent & Important', 
           'Not Urgent & Not Important', 'Urgent & Not Important'],
  primaryColor: '#8b5cf6',
  scheme: 'monochromatic'
});

// Complementary theme example
generator.generateDiagram({
  type: 'hub_spoke_4',
  labels: ['Core System', 'Module A', 'Module B', 'Module C', 'Module D'],
  primaryColor: '#dc2626',
  scheme: 'complementary'
});
```

### Python

```python
import asyncio
import json
import websockets
from datetime import datetime
from typing import List, Optional, Dict

class DiagramClient:
    def __init__(self, url: str = 'wss://deckster-diagram-service-production.up.railway.app'):
        self.url = url
        
    async def generate_diagram(
        self,
        diagram_type: str,
        labels: List[str],
        primary_color: str = "#3b82f6",
        color_scheme: str = "complementary",
        secondary_color: Optional[str] = None,
        accent_color: Optional[str] = None
    ):
        async with websockets.connect(self.url) as websocket:
            # Prepare request
            request = {
                "type": "generate_diagram",
                "request_id": f"py-{datetime.now().timestamp()}",
                "data": {
                    "content": "\\n".join(labels),
                    "diagram_type": diagram_type,
                    "theme": {
                        "primaryColor": primary_color,
                        "colorScheme": color_scheme,
                        "useSmartTheming": True
                    },
                    "data_points": [{"label": label} for label in labels]
                }
            }
            
            # Add optional colors
            if secondary_color:
                request["data"]["theme"]["secondaryColor"] = secondary_color
            if accent_color:
                request["data"]["theme"]["accentColor"] = accent_color
            
            # Send request
            await websocket.send(json.dumps(request))
            
            # Wait for response
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if data["type"] == "diagram_response":
                    return data["data"]
                elif data["type"] == "error":
                    raise Exception(f"Error: {data['data']['error']}")

# Usage
async def main():
    client = DiagramClient()
    
    # Monochromatic example
    result = await client.generate_diagram(
        diagram_type="pyramid_3_level",
        labels=["Executive", "Management", "Operations"],
        primary_color="#7c3aed",
        color_scheme="monochromatic"
    )
    print(f"Diagram URL: {result['svg_url']}")
    
    # Complementary example with custom colors
    result = await client.generate_diagram(
        diagram_type="venn_2_circle",
        labels=["Set A", "Set B", "Intersection"],
        primary_color="#e11d48",
        secondary_color="#0891b2",
        accent_color="#7c3aed",
        color_scheme="complementary"
    )
    print(f"Diagram URL: {result['svg_url']}")

asyncio.run(main())
```

### cURL/WebSocket CLI

```bash
# Using websocat or similar WebSocket CLI tool
echo '{
  "type": "generate_diagram",
  "request_id": "cli-123",
  "data": {
    "content": "Step 1\nStep 2\nStep 3",
    "diagram_type": "process_flow_3",
    "theme": {
      "primaryColor": "#059669",
      "colorScheme": "monochromatic"
    },
    "data_points": [
      {"label": "Step 1"},
      {"label": "Step 2"},
      {"label": "Step 3"}
    ]
  }
}' | websocat wss://deckster-diagram-service-production.up.railway.app
```

---

## Response Format

### Success Response

```json
{
  "type": "diagram_response",
  "request_id": "unique-id-123",
  "data": {
    "status": "success",
    "content": "<svg>...</svg>",      // Full SVG content
    "content_type": "svg",
    "diagram_type": "matrix_2x2",
    "output_type": "svg",
    "svg": {
      "content": "<svg>...</svg>",
      "is_placeholder": false
    },
    "rendering": {
      "server_rendered": true,
      "render_method": "template",
      "render_status": "success"
    },
    "metadata": {
      "generation_method": "svg_template",
      "template_used": "matrix_2x2",
      "elements_modified": 4,
      "cache_hit": false,
      "server_rendered": true,
      "theme_applied": {
        "colorScheme": "monochromatic",
        "primaryColor": "#3b82f6"
      }
    },
    "svg_url": "https://storage.url/diagram.svg",  // If stored
    "storage_path": "diagrams/session/diagram.svg"
  },
  "timestamp": "2024-08-24T12:00:00Z"
}
```

### Error Response

```json
{
  "type": "error",
  "request_id": "unique-id-123",
  "data": {
    "error": "Invalid diagram type",
    "code": "INVALID_DIAGRAM_TYPE",
    "details": "Diagram type 'unknown' is not supported",
    "status_code": 400
  },
  "timestamp": "2024-08-24T12:00:00Z"
}
```

### Status Updates

```json
{
  "type": "status_update",
  "request_id": "unique-id-123",
  "data": {
    "status": "processing",
    "message": "Generating diagram...",
    "progress": 50
  },
  "timestamp": "2024-08-24T12:00:00Z"
}
```

---

## Advanced Features

### 1. Smart Text Colors
Text automatically switches between black and white based on background luminance for optimal readability.

### 2. Seamless Borders
Borders are automatically set to match fill colors, creating a clean, modern appearance.

### 3. Gradient Removal
All gradients are replaced with solid colors from the theme palette for a flat, contemporary design.

### 4. Title Removal
Diagram titles and subtitles are automatically removed for cleaner, content-focused visuals.

### 5. Responsive Sizing
SVGs are generated with viewBox for responsive scaling across different screen sizes.

### 6. Caching
Frequently requested diagrams may be cached for faster response times.

---

## Best Practices

1. **Color Format**: Always use hex format (#RRGGBB) for colors
2. **Request IDs**: Use unique request IDs for tracking and debugging
3. **Data Points**: Provide the exact number of data points required for each diagram type
4. **Error Handling**: Implement retry logic for network failures
5. **WebSocket Management**: Implement reconnection logic for dropped connections
6. **Theme Consistency**: Use monochromatic for formal documents, complementary for data visualization

---

## Rate Limits

- **Requests per minute**: 60
- **Concurrent connections**: 10 per IP
- **Maximum message size**: 1MB
- **Connection timeout**: 5 minutes of inactivity

---

## Support

For issues, feature requests, or questions:
- GitHub Issues: [Report issues](https://github.com/your-org/deckster-diagram-service/issues)
- Documentation: [Full documentation](https://docs.your-service.com)
- API Status: [Service status page](https://status.your-service.com)

---

## Changelog

### Version 2.0.0 (Current)
- Added monochromatic and complementary color schemes
- Implemented smart theming with automatic color generation
- Added gradient removal and seamless borders
- Improved text contrast with luminance-based color selection
- Added 25 SVG template diagram types

### Version 1.0.0
- Initial release with basic diagram generation
- WebSocket-based API
- Basic color theming