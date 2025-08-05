from typing import Dict, Any, List
import json
import openai
from ..models.schemas import IntentClassification
from ..core.config import settings
from ..agents.tool_registry import tool_registry

class IntentClassifier:
    """Classifies user intents and suggests appropriate tools."""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
        self._system_prompt = self._build_system_prompt()
    
    def _initialize_client(self):
        """Initialize the OpenAI client."""
        if settings.OPENAI_API_KEY:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            print("Warning: OpenAI API key not configured for intent classification")
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for intent classification."""
        # Get available tools
        tool_definitions = tool_registry.get_tool_definitions()
        
        tools_info = []
        for tool_def in tool_definitions:
            tools_info.append(f"- {tool_def.name}: {tool_def.description} (Category: {tool_def.category})")
        
        tools_list = "\n".join(tools_info) if tools_info else "- text_generation: Generate text responses using AI language models (Category: ai)"
        
        return f"""You are an intelligent intent classifier for an agentic chat assistant. Your job is to analyze user queries and determine:

1. The primary intent of the user
2. Which tools should be used to fulfill the request
3. What parameters should be passed to those tools

Available Tools:
{tools_list}

Intent Categories:
- text_generation: User wants text generated, questions answered, creative writing, explanations
- code_generation: User wants code written, programming help, technical solutions
- web_search: User needs current information, facts, news, or web-based research
- image_generation: User wants images created, visual content, artwork
- data_analysis: User has data to analyze, wants charts, statistics, or insights
- calculation: User needs mathematical calculations, conversions, or computations
- file_processing: User wants to process files, extract information, or convert formats
- general_chat: General conversation, greetings, casual chat

Response Format:
You must respond with a valid JSON object containing:
{{
    "intent": "primary_intent_category",
    "confidence": 0.0-1.0,
    "suggested_tools": ["tool1", "tool2"],
    "parameters": {{
        "tool1": {{"param1": "value1"}},
        "tool2": {{"param2": "value2"}}
    }},
    "reasoning": "Brief explanation of why these tools were selected"
}}

Rules:
1. Always suggest at least one tool
2. If unsure, default to text_generation tool
3. Confidence should reflect how certain you are about the classification
4. Parameters should match the tool's expected input format
5. For text generation, always include the user's query as the "prompt" parameter
"""
    
    async def classify_intent(self, user_query: str, context: Dict[str, Any] = None) -> IntentClassification:
        """Classify the user's intent and suggest appropriate tools."""
        if not self.client:
            # Fallback classification without OpenAI
            return self._fallback_classification(user_query)
        
        try:
            # Prepare the messages
            messages = [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": f"Classify this query: {user_query}"}
            ]
            
            # Add context if provided
            if context:
                context_str = f"Additional context: {json.dumps(context, indent=2)}"
                messages.append({"role": "user", "content": context_str})
            
            # Get classification from OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            classification_data = json.loads(response.choices[0].message.content)
            
            # Validate and create IntentClassification object
            return IntentClassification(
                intent=classification_data.get("intent", "text_generation"),
                confidence=float(classification_data.get("confidence", 0.5)),
                suggested_tools=classification_data.get("suggested_tools", ["text_generation"]),
                parameters=classification_data.get("parameters", {"text_generation": {"prompt": user_query}}),
                reasoning=classification_data.get("reasoning", "Default classification")
            )
            
        except Exception as e:
            print(f"Intent classification failed: {str(e)}")
            return self._fallback_classification(user_query)
    
    def _fallback_classification(self, user_query: str) -> IntentClassification:
        """Provide fallback classification when OpenAI is not available."""
        query_lower = user_query.lower()
        
        # Simple keyword-based classification
        if any(word in query_lower for word in ["code", "program", "function", "script", "debug"]):
            return IntentClassification(
                intent="code_generation",
                confidence=0.7,
                suggested_tools=["text_generation"],
                parameters={"text_generation": {"prompt": f"Help with coding: {user_query}"}},
                reasoning="Detected code-related keywords"
            )
        
        elif any(word in query_lower for word in ["search", "find", "what is", "current", "news", "latest"]):
            return IntentClassification(
                intent="web_search",
                confidence=0.6,
                suggested_tools=["text_generation"],
                parameters={"text_generation": {"prompt": f"Provide information about: {user_query}"}},
                reasoning="Detected search-related keywords"
            )
        
        elif any(word in query_lower for word in ["image", "picture", "draw", "create visual", "generate image"]):
            return IntentClassification(
                intent="image_generation",
                confidence=0.8,
                suggested_tools=["text_generation"],
                parameters={"text_generation": {"prompt": f"Describe image generation request: {user_query}"}},
                reasoning="Detected image-related keywords"
            )
        
        elif any(word in query_lower for word in ["calculate", "math", "compute", "solve", "equation"]):
            return IntentClassification(
                intent="calculation",
                confidence=0.7,
                suggested_tools=["text_generation"],
                parameters={"text_generation": {"prompt": f"Help with calculation: {user_query}"}},
                reasoning="Detected calculation-related keywords"
            )
        
        else:
            # Default to text generation
            return IntentClassification(
                intent="text_generation",
                confidence=0.5,
                suggested_tools=["text_generation"],
                parameters={"text_generation": {"prompt": user_query}},
                reasoning="Default classification for general text generation"
            )
    
    async def classify_with_history(self, user_query: str, conversation_history: List[Dict] = None) -> IntentClassification:
        """Classify intent with conversation history for better context."""
        context = {}
        
        if conversation_history:
            # Extract relevant context from conversation history
            recent_messages = conversation_history[-5:]  # Last 5 messages
            context["recent_conversation"] = recent_messages
            
            # Check if user is continuing a previous topic
            if len(recent_messages) > 0:
                last_message = recent_messages[-1]
                if last_message.get("type") == "assistant":
                    context["last_assistant_response"] = last_message.get("content", "")
        
        return await self.classify_intent(user_query, context)
    
    def get_available_intents(self) -> List[str]:
        """Get list of available intent categories."""
        return [
            "text_generation",
            "code_generation", 
            "web_search",
            "image_generation",
            "data_analysis",
            "calculation",
            "file_processing",
            "general_chat"
        ]
    
    def update_system_prompt(self):
        """Update the system prompt with current tool definitions."""
        self._system_prompt = self._build_system_prompt()

# Global intent classifier instance
intent_classifier = IntentClassifier()
