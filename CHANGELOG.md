# Changelog

All notable changes to Chimera project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-10

### 🎯 Added - Full AI Control System

#### Advanced Provider/Model Management
- **Granular AI Assignment**: Complete manual control over which AI provider and specific model powers each persona (GPT-4, Claude Opus, OpenRouter models, etc.)
- **Per-Persona Customization**: Each personality can use different AI brains - Philosopher with GPT-4, Scientist with Claude, Comedian with OpenRouter
- **Real-Time Configuration**: Instant application of provider/model settings without server restart
- **Flexible Routing**: Manual overrides respected first, with intelligent auto-selection as fallback

#### API Validation & Testing System
- **Built-in API Test Suite**: Test feature validates API keys with actual provider calls before conversations start
- **Connection Validation**: Verifies API key authenticity and provider connectivity
- **Error Diagnostics**: Detailed error messages help troubleshoot API key issues

#### Advanced Status Monitoring
- **Real-Time Provider Dashboard**: Header shows configured vs. demo providers with visual icons (🤖 OpenAI, 🎯 OpenRouter, etc.)
- **Provider Health Status**: Live indicators of which AI providers are active and healthy
- **Model-Level Granularity**: View specific models assigned to personas (GPT-4, Claude-3-Opus, etc.)
- **Configuration Transparency**: Detailed tooltip showing current AI assignments per persona

#### Professional Control Features
- **Persona Selector UI**: Expandable cards with provider/model assignment controls
- **Intelligent Provider Selection**: System prioritizes user settings over automatic defaults
- **Validation Safeguards**: Test API keys before starting expensive conversations
- **Zero-Downtime Updates**: Configuration changes apply instantly without service interruption

### 🔧 Technical Improvements
- **Provider Override Logic**: Enhanced orchestrator respects manual persona configurations
- **Model Parameter Handling**: Backend properly processes and forwards model selections to providers
- **API Key Persistence**: Temporary storage with immediate reload capability during sessions
- **Enhanced Error Handling**: Better diagnostics for provider connectivity issues

### 📚 Documentation Updates
- **Provider Control Guide**: Complete documentation for persona-specific AI assignment
- **API Reference Updates**: New endpoints for testing and configuration
- **Advanced Usage Examples**: Guide for creating custom AI ensembles
- **Troubleshooting Guide**: Solutions for common provider configuration issues

---

## [0.1.1] - 2025-10-09

### ✅ Fixed
- **Test Infrastructure Issues**: Fixed syntax errors, missing dependencies, and import issues in test files
- **Conversation Memory System**: Fixed ChromaDB initialization and added missing memory processing methods
- **Package Dependencies**: Updated `requirements.txt` with missing dependencies (pytest-asyncio, chromadb)
- **Database Configuration**: Fixed import errors in database configuration and conversation memory
- **Test Environment**: Resolved asyncio fixture issues and mocking problems in conversation orchestrator tests

### 🔧 Technical Fixes
- **ChromaDB Upgrades**: Updated from deprecated Settings API to PersistentClient for vector database
- **Memory Processing**: Added persona-specific memory routing and vector memory placeholder methods
- **Test Configuration**: Fixed pytest-asyncio fixture decorations and relative import issues
- **Authentication Setup**: Ensured python-jose dependencies are properly configured

## [0.1.0] - 2025-10-08

### 🆕 Added
- **Multi-AI Conversation Orchestration**: Support for 7 AI providers (OpenAI, Claude, DeepSeek, Gemini, OpenRouter, LM Studio, Ollama)
- **Persona Management System**: 32 built-in AI personas with customization capabilities
- **GUI Persona Creator**: Point-and-click interface for designing custom AI personalities
- **Connection Manager**: Visual interface for configuring AI provider API keys
- **Provider/Model Assignment**: Assign specific AI providers and models to individual personas
- **Demo Mode**: `CHIMERA_DEMO_MODE=true` bypasses authentication for personal installations
- **Real-time Chat Interface**: WebSocket-based live conversations with typing indicators
- **Response Caching**: Redis-backed caching to improve performance and reduce API costs
- **User Authentication**: JWT-based user registration and login system
- **WebSocket API**: Real-time bidirectional communication

### 🏗️ Technical Features
- **FastAPI Backend**: Modern Python API framework with automatic documentation
- **React Frontend**: Component-based UI with Tailwind CSS styling
- **PostgreSQL/SQLite**: Flexible database support with Alembic migrations
- **Redis Integration**: Caching and real-time messaging
- **Docker/Containerization**: Complete Docker setup for development and production
- **Semantic Versioning**: Standardized release versioning with Git tags
- **Comprehensive Documentation**: Setup guides, API reference, and architecture docs

### 🔧 Infrastructure
- **Modular Architecture**: Easy addition of new AI providers and personas
- **Health Checks**: Provider availability monitoring and failover
- **Configuration Management**: Environment-based settings with Pydantic
- **Error Handling**: Comprehensive error handling with logging
- **Security**: Input validation, CORS configuration, and secure API key storage

### 📚 Documentation
- **Setup Guide**: Complete installation instructions for various environments
- **Provider Integration**: How to add new AI services
- **Persona Development**: Guidelines for creating compelling AI personalities
- **API Reference**: Full REST and WebSocket API documentation
- **Architecture Guide**: System design and technical overview
- **Versioning Policy**: Semantic versioning and release management

---

This initial release marks the transition from MVP to a feature-complete multi-AI conversational system capable of production deployment.
</xai:function_call committed to overwriting the file. The creation overwrites the old file.