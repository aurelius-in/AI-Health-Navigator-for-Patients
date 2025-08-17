# AI Health Navigator Backend

Advanced AI-powered healthcare backend system with intelligent agents, comprehensive data management, and enterprise-grade architecture.

## 🏗️ Architecture

```
backend/
├── ai_health_navigator/          # Main application package
│   ├── ai/                      # AI and Machine Learning
│   │   ├── agents/              # AI Agents (Agentic AI)
│   │   │   ├── base_agent.py    # Base agent class
│   │   │   ├── symptom_agent.py # Symptom analysis agent
│   │   │   ├── triage_agent.py  # Triage assessment agent
│   │   │   ├── provider_agent.py # Provider matching agent
│   │   │   ├── health_coach_agent.py # Health coaching agent
│   │   │   ├── emergency_agent.py # Emergency response agent
│   │   │   └── agent_orchestrator.py # Agent coordination
│   │   ├── models.py            # AI models (ML/DL)
│   │   └── llm_service.py       # LLM integration
│   ├── api/                     # FastAPI application
│   │   ├── main.py              # API entry point
│   │   ├── middleware.py        # Custom middleware
│   │   └── routes/              # API endpoints
│   ├── core/                    # Core functionality
│   │   ├── config.py            # Configuration management
│   │   └── logging.py           # Structured logging
│   └── database/                # Data access layer
│       ├── models.py            # SQLAlchemy models
│       ├── session.py           # Database session management
│       └── repositories.py      # Repository pattern
├── config/                      # Configuration files
├── scripts/                     # Utility scripts
├── tests/                       # Test suite
├── migrations/                  # Database migrations
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration
├── Dockerfile                   # Container configuration
└── docker-compose.yml          # Service orchestration
```

## 🤖 AI Agents (Agentic AI)

The backend includes a sophisticated AI agent system:

### Core Agents
- **SymptomAnalysisAgent**: Analyzes symptoms using AI models and medical knowledge
- **TriageAssessmentAgent**: Emergency triage and urgency classification
- **ProviderMatchingAgent**: Intelligent provider matching and recommendations
- **HealthCoachAgent**: Personalized health coaching and wellness guidance
- **EmergencyResponseAgent**: Emergency coordination and critical care

### Agent Orchestrator
- **AgentOrchestrator**: Coordinates multiple agents with different strategies:
  - Sequential execution
  - Parallel execution
  - Hierarchical execution
  - Adaptive execution (intelligent routing)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL
- Redis
- Docker (optional)

### Installation

1. **Clone and setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment setup**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Database setup**:
```bash
python -m ai_health_navigator.cli init
```

4. **Start the server**:
```bash
python -m ai_health_navigator.cli serve
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run individual services
docker-compose up api postgres redis
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/health_navigator

# Redis
REDIS_URL=redis://localhost:6379

# AI/ML Models
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Security
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Monitoring
SENTRY_DSN=your_sentry_dsn
PROMETHEUS_ENABLED=true
```

### Agent Configuration

Agents can be configured through the `AgentOrchestrator`:

```python
from ai_health_navigator.ai.agents import AgentOrchestrator

# Initialize orchestrator
orchestrator = AgentOrchestrator()
await orchestrator.initialize()

# Execute workflow
result = await orchestrator.execute_workflow(
    workflow_id="symptom_analysis_001",
    tasks=[...],
    strategy=OrchestrationStrategy.ADAPTIVE
)
```

## 📊 API Endpoints

### Health & Monitoring
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /agents/health` - Agent health status

### Symptom Analysis
- `POST /api/symptoms/analyze` - Analyze symptoms
- `POST /api/symptoms/batch` - Batch symptom analysis
- `GET /api/symptoms/history/{user_id}` - Symptom history

### Triage Assessment
- `POST /api/triage/assess` - Emergency triage
- `GET /api/triage/history/{user_id}` - Triage history

### Provider Management
- `GET /api/providers/search` - Search providers
- `GET /api/providers/{provider_id}` - Provider details

### Agent Management
- `GET /api/agents/stats` - Agent statistics
- `POST /api/agents/execute` - Execute agent workflow
- `GET /api/agents/capabilities` - Available capabilities

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/agents/

# Run with coverage
pytest --cov=ai_health_navigator --cov-report=html
```

## 📈 Monitoring & Observability

### Metrics
- Prometheus metrics for all endpoints
- Custom metrics for agent performance
- Database connection metrics
- Cache hit/miss ratios

### Logging
- Structured JSON logging
- Request/response logging
- Agent execution logging
- Error tracking with Sentry

### Health Checks
- Database connectivity
- Redis connectivity
- Agent health status
- External service dependencies

## 🔒 Security Features

- JWT authentication
- Role-based access control (RBAC)
- Rate limiting
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration
- Security headers

## 🚀 Production Deployment

### Kubernetes
```yaml
# Example deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-health-navigator-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-health-navigator-backend
  template:
    metadata:
      labels:
        app: ai-health-navigator-backend
    spec:
      containers:
      - name: backend
        image: ai-health-navigator/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

### Environment-Specific Configs
- Development: `config/dev.env`
- Staging: `config/staging.env`
- Production: `config/prod.env`

## 🔧 Development

### Code Quality
```bash
# Format code
black ai_health_navigator/
isort ai_health_navigator/

# Lint code
flake8 ai_health_navigator/
mypy ai_health_navigator/

# Pre-commit hooks
pre-commit install
```

### Adding New Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement required methods
3. Register in `AgentOrchestrator`
4. Add tests
5. Update documentation

Example:
```python
from .base_agent import BaseAgent, AgentContext, AgentResult

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("my_custom_agent", "Description")
    
    async def execute(self, context: AgentContext, **kwargs) -> AgentResult:
        # Implementation
        pass
    
    def validate_input(self, context: AgentContext, **kwargs) -> bool:
        # Validation
        pass
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Agent Development Guide](docs/agents.md)
- [Database Schema](docs/database.md)
- [Deployment Guide](docs/deployment.md)
- [Security Guide](docs/security.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
