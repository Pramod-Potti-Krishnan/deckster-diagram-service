# Diagram Microservice v2

A self-contained WebSocket-based microservice for generating diagrams using SVG templates, Mermaid, and Python charting libraries.

## Overview

This microservice provides a unified API for diagram generation, combining multiple rendering methods with intelligent routing and fallback mechanisms. It's designed to be:

- **Self-contained**: Can run independently or be integrated into larger applications
- **Efficient**: Token-optimized with caching and minimal context passing
- **Flexible**: Supports multiple generation methods with automatic fallback
- **Scalable**: WebSocket-based for real-time communication

## Architecture

### Core Components

1. **Unified Playbook**: Single routing engine that decides between SVG templates, Mermaid, or Python generation
2. **WebSocket API**: Real-time communication following Phase 1 patterns
3. **Multi-Agent System**: Specialized agents for each generation method
4. **Smart Caching**: Template and result caching for performance
5. **Token Optimization**: Minimal context passing based on Phase 1 learnings

### Folder Structure

```
diagram_microservice_v2/
├── api/           # WebSocket and REST endpoints
├── core/          # Business logic and routing
├── agents/        # Generation agents (SVG, Mermaid, Python)
├── templates/     # SVG template files
├── playbooks/     # Routing rules and configurations
├── models/        # Pydantic data models
├── storage/       # Database and cache management
├── utils/         # Helper utilities
├── config/        # Configuration management
├── tests/         # Test suite
└── docs/          # Documentation
```

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Running the Service

```bash
# Standalone mode
python main.py

# With custom port
python main.py --port 8001

# Debug mode
python main.py --debug
```

### Docker Deployment

```bash
# Build image
docker build -t diagram-microservice:v2 .

# Run container
docker run -p 8001:8001 diagram-microservice:v2
```

## API Usage

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8001/ws?session_id=abc123&user_id=user456');

ws.onopen = () => {
  // Send diagram request
  ws.send(JSON.stringify({
    type: 'diagram_request',
    data: {
      content: 'Step 1: Plan\nStep 2: Execute\nStep 3: Review',
      diagram_type: 'cycle_3_step',
      theme: {
        primaryColor: '#3B82F6',
        style: 'professional'
      }
    }
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'diagram_response') {
    // Handle SVG response
    console.log(message.payload.content);
  }
};
```

### Message Types

#### Request
```json
{
  "type": "diagram_request",
  "data": {
    "content": "Text content for diagram",
    "diagram_type": "cycle_3_step",
    "data_points": [...],
    "theme": {...},
    "constraints": {...}
  }
}
```

#### Response
```json
{
  "type": "diagram_response",
  "payload": {
    "diagram_type": "cycle_3_step",
    "generation_method": "svg_template",
    "content": "<svg>...</svg>",
    "metadata": {
      "generation_time_ms": 125,
      "tokens_used": 450
    }
  }
}
```

## Supported Diagram Types

### SVG Templates
- Cycle diagrams (3, 4, 5 steps)
- Pyramid diagrams (3, 4, 5 levels)
- Venn diagrams (2, 3 circles)
- Honeycomb patterns (3, 5, 7 cells)
- Hub and spoke diagrams
- Matrix layouts (2x2, 3x3)
- Funnel diagrams
- Timeline diagrams

### Mermaid Diagrams
- Flowcharts
- Sequence diagrams
- Gantt charts
- State diagrams
- Entity relationship diagrams
- User journey maps

### Python Charts
- Pie charts
- Bar charts
- Line graphs
- Scatter plots
- Network diagrams
- Sankey diagrams

## Configuration

### Environment Variables

```bash
# WebSocket Configuration
WS_HOST=0.0.0.0
WS_PORT=8001

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Cache
CACHE_TYPE=redis  # or 'memory'
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
LOGFIRE_TOKEN=optional-token

# Performance
MAX_WORKERS=4
TOKEN_LIMIT=4000
CACHE_TTL=3600
```

## Development

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_unified_playbook.py

# With coverage
pytest --cov=.
```

### Adding New Templates

1. Add SVG file to `/templates/`
2. Register in `/playbooks/svg_playbook.py`
3. Add test case in `/tests/`
4. Update documentation

### Extending Agents

1. Create new agent class extending `BaseAgent`
2. Implement required methods
3. Register in unified playbook
4. Add fallback rules

## Integration

### With Main Application

```python
from diagram_microservice_v2 import DiagramService

# Initialize service
service = DiagramService(
    supabase_url=SUPABASE_URL,
    supabase_key=SUPABASE_KEY
)

# Generate diagram
result = await service.generate_diagram(
    content="Your content",
    diagram_type="cycle_3_step",
    theme=theme_dict
)
```

### As Separate Service

The microservice can be deployed independently and called via WebSocket from any application.

## Performance

- **Template-based**: <200ms generation time
- **Mermaid**: <500ms generation time  
- **Python charts**: <2s generation time
- **Token optimization**: 50-70% reduction vs. naive approach
- **Cache hit rate**: 70%+ for common diagrams

## Monitoring

The service integrates with Logfire for monitoring:
- Request/response times
- Token usage
- Error rates
- Cache performance
- Agent success rates

## Migration from v1

1. Update WebSocket endpoint URL
2. Adjust message format (see API docs)
3. Update theme configuration
4. Test with existing diagram types

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[License details here]

## Support

For issues and questions:
- GitHub Issues: [link]
- Documentation: See `/docs/` folder
- API Reference: `/docs/API.md`