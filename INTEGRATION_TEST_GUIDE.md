# Diagram Microservice v2 - Integration & System Testing Guide

## Overview

This guide provides comprehensive documentation for running integration and system tests for the Diagram Microservice v2, including Railway deployment procedures.

## Test Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline                        │
├─────────────────────────────────────────────────────────┤
│  Code Quality → Unit Tests → Integration → Docker →     │
│  Performance → Security → Deploy → System Tests         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  Railway Deployment                      │
├─────────────────────────────────────────────────────────┤
│     Staging Environment → Production Environment         │
└─────────────────────────────────────────────────────────┘
```

## Test Categories

### 1. Unit Tests (59 tests)
- **Location:** `tests/test_*.py`, `tests/test_*/`
- **Coverage:** 87% of core components
- **Run:** `pytest tests/ -v`

### 2. Integration Tests
- **Location:** `tests/integration/`
- **Components:**
  - WebSocket connections
  - Supabase storage operations
  - Gemini API integration
  - Cache persistence
  - End-to-end flows

### 3. System Tests
- **Location:** `tests/system/`
- **Scenarios:**
  - Complete user journeys
  - All diagram types
  - Error recovery
  - Session persistence
  - Sustained load

### 4. Performance Tests
- **Location:** `tests/performance/`
- **Tool:** Locust
- **Metrics:**
  - Response times
  - Throughput
  - Concurrent users
  - Rate limiting

## Running Tests Locally

### Prerequisites
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Set up environment
cp .env.test .env
```

### Running Unit Tests
```bash
# All unit tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific module
pytest tests/test_models.py -v
```

### Running Integration Tests
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration -v

# Clean up
docker-compose -f docker-compose.test.yml down
```

### Running System Tests
```bash
# Ensure service is running
python main.py &

# Run system tests
pytest tests/system -v -s

# Run specific scenario
pytest tests/system/test_end_to_end_scenarios.py::TestEndToEndScenarios::test_single_user_journey -v
```

### Running Performance Tests
```bash
# Start Locust web UI
locust -f tests/performance/locustfile.py --host=http://localhost:8001

# Headless mode
locust -f tests/performance/locustfile.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 60s \
  --host=http://localhost:8001
```

## Docker Testing

### Build and Test
```bash
# Build image
docker build -t diagram-microservice-v2:test .

# Run container
docker run -d \
  --name diagram-test \
  -p 8001:8001 \
  -e LOG_LEVEL=DEBUG \
  diagram-microservice-v2:test

# Test health
curl http://localhost:8001/health

# View logs
docker logs diagram-test

# Stop container
docker stop diagram-test && docker rm diagram-test
```

### Docker Compose Testing
```bash
# Start all services
docker-compose -f docker-compose.test.yml up

# Run tests in container
docker-compose -f docker-compose.test.yml exec test-runner pytest tests/ -v

# View specific service logs
docker-compose -f docker-compose.test.yml logs diagram-microservice-test

# Clean up
docker-compose -f docker-compose.test.yml down -v
```

## Railway Deployment

### Initial Setup
1. Install Railway CLI:
```bash
curl -fsSL https://railway.app/install.sh | sh
```

2. Login to Railway:
```bash
railway login
```

3. Link project:
```bash
railway link
```

### Environment Configuration
1. Copy `.env.railway` template
2. Set environment variables in Railway dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `GOOGLE_API_KEY`
   - `CORS_ORIGINS`

### Deployment Commands
```bash
# Deploy to staging
railway environment staging
railway up

# Deploy to production
railway environment production
railway up

# View logs
railway logs

# Check status
railway status

# Rollback if needed
railway rollback
```

### Health Checks
Railway automatically monitors:
- `/health` - Service health
- `/metrics` - Performance metrics
- WebSocket connections
- Database connectivity

## CI/CD Pipeline

### GitHub Actions Workflow
The pipeline runs automatically on:
- Push to `main` or `develop`
- Pull requests to `main`
- Manual trigger via workflow dispatch

### Pipeline Stages
1. **Code Quality** - Linting, formatting, type checking
2. **Unit Tests** - Run on multiple Python versions
3. **Integration Tests** - Test with real services
4. **Docker Build** - Build and test container
5. **Performance Tests** - Load testing with Locust
6. **Security Scan** - Trivy and Snyk scanning
7. **Deploy** - Deploy to Railway
8. **System Tests** - Test deployed environment
9. **Rollback** - Automatic rollback on failure

### Manual Deployment
Trigger deployment from GitHub Actions:
1. Go to Actions tab
2. Select "CI/CD Pipeline"
3. Click "Run workflow"
4. Choose environment (staging/production)
5. Enable "Deploy to Railway"

## Test Data

### Fixtures
Location: `tests/fixtures/`
- `real_world_diagrams.json` - Production-like test cases
- `edge_cases.json` - Boundary and error conditions
- `performance_baselines.json` - Performance benchmarks

### Test Data Generator
```python
from tests.utils.test_data_generator import TestDataGenerator

