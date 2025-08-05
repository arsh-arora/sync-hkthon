from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import uuid
from datetime import datetime

from ..models.schemas import HealthCheck, ToolDefinition, UserQuery, AgentResponse
from ..agents.tool_registry import tool_registry
from ..agents.agent_orchestrator import agent_orchestrator
from ..api.websocket_handler import websocket_handler
from ..core.config import settings

# Create API router
api_router = APIRouter()

@api_router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    # Check service status
    services = {
        "agent_orchestrator": "healthy",
        "tool_registry": "healthy",
        "intent_classifier": "healthy"
    }
    
    # Check OpenAI API availability
    if settings.OPENAI_API_KEY:
        services["openai_api"] = "configured"
    else:
        services["openai_api"] = "not_configured"
    
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.VERSION,
        services=services
    )

@api_router.get("/tools", response_model=List[ToolDefinition])
async def get_available_tools():
    """Get all available tools and their definitions."""
    try:
        return tool_registry.get_tool_definitions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tools: {str(e)}")

@api_router.get("/tools/{tool_name}")
async def get_tool_definition(tool_name: str):
    """Get definition for a specific tool."""
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    try:
        return tool.get_definition()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tool definition: {str(e)}")

@api_router.get("/tools/categories")
async def get_tool_categories():
    """Get all available tool categories."""
    try:
        categories = tool_registry.get_categories()
        category_info = {}
        
        for category in categories:
            tools = tool_registry.get_tools_by_category(category)
            category_info[category] = {
                "tool_count": len(tools),
                "tools": [tool.name for tool in tools]
            }
        
        return {
            "categories": categories,
            "details": category_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve categories: {str(e)}")

@api_router.post("/tools/{tool_name}/execute")
async def execute_tool(tool_name: str, parameters: Dict[str, Any]):
    """Execute a specific tool with given parameters."""
    try:
        result = await tool_registry.execute_tool(tool_name, parameters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@api_router.post("/chat", response_model=AgentResponse)
async def chat_endpoint(query: UserQuery):
    """Process a chat message through the agent system (REST endpoint)."""
    try:
        response = await agent_orchestrator.process_query(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@api_router.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session."""
    try:
        history = await agent_orchestrator.get_session_history(session_id)
        
        # Convert to serializable format
        history_data = []
        for message in history:
            history_data.append({
                "id": message.id,
                "type": message.type,
                "content": [content.dict() for content in message.content],
                "timestamp": message.timestamp.isoformat(),
                "tool_results": [result.dict() for result in message.tool_results] if message.tool_results else None
            })
        
        return {
            "session_id": session_id,
            "history": history_data,
            "message_count": len(history_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session history: {str(e)}")

@api_router.get("/sessions/{session_id}/stats")
async def get_session_stats(session_id: str):
    """Get statistics for a session."""
    try:
        stats = agent_orchestrator.get_session_stats(session_id)
        if not stats:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session stats: {str(e)}")

@api_router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a session's conversation history."""
    try:
        success = agent_orchestrator.clear_session(session_id)
        if success:
            return {"message": f"Session '{session_id}' cleared successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear session: {str(e)}")

@api_router.get("/sessions")
async def get_active_sessions():
    """Get information about all active sessions."""
    try:
        sessions = agent_orchestrator.get_active_sessions()
        return {
            "active_sessions": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions: {str(e)}")

@api_router.get("/system/status")
async def get_system_status():
    """Get detailed system status information."""
    try:
        # Get tool status
        tool_status = tool_registry.get_tool_status()
        
        # Get active sessions
        active_sessions = agent_orchestrator.get_active_sessions()
        
        # Get WebSocket connections
        from ..api.websocket_handler import manager
        connection_count = manager.get_connection_count()
        
        return {
            "system": {
                "status": "operational",
                "version": settings.VERSION,
                "debug_mode": settings.DEBUG
            },
            "tools": {
                "total_tools": len(tool_status),
                "enabled_tools": len([t for t in tool_status.values() if t["enabled"]]),
                "tool_status": tool_status
            },
            "sessions": {
                "active_sessions": len(active_sessions),
                "total_messages": sum(s.get("message_count", 0) for s in active_sessions.values())
            },
            "connections": {
                "websocket_connections": connection_count
            },
            "configuration": {
                "openai_configured": bool(settings.OPENAI_API_KEY),
                "cors_origins": settings.BACKEND_CORS_ORIGINS
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve system status: {str(e)}")

@api_router.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str):
    """WebSocket endpoint for real-time chat communication."""
    await websocket_handler.handle_connection(websocket, connection_id)

# Additional utility endpoints

@api_router.post("/tools/search")
async def search_tools(query: Dict[str, str]):
    """Search for tools by name or description."""
    search_query = query.get("query", "")
    if not search_query:
        raise HTTPException(status_code=400, detail="Search query is required")
    
    try:
        matching_tools = tool_registry.search_tools(search_query)
        return {
            "query": search_query,
            "results": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category,
                    "enabled": tool.is_enabled()
                }
                for tool in matching_tools
            ],
            "count": len(matching_tools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@api_router.post("/tools/{tool_name}/toggle")
async def toggle_tool(tool_name: str):
    """Enable or disable a specific tool."""
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    try:
        if tool.is_enabled():
            tool.disable()
            status = "disabled"
        else:
            tool.enable()
            status = "enabled"
        
        return {
            "tool_name": tool_name,
            "status": status,
            "message": f"Tool '{tool_name}' has been {status}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle tool: {str(e)}")

@api_router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "Agentic Chat Assistant API",
        "endpoints": {
            "health": "/health",
            "tools": "/tools",
            "chat": "/chat",
            "websocket": "/ws/{connection_id}",
            "documentation": "/docs"
        }
    }
