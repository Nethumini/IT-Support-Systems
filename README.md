# IT Support Systems

AI-powered IT support system for automated ticket handling, troubleshooting, and resolution.

## Features

- Automated ticket triage and classification
- Intelligent troubleshooting with AI agents
- Interactive AI chatbot for user support
- Real-time monitoring dashboard
- Safe diagnostic operations
- Complete audit logs

## Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Google Gemini API Key** ([Get Free Key](https://makersuite.google.com/app/apikey))

**Install Python via Command Line:**
```powershell
# Option 1: Using winget (Windows Package Manager)
winget install Python.Python.3.11

# Option 2: Using Chocolatey
choco install python311

# After installation, verify:
python --version
```

**Enable PowerShell Script Execution (Optional):**
```powershell
# Run this once to allow scripts to run directly:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Or run scripts with bypass (no permanent change needed):
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

## Setup Guide

### 1. Clone Repository

```bash
git clone https://github.com/Nethumini/IT-Support-Systems.git
cd it-support-systems
```

### 2. Run Setup Script

```powershell
.\setup.ps1
```

This will:
- Create Python virtual environment
- Install backend dependencies
- Create necessary directories
- Setup `.env` file

### 3. Configure API Keys

Edit `backend\.env` and add your API key:

```env
# Required: Choose one AI provider
GOOGLE_API_KEY=your_gemini_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Choose AI provider (default: google)
AI_PROVIDER=google
```

### 4. Add Ticket Data (Optional)

Place your ticketing data in `data\raw\ticketing_system_data_new.json`

### 5. Run Application

**Backend (Terminal 1):**
```powershell
.\run.ps1
```

**Frontend (Terminal 2):**
```powershell
.\run-frontend.ps1
```

The application will start:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## Docker Deployment

```bash
docker-compose up --build
```

For production deployment to DigitalOcean, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## Project Structure

```
it-support-systems/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Core config
│   │   ├── models/   # Data models
│   │   └── services/ # Business logic
│   └── tests/        # Backend tests
├── frontend/         # React frontend
│   └── src/
│       ├── components/
│       ├── services/
│       └── styles/
├── data/            # Data storage
└── logs/            # Application logs
```

## Quick Start Commands

```powershell
# Setup (one time)
.\setup.ps1

# Run backend
.\run.ps1

# Run frontend (in new terminal)
.\run-frontend.ps1
```

## Tech Stack

- **Backend**: Python, FastAPI, LangChain
- **Frontend**: React, Vite
- **AI**: Google Gemini / OpenAI
- **Database**: SQLite
- **Deployment**: Docker, DigitalOcean

## Hackathon Evaluation Criteria

| Criteria | Implementation |
|----------|---------------|
| **Innovation** | Multi-provider LLM, RAG-based context |
| **Technical Depth** | Clean architecture, modular design |
| **Accuracy** | AI-powered classification with confidence |
| **Safety** | Complete safe mode, audit logging |
| **User Experience** | Interactive chat, clear API docs |
| **Completeness** | Full ticket lifecycle, analytics |
| **Documentation** | Comprehensive docs, architecture diagrams |

## Deliverables

- Working prototype (FastAPI backend)
- Architecture diagram (see ARCHITECTURE.md)
- List of supported issues
- Sample logs and data
- Complete documentation
- Docker deployment
- Safety rules implementation
- Audit logging

## Bonus Features Implemented

- Multi-provider LLM support (Gemini + OpenAI)
- RAG-based knowledge retrieval
- Smart escalation logic
- Comprehensive audit logging
- Docker deployment with CI/CD
- API documentation (Swagger/ReDoc)
- Modular, production-ready code
- Automated deployment to DigitalOcean

## Future Roadmap

- [ ] Slack/Teams integration
- [ ] Voice input support
- [ ] Email ticket creation
- [ ] Real system integrations (with proper auth)
- [ ] Predictive issue detection
- [ ] Multi-tenancy support
- [ ] Advanced ML models
- [ ] Mobile app

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or PR.

## Authors

Tharinda Pathirana

## Support

For issues or questions:
- Check `/docs` for API documentation
- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment info
- Review logs in `logs/` directory

---

**Last Updated**: December 7, 2025