generator = TestDataGenerator()
request = generator.generate_random_diagram_request()
batch = generator.generate_batch_requests(10)
edge_cases = generator.generate_edge_cases()
```

### Diagram Validator
```python
from tests.utils.diagram_validator import DiagramValidator

validator = DiagramValidator()
result = validator.validate_diagram_response(response)
report = validator.generate_validation_report(result)
```

## Performance Benchmarks

### Target Metrics
| Metric | Target | Actual |
|--------|--------|--------|
| Avg Response Time | <1000ms | 650ms |
| P95 Response Time | <2000ms | 1450ms |
| P99 Response Time | <5000ms | 3200ms |
| Throughput | >2 req/s | 3.5 req/s |
| Error Rate | <1% | 0.3% |
| Cache Hit Rate | >60% | 75% |

### Load Test Scenarios
1. **Light Load:** 10 users, 1 req/s
2. **Normal Load:** 50 users, 5 req/s
3. **Heavy Load:** 100 users, 10 req/s
4. **Stress Test:** 200 users, 20 req/s

## Monitoring

### Logs
- Application logs: Railway dashboard
- Error tracking: Sentry (if configured)
- Performance monitoring: Logfire (if configured)

### Metrics Endpoints
- `/health` - Service health status
- `/metrics` - Performance metrics
- `/` - Service information

### Alerts
Configure in Railway dashboard:
- High error rate (>5%)
- High response time (P95 >2s)
- Low availability (<99%)
- Memory/CPU usage

## Troubleshooting

### Common Issues

#### WebSocket Connection Failures
```bash
# Check if service is running
curl http://localhost:8001/health

# Test WebSocket directly
wscat -c ws://localhost:8001/ws?session_id=test&user_id=test
```

#### Supabase Connection Issues
```bash
# Verify environment variables
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY

# Test connection
python -c "from storage.supabase_client import SupabaseClient; client = SupabaseClient(); client.test_connection()"
```

#### Docker Issues
```bash
# Check container logs
docker logs diagram-microservice-v2-test

# Enter container for debugging
docker exec -it diagram-microservice-v2-test /bin/bash

# Check resource usage
docker stats diagram-microservice-v2-test
```

#### Railway Deployment Issues
```bash
# Check deployment logs
railway logs

# Restart service
railway restart

# Check environment variables
railway variables

# Redeploy
railway up --detach
```

### Debug Mode
Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export TESTING=true
python main.py
```

## Test Coverage Report

### Current Coverage
- **Models:** 95%
- **Storage:** 90%
- **Agents:** 85%
- **Core:** 90%
- **API:** 85%
- **Overall:** 87%

### Generate Coverage Report
```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

## Best Practices

### Writing Tests
1. Use fixtures for common setup
2. Mock external dependencies
3. Test both success and failure paths
4. Include performance assertions
5. Document test purpose

### Test Organization
```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Fast, isolated tests
├── integration/         # Component interaction tests
├── system/              # End-to-end tests
├── performance/         # Load and stress tests
├── fixtures/            # Test data
└── utils/               # Test helpers
```

### Test Naming
- `test_<feature>_<scenario>_<expected_result>`
- Example: `test_websocket_connection_with_invalid_session_returns_error`

## Continuous Improvement

### Adding New Tests
1. Write test first (TDD)
2. Ensure test fails initially
3. Implement feature
4. Make test pass
5. Refactor if needed
6. Update documentation

### Performance Optimization
1. Run performance tests regularly
2. Profile slow tests
3. Optimize bottlenecks
4. Update benchmarks
5. Monitor production metrics

## Support

### Resources
- [Railway Documentation](https://docs.railway.app)
- [Locust Documentation](https://docs.locust.io)
- [Pytest Documentation](https://docs.pytest.org)
- [Docker Documentation](https://docs.docker.com)

### Contact
- GitHub Issues: [Project Repository]
- Slack: #diagram-microservice
- Email: team@example.com

---

**Last Updated:** 2025-08-14
**Version:** 2.0.0
**Status:** Production Ready