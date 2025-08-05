# Codebase Summary - Agentic Chat Assistant

## Project Structure Overview

```
/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── agents/         # Agent system and tool orchestration
│   │   ├── tools/          # Individual tool implementations
│   │   ├── models/         # Pydantic models and schemas
│   │   ├── core/           # Core configuration and utilities
│   │   └── api/            # API routes and WebSocket handlers
│   ├── requirements.txt    # Python dependencies
│   └── main.py            # Application entry point
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API and WebSocket services
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Utility functions
│   ├── package.json       # Node.js dependencies
│   └── vite.config.ts     # Vite configuration
└── cline_docs/            # Project documentation
```

## Key Components and Their Interactions

### Backend Components

#### Agent System (`backend/app/agents/`)
- **AgentOrchestrator**: Main coordinator that receives user queries and routes them to appropriate tools
- **IntentClassifier**: LLM-based system that analyzes user queries to determine intent and required tools
- **ToolRegistry**: Central registry that manages all available tools and their capabilities
- **ResponseStreamer**: Handles streaming responses back to the frontend via WebSocket

#### Tools (`backend/app/tools/`)
- **BaseTool**: Abstract base class defining the tool interface
- **TextGenerationTool**: Handles general text generation using OpenAI API
- **CodeExecutionTool**: Executes code in sandboxed environments
- **WebSearchTool**: Performs web searches and information retrieval
- **ImageGenerationTool**: Generates images using DALL-E or similar APIs
- **DataAnalysisTool**: Processes and analyzes data files
- **CalculatorTool**: Performs mathematical calculations

#### API Layer (`backend/app/api/`)
- **WebSocket Handler**: Manages real-time communication with frontend
- **REST Endpoints**: Traditional HTTP endpoints for configuration and health checks

### Frontend Components

#### Core Components (`frontend/src/components/`)
- **ChatInterface**: Main chat UI with message display and input
- **MessageBubble**: Individual message rendering with support for different content types
- **ToolExecutionIndicator**: Shows real-time tool execution status
- **ResponseRenderer**: Handles rendering of different response types (text, code, images, charts)

#### Services (`frontend/src/services/`)
- **WebSocketService**: Manages WebSocket connection and message handling
- **AgentService**: Handles communication with the agent system
- **StateManager**: Manages chat history and application state

## Data Flow

### Query Processing Flow
1. **User Input**: User types message in chat interface
2. **WebSocket Transmission**: Message sent to backend via WebSocket
3. **Intent Classification**: AgentOrchestrator uses IntentClassifier to analyze query
4. **Tool Selection**: Based on intent, appropriate tools are selected from ToolRegistry
5. **Tool Execution**: Selected tools execute asynchronously
6. **Response Streaming**: Results stream back to frontend in real-time
7. **UI Updates**: Frontend updates chat interface with streaming responses

### Tool Execution Flow
1. **Tool Invocation**: AgentOrchestrator invokes selected tools with parsed parameters
2. **Async Execution**: Tools execute independently with progress callbacks
3. **Result Aggregation**: Results are collected and formatted
4. **Error Handling**: Failures are caught and fallback mechanisms activated
5. **Response Delivery**: Final results delivered to user via WebSocket

## External Dependencies

### AI and ML Services
- **OpenAI API**: Primary LLM for text generation and intent classification
- **Alternative LLM APIs**: Fallback options for redundancy
- **Image Generation APIs**: DALL-E, Stable Diffusion, or similar services

### External APIs and Services
- **Web Search APIs**: Google Custom Search, Bing Search API
- **Weather APIs**: OpenWeatherMap or similar services
- **Code Execution**: Sandboxed execution environments
- **File Processing**: Libraries for PDF, CSV, Excel processing

### Infrastructure Dependencies
- **WebSocket**: Real-time communication protocol
- **HTTP Client Libraries**: For external API calls
- **Database**: Optional for conversation history (SQLite/PostgreSQL)

## Recent Significant Changes
- Initial project setup and documentation structure created
- Technology stack defined with focus on real-time communication
- Agentic architecture planned with tool registry pattern

## User Feedback Integration and Its Impact on Development
- No user feedback yet as development is in initial planning phase
- Architecture designed to be extensible for adding new tools based on user needs
- Real-time streaming responses planned to provide immediate feedback to users

## Development Status
- **Phase**: Initial setup and planning
- **Next Steps**: Begin implementation with Python backend structure
- **Priority**: Establish baseline functionality with one working tool before expanding
