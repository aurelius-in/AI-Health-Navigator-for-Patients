"""
Enhanced Agent API routes for AI Health Navigator.

This module provides endpoints for the enhanced agentic AI system with
advanced capabilities including memory sharing, collaborative reasoning,
and autonomous decision-making.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ...ai.agents.enhanced_agent_orchestrator import (
    EnhancedAgentOrchestrator, CollaborationType, WorkflowType, 
    CollaborativeTask, CollaborationResult
)
from ...ai.agents.enhanced_base_agent import AgentContext, AgentPriority
from ...core.logging import get_logger
from ...database import get_db_session

logger = get_logger(__name__)
router = APIRouter(prefix="/enhanced-agents", tags=["enhanced-agents"])

# Global enhanced orchestrator instance
enhanced_orchestrator = EnhancedAgentOrchestrator()


class EnhancedAgentExecutionRequest(BaseModel):
    """Request model for enhanced agent execution."""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    workflow_type: WorkflowType = Field(..., description="Type of workflow to execute")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the workflow")
    collaboration_type: Optional[CollaborationType] = Field(None, description="Collaboration type override")
    enable_memory_sharing: bool = Field(True, description="Enable memory sharing between agents")
    enable_reasoning_sharing: bool = Field(True, description="Enable reasoning sharing between agents")
    autonomy_level: float = Field(0.7, description="Autonomy level (0.0-1.0)")


class EnhancedAgentStatsResponse(BaseModel):
    """Response model for enhanced agent statistics."""
    agent_name: str
    status: str
    memory_count: int
    reasoning_count: int
    learning_outcomes: int
    autonomy_level: float
    collaboration_count: int
    success_rate: float


class CollaborationInsightsResponse(BaseModel):
    """Response model for collaboration insights."""
    collaboration_effectiveness: float
    knowledge_gained: List[Dict[str, Any]]
    patterns_discovered: List[Dict[str, Any]]
    improvement_suggestions: List[str]
    cross_agent_learning: List[Dict[str, Any]]
    consensus_reached: bool
    memory_shared_count: int
    reasoning_chains_count: int


class AdvancedSymptomAnalysisRequest(BaseModel):
    """Request model for advanced symptom analysis with agentic AI."""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    symptoms: List[str] = Field(..., description="List of symptoms")
    severity: str = Field(..., description="Symptom severity")
    duration: str = Field(..., description="Symptom duration")
    additional_context: Dict[str, Any] = Field({}, description="Additional context")
    enable_autonomous_decision_making: bool = Field(True, description="Enable autonomous decisions")
    enable_memory_integration: bool = Field(True, description="Enable memory integration")
    enable_cross_agent_collaboration: bool = Field(True, description="Enable cross-agent collaboration")


@router.on_event("startup")
async def startup_event():
    """Initialize the enhanced agent orchestrator on startup."""
    try:
        await enhanced_orchestrator.initialize()
        logger.info("Enhanced agent orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize enhanced agent orchestrator: {e}")
        raise


@router.post("/execute-collaborative-workflow")
async def execute_collaborative_workflow(request: EnhancedAgentExecutionRequest):
    """
    Execute a collaborative workflow with enhanced agentic AI capabilities.
    
    This endpoint demonstrates advanced features like:
    - Memory sharing between agents
    - Collaborative reasoning
    - Autonomous decision-making
    - Cross-agent learning
    - Consensus building
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=request.user_id,
            session_id=request.session_id,
            request_id=f"enhanced_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            metadata={
                "source": "enhanced_api",
                "autonomy_level": request.autonomy_level,
                "memory_sharing": request.enable_memory_sharing,
                "reasoning_sharing": request.enable_reasoning_sharing
            },
            priority=AgentPriority.HIGH if "emergency" in str(request.parameters) else AgentPriority.NORMAL
        )
        
        # Execute collaborative workflow
        workflow_id = f"collaborative_{datetime.utcnow().timestamp()}"
        result = await enhanced_orchestrator.execute_collaborative_workflow(
            workflow_id=workflow_id,
            workflow_type=request.workflow_type,
            context=context,
            parameters=request.parameters,
            collaboration_type=request.collaboration_type
        )
        
        return {
            "workflow_id": workflow_id,
            "success": result.success,
            "execution_time": result.execution_time,
            "collaboration_type": result.collaboration_type.value,
            "consensus_reached": result.consensus_reached,
            "agent_results": {
                task_id: {
                    "success": agent_result.success,
                    "confidence": agent_result.confidence,
                    "reasoning": agent_result.reasoning,
                    "data_summary": _summarize_agent_data(agent_result.data)
                }
                for task_id, agent_result in result.results.items()
            },
            "collaboration_insights": {
                "effectiveness": result.collaboration_insights.get("collaboration_effectiveness", 0.0),
                "knowledge_gained_count": len(result.collaboration_insights.get("knowledge_gained", [])),
                "patterns_discovered_count": len(result.collaboration_insights.get("patterns_discovered", [])),
                "improvement_suggestions": result.collaboration_insights.get("improvement_suggestions", []),
                "cross_agent_learning_count": len(result.collaboration_insights.get("cross_agent_learning", []))
            },
            "memory_sharing": {
                "shared_memories_count": len(result.memory_shared),
                "memory_types": list(set(m.memory_type.value for m in result.memory_shared)),
                "average_importance": sum(m.importance for m in result.memory_shared) / len(result.memory_shared) if result.memory_shared else 0.0
            },
            "reasoning_chains": {
                "reasoning_chains_count": len(result.reasoning_chains),
                "reasoning_summary": _summarize_reasoning_chains(result.reasoning_chains)
            },
            "metadata": result.metadata
        }
        
    except Exception as e:
        logger.error(f"Enhanced agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced agent execution failed: {str(e)}")


