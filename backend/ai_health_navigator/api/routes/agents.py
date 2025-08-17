"""
Agent Management API routes for AI Health Navigator.

This module provides endpoints for managing and executing AI agents,
including comprehensive health assessments and multi-agent workflows.
"""

from typing import Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ...ai.agents import AgentOrchestrator, AgentTask, AgentContext, AgentPriority, OrchestrationStrategy
from ...core.logging import get_logger
from ...database import get_db_session

logger = get_logger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])

# Global orchestrator instance
orchestrator = AgentOrchestrator()


class AgentExecutionRequest(BaseModel):
    """Request model for agent execution."""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    request_data: Dict[str, Any] = Field(..., description="Request data for agents")
    strategy: OrchestrationStrategy = Field(OrchestrationStrategy.ADAPTIVE, description="Orchestration strategy")
    timeout: float = Field(300.0, description="Execution timeout in seconds")


class AgentStatsResponse(BaseModel):
    """Response model for agent statistics."""
    agent_name: str
    status: str
    total_executions: int
    success_count: int
    error_count: int
    success_rate: float
    average_execution_time: float
    last_execution: datetime = None


class AgentHealthResponse(BaseModel):
    """Response model for agent health status."""
    overall: str
    agents: Dict[str, Dict[str, Any]]
    timestamp: str


class ComprehensiveHealthAssessmentRequest(BaseModel):
    """Request model for comprehensive health assessment."""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    
    # Symptom analysis
    symptoms: List[str] = Field([], description="List of symptoms")
    severity: str = Field("mild", description="Symptom severity")
    duration: str = Field("", description="Symptom duration")
    
    # Medication management
    medications: List[str] = Field([], description="Current medications")
    patient_conditions: List[str] = Field([], description="Patient conditions")
    allergies: List[str] = Field([], description="Known allergies")
    
    # Preventive care
    age: int = Field(..., description="Patient age")
    gender: str = Field(..., description="Patient gender")
    family_history: List[str] = Field([], description="Family history")
    lifestyle_factors: List[str] = Field([], description="Lifestyle factors")
    
    # Mental health
    mood_assessment: Dict[str, Any] = Field({}, description="Mood assessment")
    current_stressors: List[str] = Field([], description="Current stressors")
    sleep_quality: str = Field("unknown", description="Sleep quality")
    social_support: str = Field("unknown", description="Social support level")


@router.on_event("startup")
async def startup_event():
    """Initialize the agent orchestrator on startup."""
    try:
        await orchestrator.initialize()
        logger.info("Agent orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent orchestrator: {e}")
        raise


@router.get("/health", response_model=AgentHealthResponse)
async def get_agent_health():
    """Get health status of all agents."""
    try:
        health_status = await orchestrator.health_check()
        return AgentHealthResponse(**health_status)
    except Exception as e:
        logger.error(f"Failed to get agent health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent health")


@router.get("/stats", response_model=List[AgentStatsResponse])
async def get_agent_stats():
    """Get statistics for all agents."""
    try:
        stats = orchestrator.get_agent_stats()
        return [AgentStatsResponse(**agent_stats) for agent_stats in stats.values()]
    except Exception as e:
        logger.error(f"Failed to get agent stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent stats")


