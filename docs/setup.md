# Chimera Setup Guide

This guide will help you set up Chimera locally for development or production use.

## 📋 Prerequisites

**Required:**
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **Git**: Latest version

**AI Provider API Keys** (at least one required):
- **OpenAI**: [Get API key](https://platform.openai.com/api-keys)
- **Anthropic (Claude)**: [Get API key](https://console.anthropic.com/)
- **DeepSeek**: [Get API key](https://platform.deepseek.com/)
- **Google AI (Gemini)**: [Get API key](https://makersuite.google.com/app/apikey)

## 🚀 Quick Start (Docker - Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/chimera.git
cd chimera
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

Required environment variables in backend/.env:
```bash
# Database (use SQLite for local dev, PostgreSQL for production)
DATABASE_URL=sqlite:///./chimera.db  # or postgresql://...

# Redis
REDIS_URL=redis://localhost:6379

# AI Provider API Keys (add at least one)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Settings
SECRET_KEY=your_super_secret_key_here
DEBUG=true
```

### 3. Start the Application
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Verify Installation
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

🎉 **That's it!** You should now have Chimera running with AI personalities ready to chat.

## 🛠️ Manual Setup (Development)

For development without Docker:

### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (uses SQLite by default)
alembic upgrade head

# Start Redis (optional for WebSockets)
redis-server  # In separate terminal

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🐛 Troubleshooting

### Port Conflicts
```bash
# Check what's using ports
sudo lsof -i :3000  # Frontend
sudo lsof -i :8000  # Backend

# Kill processes using ports
sudo kill -9 <PID>
```

### Docker Issues
```bash
# Clean up Docker
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up
```

### Database Connection Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
cd backend && alembic upgrade head
```

## 📊 Health Check
```bash
# Check backend health
curl http://localhost:8000/health

# Check all services
curl http://localhost:8000/health/providers
```

## 🆘 Getting Help

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Documentation**: Check other docs in this directory

---

Happy conversing! 🎭✨