from typing import Dict, Any
import openai
from ..tools.base_tool import BaseTool
from ..models.schemas import ToolResult, ToolStatus, ToolDefinition
from ..core.config import settings

class TextGenerationTool(BaseTool):
    """Tool for generating text using OpenAI's GPT models."""
    
    def __init__(self):
        super().__init__(
            name="text_generation",
            description="Generate text responses using AI language models",
            category="ai"
        )
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the OpenAI client."""
        if settings.OPENAI_API_KEY:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            print("Warning: OpenAI API key not configured")
            self.enabled = False
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute text generation."""
        if not self.client:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                error="OpenAI client not initialized - check API key"
            )
        
        try:
            prompt = parameters.get("prompt", "")
            max_tokens = parameters.get("max_tokens", settings.OPENAI_MAX_TOKENS)
            temperature = parameters.get("temperature", settings.OPENAI_TEMPERATURE)
            model = parameters.get("model", settings.OPENAI_MODEL)
            
            await self._report_progress("Generating text response...", 0.3)
            
            # Create the chat completion
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
            
            await self._report_progress("Processing response...", 0.8)
            
            # Extract the generated text
            generated_text = response.choices[0].message.content
            
            result_data = {
                "generated_text": generated_text,
                "model_used": model,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "finish_reason": response.choices[0].finish_reason
            }
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                result=result_data
            )
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                error=f"Text generation failed: {str(e)}"
            )
    
    def get_definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters={
                "prompt": {
                    "type": "string",
                    "description": "The text prompt to generate a response for"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum number of tokens to generate",
                    "default": settings.OPENAI_MAX_TOKENS,
                    "minimum": 1,
                    "maximum": 4000
                },
                "temperature": {
                    "type": "number",
                    "description": "Creativity level (0.0 to 1.0)",
                    "default": settings.OPENAI_TEMPERATURE,
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "model": {
                    "type": "string",
                    "description": "OpenAI model to use",
                    "default": settings.OPENAI_MODEL,
                    "enum": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
                }
            },
            required_params=["prompt"],
            category=self.category
        )
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate the provided parameters."""
        if not parameters.get("prompt"):
            return False
        
        # Validate optional parameters if provided
        max_tokens = parameters.get("max_tokens")
        if max_tokens is not None and (not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 4000):
            return False
        
        temperature = parameters.get("temperature")
        if temperature is not None and (not isinstance(temperature, (int, float)) or temperature < 0.0 or temperature > 1.0):
            return False
        
        model = parameters.get("model")
        if model is not None and model not in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]:
            return False
        
        return True
    
    async def generate_streaming_response(self, parameters: Dict[str, Any], callback):
        """Generate streaming text response."""
        if not self.client:
            await callback("error", "OpenAI client not initialized")
            return
        
        try:
            prompt = parameters.get("prompt", "")
            max_tokens = parameters.get("max_tokens", settings.OPENAI_MAX_TOKENS)
            temperature = parameters.get("temperature", settings.OPENAI_TEMPERATURE)
            model = parameters.get("model", settings.OPENAI_MODEL)
            
            # Create streaming completion
            stream = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    await callback("chunk", chunk.choices[0].delta.content)
            
            await callback("complete", "")
            
        except Exception as e:
            await callback("error", f"Streaming failed: {str(e)}")