@router.post("/execute")
async def execute_agents(request: AgentExecutionRequest):
    """Execute agents based on request data."""
    try:
        # Create agent context
        context = AgentContext(
            user_id=request.user_id,
            session_id=request.session_id,
            request_id=f"req_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            metadata={"source": "api"},
            priority=AgentPriority.NORMAL
        )
        
        # Route request to appropriate agents
        tasks = await orchestrator.route_request(context, request.request_data)
        
        if not tasks:
            raise HTTPException(status_code=400, detail="No suitable agents found for request")
        
        # Execute workflow
        workflow_id = f"workflow_{datetime.utcnow().timestamp()}"
        result = await orchestrator.execute_workflow(
            workflow_id=workflow_id,
            tasks=tasks,
            strategy=request.strategy,
            timeout=request.timeout
        )
        
        return {
            "workflow_id": workflow_id,
            "success": result.success,
            "execution_time": result.execution_time,
            "strategy_used": result.strategy_used.value,
            "results": {
                agent_name: {
                    "success": agent_result.success,
                    "confidence": agent_result.confidence,
                    "data": agent_result.data,
                    "reasoning": agent_result.reasoning
                }
                for agent_name, agent_result in result.results.items()
            },
            "metadata": result.metadata
        }
        
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@router.post("/comprehensive-assessment")
async def comprehensive_health_assessment(
    request: ComprehensiveHealthAssessmentRequest,
    background_tasks: BackgroundTasks
):
    """Perform comprehensive health assessment using multiple agents."""
    try:
        # Create agent context
        context = AgentContext(
            user_id=request.user_id,
            session_id=request.session_id,
            request_id=f"comprehensive_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            metadata={"assessment_type": "comprehensive"},
            priority=AgentPriority.HIGH
        )
        
        # Create tasks for different assessment types
        tasks = []
        
        # Symptom analysis task
        if request.symptoms:
            tasks.append(AgentTask(
                agent_type=orchestrator.agent_registry["symptom_analysis"],
                context=context,
                parameters={
                    "symptoms": request.symptoms,
                    "severity": request.severity,
                    "duration": request.duration
                },
                priority=AgentPriority.HIGH if request.severity == "severe" else AgentPriority.NORMAL
            ))
        
        # Medication management task
        if request.medications:
            tasks.append(AgentTask(
                agent_type=orchestrator.agent_registry["medication_management"],
                context=context,
                parameters={
                    "medications": request.medications,
                    "patient_conditions": request.patient_conditions,
                    "allergies": request.allergies,
                    "age": request.age
                },
                priority=AgentPriority.HIGH
            ))
        
        # Preventive care task
        tasks.append(AgentTask(
            agent_type=orchestrator.agent_registry["preventive_care"],
            context=context,
            parameters={
                "age": request.age,
                "gender": request.gender,
                "family_history": request.family_history,
                "lifestyle_factors": request.lifestyle_factors,
                "current_conditions": request.patient_conditions
            },
            priority=AgentPriority.NORMAL
        ))
        
        # Mental health task
        if request.mood_assessment or request.current_stressors:
            tasks.append(AgentTask(
                agent_type=orchestrator.agent_registry["mental_health"],
                context=context,
                parameters={
                    "symptoms": request.symptoms,
                    "mood_assessment": request.mood_assessment,
                    "current_stressors": request.current_stressors,
                    "sleep_quality": request.sleep_quality,
                    "social_support": request.social_support
                },
                priority=AgentPriority.CRITICAL if request.mood_assessment.get("suicidal_thoughts") else AgentPriority.HIGH
            ))
        
        if not tasks:
            raise HTTPException(status_code=400, detail="No assessment data provided")
        
        # Execute comprehensive assessment
        workflow_id = f"comprehensive_{datetime.utcnow().timestamp()}"
        result = await orchestrator.execute_workflow(
            workflow_id=workflow_id,
            tasks=tasks,
            strategy=OrchestrationStrategy.ADAPTIVE,
            timeout=300.0
        )
        
        # Add background task for analytics
        background_tasks.add_task(log_comprehensive_assessment, workflow_id, request.user_id, result)
        
        # Compile comprehensive results
        comprehensive_results = {
            "workflow_id": workflow_id,
            "assessment_timestamp": datetime.utcnow().isoformat(),
            "user_id": request.user_id,
            "overall_health_score": calculate_health_score(result.results),
            "risk_level": determine_overall_risk(result.results),
            "priority_recommendations": extract_priority_recommendations(result.results),
            "assessments": {
                "symptom_analysis": extract_agent_result("SymptomAnalysisAgent", result.results),
                "medication_management": extract_agent_result("MedicationManagementAgent", result.results),
                "preventive_care": extract_agent_result("PreventiveCareAgent", result.results),
                "mental_health": extract_agent_result("MentalHealthAgent", result.results)
            },
            "execution_summary": {
                "success": result.success,
                "execution_time": result.execution_time,
                "agents_executed": len(result.results),
                "successful_agents": sum(1 for r in result.results.values() if r.success)
            }
        }
        
        return comprehensive_results
        
    except Exception as e:
        logger.error(f"Comprehensive assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive assessment failed: {str(e)}")


