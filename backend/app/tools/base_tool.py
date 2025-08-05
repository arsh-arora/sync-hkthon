from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
import asyncio
import time
from ..models.schemas import ToolResult, ToolStatus, ToolDefinition

class BaseTool(ABC):
    """Abstract base class for all agent tools."""
    
    def __init__(self, name: str, description: str, category: str = "general"):
        self.name = name
        self.description = description
        self.category = category
        self.enabled = True
        self._progress_callback: Optional[Callable] = None
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """Return the tool definition including parameters schema."""
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate that the provided parameters are correct."""
        pass
    
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """Set a callback function to report progress updates."""
        self._progress_callback = callback
    
    async def _report_progress(self, message: str, progress: float = 0.0):
        """Report progress to the callback if available."""
        if self._progress_callback:
            await asyncio.create_task(
                asyncio.coroutine(self._progress_callback)(message, progress)
            )
    
    async def _safe_execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Safely execute the tool with error handling and timing."""
        start_time = time.time()
        
        try:
            # Validate parameters
            if not self.validate_parameters(parameters):
                return ToolResult(
                    tool_name=self.name,
                    status=ToolStatus.FAILED,
                    error="Invalid parameters provided",
                    execution_time=time.time() - start_time
                )
            
            # Report start
            await self._report_progress(f"Starting {self.name}...", 0.0)
            
            # Execute the tool
            result = await self.execute(parameters)
            
            # Update execution time
            result.execution_time = time.time() - start_time
            
            # Report completion
            if result.status == ToolStatus.COMPLETED:
                await self._report_progress(f"{self.name} completed successfully", 1.0)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = f"Tool execution failed: {str(e)}"
            
            await self._report_progress(f"{self.name} failed: {str(e)}", 0.0)
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                error=error_message,
                execution_time=execution_time
            )
    
    def is_enabled(self) -> bool:
        """Check if the tool is enabled."""
        return self.enabled
    
    def enable(self):
        """Enable the tool."""
        self.enabled = True
    
    def disable(self):
        """Disable the tool."""
        self.enabled = False
    
    def get_required_parameters(self) -> List[str]:
        """Get list of required parameters."""
        definition = self.get_definition()
        return definition.required_params
    
    def __str__(self) -> str:
        return f"{self.name} ({self.category}): {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})>"
