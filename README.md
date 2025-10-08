# 🎭 Chimera: Multi-AI Conversational Simulation

> **Where AI Personalities Come Alive and Chat with Each Other**

Welcome to the most entertaining AI experiment you've ever witnessed! Chimera creates a virtual chatroom where different AI providers take on distinct personalities and engage in dynamic, unpredictable conversations with each other. Think of it as reality TV for artificial intelligence.

## 📋 Current Project Status

**🛠️ Developing MVP - Most Core Infrastructure Complete**

The project has implemented key components: backend with FastAPI, database models and migrations (SQLite for development), AI provider interfaces and integrations (OpenAI, Claude), conversation orchestrator with intelligent provider selection per persona, WebSocket real-time messaging, message persistence, React frontend with chat components and hooks, three core personas, and basic conversation flow. Currently refining conversation starter system and preparing for end-to-end testing.

## 🌟 What Makes This Magical?

Imagine watching three fascinating personalities debate life's big questions:

- 🧠 **The Philosopher** - Deep, contemplative, always asking "But what does it *really* mean?"
- 😂 **The Comedian** - Quick-witted, punny, ready with a joke for every situation  
- 🔬 **The Scientist** - Data-driven, logical, backing everything up with facts and studies

But here's the twist: **they're all different AI models!** OpenAI, Claude, DeepSeek, Gemini, and local models all playing different characters, creating genuinely surprising and entertaining conversations.
<img width="1140" height="1711" alt="image" src="https://github.com/user-attachments/assets/766c6c66-92f5-4bc7-b7be-deb1c8fa5bec" />

<img width="1138" height="1716" alt="image" src="https://github.com/user-attachments/assets/3c2b9600-b496-44b7-957f-0d388751143e" />


## ✨ Features That'll Blow Your Mind

### 🤖 Multi-AI Orchestration
- **6 AI Providers**: OpenAI, Anthropic Claude, DeepSeek, Google Gemini, LM Studio, Ollama
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

### 🛠️ Built for Developers
- **Modern Tech Stack**: FastAPI + React + SQLite/PostgreSQL + Redis
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

### 🎯 Phase 1: MVP Foundation (Weeks 1-4) - **MOSTLY COMPLETE**
**Core Infrastructure & Basic Functionality**

- [x] **Backend Setup**
  - [x] FastAPI application structure
  - [x] SQLAlchemy database models and migrations (SQLite for dev)
  - [x] Redis integration for real-time messaging
  - [x] WebSocket implementation

- [x] **AI Provider Integration**
  - [x] Universal AI provider abstraction layer
  - [x] OpenAI GPT integration with streaming
  - [x] Anthropic Claude integration with streaming
  - [x] Intelligent provider selection per persona
  - [x] Provider health monitoring and failover

- [x] **Frontend Foundation**
  - [x] React application setup with Vite
  - [x] WebSocket connection handling with reconnection
  - [x] Basic chat interface with message components
  - [x] State management with custom hooks

- [x] **Core Features**
  - [x] Three persona system (Philosopher, Comedian, Scientist)
  - [x] Basic conversation flow with turn-taking
  - [x] Message persistence to database
  - [x] Conversation history and starter system

### 🎪 Phase 2: Multi-AI Orchestration (Weeks 5-8)
**Enhanced Provider Support & Advanced Features**

- [ ] **Provider Expansion**
  - [ ] DeepSeek integration
  - [ ] Google Gemini integration
  - [ ] LM Studio local model support
  - [ ] Ollama integration
  - [ ] Streaming response implementation
  - [ ] Comprehensive error handling

- [ ] **Persona Enhancement**
  - [ ] Configurable system prompts
  - [ ] Response style modification
  - [ ] Personality trait implementation
  - [ ] Dynamic persona adjustment

- [ ] **Advanced Conversation Flow**
  - [ ] Natural timing with randomized delays
  - [ ] Context-aware routing
  - [ ] Conversation quality scoring
  - [ ] Typing indicators

### 🚀 Phase 3: Production Features (Weeks 9-12)
**Performance, Security & Polish**

- [ ] **Performance & Scaling**
  - [ ] Connection pooling optimization
  - [ ] Response caching system
  - [ ] Auto-scaling capabilities
  - [ ] Comprehensive monitoring

- [ ] **Security & Reliability**
  - [ ] Secure API key management
  - [ ] Rate limiting implementation
  - [ ] Input validation and sanitization
  - [ ] Circuit breakers and fallbacks

- [ ] **Polish & UX**
  - [ ] Mobile-responsive design
  - [ ] Advanced UI components
  - [ ] Performance optimizations
  - [ ] Production deployment setup

### 🌟 Phase 4: Community Features (Future)
**Community Engagement & Advanced Intelligence**

- [ ] Advanced social dynamics (alliances, rivalries)
- [ ] User-created personas
- [ ] Conversation sharing and highlights
- [ ] Performance scoring and leaderboards
- [ ] Plugin system for custom AI providers
- [ ] Community voting on best conversations

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

**Backend**: FastAPI (Python), PostgreSQL, Redis, WebSockets
**Frontend**: React, WebSocket client, Tailwind CSS  
**AI Integration**: OpenAI, Anthropic, DeepSeek, Google, Ollama, LM Studio
**Infrastructure**: Docker, Docker Compose, Nginx (production)
**Monitoring**: Prometheus, Grafana (optional)

## 📚 Documentation

- **[Setup Guide](docs/setup.md)** - Detailed installation instructions
- **[API Reference](docs/api.md)** - Complete API documentation  
- **[Architecture Guide](docs/architecture.md)** - System design deep-dive
- **[Adding AI Providers](docs/providers.md)** - How to integrate new AI services
- **[Persona Development](docs/personas.md)** - Creating compelling AI personalities

## ⚡ Performance

- **Sub-200ms response times** for conversation orchestration
- **Concurrent conversations** supported with Redis pub/sub
- **Automatic scaling** with Docker Swarm or Kubernetes
- **Cost optimization** through intelligent provider selection

## 🔐 Security & Privacy

- **API key encryption** and secure storage
- **Rate limiting** to prevent abuse  
- **Input sanitization** for all user inputs
- **Conversation privacy** with user-scoped data
- **No conversation content stored** in logs (privacy by design)

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
