# Agentic Chat Assistant

An intelligent agentic chat assistant that routes different types of queries to specialized tools using React frontend and Python backend.

## 🚀 Features

- **Agentic System**: Intelligent query routing to appropriate tools
- **Real-time Communication**: WebSocket-based chat with progress indicators
- **Multiple Tools**: Text generation, code execution, web search, image generation, and more
- **Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- **Type Safety**: Full TypeScript support for better development experience
- **Scalable Architecture**: Modular design for easy tool addition and maintenance

## 🏗️ Architecture

### Backend (Python + FastAPI)
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **WebSocket Support**: Real-time bidirectional communication
- **Agentic System**: Intent classification and tool orchestration
- **Tool Registry**: Centralized management of available tools
- **OpenAI Integration**: GPT-based text generation and intent classification

### Frontend (React + TypeScript)
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type safety and better development experience
- **Tailwind CSS**: Utility-first CSS framework
- **Zustand**: Lightweight state management
- **Socket.IO**: Enhanced WebSocket communication

## 📁 Project Structure

```
/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── agents/         # Agent system and tool orchestration
│   │   │   ├── agent_orchestrator.py
│   │   │   ├── intent_classifier.py
│   │   │   └── tool_registry.py
│   │   ├── tools/          # Individual tool implementations
│   │   │   ├── base_tool.py
│   │   │   └── text_generation_tool.py
│   │   ├── models/         # Pydantic models and schemas
│   │   │   └── schemas.py
│   │   ├── core/           # Core configuration and utilities
│   │   │   └── config.py
│   │   └── api/            # API routes and WebSocket handlers
│   │       ├── routes.py
│   │       └── websocket_handler.py
│   ├── requirements.txt    # Python dependencies
│   ├── main.py            # Application entry point
│   └── .env.example       # Environment variables template
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── ProgressIndicator.tsx
│   │   ├── hooks/          # Custom React hooks
│   │   │   └── useChat.ts
│   │   ├── services/       # API and WebSocket services
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   ├── stores/         # State management
│   │   │   └── chatStore.ts
│   │   ├── types/          # TypeScript type definitions
│   │   │   └── index.ts
│   │   ├── App.tsx         # Main App component
│   │   ├── main.tsx        # React entry point
│   │   └── index.css       # Global styles
│   ├── package.json       # Node.js dependencies
│   ├── vite.config.ts     # Vite configuration
│   ├── tailwind.config.js # Tailwind CSS configuration
│   └── tsconfig.json      # TypeScript configuration
└── cline_docs/            # Project documentation
    ├── projectRoadmap.md
    ├── currentTask.md
    ├── techStack.md
    └── codebaseSummary.md
```

## 🛠️ Installation & Setup

### Option 1: Docker Compose (Recommended)

#### Prerequisites
- Docker
- Docker Compose

#### Quick Start
1. **Clone the repository and navigate to the project directory**

2. **Set up environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env file and add your OpenAI API key
   ```

3. **Run the entire system with one command:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`

5. **To stop the system:**
   ```bash
   docker-compose down
   ```

### Option 2: Manual Setup

#### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

#### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file and add your OpenAI API key
   ```

5. **Run the backend server:**
   ```bash
   python main.py
   ```

   The backend will be available at `http://localhost:8000`

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

   The frontend will be available at `http://localhost:5173`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Security
SECRET_KEY=your-secret-key-change-in-production

# API Configuration
API_V1_STR=/api/v1

# CORS Origins
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# OpenAI Model Configuration
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
```

## 🎯 Usage

1. **Start both servers** (backend and frontend)
2. **Open your browser** and navigate to `http://localhost:5173`
3. **Start chatting** with the agentic assistant
4. **Try different types of queries:**
   - "Write a poem about AI"
   - "Help me debug this Python code"
   - "Search for the latest news about technology"
   - "Generate an image of a sunset"

## 🔌 API Endpoints

### REST API
- `GET /api/v1/health` - Health check
- `GET /api/v1/tools` - Get available tools
- `POST /api/v1/chat` - Send chat message (REST fallback)
- `GET /api/v1/sessions/{session_id}/history` - Get conversation history
- `GET /api/v1/system/status` - Get system status

### WebSocket
- `WS /api/v1/ws/{connection_id}` - Real-time chat communication

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## 🧩 Adding New Tools

To add a new tool to the system:

1. **Create a new tool class** in `backend/app/tools/`:
   ```python
   from .base_tool import BaseTool
   from ..models.schemas import ToolResult, ToolStatus, ToolDefinition

   class MyNewTool(BaseTool):
       def __init__(self):
           super().__init__(
               name="my_new_tool",
               description="Description of what this tool does",
               category="utility"
           )
       
       async def execute(self, parameters):
           # Tool implementation
           return ToolResult(
               tool_name=self.name,
               status=ToolStatus.COMPLETED,
               result={"output": "Tool result"}
           )
       
       def get_definition(self):
           # Return tool definition
           pass
       
       def validate_parameters(self, parameters):
           # Validate parameters
           return True
   ```

2. **Register the tool** in `backend/app/agents/tool_registry.py`:
   ```python
   from ..tools.my_new_tool import MyNewTool
   
   def _initialize_default_tools(self):
       # Add your tool
       new_tool = MyNewTool()
       self.register_tool(new_tool)
   ```

3. **Update the intent classifier** to recognize queries for your tool

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm run test
```

## 📦 Building for Production

### Backend
```bash
cd backend
# Install production dependencies
pip install -r requirements.txt

# Run with production settings
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
# Serve the built files with a static server
npm run preview
```

## 🐛 Troubleshooting

### Common Issues

1. **WebSocket connection fails:**
   - Check if backend is running on port 8000
   - Verify CORS settings in backend configuration
   - Check browser console for error messages

2. **OpenAI API errors:**
   - Verify your API key is correct and has sufficient credits
   - Check rate limits and quotas
   - Ensure the model name is correct

3. **Frontend build errors:**
   - Clear node_modules and reinstall dependencies
   - Check TypeScript errors in the console
   - Verify all imports are correct

### Debug Mode

Enable debug mode by setting `DEBUG=true` in your `.env` file. This will:
- Show detailed error messages
- Enable request/response logging
- Display debug information in the UI

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- FastAPI team for the excellent web framework
- React team for the frontend framework
- All the open-source contributors who made this project possible

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Look through existing [GitHub issues](https://github.com/your-repo/issues)
3. Create a new issue with detailed information about your problem

---

**Built with ❤️ for the Synchrony Hackathon**
# sync-hkthon
