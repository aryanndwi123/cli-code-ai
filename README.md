# klix Code - AI-Powered Development Assistant

A hybrid TypeScript/Python CLI tool that provides AI-powered assistance for software development tasks, similar to klix Code.

## Architecture

This project uses a hybrid architecture:

- **Python Backend**: FastAPI server handling authentication, AI integration, and heavy computational tasks
- **TypeScript Frontend**: Modern CLI interface with excellent user experience
- **Shared Types**: Common interfaces and protocols between frontend and backend

## Project Structure

```
klix-code-ai/
├── backend/               # Python FastAPI backend
│   ├── src/
│   │   ├── auth/         # Authentication system
│   │   ├── core/         # Core functionality
│   │   └── main.py       # FastAPI app entry point
│   └── requirements.txt
├── frontend/             # TypeScript CLI
│   ├── src/
│   │   ├── cli/         # CLI commands and interface
│   │   ├── types/       # TypeScript definitions
│   │   └── utils/       # Utility functions
│   └── package.json
└── shared/              # Shared types and schemas
```


```
backend/
├── agent/
│   ├── orchestrator.py      # Main agent loop
│   ├── planner.py           # Task decomposition
│   ├── context_manager.py   # Context window management
│   └── tool_executor.py     # Tool execution logic
├── tools/
│   ├── code_editor.py       # File read/write/edit
│   ├── code_analyzer.py     # Tree-sitter, AST analysis
│   ├── lsp_client.py        # LSP integration
│   ├── shell_executor.py    # Run commands
│   └── git_operations.py    # Git integration
├── llm/
│   ├── client.py            # Anthropic API client
│   ├── prompt_builder.py    # System prompts, context
│   └── streaming.py         # SSE handling
└── state/
    ├── session.py           # Session persistence
    └── history.py           # Conversation history
```

```
cli/
├── commands/
│   ├── init.ts              // Project initialization
│   ├── chat.ts              // Interactive mode
│   └── task.ts              // One-shot tasks
├── ui/
│   ├── renderer.ts          // Output formatting
│   ├── progress.ts          // Progress indicators
│   └── diff_viewer.ts       // Code diff display
├── ipc/
│   └── backend_client.ts    // Python backend communication
└── config/
    └── settings.ts          // User preferences
```

## Features

### Authentication System
- JWT-based authentication
- Secure token storage (keytar on supported platforms)
- API key management
- User profiles and session management

### CLI Interface
- Modern, interactive commands
- Beautiful terminal UI with colors and progress indicators
- Secure credential handling
- Configuration management

### Security Features
- Password hashing with bcrypt
- JWT tokens with expiration
- Secure token storage
- API key authentication for programmatic access

## Quick Start

### Backend Setup

1. **Create virtual environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment**:
```bash
cp ../.env.example .env
# Edit .env with your configuration
```

4. **Start the server**:
```bash
python -m src.main
# Server will run on http://localhost:8000
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Build the CLI**:
```bash
npm run build
```

3. **Link for global usage**:
```bash
npm link
```

4. **Use the CLI**:
```bash
klix-code --help
klix-code auth signup
klix-code auth signin
```

## Usage

### Authentication

**Sign up for a new account**:
```bash
klix-code auth signup
```

**Sign in**:
```bash
klix-code auth signin
```

**Check status**:
```bash
klix-code auth status
```

**Sign out**:
```bash
klix-code auth logout
```

### Configuration

**Set API URL**:
```bash
klix-code config --set-api-url http://your-server.com/api
```

**Show configuration**:
```bash
klix-code config --show
```

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
python -m src.main  # Starts with hot reload
```

### Frontend Development

```bash
cd frontend
npm run dev  # Runs TypeScript directly with ts-node
```

### API Documentation

When the backend is running, visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Environment Variables

Key environment variables (see `.env.example`):

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT signing secret
- `ANTHROPIC_API_KEY`: For AI integration
- `API_HOST/API_PORT`: Server configuration

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **JWT**: Authentication tokens
- **bcrypt**: Password hashing

### Frontend
- **TypeScript**: Type-safe JavaScript
- **Commander.js**: CLI framework
- **Inquirer.js**: Interactive prompts
- **Chalk**: Terminal colors
- **Keytar**: Secure credential storage

## Next Steps

This foundation provides:
1. ✅ Robust authentication system
2. ✅ Modern CLI interface
3. ✅ Secure token management
4. ✅ Configuration management
5. ✅ API documentation

**Coming next**:
- Tool implementation (file operations, search, git)
- AI model integration
- Agent system for complex tasks
- Real-time collaboration features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details