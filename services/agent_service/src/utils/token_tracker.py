import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from groq import Groq
from groq.types.chat import ChatCompletion


@dataclass
class TokenUsage:
    """Data class to store token usage information"""
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_estimate: Optional[float] = None

class TokenTracker:
    """Utility class to track LLM token usage across agents"""
    
    def __init__(self):
        self.usage_history: Dict[str, TokenUsage] = {}
    
    def track_completion(self, agent_name: str, response: ChatCompletion, model: str) -> TokenUsage:
        """Track token usage from a Groq completion response"""
        usage = response.usage
        
        token_usage = TokenUsage(
            model=model,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            total_tokens=usage.prompt_tokens + usage.completion_tokens
        )
        
        # Store with agent name as key
        self.usage_history[agent_name] = token_usage
        return token_usage
    
    def get_agent_usage(self, agent_name: str) -> Optional[TokenUsage]:
        """Get token usage for a specific agent"""
        return self.usage_history.get(agent_name)
    
    def get_all_usage(self) -> Dict[str, Dict[str, Any]]:
        """Get all token usage as dictionary"""
        return {agent: asdict(usage) for agent, usage in self.usage_history.items()}
    
    def reset(self):
        """Reset usage history"""
        self.usage_history.clear()

# Global token tracker instance
token_tracker = TokenTracker() 