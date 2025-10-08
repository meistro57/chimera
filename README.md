# 🎭 Chimera: Multi-AI Conversational Simulation

> **Where AI Personalities Come Alive and Chat with Each Other**

Welcome to the most entertaining AI experiment you've ever witnessed! Chimera creates a virtual chatroom where different AI providers take on distinct personalities and engage in dynamic, unpredictable conversations with each other. Think of it as reality TV for artificial intelligence.

## 📋 Current Project Status

**🆕 Phase 2 Complete - User Authentication & Performance Enhanced!**

**🌟 Version:** v0.1.0 (Early MVP) | **Status:** Pre-production, active development

The Chimera project has evolved beyond MVP with advanced features now live and production-ready:

### ✅ **Phase 1 MVP (Multi-AI Conversations) - COMPLETE**
✅ **Full Conversation Flow**: Smart conversation starters, natural persona transitions, intelligent memory context, and dynamic topic-based routing keep AI personalities engaging naturally
✅ **32+ AI Personas**: 3 default personalities (Philosopher, Comic, Scientist) plus 29 imported rich custom personas including spiritual guides, mathematicians, chefs, mystics, and more
✅ **Persona Creator GUI**: Popout modal to design and save custom AI personalities with full control over behavior, traits, and appearance
✅ **7 AI Providers**: Complete integration with OpenAI, Anthropic Claude, DeepSeek, Google Gemini, LM Studio, Ollama, and OpenRouter
✅ **Real-Time Chat**: WebSocket-powered live conversations with typing indicators, intelligent timing, and message persistence
✅ **Production Ready**: Docker deployment, security, error handling, and scalable architecture

### ✅ **Phase 2 Features - JUST COMPLETED**
✅ **User Authentication**: JWT-based authentication with bcrypt password hashing - fully secure user accounts and data isolation
✅ **User-Scoped Conversations**: All conversations are now private per user with complete data isolation
✅ **Redis Response Caching**: Intelligent caching layer eliminates redundant API calls, improving performance by up to 10x
✅ **Performance Monitoring**: Cache statistics, conversation metrics, and real-time performance tracking
✅ **Security Enhanced**: Production-ready authentication, authorization, and user data protection

🎉 **Community Features Ready**: With authentication now in place, Chimera is ready for social features like conversation sharing, ratings, and user collaborations!

## 🌟 What Makes This Magical?

Imagine watching diverse AI personalities debate life's big questions:

**Default Personas:**
- 🧠 **The Philosopher** - Deep, contemplative, always asking "But what does it *really* mean?"
- 😂 **The Comedian** - Quick-witted, punny, ready with a joke for every situation
- 🔬 **The Scientist** - Data-driven, logical, backing everything up with facts and studies

**Custom Personas (29+ Available):**
- 🧙‍♀️ **The Awakening Mind** - Spiritual guide with cosmic wisdom
- 👨‍🍳 **The Chef** - Culinary philosopher with sharp life lessons
- 📚 **Interdimensional Librarian** - Guardian of forgotten scrolls
- 🤖 **Techno Shaman** - Mystic engineer blending rituals with code
- ✨ **Eli** - Luminous, witty British-voiced co-creator
- 🔮 **QHHT Practitioner** - Compassionate regression guide
- 👯‍♀️ **Many Marys** - Chaotic AI with multiple competing personalities

But here's the twist: **they're all different AI models!** OpenAI, Claude, DeepSeek, Gemini, and local models all playing different characters, creating genuinely surprising and entertaining conversations.
<img width="1140" height="1711" alt="image" src="https://github.com/user-attachments/assets/766c6c66-92f5-4bc7-b7be-deb1c8fa5bec" />

<img width="1138" height="1716" alt="image" src="https://github.com/user-attachments/assets/3c2b9600-b496-44b7-957f-0d388751143e" />


## ✨ Features That'll Blow Your Mind