@router.post("/advanced-symptom-analysis")
async def advanced_symptom_analysis(request: AdvancedSymptomAnalysisRequest):
    """
    Perform advanced symptom analysis using enhanced agentic AI capabilities.
    
    This endpoint demonstrates:
    - Memory-based symptom analysis
    - Context-aware reasoning
    - Autonomous diagnostic suggestions
    - Cross-agent collaboration for comprehensive assessment
    """
    try:
        # Create comprehensive parameters
        parameters = {
            "symptoms": request.symptoms,
            "severity": request.severity,
            "duration": request.duration,
            "additional_context": request.additional_context,
            "enable_autonomous_decision_making": request.enable_autonomous_decision_making,
            "enable_memory_integration": request.enable_memory_integration,
            "enable_cross_agent_collaboration": request.enable_cross_agent_collaboration
        }
        
        # Create agent context
        context = AgentContext(
            user_id=request.user_id,
            session_id=request.session_id,
            request_id=f"advanced_symptom_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            metadata={
                "analysis_type": "advanced_symptom",
                "autonomous_enabled": request.enable_autonomous_decision_making,
                "memory_enabled": request.enable_memory_integration,
                "collaboration_enabled": request.enable_cross_agent_collaboration
            },
            priority=AgentPriority.CRITICAL if request.severity == "severe" else AgentPriority.HIGH
        )
        
        # Execute comprehensive diagnostic workflow
        workflow_id = f"advanced_symptom_{datetime.utcnow().timestamp()}"
        result = await enhanced_orchestrator.execute_collaborative_workflow(
            workflow_id=workflow_id,
            workflow_type=WorkflowType.DIAGNOSTIC,
            context=context,
            parameters=parameters,
            collaboration_type=CollaborationType.COLLABORATIVE
        )
        
        # Extract advanced insights
        advanced_insights = await _extract_advanced_symptom_insights(result, parameters)
        
        return {
            "workflow_id": workflow_id,
            "success": result.success,
            "execution_time": result.execution_time,
            "symptom_analysis": {
                "symptoms_analyzed": request.symptoms,
                "severity_assessment": request.severity,
                "duration_analysis": request.duration,
                "autonomous_decisions_made": advanced_insights.get("autonomous_decisions", 0),
                "memory_integration_used": advanced_insights.get("memory_integration", False),
                "cross_agent_collaboration": advanced_insights.get("cross_agent_collaboration", False)
            },
            "advanced_insights": advanced_insights,
            "agent_capabilities_demonstrated": [
                "Memory-based pattern recognition",
                "Context-aware reasoning",
                "Autonomous decision-making",
                "Cross-agent collaboration",
                "Learning and adaptation",
                "Consensus building"
            ],
            "collaboration_effectiveness": result.collaboration_insights.get("collaboration_effectiveness", 0.0),
            "consensus_reached": result.consensus_reached,
            "recommendations": _extract_recommendations_from_results(result.results)
        }
        
    except Exception as e:
        logger.error(f"Advanced symptom analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Advanced symptom analysis failed: {str(e)}")


