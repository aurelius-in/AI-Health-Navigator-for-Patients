"""
Base Agent class for AI Health Navigator.

This module defines the base class for all AI agents in the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

from ...core.config import get_settings
from ...core.logging import get_logger

logger = get_logger(__name__)


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class AgentPriority(str, Enum):
    """Agent priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentContext:
    """Context information for agent execution."""
    user_id: str
    session_id: str
    request_id: str
    timestamp: datetime
    metadata: Dict[str, Any]
    priority: AgentPriority = AgentPriority.NORMAL


@dataclass
class AgentResult:
    """Result from agent execution."""
    success: bool
    data: Dict[str, Any]
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]
    execution_time: float
    timestamp: datetime


class BaseAgent(ABC):
    """
    Base class for all AI agents in the system.
    
    This class provides common functionality for agent lifecycle management,
    error handling, logging, and result processing.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.settings = get_settings()
        self.logger = get_logger(f"agent.{name}")
        self.execution_history: List[AgentResult] = []
        self.error_count = 0
        self.success_count = 0
        self.total_execution_time = 0.0

    @abstractmethod
    async def execute(self, context: AgentContext, **kwargs) -> AgentResult:
        """
        Execute the agent's main logic.
        
        Args:
            context: Agent execution context
            **kwargs: Additional parameters specific to the agent
            
        Returns:
            AgentResult: The result of the agent's execution
        """
        pass

    @abstractmethod
    def validate_input(self, context: AgentContext, **kwargs) -> bool:
        """
        Validate input parameters for the agent.
        
        Args:
            context: Agent execution context
            **kwargs: Additional parameters to validate
            
        Returns:
            bool: True if input is valid, False otherwise
        """
        pass

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        """
        Run the agent with proper lifecycle management.
        
        Args:
            context: Agent execution context
            **kwargs: Additional parameters for the agent
            
        Returns:
            AgentResult: The result of the agent's execution
        """
        start_time = datetime.utcnow()
        
        try:
            # Validate input
            if not self.validate_input(context, **kwargs):
                raise ValueError(f"Invalid input for agent {self.name}")

            # Update status
            self.status = AgentStatus.RUNNING
            self.logger.info(f"Starting agent execution", extra={
                "agent": self.name,
                "user_id": context.user_id,
                "request_id": context.request_id,
                "priority": context.priority.value
            })

            # Execute agent logic
            result = await self.execute(context, **kwargs)
            
            # Update status and metrics
            self.status = AgentStatus.COMPLETED
            self.success_count += 1
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.total_execution_time += execution_time
            
            # Update result with execution time
            result.execution_time = execution_time
            result.timestamp = datetime.utcnow()
            
            # Store in history
            self.execution_history.append(result)
            
            self.logger.info(f"Agent execution completed successfully", extra={
                "agent": self.name,
                "user_id": context.user_id,
                "request_id": context.request_id,
                "execution_time": execution_time,
                "confidence": result.confidence
            })
            
            return result

        except Exception as e:
            # Handle errors
            self.status = AgentStatus.FAILED
            self.error_count += 1
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.error(f"Agent execution failed", extra={
                "agent": self.name,
                "user_id": context.user_id,
                "request_id": context.request_id,
                "error": str(e),
                "execution_time": execution_time
            })
            
            # Return error result
            return AgentResult(
                success=False,
                data={"error": str(e)},
                confidence=0.0,
                reasoning=f"Agent execution failed: {str(e)}",
                metadata={"error_type": type(e).__name__},
                execution_time=execution_time,
                timestamp=datetime.utcnow()
            )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics.
        
        Returns:
            Dict containing agent statistics
        """
        return {
            "name": self.name,
            "status": self.status.value,
            "total_executions": len(self.execution_history),
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / max(1, len(self.execution_history)),
            "average_execution_time": self.total_execution_time / max(1, len(self.execution_history)),
            "last_execution": self.execution_history[-1].timestamp if self.execution_history else None
        }

    def reset_stats(self):
        """Reset agent statistics."""
        self.execution_history.clear()
        self.error_count = 0
        self.success_count = 0
        self.total_execution_time = 0.0
        self.status = AgentStatus.IDLE

    def can_handle(self, context: AgentContext, **kwargs) -> bool:
        """
        Check if this agent can handle the given context and parameters.
        
        Args:
            context: Agent execution context
            **kwargs: Additional parameters
            
        Returns:
            bool: True if agent can handle the request
        """
        return True

    async def preprocess(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """
        Preprocess input data before execution.
        
        Args:
            context: Agent execution context
            **kwargs: Additional parameters
            
        Returns:
            Dict: Preprocessed data
        """
        return kwargs

    async def postprocess(self, result: AgentResult, context: AgentContext) -> AgentResult:
        """
        Postprocess the result after execution.
        
        Args:
            result: The agent result
            context: Agent execution context
            
        Returns:
            AgentResult: Postprocessed result
        """
        return result

    def get_required_capabilities(self) -> List[str]:
        """
        Get list of capabilities required by this agent.
        
        Returns:
            List of capability strings
        """
        return []

    def get_provided_capabilities(self) -> List[str]:
        """
        Get list of capabilities provided by this agent.
        
        Returns:
            List of capability strings
        """
        return [self.name]