@router.get("/capabilities")
async def get_agent_capabilities():
    """Get capabilities of all available agents."""
    try:
        capabilities = {}
        for agent_name, agent_class in orchestrator.agent_registry.items():
            # Create a temporary instance to get capabilities
            temp_agent = agent_class()
            capabilities[agent_name] = {
                "name": temp_agent.name,
                "description": temp_agent.description,
                "capabilities": temp_agent.get_provided_capabilities()
            }
        
        return capabilities
        
    except Exception as e:
        logger.error(f"Failed to get agent capabilities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent capabilities")


@router.get("/workflow-history")
async def get_workflow_history(limit: int = 100):
    """Get recent workflow execution history."""
    try:
        history = orchestrator.get_workflow_history(limit=limit)
        return [
            {
                "workflow_id": workflow.workflow_id,
                "success": workflow.success,
                "execution_time": workflow.execution_time,
                "strategy_used": workflow.strategy_used.value,
                "timestamp": workflow.timestamp.isoformat(),
                "metadata": workflow.metadata
            }
            for workflow in history
        ]
        
    except Exception as e:
        logger.error(f"Failed to get workflow history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get workflow history")


# Helper functions

def calculate_health_score(results: Dict[str, Any]) -> float:
    """Calculate overall health score from agent results."""
    if not results:
        return 0.0
    
    total_score = 0.0
    total_weight = 0.0
    
    for agent_name, result in results.items():
        if result.success:
            # Weight different agents differently
            weight = 1.0
            if "SymptomAnalysisAgent" in agent_name:
                weight = 0.3
            elif "MedicationManagementAgent" in agent_name:
                weight = 0.25
            elif "PreventiveCareAgent" in agent_name:
                weight = 0.25
            elif "MentalHealthAgent" in agent_name:
                weight = 0.2
            
            score = result.confidence * 100  # Convert to percentage
            total_score += score * weight
            total_weight += weight
    
    return total_score / total_weight if total_weight > 0 else 0.0


def determine_overall_risk(results: Dict[str, Any]) -> str:
    """Determine overall risk level from agent results."""
    risk_levels = []
    
    for agent_name, result in results.items():
        if result.success and result.data:
            if "risk_level" in result.data:
                risk_levels.append(result.data["risk_level"])
            elif "urgency" in result.data:
                risk_levels.append(result.data["urgency"])
    
    if not risk_levels:
        return "unknown"
    
    # Determine highest risk level
    risk_priority = {"critical": 4, "high": 3, "moderate": 2, "low": 1, "unknown": 0}
    highest_risk = max(risk_levels, key=lambda x: risk_priority.get(x, 0))
    
    return highest_risk


def extract_priority_recommendations(results: Dict[str, Any]) -> List[str]:
    """Extract priority recommendations from agent results."""
    recommendations = []
    
    for agent_name, result in results.items():
        if result.success and result.data:
            if "recommendations" in result.data:
                recommendations.extend(result.data["recommendations"])
            elif "priority_recommendations" in result.data:
                recommendations.extend(result.data["priority_recommendations"])
    
    # Remove duplicates and prioritize urgent recommendations
    unique_recommendations = list(set(recommendations))
    urgent_recommendations = [r for r in unique_recommendations if "URGENT" in r.upper()]
    other_recommendations = [r for r in unique_recommendations if "URGENT" not in r.upper()]
    
    return urgent_recommendations + other_recommendations[:5]  # Limit to top 5 non-urgent


def extract_agent_result(agent_name: str, results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract result for a specific agent."""
    for name, result in results.items():
        if agent_name in name:
            return {
                "success": result.success,
                "confidence": result.confidence,
                "data": result.data,
                "reasoning": result.reasoning
            }
    
    return {"success": False, "confidence": 0.0, "data": {}, "reasoning": "Agent not executed"}


async def log_comprehensive_assessment(workflow_id: str, user_id: str, result: Any):
    """Log comprehensive assessment results for analytics."""
    try:
        logger.info(f"Comprehensive assessment completed", extra={
            "workflow_id": workflow_id,
            "user_id": user_id,
            "success": result.success,
            "execution_time": result.execution_time,
            "agents_count": len(result.results)
        })
        
        # Here you would typically save to database or analytics service
        # For now, just log the event
        
    except Exception as e:
        logger.error(f"Failed to log comprehensive assessment: {e}")