@router.get("/stats", response_model=List[EnhancedAgentStatsResponse])
async def get_enhanced_agent_stats():
    """Get comprehensive statistics for enhanced agents."""
    try:
        stats = []
        for name, agent in enhanced_orchestrator.agents.items():
            agent_stats = agent.get_stats()
            stats.append(EnhancedAgentStatsResponse(
                agent_name=name,
                status=agent.status.value,
                memory_count=len(agent.episodic_memory) + len(agent.short_term_memory),
                reasoning_count=len(agent.reasoning_history),
                learning_outcomes=len(agent.learning_outcomes),
                autonomy_level=agent.autonomy_level,
                collaboration_count=len(agent.communication_buffer),
                success_rate=agent_stats.get("success_rate", 0.0)
            ))
        return stats
    except Exception as e:
        logger.error(f"Failed to get enhanced agent stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get enhanced agent stats")


@router.get("/collaboration-insights", response_model=CollaborationInsightsResponse)
async def get_collaboration_insights():
    """Get insights from agent collaborations."""
    try:
        collaboration_stats = enhanced_orchestrator.get_collaboration_stats()
        
        if not enhanced_orchestrator.collaboration_history:
            return CollaborationInsightsResponse(
                collaboration_effectiveness=0.0,
                knowledge_gained=[],
                patterns_discovered=[],
                improvement_suggestions=[],
                cross_agent_learning=[],
                consensus_reached=False,
                memory_shared_count=0,
                reasoning_chains_count=0
            )
        
        # Get latest collaboration result
        latest_collaboration = enhanced_orchestrator.collaboration_history[-1]
        
        return CollaborationInsightsResponse(
            collaboration_effectiveness=latest_collaboration.collaboration_insights.get("collaboration_effectiveness", 0.0),
            knowledge_gained=latest_collaboration.collaboration_insights.get("knowledge_gained", []),
            patterns_discovered=latest_collaboration.collaboration_insights.get("patterns_discovered", []),
            improvement_suggestions=latest_collaboration.collaboration_insights.get("improvement_suggestions", []),
            cross_agent_learning=latest_collaboration.collaboration_insights.get("cross_agent_learning", []),
            consensus_reached=latest_collaboration.consensus_reached,
            memory_shared_count=len(latest_collaboration.memory_shared),
            reasoning_chains_count=len(latest_collaboration.reasoning_chains)
        )
    except Exception as e:
        logger.error(f"Failed to get collaboration insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get collaboration insights")


@router.get("/capabilities")
async def get_enhanced_agent_capabilities():
    """Get capabilities of enhanced agents."""
    try:
        capabilities = {}
        for name, agent in enhanced_orchestrator.agents.items():
            capabilities[name] = {
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.get_provided_capabilities(),
                "autonomy_level": agent.autonomy_level,
                "memory_systems": [
                    "short_term_memory",
                    "long_term_memory", 
                    "episodic_memory",
                    "semantic_memory",
                    "procedural_memory"
                ],
                "reasoning_capabilities": [
                    "deductive_reasoning",
                    "inductive_reasoning",
                    "abductive_reasoning",
                    "analogical_reasoning",
                    "critical_reasoning"
                ],
                "autonomous_capabilities": [
                    "goal_setting",
                    "planning",
                    "decision_making",
                    "learning",
                    "adaptation"
                ]
            }
        return capabilities
    except Exception as e:
        logger.error(f"Failed to get enhanced agent capabilities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get enhanced agent capabilities")


