"""
Enhanced Agent Orchestrator with Advanced Coordination Capabilities.

This orchestrator manages advanced AI agents with memory sharing,
collaborative reasoning, and intelligent workflow management.
"""

from typing import Dict, Any, List, Optional, Type
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass
from enum import Enum
import uuid

from .enhanced_base_agent import EnhancedBaseAgent, AgentContext, AgentResult, AgentPriority, AgentMemoryType, MemoryItem
from .enhanced_symptom_agent import EnhancedSymptomAnalysisAgent
from ...core.logging import get_logger

logger = get_logger(__name__)


class CollaborationType(str, Enum):
    """Types of agent collaboration."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    ADAPTIVE = "adaptive"
    COLLABORATIVE = "collaborative"
    CONSENSUS = "consensus"


class WorkflowType(str, Enum):
    """Types of workflows."""
    DIAGNOSTIC = "diagnostic"
    TREATMENT = "treatment"
    PREVENTIVE = "preventive"
    EMERGENCY = "emergency"
    COMPREHENSIVE = "comprehensive"


@dataclass
class CollaborativeTask:
    """Task for collaborative agent execution."""
    task_id: str
    agent_type: Type[EnhancedBaseAgent]
    context: AgentContext
    parameters: Dict[str, Any]
    priority: AgentPriority
    dependencies: List[str] = None
    collaboration_requirements: List[str] = None
    memory_sharing: bool = True
    reasoning_sharing: bool = True
    timeout: float = 30.0


@dataclass
class CollaborationResult:
    """Result from collaborative agent execution."""
    success: bool
    results: Dict[str, AgentResult]
    collaboration_insights: Dict[str, Any]
    consensus_reached: bool
    workflow_id: str
    execution_time: float
    collaboration_type: CollaborationType
    memory_shared: List[MemoryItem]
    reasoning_chains: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: datetime


class EnhancedAgentOrchestrator:
    """
    Enhanced orchestrator for advanced AI agents with collaborative capabilities.
    
    This orchestrator provides:
    - Memory sharing between agents
    - Collaborative reasoning
    - Intelligent workflow management
    - Consensus building
    - Adaptive coordination
    - Cross-agent learning
    """

    def __init__(self):
        self.agents: Dict[str, EnhancedBaseAgent] = {}
        self.agent_registry: Dict[str, Type[EnhancedBaseAgent]] = {}
        self.shared_memory: Dict[str, MemoryItem] = {}
        self.collaboration_history: List[CollaborationResult] = []
        self.workflow_templates: Dict[str, Dict[str, Any]] = {}
        self.agent_relationships: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger(__name__)
        
        self._initialize_agent_registry()
        self._initialize_workflow_templates()

    def _initialize_agent_registry(self):
        """Initialize the registry of available enhanced agents."""
        self.agent_registry = {
            "enhanced_symptom_analysis": EnhancedSymptomAnalysisAgent,
            # Add other enhanced agents as they are implemented
            # "enhanced_medication_management": EnhancedMedicationManagementAgent,
            # "enhanced_preventive_care": EnhancedPreventiveCareAgent,
            # "enhanced_mental_health": EnhancedMentalHealthAgent,
        }

    def _initialize_workflow_templates(self):
        """Initialize workflow templates for different scenarios."""
        self.workflow_templates = {
            WorkflowType.DIAGNOSTIC: {
                "agents": ["enhanced_symptom_analysis"],
                "collaboration_type": CollaborationType.SEQUENTIAL,
                "memory_sharing": True,
                "reasoning_sharing": True,
                "timeout": 120.0
            },
            WorkflowType.COMPREHENSIVE: {
                "agents": ["enhanced_symptom_analysis", "enhanced_medication_management", "enhanced_preventive_care"],
                "collaboration_type": CollaborationType.COLLABORATIVE,
                "memory_sharing": True,
                "reasoning_sharing": True,
                "timeout": 300.0
            },
            WorkflowType.EMERGENCY: {
                "agents": ["enhanced_symptom_analysis"],
                "collaboration_type": CollaborationType.ADAPTIVE,
                "memory_sharing": True,
                "reasoning_sharing": False,  # Fast execution
                "timeout": 30.0
            }
        }

    async def initialize(self):
        """Initialize all registered enhanced agents."""
        try:
            for agent_name, agent_class in self.agent_registry.items():
                agent = agent_class()
                await agent.initialize()
                self.agents[agent_name] = agent
                self.logger.info(f"Initialized enhanced agent: {agent_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize enhanced agents: {e}")
            raise

    async def execute_collaborative_workflow(
        self,
        workflow_id: str,
        workflow_type: WorkflowType,
        context: AgentContext,
        parameters: Dict[str, Any],
        collaboration_type: Optional[CollaborationType] = None
    ) -> CollaborationResult:
        """
        Execute a collaborative workflow with multiple agents.
        
        Args:
            workflow_id: Unique identifier for the workflow
            workflow_type: Type of workflow to execute
            context: Agent execution context
            parameters: Parameters for the workflow
            collaboration_type: Override default collaboration type
            
        Returns:
            CollaborationResult: Results from the collaborative workflow
        """
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting collaborative workflow: {workflow_id}", extra={
                "workflow_id": workflow_id,
                "workflow_type": workflow_type.value,
                "collaboration_type": collaboration_type.value if collaboration_type else "default"
            })

            # Get workflow template
            template = self.workflow_templates.get(workflow_type.value, {})
            if not template:
                raise ValueError(f"Unknown workflow type: {workflow_type}")

            # Create collaborative tasks
            tasks = await self._create_collaborative_tasks(
                template, context, parameters, collaboration_type
            )

            # Execute based on collaboration type
            collab_type = collaboration_type or CollaborationType(template.get("collaboration_type", "sequential"))
            
            if collab_type == CollaborationType.SEQUENTIAL:
                results = await self._execute_sequential_collaboration(tasks, template)
            elif collab_type == CollaborationType.PARALLEL:
                results = await self._execute_parallel_collaboration(tasks, template)
            elif collab_type == CollaborationType.COLLABORATIVE:
                results = await self._execute_collaborative_workflow(tasks, template)
            elif collab_type == CollaborationType.CONSENSUS:
                results = await self._execute_consensus_workflow(tasks, template)
            elif collab_type == CollaborationType.ADAPTIVE:
                results = await self._execute_adaptive_workflow(tasks, template)
            else:
                raise ValueError(f"Unknown collaboration type: {collab_type}")

            # Share memories and reasoning
            shared_memories = await self._share_memories_between_agents(tasks, results, template)
            reasoning_chains = await self._share_reasoning_between_agents(tasks, results, template)

            # Build consensus if needed
            consensus_reached = await self._build_consensus(results, template)

            # Generate collaboration insights
            collaboration_insights = await self._generate_collaboration_insights(results, shared_memories, reasoning_chains)

            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = CollaborationResult(
                success=all(r.success for r in results.values()),
                results=results,
                collaboration_insights=collaboration_insights,
                consensus_reached=consensus_reached,
                workflow_id=workflow_id,
                execution_time=execution_time,
                collaboration_type=collab_type,
                memory_shared=shared_memories,
                reasoning_chains=reasoning_chains,
                metadata={
                    "workflow_type": workflow_type.value,
                    "agent_count": len(tasks),
                    "successful_agents": sum(1 for r in results.values() if r.success)
                },
                timestamp=datetime.utcnow()
            )

            # Store in history
            self.collaboration_history.append(result)
            
            self.logger.info(f"Collaborative workflow completed: {workflow_id}", extra={
                "workflow_id": workflow_id,
                "success": result.success,
                "execution_time": execution_time,
                "consensus_reached": consensus_reached
            })

            return result

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.error(f"Collaborative workflow failed: {workflow_id}", extra={
                "workflow_id": workflow_id,
                "error": str(e),
                "execution_time": execution_time
            })
            
            return CollaborationResult(
                success=False,
                results={},
                collaboration_insights={"error": str(e)},
                consensus_reached=False,
                workflow_id=workflow_id,
                execution_time=execution_time,
                collaboration_type=collaboration_type or CollaborationType.SEQUENTIAL,
                memory_shared=[],
                reasoning_chains=[],
                metadata={"error": str(e)},
                timestamp=datetime.utcnow()
            )

    async def _create_collaborative_tasks(
        self, template: Dict[str, Any], context: AgentContext, 
        parameters: Dict[str, Any], collaboration_type: Optional[CollaborationType]
    ) -> List[CollaborativeTask]:
        """Create collaborative tasks based on workflow template."""
        tasks = []
        agent_names = template.get("agents", [])
        
        for i, agent_name in enumerate(agent_names):
            agent_class = self.agent_registry.get(agent_name)
            if not agent_class:
                self.logger.warning(f"Agent not found: {agent_name}")
                continue
            
            # Determine dependencies based on collaboration type
            dependencies = []
            if collaboration_type == CollaborationType.SEQUENTIAL and i > 0:
                dependencies = [f"task_{i-1}"]
            
            # Determine collaboration requirements
            collaboration_requirements = []
            if template.get("memory_sharing", False):
                collaboration_requirements.append("memory_sharing")
            if template.get("reasoning_sharing", False):
                collaboration_requirements.append("reasoning_sharing")
            
            task = CollaborativeTask(
                task_id=f"task_{i}",
                agent_type=agent_class,
                context=context,
                parameters=parameters,
                priority=AgentPriority.HIGH if "emergency" in parameters else AgentPriority.NORMAL,
                dependencies=dependencies,
                collaboration_requirements=collaboration_requirements,
                memory_sharing=template.get("memory_sharing", False),
                reasoning_sharing=template.get("reasoning_sharing", False),
                timeout=template.get("timeout", 30.0)
            )
            tasks.append(task)
        
        return tasks

    async def _execute_sequential_collaboration(
        self, tasks: List[CollaborativeTask], template: Dict[str, Any]
    ) -> Dict[str, AgentResult]:
        """Execute tasks sequentially with memory sharing."""
        results = {}
        shared_context = {}
        
        for task in tasks:
            try:
                # Enhance parameters with shared context
                enhanced_parameters = self._enhance_parameters_with_context(task.parameters, shared_context)
                
                # Execute task
                agent = self._get_agent_for_task(task)
                result = await asyncio.wait_for(
                    agent.run(task.context, **enhanced_parameters),
                    timeout=task.timeout
                )
                
                results[task.task_id] = result
                
                # Update shared context with results
                if task.memory_sharing:
                    shared_context.update(self._extract_shared_context(result))
                
                # Check if we should continue based on result
                if not result.success and task.priority == AgentPriority.CRITICAL:
                    break
                    
            except asyncio.TimeoutError:
                self.logger.error(f"Task timeout: {task.task_id}")
                results[task.task_id] = self._create_timeout_result(task)
            except Exception as e:
                self.logger.error(f"Task failed: {task.task_id}", extra={"error": str(e)})
                results[task.task_id] = self._create_error_result(task, str(e))
        
        return results

    async def _execute_parallel_collaboration(
        self, tasks: List[CollaborativeTask], template: Dict[str, Any]
    ) -> Dict[str, AgentResult]:
        """Execute tasks in parallel with shared context."""
        async def execute_task(task: CollaborativeTask) -> tuple[str, AgentResult]:
            try:
                agent = self._get_agent_for_task(task)
                result = await asyncio.wait_for(
                    agent.run(task.context, **task.parameters),
                    timeout=task.timeout
                )
                return task.task_id, result
            except asyncio.TimeoutError:
                return task.task_id, self._create_timeout_result(task)
            except Exception as e:
                return task.task_id, self._create_error_result(task, str(e))

        # Execute all tasks concurrently
        task_coroutines = [execute_task(task) for task in tasks]
        results_list = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Convert to dictionary
        results = {}
        for result in results_list:
            if isinstance(result, tuple):
                task_id, agent_result = result
                results[task_id] = agent_result
            else:
                # Handle exceptions from gather
                self.logger.error(f"Task execution failed: {result}")
        
        return results

    async def _execute_collaborative_workflow(
        self, tasks: List[CollaborativeTask], template: Dict[str, Any]
    ) -> Dict[str, AgentResult]:
        """Execute tasks with full collaboration and memory sharing."""
        # First pass: Execute all tasks to gather initial results
        initial_results = await self._execute_parallel_collaboration(tasks, template)
        
        # Second pass: Share results and re-execute with enhanced context
        enhanced_results = {}
        shared_memories = []
        
        for task in tasks:
            try:
                # Gather shared memories from other agents
                other_memories = []
                for other_task in tasks:
                    if other_task.task_id != task.task_id:
                        other_result = initial_results.get(other_task.task_id)
                        if other_result and other_result.success:
                            other_memories.extend(self._extract_memories_from_result(other_result))
                
                # Enhance parameters with shared memories
                enhanced_parameters = task.parameters.copy()
                enhanced_parameters["shared_memories"] = other_memories
                enhanced_parameters["collaborative_context"] = self._build_collaborative_context(initial_results)
                
                # Re-execute with enhanced context
                agent = self._get_agent_for_task(task)
                result = await asyncio.wait_for(
                    agent.run(task.context, **enhanced_parameters),
                    timeout=task.timeout
                )
                
                enhanced_results[task.task_id] = result
                shared_memories.extend(self._extract_memories_from_result(result))
                
            except Exception as e:
                self.logger.error(f"Collaborative task failed: {task.task_id}", extra={"error": str(e)})
                enhanced_results[task.task_id] = self._create_error_result(task, str(e))
        
        return enhanced_results

    async def _execute_consensus_workflow(
        self, tasks: List[CollaborativeTask], template: Dict[str, Any]
    ) -> Dict[str, AgentResult]:
        """Execute tasks and build consensus among results."""
        # Execute all tasks
        results = await self._execute_parallel_collaboration(tasks, template)
        
        # Build consensus
        consensus_result = await self._build_consensus_among_agents(results, tasks)
        
        # Update all results with consensus information
        for task_id in results:
            if results[task_id].success:
                results[task_id].data["consensus"] = consensus_result
        
        return results

    async def _execute_adaptive_workflow(
        self, tasks: List[CollaborativeTask], template: Dict[str, Any]
    ) -> Dict[str, AgentResult]:
        """Execute tasks with adaptive coordination based on results."""
        results = {}
        active_tasks = tasks.copy()
        
        while active_tasks:
            # Execute current batch of tasks
            batch_results = await self._execute_parallel_collaboration(active_tasks, template)
            results.update(batch_results)
            
            # Analyze results and determine next steps
            next_tasks = await self._determine_next_tasks(active_tasks, batch_results, template)
            
            if not next_tasks:
                break
            
            # Update active tasks for next iteration
            active_tasks = next_tasks
        
        return results

    async def _share_memories_between_agents(
        self, tasks: List[CollaborativeTask], results: Dict[str, AgentResult], 
        template: Dict[str, Any]
    ) -> List[MemoryItem]:
        """Share memories between agents."""
        shared_memories = []
        
        if not template.get("memory_sharing", False):
            return shared_memories
        
        for task in tasks:
            result = results.get(task.task_id)
            if result and result.success:
                # Extract memories from agent
                agent = self._get_agent_for_task(task)
                agent_memories = self._extract_memories_from_agent(agent)
                
                # Filter relevant memories for sharing
                relevant_memories = self._filter_relevant_memories(agent_memories, task.context)
                shared_memories.extend(relevant_memories)
        
        # Store in shared memory
        for memory in shared_memories:
            self.shared_memory[memory.id] = memory
        
        return shared_memories

    async def _share_reasoning_between_agents(
        self, tasks: List[CollaborativeTask], results: Dict[str, AgentResult], 
        template: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Share reasoning chains between agents."""
        reasoning_chains = []
        
        if not template.get("reasoning_sharing", False):
            return reasoning_chains
        
        for task in tasks:
            result = results.get(task.task_id)
            if result and result.success:
                # Extract reasoning from agent
                agent = self._get_agent_for_task(task)
                agent_reasoning = self._extract_reasoning_from_agent(agent)
                
                reasoning_chains.extend(agent_reasoning)
        
        return reasoning_chains

    async def _build_consensus(self, results: Dict[str, AgentResult], template: Dict[str, Any]) -> bool:
        """Build consensus among agent results."""
        if not results:
            return False
        
        # Extract key decisions from results
        decisions = []
        for result in results.values():
            if result.success and result.data:
                decision = self._extract_decision_from_result(result)
                if decision:
                    decisions.append(decision)
        
        if not decisions:
            return False
        
        # Check for consensus
        consensus_threshold = template.get("consensus_threshold", 0.7)
        agreement_score = self._calculate_agreement_score(decisions)
        
        return agreement_score >= consensus_threshold

    async def _build_consensus_among_agents(
        self, results: Dict[str, AgentResult], tasks: List[CollaborativeTask]
    ) -> Dict[str, Any]:
        """Build detailed consensus among agents."""
        consensus_data = {
            "agreement_score": 0.0,
            "consensus_reached": False,
            "conflicting_views": [],
            "agreed_points": [],
            "recommendations": []
        }
        
        # Extract all recommendations and assessments
        all_recommendations = []
        all_assessments = []
        
        for result in results.values():
            if result.success and result.data:
                recommendations = result.data.get("recommendations", [])
                assessments = result.data.get("assessments", {})
                
                all_recommendations.extend(recommendations)
                all_assessments.append(assessments)
        
        # Analyze agreement
        if all_recommendations:
            agreement_score = self._analyze_recommendation_agreement(all_recommendations)
            consensus_data["agreement_score"] = agreement_score
            consensus_data["consensus_reached"] = agreement_score >= 0.7
        
        # Identify agreed and conflicting points
        if all_assessments:
            agreed_points, conflicting_points = self._analyze_assessment_agreement(all_assessments)
            consensus_data["agreed_points"] = agreed_points
            consensus_data["conflicting_views"] = conflicting_points
        
        # Generate consensus recommendations
        consensus_data["recommendations"] = self._generate_consensus_recommendations(
            all_recommendations, consensus_data["agreement_score"]
        )
        
        return consensus_data

    async def _generate_collaboration_insights(
        self, results: Dict[str, AgentResult], shared_memories: List[MemoryItem], 
        reasoning_chains: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate insights from the collaboration."""
        insights = {
            "collaboration_effectiveness": 0.0,
            "knowledge_gained": [],
            "patterns_discovered": [],
            "improvement_suggestions": [],
            "cross_agent_learning": []
        }
        
        # Calculate collaboration effectiveness
        success_rate = sum(1 for r in results.values() if r.success) / len(results) if results else 0.0
        memory_utilization = len(shared_memories) / max(1, len(results))
        reasoning_depth = len(reasoning_chains) / max(1, len(results))
        
        insights["collaboration_effectiveness"] = (success_rate * 0.4 + memory_utilization * 0.3 + reasoning_depth * 0.3)
        
        # Extract knowledge gained
        for result in results.values():
            if result.success and result.data:
                knowledge = self._extract_knowledge_from_result(result)
                insights["knowledge_gained"].extend(knowledge)
        
        # Identify patterns across agents
        insights["patterns_discovered"] = self._identify_cross_agent_patterns(results, shared_memories)
        
        # Generate improvement suggestions
        insights["improvement_suggestions"] = self._generate_improvement_suggestions(results, insights)
        
        # Identify cross-agent learning opportunities
        insights["cross_agent_learning"] = self._identify_learning_opportunities(results, shared_memories)
        
        return insights

    async def _determine_next_tasks(
        self, current_tasks: List[CollaborativeTask], results: Dict[str, AgentResult], 
        template: Dict[str, Any]
    ) -> List[CollaborativeTask]:
        """Determine next tasks based on current results."""
        next_tasks = []
        
        for task in current_tasks:
            result = results.get(task.task_id)
            if result and result.success:
                # Check if task suggests follow-up actions
                follow_up_actions = result.data.get("follow_up_actions", [])
                if follow_up_actions:
                    # Create new tasks for follow-up actions
                    for action in follow_up_actions:
                        new_task = self._create_follow_up_task(task, action, template)
                        next_tasks.append(new_task)
        
        return next_tasks

    # Helper methods
    def _get_agent_for_task(self, task: CollaborativeTask) -> EnhancedBaseAgent:
        """Get the appropriate agent instance for a task."""
        agent_name = task.agent_type.__name__.lower().replace('enhanced', '').replace('agent', '')
        
        if agent_name not in self.agents:
            raise ValueError(f"Agent not found: {agent_name}")
        
        return self.agents[agent_name]

    def _enhance_parameters_with_context(self, parameters: Dict[str, Any], shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance parameters with shared context."""
        enhanced = parameters.copy()
        enhanced["shared_context"] = shared_context
        return enhanced

    def _extract_shared_context(self, result: AgentResult) -> Dict[str, Any]:
        """Extract shared context from agent result."""
        if not result.success or not result.data:
            return {}
        
        return {
            "insights": result.data.get("insights", {}),
            "patterns": result.data.get("patterns", {}),
            "recommendations": result.data.get("recommendations", [])
        }

    def _extract_memories_from_result(self, result: AgentResult) -> List[MemoryItem]:
        """Extract memories from agent result."""
        if not result.success or not result.data:
            return []
        
        # This would extract memories from the result
        # For now, return empty list
        return []

    def _extract_memories_from_agent(self, agent: EnhancedBaseAgent) -> List[MemoryItem]:
        """Extract memories from an agent."""
        memories = []
        memories.extend(agent.episodic_memory)
        memories.extend(agent.short_term_memory)
        return memories

    def _filter_relevant_memories(self, memories: List[MemoryItem], context: AgentContext) -> List[MemoryItem]:
        """Filter memories relevant to the current context."""
        relevant = []
        for memory in memories:
            # Simple relevance check - could be more sophisticated
            if memory.importance > 0.5:
                relevant.append(memory)
        return relevant

    def _extract_reasoning_from_agent(self, agent: EnhancedBaseAgent) -> List[Dict[str, Any]]:
        """Extract reasoning chains from an agent."""
        return [{"agent": agent.name, "reasoning": step.reasoning_process} for step in agent.reasoning_history[-5:]]

    def _build_collaborative_context(self, results: Dict[str, AgentResult]) -> Dict[str, Any]:
        """Build collaborative context from results."""
        context = {
            "agent_count": len(results),
            "successful_agents": sum(1 for r in results.values() if r.success),
            "insights": {},
            "recommendations": []
        }
        
        for result in results.values():
            if result.success and result.data:
                context["insights"].update(result.data.get("insights", {}))
                context["recommendations"].extend(result.data.get("recommendations", []))
        
        return context

    def _extract_decision_from_result(self, result: AgentResult) -> Optional[Dict[str, Any]]:
        """Extract decision from agent result."""
        if not result.data:
            return None
        
        return {
            "decision": result.data.get("decision"),
            "confidence": result.confidence,
            "reasoning": result.reasoning
        }

    def _calculate_agreement_score(self, decisions: List[Dict[str, Any]]) -> float:
        """Calculate agreement score among decisions."""
        if not decisions:
            return 0.0
        
        # Simple agreement calculation
        # In practice, this would be more sophisticated
        return 0.8  # Placeholder

    def _analyze_recommendation_agreement(self, recommendations: List[str]) -> float:
        """Analyze agreement among recommendations."""
        if not recommendations:
            return 0.0
        
        # Simple analysis - count unique recommendations
        unique_recommendations = set(recommendations)
        agreement_score = 1.0 - (len(unique_recommendations) / len(recommendations))
        
        return agreement_score

    def _analyze_assessment_agreement(
        self, assessments: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Analyze agreement among assessments."""
        agreed_points = []
        conflicting_points = []
        
        # Simple analysis - in practice, this would be more sophisticated
        for assessment in assessments:
            if assessment.get("confidence", 0.0) > 0.8:
                agreed_points.append(assessment)
            else:
                conflicting_points.append(assessment)
        
        return agreed_points, conflicting_points

    def _generate_consensus_recommendations(self, recommendations: List[str], agreement_score: float) -> List[str]:
        """Generate consensus recommendations."""
        if agreement_score >= 0.8:
            # High agreement - return most common recommendations
            from collections import Counter
            counter = Counter(recommendations)
            return [rec for rec, count in counter.most_common(3)]
        else:
            # Low agreement - return all recommendations with confidence levels
            return [f"{rec} (confidence: {agreement_score:.2f})" for rec in set(recommendations)]

    def _extract_knowledge_from_result(self, result: AgentResult) -> List[Dict[str, Any]]:
        """Extract knowledge from agent result."""
        knowledge = []
        
        if result.data:
            # Extract patterns
            patterns = result.data.get("patterns", {})
            if patterns:
                knowledge.append({"type": "pattern", "content": patterns})
            
            # Extract insights
            insights = result.data.get("insights", {})
            if insights:
                knowledge.append({"type": "insight", "content": insights})
        
        return knowledge

    def _identify_cross_agent_patterns(
        self, results: Dict[str, AgentResult], shared_memories: List[MemoryItem]
    ) -> List[Dict[str, Any]]:
        """Identify patterns across agents."""
        patterns = []
        
        # Analyze patterns in results
        for result in results.values():
            if result.success and result.data:
                result_patterns = result.data.get("patterns", {})
                if result_patterns:
                    patterns.append({
                        "source": "agent_result",
                        "patterns": result_patterns
                    })
        
        # Analyze patterns in shared memories
        if shared_memories:
            memory_patterns = self._analyze_memory_patterns(shared_memories)
            patterns.append({
                "source": "shared_memories",
                "patterns": memory_patterns
            })
        
        return patterns

    def _analyze_memory_patterns(self, memories: List[MemoryItem]) -> Dict[str, Any]:
        """Analyze patterns in shared memories."""
        # Simple pattern analysis
        return {
            "memory_count": len(memories),
            "memory_types": list(set(m.memory_type.value for m in memories)),
            "importance_distribution": {
                "high": len([m for m in memories if m.importance > 0.7]),
                "medium": len([m for m in memories if 0.3 <= m.importance <= 0.7]),
                "low": len([m for m in memories if m.importance < 0.3])
            }
        }

    def _generate_improvement_suggestions(
        self, results: Dict[str, AgentResult], insights: Dict[str, Any]
    ) -> List[str]:
        """Generate improvement suggestions based on collaboration results."""
        suggestions = []
        
        effectiveness = insights.get("collaboration_effectiveness", 0.0)
        
        if effectiveness < 0.5:
            suggestions.append("Improve agent coordination and communication")
        if effectiveness < 0.7:
            suggestions.append("Enhance memory sharing mechanisms")
        if effectiveness < 0.8:
            suggestions.append("Optimize reasoning chain sharing")
        
        return suggestions

    def _identify_learning_opportunities(
        self, results: Dict[str, AgentResult], shared_memories: List[MemoryItem]
    ) -> List[Dict[str, Any]]:
        """Identify cross-agent learning opportunities."""
        opportunities = []
        
        # Analyze successful collaborations
        successful_results = [r for r in results.values() if r.success]
        if len(successful_results) > 1:
            opportunities.append({
                "type": "successful_collaboration",
                "description": f"{len(successful_results)} agents successfully collaborated",
                "learning_value": "high"
            })
        
        # Analyze shared memory utilization
        if shared_memories:
            opportunities.append({
                "type": "memory_sharing",
                "description": f"Shared {len(shared_memories)} memories between agents",
                "learning_value": "medium"
            })
        
        return opportunities

    def _create_follow_up_task(
        self, original_task: CollaborativeTask, action: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> CollaborativeTask:
        """Create a follow-up task based on an action."""
        return CollaborativeTask(
            task_id=f"{original_task.task_id}_followup_{uuid.uuid4().hex[:8]}",
            agent_type=original_task.agent_type,
            context=original_task.context,
            parameters=action.get("parameters", {}),
            priority=AgentPriority.NORMAL,
            dependencies=[original_task.task_id],
            collaboration_requirements=original_task.collaboration_requirements,
            memory_sharing=original_task.memory_sharing,
            reasoning_sharing=original_task.reasoning_sharing,
            timeout=template.get("timeout", 30.0)
        )

    def _create_timeout_result(self, task: CollaborativeTask) -> AgentResult:
        """Create a timeout result."""
        return AgentResult(
            success=False,
            data={"error": "Task timeout"},
            confidence=0.0,
            reasoning=f"Task {task.task_id} timed out after {task.timeout}s",
            metadata={"timeout": task.timeout},
            execution_time=task.timeout,
            timestamp=datetime.utcnow()
        )

    def _create_error_result(self, task: CollaborativeTask, error: str) -> AgentResult:
        """Create an error result."""
        return AgentResult(
            success=False,
            data={"error": error},
            confidence=0.0,
            reasoning=f"Task {task.task_id} failed: {error}",
            metadata={"error_type": "execution_error"},
            execution_time=0.0,
            timestamp=datetime.utcnow()
        )

    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Get statistics about collaborations."""
        if not self.collaboration_history:
            return {"total_collaborations": 0}
        
        total_collaborations = len(self.collaboration_history)
        successful_collaborations = sum(1 for c in self.collaboration_history if c.success)
        avg_execution_time = sum(c.execution_time for c in self.collaboration_history) / total_collaborations
        
        return {
            "total_collaborations": total_collaborations,
            "successful_collaborations": successful_collaborations,
            "success_rate": successful_collaborations / total_collaborations,
            "average_execution_time": avg_execution_time,
            "collaboration_types_used": list(set(c.collaboration_type.value for c in self.collaboration_history))
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all enhanced agents."""
        health_status = {
            "overall": "healthy",
            "agents": {},
            "collaboration_system": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for name, agent in self.agents.items():
            try:
                agent_stats = agent.get_stats()
                health_status["agents"][name] = {
                    "status": agent.status.value,
                    "success_rate": agent_stats.get("success_rate", 0.0),
                    "memory_count": len(agent.episodic_memory) + len(agent.short_term_memory),
                    "reasoning_count": len(agent.reasoning_history),
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
