# Contributing to Chimera

Thank you for your interest in contributing to Chimera! This document provides guidelines and instructions for contributing to our multi-AI conversational simulation project.

## 🎯 Ways to Contribute

### 🌟 Easy Contributions
- **Add conversation starter topics**: Expand the list of interesting discussion topics
- **Create additional AI personas**: Design new personality types with unique traits
- **Improve UI/UX**: Enhance the user interface and experience
- **Write tests**: Add test coverage for conversation scenarios
- **Documentation**: Help improve and expand documentation
- **Bug reports**: Report issues you encounter

### 🚀 Advanced Contributions
- **Integrate new AI providers**: Add support for additional AI services
- **Build conversation analytics**: Create insights and metrics dashboards
- **Optimize performance**: Improve response times and resource usage
- **Add gamification features**: Implement scoring, achievements, and social features
- **Security enhancements**: Strengthen security measures and privacy features

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git

### Local Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/chimera.git
   cd chimera
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Add your API keys for AI providers
   ```

3. **Start the development environment**
   ```bash
   # Using Docker (recommended)
   docker-compose up --build
   ```

4. **Verify installation**
   - Backend: http://localhost:8000/docs
   - Frontend: http://localhost:3000

## 📋 Development Guidelines

### Code Style

#### Python (Backend)
- Follow PEP 8 style guidelines
- Use type hints for all functions and methods
- Use async/await for all I/O operations
- Add comprehensive docstrings to classes and functions

#### JavaScript/React (Frontend)
- Use ES6+ features and modern React patterns
- Use TypeScript for type safety
- Follow functional component patterns with hooks
- Use meaningful component and variable names

### Git Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Ensure existing tests pass

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new AI provider integration"
   ```

4. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 🧪 Testing

Run tests before submitting:

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# All tests
make test
```

## 📝 Documentation

When contributing, please ensure:
- Code comments explain complex logic
- API documentation is updated for API changes
- README updates for installation and usage changes
- Architecture docs for significant changes

## 🙏 Recognition

Contributors are recognized in project README, release notes, and the contributors page.

---

Thank you for helping make Chimera amazing! 🎭✨