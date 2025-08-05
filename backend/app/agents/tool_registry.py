from typing import Dict, List, Optional, Type
import asyncio
from ..tools.base_tool import BaseTool
from ..tools.text_generation_tool import TextGenerationTool
from ..models.schemas import ToolDefinition, ToolResult

class ToolRegistry:
    """Central registry for managing all available tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tool_categories: Dict[str, List[str]] = {}
        self._initialize_default_tools()
    
    def _initialize_default_tools(self):
        """Initialize the default set of tools."""
        # Add text generation tool
        text_tool = TextGenerationTool()
        self.register_tool(text_tool)
    
    def register_tool(self, tool: BaseTool) -> bool:
        """Register a new tool in the registry."""
        try:
            if tool.name in self._tools:
                print(f"Warning: Tool '{tool.name}' already exists. Overwriting.")
            
            self._tools[tool.name] = tool
            
            # Update category mapping
            if tool.category not in self._tool_categories:
                self._tool_categories[tool.category] = []
            
            if tool.name not in self._tool_categories[tool.category]:
                self._tool_categories[tool.category].append(tool.name)
            
            print(f"Tool '{tool.name}' registered successfully in category '{tool.category}'")
            return True
            
        except Exception as e:
            print(f"Failed to register tool '{tool.name}': {str(e)}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool from the registry."""
        if tool_name not in self._tools:
            return False
        
        tool = self._tools[tool_name]
        category = tool.category
        
        # Remove from tools dict
        del self._tools[tool_name]
        
        # Remove from category mapping
        if category in self._tool_categories:
            if tool_name in self._tool_categories[category]:
                self._tool_categories[category].remove(tool_name)
            
            # Remove empty categories
            if not self._tool_categories[category]:
                del self._tool_categories[category]
        
        print(f"Tool '{tool_name}' unregistered successfully")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def get_enabled_tools(self) -> Dict[str, BaseTool]:
        """Get all enabled tools."""
        return {name: tool for name, tool in self._tools.items() if tool.is_enabled()}
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """Get all tools in a specific category."""
        if category not in self._tool_categories:
            return []
        
        return [self._tools[tool_name] for tool_name in self._tool_categories[category] 
                if tool_name in self._tools and self._tools[tool_name].is_enabled()]
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """Get definitions for all enabled tools."""
        definitions = []
        for tool in self.get_enabled_tools().values():
            try:
                definitions.append(tool.get_definition())
            except Exception as e:
                print(f"Failed to get definition for tool '{tool.name}': {str(e)}")
        
        return definitions
    
    def get_categories(self) -> List[str]:
        """Get all available tool categories."""
        return list(self._tool_categories.keys())
    
    async def execute_tool(self, tool_name: str, parameters: Dict, progress_callback=None) -> ToolResult:
        """Execute a tool with given parameters."""
        tool = self.get_tool(tool_name)
        
        if not tool:
            return ToolResult(
                tool_name=tool_name,
                status="failed",
                error=f"Tool '{tool_name}' not found"
            )
        
        if not tool.is_enabled():
            return ToolResult(
                tool_name=tool_name,
                status="failed",
                error=f"Tool '{tool_name}' is disabled"
            )
        
        # Set progress callback if provided
        if progress_callback:
            tool.set_progress_callback(progress_callback)
        
        # Execute the tool safely
        return await tool._safe_execute(parameters)
    
    async def execute_multiple_tools(self, tool_requests: List[Dict]) -> List[ToolResult]:
        """Execute multiple tools concurrently."""
        tasks = []
        
        for request in tool_requests:
            tool_name = request.get("tool_name")
            parameters = request.get("parameters", {})
            
            if tool_name:
                task = self.execute_tool(tool_name, parameters)
                tasks.append(task)
        
        if not tasks:
            return []
        
        # Execute all tools concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                tool_name = tool_requests[i].get("tool_name", "unknown")
                processed_results.append(ToolResult(
                    tool_name=tool_name,
                    status="failed",
                    error=f"Tool execution exception: {str(result)}"
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def enable_tool(self, tool_name: str) -> bool:
        """Enable a specific tool."""
        tool = self.get_tool(tool_name)
        if tool:
            tool.enable()
            return True
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """Disable a specific tool."""
        tool = self.get_tool(tool_name)
        if tool:
            tool.disable()
            return True
        return False
    
    def get_tool_status(self) -> Dict[str, Dict]:
        """Get status information for all tools."""
        status = {}
        for name, tool in self._tools.items():
            status[name] = {
                "enabled": tool.is_enabled(),
                "category": tool.category,
                "description": tool.description
            }
        return status
    
    def search_tools(self, query: str) -> List[BaseTool]:
        """Search for tools by name or description."""
        query_lower = query.lower()
        matching_tools = []
        
        for tool in self.get_enabled_tools().values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower() or
                query_lower in tool.category.lower()):
                matching_tools.append(tool)
        
        return matching_tools

# Global tool registry instance
tool_registry = ToolRegistry()
