# Mermaid Server-Side Rendering

## Overview

The diagram microservice now supports **server-side rendering of Mermaid diagrams to SVG**. This means Mermaid diagrams are converted to actual SVG paths and shapes on the server, rather than returning just the Mermaid syntax for client-side rendering.

## Features

- ✅ **Full SVG rendering** - Mermaid diagrams are converted to complete SVG with paths, shapes, and text
- ✅ **Scalable vectors** - Output is true SVG that scales perfectly at any size
- ✅ **No client dependencies** - Works without requiring Mermaid.js on the client
- ✅ **Theme support** - Applies custom colors and styles during rendering
- ✅ **Automatic fallback** - Falls back to placeholder SVG if rendering fails

## How It Works

1. **Mermaid CLI Integration**
   - Uses the official `@mermaid-js/mermaid-cli` npm package
   - Runs in headless Chromium for accurate rendering
   - Converts Mermaid syntax to SVG on the server

2. **Rendering Process**
   ```
   Mermaid Code → Temp File → mmdc CLI → SVG Output → Clean & Return
   ```

3. **Fallback Mechanism**
   - If Mermaid CLI fails, returns placeholder SVG
   - Placeholder includes embedded Mermaid code for client-side rendering
   - Ensures service never fails completely

## Configuration

### Environment Variables

- `MERMAID_SERVER_RENDER` - Enable/disable server-side rendering (default: `"true"`)
  - `"true"` - Render Mermaid to SVG on server
  - `"false"` - Return placeholder for client-side rendering

### Docker Requirements

The Dockerfile has been updated to include:
- Node.js 18+
- npm
- @mermaid-js/mermaid-cli
- Chromium dependencies for puppeteer

## Supported Diagram Types

All Mermaid diagram types are supported:
- ✅ Flowchart
- ✅ Sequence Diagram
- ✅ Gantt Chart
- ✅ Pie Chart
- ✅ Journey Map
- ✅ Mind Map
- ✅ State Diagram
- ✅ Architecture Diagram
- ✅ Network Diagram
- ✅ Concept Map

## API Response

### With Server-Side Rendering

```json
{
  "content": "<svg>...</svg>",  // Fully rendered SVG
  "content_type": "svg",
  "metadata": {
    "generation_method": "mermaid_server",
    "server_rendered": true,
    "mermaid_code": "flowchart TD..."
  }
}
```

### With Client-Side Rendering (Fallback)

```json
{
  "content": "<svg>...</svg>",  // Placeholder with embedded code
  "content_type": "svg",
  "metadata": {
    "generation_method": "mermaid_placeholder",
    "server_rendered": false,
    "mermaid_code": "flowchart TD..."
  }
}
```

## Deployment

### Railway Deployment

The service is ready for Railway deployment. The Docker container includes all necessary dependencies.

### Local Development

For local development without Docker:
```bash
# Install Mermaid CLI globally
npm install -g @mermaid-js/mermaid-cli

# Set environment variable
export MERMAID_SERVER_RENDER=true

# Run the service
python main.py
```

## Testing

### Test Scripts

1. **test_mermaid_svg.py** - Tests actual Mermaid rendering
2. **test_mermaid_fallback.py** - Tests fallback mechanism
3. **test_railway_api_comprehensive.py** - Full API test including Mermaid

### Running Tests

```bash
# Test rendering (requires mmdc installed)
python test_mermaid_svg.py

# Test fallback (works without mmdc)
python test_mermaid_fallback.py
```

## Benefits

1. **Better Compatibility** - SVG works everywhere (PowerPoint, Keynote, web)
2. **Consistent Rendering** - Same output regardless of client
3. **Smaller Payload** - SVG is more compact than PNG
4. **Text Selectable** - Text in SVG remains selectable and searchable
5. **Perfect Quality** - Vector graphics scale without pixelation

## Troubleshooting

### Common Issues

1. **"mmdc not found"**
   - Ensure Docker build includes Node.js and npm install steps
   - Check Mermaid CLI is installed: `npm list -g @mermaid-js/mermaid-cli`

2. **Rendering timeout**
   - Complex diagrams may take longer
   - Default timeout is 30 seconds
   - Check container has enough memory

3. **Chromium errors**
   - Ensure all Chromium dependencies are installed
   - Check Docker logs for missing libraries

### Logs

Enable debug logging to see rendering details:
```bash
export LOG_LEVEL=DEBUG
```

## Future Enhancements

- [ ] Add caching for rendered diagrams
- [ ] Support custom Mermaid themes
- [ ] Add PNG export option
- [ ] Implement batch rendering
- [ ] Add performance metrics