@router.get("/health")
async def get_enhanced_agent_health():
    """Get health status of enhanced agents."""
    try:
        health_status = await enhanced_orchestrator.health_check()
        return health_status
    except Exception as e:
        logger.error(f"Failed to get enhanced agent health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get enhanced agent health")


@router.get("/collaboration-history")
async def get_collaboration_history(limit: int = 10):
    """Get recent collaboration history."""
    try:
        history = enhanced_orchestrator.collaboration_history[-limit:] if enhanced_orchestrator.collaboration_history else []
        return [
            {
                "workflow_id": collaboration.workflow_id,
                "success": collaboration.success,
                "execution_time": collaboration.execution_time,
                "collaboration_type": collaboration.collaboration_type.value,
                "consensus_reached": collaboration.consensus_reached,
                "agent_count": collaboration.metadata.get("agent_count", 0),
                "successful_agents": collaboration.metadata.get("successful_agents", 0),
                "memory_shared_count": len(collaboration.memory_shared),
                "reasoning_chains_count": len(collaboration.reasoning_chains),
                "timestamp": collaboration.timestamp.isoformat()
            }
            for collaboration in history
        ]
    except Exception as e:
        logger.error(f"Failed to get collaboration history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get collaboration history")


@router.post("/demonstrate-agentic-capabilities")
async def demonstrate_agentic_capabilities():
    """
    Demonstrate the advanced agentic AI capabilities.
    
    This endpoint showcases:
    - Memory systems and learning
    - Advanced reasoning capabilities
    - Autonomous decision-making
    - Cross-agent collaboration
    - Pattern recognition and adaptation
    """
    try:
        # Create a demonstration workflow
        demo_parameters = {
            "symptoms": ["chest pain", "shortness of breath", "fatigue"],
            "severity": "moderate",
            "duration": "2 days",
            "demo_mode": True,
            "showcase_capabilities": [
                "memory_integration",
                "advanced_reasoning",
                "autonomous_decisions",
                "cross_agent_collaboration",
                "pattern_recognition",
                "learning_and_adaptation"
            ]
        }
        
        context = AgentContext(
            user_id="demo_user",
            session_id="demo_session",
            request_id=f"demo_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            metadata={"demo": True, "showcase_capabilities": True},
            priority=AgentPriority.NORMAL
        )
        
        # Execute demonstration workflow
        workflow_id = f"demo_{datetime.utcnow().timestamp()}"
        result = await enhanced_orchestrator.execute_collaborative_workflow(
            workflow_id=workflow_id,
            workflow_type=WorkflowType.COMPREHENSIVE,
            context=context,
            parameters=demo_parameters,
            collaboration_type=CollaborationType.COLLABORATIVE
        )
        
        return {
            "demonstration_id": workflow_id,
            "capabilities_demonstrated": {
                "memory_systems": {
                    "episodic_memory": "Stores and retrieves past experiences",
                    "semantic_memory": "Maintains medical knowledge and rules",
                    "procedural_memory": "Learns and improves procedures",
                    "memory_sharing": "Agents share relevant memories"
                },
                "reasoning_capabilities": {
                    "deductive": "Applies medical rules to symptoms",
                    "inductive": "Identifies patterns in data",
                    "abductive": "Finds best explanations",
                    "analogical": "Uses similar cases for reasoning",
                    "critical": "Evaluates evidence and assumptions"
                },
                "autonomous_capabilities": {
                    "goal_setting": "Autonomously sets healthcare goals",
                    "planning": "Creates execution plans",
                    "decision_making": "Makes autonomous decisions",
                    "learning": "Learns from experiences",
                    "adaptation": "Adapts to changing circumstances"
                },
                "collaboration_features": {
                    "memory_sharing": len(result.memory_shared),
                    "reasoning_sharing": len(result.reasoning_chains),
                    "consensus_building": result.consensus_reached,
                    "cross_agent_learning": len(result.collaboration_insights.get("cross_agent_learning", []))
                }
            },
            "demonstration_results": {
                "success": result.success,
                "execution_time": result.execution_time,
                "collaboration_effectiveness": result.collaboration_insights.get("collaboration_effectiveness", 0.0),
                "knowledge_gained": len(result.collaboration_insights.get("knowledge_gained", [])),
                "patterns_discovered": len(result.collaboration_insights.get("patterns_discovered", [])),
                "improvement_suggestions": result.collaboration_insights.get("improvement_suggestions", [])
            },
            "agentic_ai_benefits": [
                "Improved diagnostic accuracy through memory integration",
                "Faster decision-making with autonomous capabilities",
                "Better outcomes through collaborative reasoning",
                "Continuous learning and adaptation",
                "Pattern recognition across multiple cases",
                "Consensus building for complex decisions"
            ]
        }
        
    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Demonstration failed: {str(e)}")


