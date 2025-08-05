from typing import Dict, Any, List, Optional, Callable
import asyncio
import time
import uuid
from ..models.schemas import (
    UserQuery, AgentResponse, ChatMessage, MessageContent, 
    ContentType, MessageType, ToolResult
)
from ..agents.intent_classifier import intent_classifier
from ..agents.tool_registry import tool_registry

class AgentOrchestrator:
    """Main orchestrator that coordinates intent classification and tool execution."""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.conversation_history: Dict[str, List[ChatMessage]] = {}
    
    async def process_query(
        self, 
        query: UserQuery, 
        progress_callback: Optional[Callable] = None
    ) -> AgentResponse:
        """Process a user query through the complete agentic pipeline."""
        start_time = time.time()
        session_id = query.session_id or str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        
        try:
            # Initialize session if needed
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "created_at": time.time(),
                    "message_count": 0
                }
                self.conversation_history[session_id] = []
            
            # Update session
            self.active_sessions[session_id]["message_count"] += 1
            
            # Add user message to history
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                type=MessageType.USER,
                content=[MessageContent(type=ContentType.TEXT, content=query.message)],
                session_id=session_id,
                user_id=query.user_id
            )
            self.conversation_history[session_id].append(user_message)
            
            # Report progress
            if progress_callback:
                await progress_callback("Analyzing your request...", 0.1)
            
            # Step 1: Classify intent
            conversation_history = self._get_conversation_context(session_id)
            classification = await intent_classifier.classify_with_history(
                query.message, 
                conversation_history
            )
            
            if progress_callback:
                await progress_callback(f"Intent classified: {classification.intent}", 0.3)
            
            # Step 2: Execute tools
            tool_results = []
            if classification.suggested_tools:
                if progress_callback:
                    await progress_callback("Executing tools...", 0.5)
                
                # Prepare tool execution requests
                tool_requests = []
                for tool_name in classification.suggested_tools:
                    if tool_name in classification.parameters:
                        tool_requests.append({
                            "tool_name": tool_name,
                            "parameters": classification.parameters[tool_name]
                        })
                
                # Execute tools
                if tool_requests:
                    tool_results = await tool_registry.execute_multiple_tools(tool_requests)
                
                if progress_callback:
                    await progress_callback("Processing results...", 0.8)
            
            # Step 3: Format response
            response_content = await self._format_response(
                classification, 
                tool_results, 
                query.message
            )
            
            # Create agent response
            agent_response = AgentResponse(
                message_id=message_id,
                response_type=MessageType.ASSISTANT,
                content=response_content,
                tools_used=classification.suggested_tools,
                processing_time=time.time() - start_time,
                session_id=session_id
            )
            
            # Add assistant message to history
            assistant_message = ChatMessage(
                id=message_id,
                type=MessageType.ASSISTANT,
                content=response_content,
                session_id=session_id,
                tool_results=tool_results
            )
            self.conversation_history[session_id].append(assistant_message)
            
            if progress_callback:
                await progress_callback("Response ready!", 1.0)
            
            return agent_response
            
        except Exception as e:
            # Handle errors gracefully
            error_content = [MessageContent(
                type=ContentType.ERROR,
                content=f"I encountered an error processing your request: {str(e)}",
                metadata={"error_type": type(e).__name__}
            )]
            
            return AgentResponse(
                message_id=message_id,
                response_type=MessageType.ERROR,
                content=error_content,
                processing_time=time.time() - start_time,
                session_id=session_id
            )
    
    async def _format_response(
        self, 
        classification, 
        tool_results: List[ToolResult], 
        original_query: str
    ) -> List[MessageContent]:
        """Format the final response based on tool results."""
        content_parts = []
        
        # If we have successful tool results, format them
        successful_results = [r for r in tool_results if r.status == "completed"]
        failed_results = [r for r in tool_results if r.status == "failed"]
        
        if successful_results:
            for result in successful_results:
                if result.tool_name == "text_generation" and result.result:
                    # Handle text generation results
                    generated_text = result.result.get("generated_text", "")
                    if generated_text:
                        content_parts.append(MessageContent(
                            type=ContentType.TEXT,
                            content=generated_text,
                            metadata={
                                "tool_used": result.tool_name,
                                "model": result.result.get("model_used"),
                                "tokens": result.result.get("tokens_used"),
                                "execution_time": result.execution_time
                            }
                        ))
                
                elif result.tool_name == "code_execution" and result.result:
                    # Handle code execution results
                    code_output = result.result.get("output", "")
                    content_parts.append(MessageContent(
                        type=ContentType.CODE,
                        content=code_output,
                        metadata={
                            "tool_used": result.tool_name,
                            "language": result.result.get("language"),
                            "execution_time": result.execution_time
                        }
                    ))
                
                elif result.tool_name == "image_generation" and result.result:
                    # Handle image generation results
                    image_url = result.result.get("image_url", "")
                    content_parts.append(MessageContent(
                        type=ContentType.IMAGE,
                        content={"url": image_url, "description": result.result.get("description", "")},
                        metadata={
                            "tool_used": result.tool_name,
                            "execution_time": result.execution_time
                        }
                    ))
                
                else:
                    # Handle other tool results generically
                    content_parts.append(MessageContent(
                        type=ContentType.DATA,
                        content=result.result or {},
                        metadata={
                            "tool_used": result.tool_name,
                            "execution_time": result.execution_time
                        }
                    ))
        
        # Handle failed results
        if failed_results:
            error_messages = []
            for result in failed_results:
                error_messages.append(f"Tool '{result.tool_name}' failed: {result.error}")
            
            content_parts.append(MessageContent(
                type=ContentType.ERROR,
                content="Some tools encountered errors:\n" + "\n".join(error_messages),
                metadata={"failed_tools": [r.tool_name for r in failed_results]}
            ))
        
        # If no successful results, provide a fallback response
        if not successful_results:
            fallback_content = self._generate_fallback_response(classification, original_query)
            content_parts.append(fallback_content)
        
        return content_parts
    
    def _generate_fallback_response(self, classification, original_query: str) -> MessageContent:
        """Generate a fallback response when tools fail."""
        fallback_responses = {
            "text_generation": f"I understand you're asking: '{original_query}'. I'd be happy to help, but I'm currently unable to generate a detailed response. Please try again or rephrase your question.",
            "code_generation": f"I see you need help with coding. While I can't execute code right now, I can suggest that you're looking for help with: '{original_query}'. Please try again later.",
            "web_search": f"You're looking for information about: '{original_query}'. I'm currently unable to search the web, but I recommend checking reliable sources for this information.",
            "image_generation": f"I understand you want to create an image related to: '{original_query}'. Image generation is currently unavailable, but I can help describe what such an image might look like.",
            "calculation": f"I see you need help with calculations: '{original_query}'. While my calculation tools are unavailable, you might want to use a calculator or math software.",
            "data_analysis": f"You're looking to analyze data related to: '{original_query}'. Data analysis tools are currently unavailable, but I can suggest general approaches to your analysis needs."
        }
        
        fallback_text = fallback_responses.get(
            classification.intent, 
            f"I received your message: '{original_query}'. I'm currently unable to process this request fully, but I'm here to help. Please try again or ask something else."
        )
        
        return MessageContent(
            type=ContentType.TEXT,
            content=fallback_text,
            metadata={"fallback": True, "original_intent": classification.intent}
        )
    
    def _get_conversation_context(self, session_id: str) -> List[Dict]:
        """Get conversation context for intent classification."""
        if session_id not in self.conversation_history:
            return []
        
        # Convert recent messages to simple dict format
        recent_messages = self.conversation_history[session_id][-5:]
        context = []
        
        for msg in recent_messages:
            context.append({
                "type": msg.type,
                "content": msg.content[0].content if msg.content else "",
                "timestamp": msg.timestamp.isoformat()
            })
        
        return context
    
    async def get_session_history(self, session_id: str) -> List[ChatMessage]:
        """Get conversation history for a session."""
        return self.conversation_history.get(session_id, [])
    
    def get_active_sessions(self) -> Dict[str, Dict]:
        """Get information about active sessions."""
        return self.active_sessions.copy()
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session's data."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
        return True
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session."""
        if session_id not in self.active_sessions:
            return {}
        
        session_data = self.active_sessions[session_id]
        history = self.conversation_history.get(session_id, [])
        
        return {
            "session_id": session_id,
            "created_at": session_data["created_at"],
            "message_count": session_data["message_count"],
            "conversation_length": len(history),
            "last_activity": history[-1].timestamp.isoformat() if history else None
        }

# Global agent orchestrator instance
agent_orchestrator = AgentOrchestrator()
