"""
Agent Orchestrator for AI Health Navigator.

This module orchestrates multiple AI agents to provide comprehensive
healthcare assistance and decision-making.
"""

from typing import Dict, Any, List, Optional, Type
from datetime import datetime
import asyncio
from dataclasses import dataclass
from enum import Enum

from .base_agent import BaseAgent, AgentContext, AgentResult, AgentPriority
from .symptom_agent import SymptomAnalysisAgent
from .medication_agent import MedicationManagementAgent
from .preventive_care_agent import PreventiveCareAgent
from .mental_health_agent import MentalHealthAgent
from ...core.logging import get_logger

logger = get_logger(__name__)


class OrchestrationStrategy(str, Enum):
    """Orchestration strategies for agent coordination."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    ADAPTIVE = "adaptive"


@dataclass
class AgentTask:
    """Task definition for agent execution."""
    agent_type: Type[BaseAgent]
    context: AgentContext
    parameters: Dict[str, Any]
    priority: AgentPriority
    dependencies: List[str] = None
    timeout: float = 30.0


@dataclass
class OrchestrationResult:
    """Result from agent orchestration."""
    success: bool
    results: Dict[str, AgentResult]
    workflow_id: str
    execution_time: float
    strategy_used: OrchestrationStrategy
    metadata: Dict[str, Any]
    timestamp: datetime


class AgentOrchestrator:
    """
    Orchestrates multiple AI agents for comprehensive healthcare assistance.
    
    This class manages agent lifecycle, coordinates execution strategies,
    and provides intelligent routing of requests to appropriate agents.
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_registry: Dict[str, Type[BaseAgent]] = {}
        self.workflow_history: List[OrchestrationResult] = []
        self.logger = get_logger(__name__)
        self._initialize_agent_registry()

    def _initialize_agent_registry(self):
        """Initialize the registry of available agents."""
        self.agent_registry = {
            "symptom_analysis": SymptomAnalysisAgent,
            "medication_management": MedicationManagementAgent,
            "preventive_care": PreventiveCareAgent,
            "mental_health": MentalHealthAgent,
            # Add other agents as they are implemented
            # "triage_assessment": TriageAssessmentAgent,
            # "provider_matching": ProviderMatchingAgent,
            # "health_coach": HealthCoachAgent,
            # "emergency_response": EmergencyResponseAgent,
        }

    async def initialize(self):
        """Initialize all registered agents."""
        try:
            for agent_name, agent_class in self.agent_registry.items():
                agent = agent_class()
                if hasattr(agent, 'initialize'):
                    await agent.initialize()
                self.agents[agent_name] = agent
                self.logger.info(f"Initialized agent: {agent_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise

    async def execute_workflow(
        self,
        workflow_id: str,
        tasks: List[AgentTask],
        strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE,
        timeout: float = 300.0
    ) -> OrchestrationResult:
        """
        Execute a workflow of agent tasks.
        
        Args:
            workflow_id: Unique identifier for the workflow
            tasks: List of tasks to execute
            strategy: Orchestration strategy to use
            timeout: Overall timeout for the workflow
            
        Returns:
            OrchestrationResult: Results from the workflow execution
        """
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting workflow: {workflow_id}", extra={
                "workflow_id": workflow_id,
                "task_count": len(tasks),
                "strategy": strategy.value
            })

            # Execute based on strategy
            if strategy == OrchestrationStrategy.SEQUENTIAL:
                results = await self._execute_sequential(tasks, timeout)
            elif strategy == OrchestrationStrategy.PARALLEL:
                results = await self._execute_parallel(tasks, timeout)
            elif strategy == OrchestrationStrategy.HIERARCHICAL:
                results = await self._execute_hierarchical(tasks, timeout)
            elif strategy == OrchestrationStrategy.ADAPTIVE:
                results = await self._execute_adaptive(tasks, timeout)
            else:
                raise ValueError(f"Unknown orchestration strategy: {strategy}")

            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = OrchestrationResult(
                success=all(r.success for r in results.values()),
                results=results,
                workflow_id=workflow_id,
                execution_time=execution_time,
                strategy_used=strategy,
                metadata={
                    "task_count": len(tasks),
                    "successful_tasks": sum(1 for r in results.values() if r.success),
                    "failed_tasks": sum(1 for r in results.values() if not r.success)
                },
                timestamp=datetime.utcnow()
            )

            # Store in history
            self.workflow_history.append(result)
            
            self.logger.info(f"Workflow completed: {workflow_id}", extra={
                "workflow_id": workflow_id,
                "success": result.success,
                "execution_time": execution_time,
                "successful_tasks": result.metadata["successful_tasks"]
            })

            return result

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.error(f"Workflow failed: {workflow_id}", extra={
                "workflow_id": workflow_id,
                "error": str(e),
                "execution_time": execution_time
            })
            
            return OrchestrationResult(
                success=False,
                results={},
                workflow_id=workflow_id,
                execution_time=execution_time,
                strategy_used=strategy,
                metadata={"error": str(e)},
                timestamp=datetime.utcnow()
            )

    async def _execute_sequential(self, tasks: List[AgentTask], timeout: float) -> Dict[str, AgentResult]:
        """Execute tasks sequentially."""
        results = {}
        
        for task in tasks:
            try:
                agent = self._get_agent_for_task(task)
                result = await asyncio.wait_for(
                    agent.run(task.context, **task.parameters),
                    timeout=task.timeout
                )
                results[task.agent_type.__name__] = result
                
                # Check if we should continue based on result
                if not result.success and task.priority == AgentPriority.CRITICAL:
                    break
                    
            except asyncio.TimeoutError:
                self.logger.error(f"Task timeout: {task.agent_type.__name__}")
                results[task.agent_type.__name__] = self._create_timeout_result(task)
            except Exception as e:
                self.logger.error(f"Task failed: {task.agent_type.__name__}", extra={"error": str(e)})
                results[task.agent_type.__name__] = self._create_error_result(task, str(e))
        
        return results

    async def _execute_parallel(self, tasks: List[AgentTask], timeout: float) -> Dict[str, AgentResult]:
        """Execute tasks in parallel."""
        async def execute_task(task: AgentTask) -> tuple[str, AgentResult]:
            try:
                agent = self._get_agent_for_task(task)
                result = await asyncio.wait_for(
                    agent.run(task.context, **task.parameters),
                    timeout=task.timeout
                )
                return task.agent_type.__name__, result
            except asyncio.TimeoutError:
                return task.agent_type.__name__, self._create_timeout_result(task)
            except Exception as e:
                return task.agent_type.__name__, self._create_error_result(task, str(e))

        # Execute all tasks concurrently
        task_coroutines = [execute_task(task) for task in tasks]
        results_list = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Convert to dictionary
        results = {}
        for result in results_list:
            if isinstance(result, tuple):
                agent_name, agent_result = result
                results[agent_name] = agent_result
            else:
                # Handle exceptions from gather
                self.logger.error(f"Task execution failed: {result}")
        
        return results

    async def _execute_hierarchical(self, tasks: List[AgentTask], timeout: float) -> Dict[str, AgentResult]:
        """Execute tasks in hierarchical order based on dependencies."""
        # Build dependency graph
        task_graph = self._build_dependency_graph(tasks)
        
        # Execute in topological order
        results = {}
        executed = set()
        
        while len(executed) < len(tasks):
            # Find tasks that can be executed (all dependencies satisfied)
            ready_tasks = []
            for task in tasks:
                if task.agent_type.__name__ not in executed:
                    dependencies = task_graph.get(task.agent_type.__name__, [])
                    if all(dep in executed for dep in dependencies):
                        ready_tasks.append(task)
            
            if not ready_tasks:
                # Circular dependency or missing tasks
                break
            
            # Execute ready tasks in parallel
            task_coroutines = []
            for task in ready_tasks:
                task_coroutines.append(self._execute_single_task(task))
            
            batch_results = await asyncio.gather(*task_coroutines, return_exceptions=True)
            
            for i, result in enumerate(batch_results):
                if isinstance(result, AgentResult):
                    results[ready_tasks[i].agent_type.__name__] = result
                    executed.add(ready_tasks[i].agent_type.__name__)
        
        return results

    async def _execute_adaptive(self, tasks: List[AgentTask], timeout: float) -> Dict[str, AgentResult]:
        """Execute tasks using adaptive strategy based on context and priorities."""
        # Sort tasks by priority
        sorted_tasks = sorted(tasks, key=lambda t: self._priority_score(t.priority), reverse=True)
        
        # Group tasks by priority
        priority_groups = {}
        for task in sorted_tasks:
            priority = task.priority.value
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(task)
        
        results = {}
        
        # Execute critical tasks first (sequential for safety)
        if AgentPriority.CRITICAL.value in priority_groups:
            critical_results = await self._execute_sequential(
                priority_groups[AgentPriority.CRITICAL.value], 
                timeout * 0.5  # Use half timeout for critical tasks
            )
            results.update(critical_results)
            
            # Check if we should continue
            if not all(r.success for r in critical_results.values()):
                return results
        
        # Execute remaining tasks in parallel
        remaining_tasks = []
        for priority in [AgentPriority.HIGH.value, AgentPriority.NORMAL.value, AgentPriority.LOW.value]:
            if priority in priority_groups:
                remaining_tasks.extend(priority_groups[priority])
        
        if remaining_tasks:
            remaining_results = await self._execute_parallel(remaining_tasks, timeout * 0.5)
            results.update(remaining_results)
        
        return results

    def _get_agent_for_task(self, task: AgentTask) -> BaseAgent:
        """Get the appropriate agent instance for a task."""
        agent_name = task.agent_type.__name__.lower().replace('agent', '')
        
        if agent_name not in self.agents:
            raise ValueError(f"Agent not found: {agent_name}")
        
        return self.agents[agent_name]

    def _build_dependency_graph(self, tasks: List[AgentTask]) -> Dict[str, List[str]]:
        """Build dependency graph for tasks."""
        graph = {}
        
        for task in tasks:
            if task.dependencies:
                graph[task.agent_type.__name__] = task.dependencies
            else:
                graph[task.agent_type.__name__] = []
        
        return graph

    def _priority_score(self, priority: AgentPriority) -> int:
        """Convert priority to numeric score for sorting."""
        scores = {
            AgentPriority.CRITICAL: 4,
            AgentPriority.HIGH: 3,
            AgentPriority.NORMAL: 2,
            AgentPriority.LOW: 1
        }
        return scores.get(priority, 0)

    async def _execute_single_task(self, task: AgentTask) -> AgentResult:
        """Execute a single task."""
        try:
            agent = self._get_agent_for_task(task)
            return await agent.run(task.context, **task.parameters)
        except Exception as e:
            return self._create_error_result(task, str(e))

    def _create_timeout_result(self, task: AgentTask) -> AgentResult:
        """Create a timeout result."""
        return AgentResult(
            success=False,
            data={"error": "Task timeout"},
            confidence=0.0,
            reasoning=f"Task {task.agent_type.__name__} timed out after {task.timeout}s",
            metadata={"timeout": task.timeout},
            execution_time=task.timeout,
            timestamp=datetime.utcnow()
        )

    def _create_error_result(self, task: AgentTask, error: str) -> AgentResult:
        """Create an error result."""
        return AgentResult(
            success=False,
            data={"error": error},
            confidence=0.0,
            reasoning=f"Task {task.agent_type.__name__} failed: {error}",
            metadata={"error_type": "execution_error"},
            execution_time=0.0,
            timestamp=datetime.utcnow()
        )

    async def route_request(self, context: AgentContext, request_data: Dict[str, Any]) -> List[AgentTask]:
        """
        Intelligently route a request to appropriate agents.
        
        Args:
            context: Request context
            request_data: Request data
            
        Returns:
            List of tasks to execute
        """
        tasks = []
        
        # Analyze request to determine required agents
        if "symptoms" in request_data:
            tasks.append(AgentTask(
                agent_type=SymptomAnalysisAgent,
                context=context,
                parameters=request_data,
                priority=AgentPriority.HIGH if request_data.get("severity") == "severe" else AgentPriority.NORMAL
            ))
        
        # Medication management
        if "medications" in request_data:
            tasks.append(AgentTask(
                agent_type=MedicationManagementAgent,
                context=context,
                parameters=request_data,
                priority=AgentPriority.HIGH if request_data.get("risk_level") == "critical" else AgentPriority.NORMAL
            ))
        
        # Preventive care planning
        if "age" in request_data and "gender" in request_data:
            tasks.append(AgentTask(
                agent_type=PreventiveCareAgent,
                context=context,
                parameters=request_data,
                priority=AgentPriority.NORMAL
            ))
        
        # Mental health support
        if "mood_assessment" in request_data or "crisis_indicators" in request_data:
            tasks.append(AgentTask(
                agent_type=MentalHealthAgent,
                context=context,
                parameters=request_data,
                priority=AgentPriority.CRITICAL if request_data.get("crisis_risk") == "high" else AgentPriority.HIGH
            ))
        
        # Add more routing logic for other agent types
        # if "triage" in request_data:
        #     tasks.append(AgentTask(...))
        
        return tasks

    def get_agent_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all agents."""
        stats = {}
        for name, agent in self.agents.items():
            stats[name] = agent.get_stats()
        return stats

    def get_workflow_history(self, limit: int = 100) -> List[OrchestrationResult]:
        """Get recent workflow history."""
        return self.workflow_history[-limit:]

    def register_agent(self, name: str, agent_class: Type[BaseAgent]):
        """Register a new agent type."""
        self.agent_registry[name] = agent_class
        self.logger.info(f"Registered agent: {name}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents."""
        health_status = {
            "overall": "healthy",
            "agents": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for name, agent in self.agents.items():
            try:
                agent_stats = agent.get_stats()
                health_status["agents"][name] = {
                    "status": agent.status.value,
                    "success_rate": agent_stats.get("success_rate", 0.0),
                    "last_execution": agent_stats.get("last_execution"),
                    "healthy": agent.status.value != "failed"
                }
            except Exception as e:
                health_status["agents"][name] = {
                    "status": "error",
                    "error": str(e),
                    "healthy": False
                }
        
        # Check overall health
        unhealthy_agents = sum(1 for agent in health_status["agents"].values() if not agent["healthy"])
        if unhealthy_agents > 0:
            health_status["overall"] = "degraded"
        if unhealthy_agents == len(self.agents):
            health_status["overall"] = "unhealthy"
        
        return health_status