# Helper functions
def _summarize_agent_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize agent data for API response."""
    if not data:
        return {"summary": "No data available"}
    
    summary = {
        "data_type": type(data).__name__,
        "key_fields": list(data.keys()),
        "has_recommendations": "recommendations" in data,
        "has_assessments": "assessments" in data,
        "has_patterns": "patterns" in data
    }
    
    if "recommendations" in data:
        summary["recommendation_count"] = len(data["recommendations"])
    
    if "assessments" in data:
        summary["assessment_count"] = len(data["assessments"])
    
    return summary


def _summarize_reasoning_chains(reasoning_chains: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize reasoning chains for API response."""
    if not reasoning_chains:
        return {"summary": "No reasoning chains available"}
    
    return {
        "total_chains": len(reasoning_chains),
        "agents_involved": list(set(chain.get("agent", "unknown") for chain in reasoning_chains)),
        "reasoning_types": list(set(chain.get("reasoning_type", "unknown") for chain in reasoning_chains))
    }


async def _extract_advanced_symptom_insights(result: CollaborationResult, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Extract advanced insights from symptom analysis results."""
    insights = {
        "autonomous_decisions": 0,
        "memory_integration": False,
        "cross_agent_collaboration": False,
        "pattern_recognition": False,
        "learning_applied": False,
        "reasoning_depth": 0
    }
    
    # Analyze results for advanced capabilities
    for agent_result in result.results.values():
        if agent_result.success and agent_result.data:
            # Check for autonomous decisions
            if "autonomous_decision" in str(agent_result.data).lower():
                insights["autonomous_decisions"] += 1
            
            # Check for memory integration
            if "memory" in str(agent_result.data).lower():
                insights["memory_integration"] = True
            
            # Check for pattern recognition
            if "pattern" in str(agent_result.data).lower():
                insights["pattern_recognition"] = True
            
            # Check for learning
            if "learning" in str(agent_result.data).lower():
                insights["learning_applied"] = True
    
    # Check for cross-agent collaboration
    if len(result.results) > 1:
        insights["cross_agent_collaboration"] = True
    
    # Calculate reasoning depth
    insights["reasoning_depth"] = len(result.reasoning_chains)
    
    return insights


def _extract_recommendations_from_results(results: Dict[str, Any]) -> List[str]:
    """Extract recommendations from agent results."""
    recommendations = []
    
    for result in results.values():
        if result.success and result.data:
            if "recommendations" in result.data:
                recommendations.extend(result.data["recommendations"])
            elif "recommendation" in result.data:
                recommendations.append(result.data["recommendation"])
    
    return list(set(recommendations))  # Remove duplicates