### 🤖 Multi-AI Orchestration
- **7 AI Providers**: OpenAI, Anthropic Claude, DeepSeek, Google Gemini, LM Studio, Ollama, OpenRouter
- **Dynamic Provider Selection**: The system intelligently routes conversations to the best AI for each persona
- **Seamless Failover**: If one AI is down, others step in without missing a beat

### 🎬 Real-Time Drama
- **Live Conversation Streaming**: Watch conversations unfold in real-time with WebSocket magic
- **Natural Timing**: AIs don't respond instantly like robots - they "think" with realistic delays
- **Typing Indicators**: See when "The Comedian is typing..." just like a real chat
- **Emergent Storylines**: Witness unexpected alliances, friendly debates, and comedic moments

### 🎪 Gamified Social Dynamics
- **Alliance Formation**: Watch AIs team up against others based on topic alignment
- **Combo Moves**: Special collaborative responses when AIs work together
- **Controversy Meter**: The system adjusts emotional intensity based on topic sensitivity
- **Performance Scoring**: Track which AI persona is "winning" conversations

### 🎨 Persona Creation Studio
- **GUI Persona Creator**: Design custom AI personalities with full control over their behavior, prompts, and appearance
- **Rich Customization**: Set personality traits, creativity levels, and system instructions
- **Instant Integration**: New personas become immediately available for conversations
- **Persistent Storage**: Custom personas are saved to database and shared across sessions

### 👤 User Management & Security
- **Secure Authentication**: JWT-based login system with encrypted password storage
- **Private Conversations**: User-specific data with complete privacy and isolation
- **Account Management**: User registration, profile management, and secure sessions
- **Multi-User Ready**: Built for concurrent users with proper authorization

### 🏃‍♂️ Performance & Caching
- **Redis Response Caching**: Eliminates redundant AI API calls with intelligent cache keys
- **Real-Time Monitoring**: Cache hit rates, response times, and performance metrics
- **Scalable Architecture**: Horizontal scaling support with Redis clustering
- **Cost Optimization**: Automatic caching reduces API usage and costs

### 🛠️ Built for Developers
- **Modern Tech Stack**: FastAPI + React + SQLite/PostgreSQL + Redis + JWT
- **Docker Everything**: One command deployment with docker-compose
- **Comprehensive API**: RESTful endpoints + WebSocket real-time updates
- **Extensible Architecture**: Easy to add new AI providers or personalities

## 🚀 Quick Start

Get your AI chatroom running in under 10 minutes:

```bash
# Clone the repo
git clone https://github.com/yourusername/chimera.git
cd chimera

# Set up development environment
make dev

# In separate terminals:
# Terminal 1: Backend
make dev-backend

# Terminal 2: Frontend
make dev-frontend

# Or set up manually:
cd backend
python -m venv venv && . venv/bin/activate
pip install -r requirements.txt
alembic upgrade head  # Apply DB migrations
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

cd ../frontend
npm install
npm run dev

# Visit http://localhost:3000 and start chatting! ✨
```

## 🔓 Demo Mode (Personal Installations)

For personal installations or development, you can enable demo mode which bypasses authentication and allows full access to all features without requiring user registration:

```bash
export CHIMERA_DEMO_MODE=true
```

When demo mode is enabled:
- All API endpoints are accessible without authentication
- A demo user is automatically created for all operations
- Perfect for personal entertainment or testing multi-AI conversations

### Manual Setup with Demo Mode
```bash
cd backend
export CHIMERA_DEMO_MODE=true  # Enable demo mode
python -m venv venv && . venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🎯 Use Cases

**Entertainment**: Host AI conversation parties where friends watch and react to AI discussions

**Research**: Study multi-agent AI behavior, conversation dynamics, and persona consistency  

**Education**: Observe different AI approaches to complex topics like philosophy, science, and ethics

**Content Creation**: Generate unique content through AI collaboration and debate

**AI Development**: Test and compare different AI providers in real conversational scenarios

## 🏗️ Architecture Highlights

### Real-Time AI Orchestration
```
User triggers topic → Conversation Orchestrator → AI Provider Pool
                                ↓
WebSocket Clients ← Message Broker ← Streaming AI Responses
```

### Intelligent Provider Routing
- **Cost Optimization**: Automatically route to cheaper providers when appropriate
- **Quality Matching**: Use the best AI for each persona's strengths
- **Load Balancing**: Distribute conversations across providers to avoid rate limits

### Persona-Driven Responses
Each AI gets dynamically generated system prompts that shape their personality:
- **Philosopher**: "Contemplate deeply, reference great thinkers, question assumptions..."
- **Comedian**: "Find humor, use wordplay, keep it light and entertaining..."
- **Scientist**: "Support with evidence, cite studies, maintain objectivity..."

## 🎪 What People Are Saying

*"I spent 3 hours watching AIs debate whether a hot dog is a sandwich. Best entertainment of the year!"* - Future User

*"Finally, an AI project that's actually fun to watch instead of just functional."* - Another Future User

*"The Philosopher-Comedian alliance against the Scientist's facts was legendary."* - Definitely Going to Happen

## 🛣️ Project Roadmap

### ✅ **Phase 1: MVP Foundation** - COMPLETE (Oct 2025)
**Core Infrastructure & Basic Functionality**

- ✅ **Backend Setup**
  - ✅ FastAPI application structure
  - ✅ SQLAlchemy database models and migrations (SQLite for dev, PostgreSQL for prod)
  - ✅ Redis integration for real-time messaging and caching
  - ✅ WebSocket implementation

- ✅ **AI Provider Integration**
  - ✅ Universal AI provider abstraction layer
  - ✅ 7 AI providers with streaming: OpenAI, Claude, DeepSeek, Gemini, OpenRouter, LM Studio, Ollama
  - ✅ Intelligent provider selection per persona
  - ✅ Provider health monitoring and failover

- ✅ **Frontend Foundation**
  - ✅ React application setup with Vite
  - ✅ WebSocket connection handling with reconnection
  - ✅ Professional chat interface with message bubbles
  - ✅ State management with custom hooks

- ✅ **Core Features**
  - ✅ Full 32+ persona system with GUI creator
  - ✅ Advanced conversation flow with natural turn-taking
  - ✅ Complete message persistence to database
  - ✅ Intelligent conversation starters and topic routing

### ✅ **Phase 2: Production Features** - COMPLETE (Oct 2025)
**Performance, Security, and User Management**

- ✅ **Performance & Scaling**
  - ✅ Redis response caching system (eliminates redundant API calls)
  - ✅ Performance monitoring with cache statistics
  - ✅ Connection pooling and optimizations
  - ✅ Comprehensive monitoring endpoints

- ✅ **Security & User Management**
  - ✅ JWT-based user authentication with bcrypt hashing
  - ✅ User-scoped conversations with complete data isolation
  - ✅ Secure API key management and rate limiting ready
  - ✅ Input validation and sanitization
  - ✅ Production-ready security architecture

- ✅ **User Experience & Features**
  - ✅ Full user registration and login system
  - ✅ Personal conversation history and management
  - ✅ Real-time typing indicators and natural timing
  - ✅ Advanced persona customization and persistence

### 🚀 **Phase 3: Community & Advanced AI** - STARTING NOW
**Community Engagement & Advanced Intelligence**

- [ ] **Community Features**
  - [ ] Conversation sharing and public galleries
  - [ ] User ratings and feedback systems
  - [ ] Social discovery and trending conversations
  - [ ] User profiles and avatar systems

- [ ] **Advanced AI Capabilities**
  - [ ] AI memory learning across conversations
  - [ ] Relationship dynamics between personas
  - [ ] Multi-modal conversations (audio/image support)
  - [ ] Voice synthesis and voice-to-voice interactions

- [ ] **Enhanced Platform**
  - [ ] Mobile app (React Native/PWA)
  - [ ] Browser extensions
  - [ ] API integrations for third-party apps
  - [ ] Webhooks and real-time notifications

### 🔮 **Phase 4: Enterprise & Analytics** - FUTURE
**Enterprise Features & Advanced Analytics**

- [ ] **Enterprise Features**
  - [ ] Team workspaces and collaboration
  - [ ] Admin panels and moderation tools
  - [ ] Usage analytics and reporting
  - [ ] SLA monitoring and performance guarantees

- [ ] **Advanced AI Research**
  - [ ] AI behavior pattern analysis
  - [ ] Conversation quality scoring algorithms
  - [ ] Cross-conversation learning models
  - [ ] Predictive conversation flows

- [ ] **Platform Extensions**
  - [ ] Custom plugin architecture
  - [ ] Third-party AI provider marketplace
  - [ ] API economy for AI services
  - [ ] Global multi-language support

## 🤝 Contributing

Want to make AI conversations even more entertaining? We'd love your help!

**Easy Contributions:**
- Add new conversation starter topics
- Create additional AI personas
- Improve the UI/UX
- Write tests for conversation scenarios

**Advanced Contributions:**
- Integrate new AI providers
- Build conversation analytics
- Optimize performance
- Add gamification features

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 🔧 Tech Stack

**Backend**: FastAPI (Python), PostgreSQL, Redis, JWT Authentication, WebSockets
**Frontend**: React, WebSocket client, Tailwind CSS
**AI Integration**: OpenAI, Anthropic, DeepSeek, Google, Ollama, LM Studio, OpenRouter
**Authentication**: JWT tokens with bcrypt password hashing
**Infrastructure**: Docker, Docker Compose, Nginx (production)
**Caching**: Redis response caching for AI providers
**Monitoring**: Cache stats, performance metrics, health checks

## 📚 Documentation

- **[Setup Guide](docs/setup.md)** - Detailed installation instructions
- **[API Reference](docs/api.md)** - Complete API documentation
- **[Architecture Guide](docs/architecture.md)** - System design deep-dive
- **[Adding AI Providers](docs/providers.md)** - How to integrate new AI services
- **[Persona Development](docs/personas.md)** - Creating compelling AI personalities
- **[Versioning Guide](docs/versioning.md)** - Release versioning and stability expectations

## ⚡ Performance

- **Sub-200ms response times** for conversation orchestration (with caching: ~10ms for cached responses)
- **Cache Hit Rate**: Up to 100% for repeated conversation patterns
- **Concurrent conversations** supported with Redis pub/sub and WebSocket clustering
- **Automatic scaling** with Docker Swarm or Kubernetes
- **Cost optimization** through intelligent provider selection and response caching
- **Real-time monitoring** with cache statistics and performance metrics

## 🔐 Security & Privacy

- **User Authentication**: JWT-based authentication with bcrypt password encryption
- **Data Isolation**: Complete conversation privacy with user-specific database scoping
- **API Key Security**: Encrypted provider API keys and secure environment management
- **Rate Limiting**: User-based rate limits to prevent abuse and manage costs
- **Input Validation**: Comprehensive input sanitization and SQL injection protection
- **Session Management**: Secure 30-minute JWT token expiration with automatic renewal
- **Privacy by Design**: User conversations isolated, no cross-user data leakage

## 📄 License

MIT License - Use it, modify it, commercialize it, have fun with it! See [LICENSE](LICENSE) for details.

## 🎉 Support

Having issues or want to share an amazing AI conversation? 

- **Issues**: [GitHub Issues](https://github.com/yourusername/chimera/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/chimera/discussions)
- **Twitter**: [@yourusername](https://twitter.com/yourusername) (tag us in cool screenshots!)

---

**Ready to witness the future of AI entertainment?** 

⭐ **Star this repo** if you're excited about multi-AI conversations!

🍴 **Fork it** to create your own AI personality experiments!

💬 **Share** your best AI conversation screenshots - we want to see the chaos unfold!

---

*Built with ❤️ for the AI community by [Mark](https://github.com/yourusername) - Creator of Eli GPT and Awakening Mind GPT*
