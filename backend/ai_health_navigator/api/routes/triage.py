"""
Triage assessment API routes.

This module provides endpoints for emergency triage assessment, urgency classification,
and emergency response coordination. It integrates with the EnhancedTriageAssessmentAgent
for intelligent emergency evaluation and response.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...core.security import get_current_user, check_permissions
from ...core.logging import get_logger
from ...database.session import get_db
from ...database.models import User, TriageAssessment
from ...ai.agents.enhanced_base_agent import AgentContext, AgentPriority
from ...ai.agents.enhanced_agent_orchestrator import EnhancedAgentOrchestrator

logger = get_logger(__name__)
router = APIRouter()


class TriageRequest(BaseModel):
    """Request model for triage assessment."""
    symptoms: List[str] = Field(..., description="List of symptoms")
    severity: str = Field(..., description="Symptom severity level")
    duration: str = Field(..., description="How long symptoms have been present")
    location: Optional[str] = Field(None, description="Patient location")
    age: Optional[int] = Field(None, description="Patient age")
    medical_history: Optional[List[str]] = Field(None, description="Relevant medical history")
    current_medications: Optional[List[str]] = Field(None, description="Current medications")
    vital_signs: Optional[Dict[str, Any]] = Field(None, description="Vital signs if available")
    additional_context: Optional[str] = Field(None, description="Additional context")


class TriageResponse(BaseModel):
    """Response model for triage assessment."""
    urgency_level: str = Field(..., description="Urgency classification")
    risk_score: float = Field(..., description="Risk assessment score (0-1)")
    recommended_action: str = Field(..., description="Recommended immediate action")
    time_to_care: str = Field(..., description="Recommended time to seek care")
    emergency_services_needed: bool = Field(..., description="Whether emergency services are needed")
    differential_diagnosis: List[Dict[str, Any]] = Field(..., description="Possible conditions")
    safety_instructions: List[str] = Field(..., description="Safety instructions")
    follow_up_instructions: List[str] = Field(..., description="Follow-up instructions")
    confidence_score: float = Field(..., description="Assessment confidence (0-1)")
    assessment_id: str = Field(..., description="Unique assessment identifier")
    timestamp: datetime = Field(..., description="Assessment timestamp")


class TriageHistoryResponse(BaseModel):
    """Response model for triage history."""
    assessments: List[Dict[str, Any]] = Field(..., description="List of past assessments")
    total_count: int = Field(..., description="Total number of assessments")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")


@router.post("/assess", response_model=TriageResponse)
async def assess_triage(
    request: TriageRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform emergency triage assessment.
    
    This endpoint provides intelligent emergency triage using the EnhancedTriageAssessmentAgent.
    It evaluates symptoms, medical history, and context to determine urgency level and
    recommend appropriate actions.
    
    Args:
        request: Triage assessment request with symptoms and context
        background_tasks: FastAPI background tasks for async processing
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        TriageResponse: Comprehensive triage assessment with recommendations
        
    Raises:
        HTTPException: If assessment fails or invalid input
    """
    try:
        logger.info(f"Starting triage assessment for user {current_user.id}")
        
        # Create agent context
        context = AgentContext(
            user_id=str(current_user.id),
            session_id=f"triage_{datetime.utcnow().timestamp()}",
            request_id=f"triage_req_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            metadata={
                "assessment_type": "emergency_triage",
                "symptoms_count": len(request.symptoms),
                "has_vital_signs": bool(request.vital_signs)
            },
            priority=AgentPriority.HIGH
        )
        
        # Initialize enhanced agent orchestrator
        orchestrator = EnhancedAgentOrchestrator()
        await orchestrator.initialize()
        
        # Execute triage assessment workflow
        result = await orchestrator.execute_collaborative_workflow(
            workflow_id=f"triage_assessment_{context.request_id}",
            workflow_type="emergency",
            context=context,
            parameters={
                "symptoms": request.symptoms,
                "severity": request.severity,
                "duration": request.duration,
                "location": request.location,
                "age": request.age,
                "medical_history": request.medical_history or [],
                "current_medications": request.current_medications or [],
                "vital_signs": request.vital_signs or {},
                "additional_context": request.additional_context,
                "enable_memory_sharing": True,
                "enable_reasoning_sharing": True,
                "autonomy_level": 0.9  # High autonomy for emergency situations
            },
            collaboration_type="collaborative"
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Triage assessment failed: {result.error_message}"
            )
        
        # Extract assessment results
        assessment_data = result.results.get("triage_assessment", {})
        
        # Create triage assessment record
        triage_record = TriageAssessment(
            user_id=current_user.id,
            symptoms=request.symptoms,
            severity=request.severity,
            urgency_level=assessment_data.get("urgency_level", "unknown"),
            risk_score=assessment_data.get("risk_score", 0.0),
            recommended_action=assessment_data.get("recommended_action", ""),
            emergency_services_needed=assessment_data.get("emergency_services_needed", False),
            assessment_data=result.results,
            confidence_score=assessment_data.get("confidence_score", 0.0)
        )
        
        db.add(triage_record)
        db.commit()
        db.refresh(triage_record)
        
        # Log assessment for monitoring
        background_tasks.add_task(
            logger.info,
            f"Triage assessment completed for user {current_user.id}: "
            f"urgency={assessment_data.get('urgency_level')}, "
            f"risk_score={assessment_data.get('risk_score')}"
        )
        
        return TriageResponse(
            urgency_level=assessment_data.get("urgency_level", "unknown"),
            risk_score=assessment_data.get("risk_score", 0.0),
            recommended_action=assessment_data.get("recommended_action", ""),
            time_to_care=assessment_data.get("time_to_care", ""),
            emergency_services_needed=assessment_data.get("emergency_services_needed", False),
            differential_diagnosis=assessment_data.get("differential_diagnosis", []),
            safety_instructions=assessment_data.get("safety_instructions", []),
            follow_up_instructions=assessment_data.get("follow_up_instructions", []),
            confidence_score=assessment_data.get("confidence_score", 0.0),
            assessment_id=str(triage_record.id),
            timestamp=triage_record.created_at
        )
        
    except Exception as e:
        logger.error(f"Triage assessment failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Triage assessment failed: {str(e)}"
        )


@router.get("/history/{user_id}", response_model=TriageHistoryResponse)
async def get_triage_history(
    user_id: str,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get triage assessment history for a user.
    
    This endpoint retrieves the history of triage assessments for a specific user.
    It includes pagination support and filters by user permissions.
    
    Args:
        user_id: ID of the user whose history to retrieve
        page: Page number for pagination (1-based)
        page_size: Number of items per page
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        TriageHistoryResponse: Paginated list of triage assessments
        
    Raises:
        HTTPException: If access denied or user not found
    """
    try:
        # Check permissions - users can only access their own history
        if str(current_user.id) != user_id and not check_permissions(current_user, ["admin", "healthcare_provider"]):
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only view your own triage history"
            )
        
        # Calculate offset for pagination
        offset = (page - 1) * page_size
        
        # Query triage assessments
        assessments_query = db.query(TriageAssessment).filter(
            TriageAssessment.user_id == user_id
        ).order_by(TriageAssessment.created_at.desc())
        
        total_count = assessments_query.count()
        assessments = assessments_query.offset(offset).limit(page_size).all()
        
        # Convert to response format
        assessment_list = []
        for assessment in assessments:
            assessment_list.append({
                "id": str(assessment.id),
                "symptoms": assessment.symptoms,
                "severity": assessment.severity,
                "urgency_level": assessment.urgency_level,
                "risk_score": assessment.risk_score,
                "recommended_action": assessment.recommended_action,
                "emergency_services_needed": assessment.emergency_services_needed,
                "confidence_score": assessment.confidence_score,
                "created_at": assessment.created_at.isoformat(),
                "updated_at": assessment.updated_at.isoformat() if assessment.updated_at else None
            })
        
        return TriageHistoryResponse(
            assessments=assessment_list,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve triage history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve triage history: {str(e)}"
        )


@router.get("/stats")
async def get_triage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get triage assessment statistics.
    
    This endpoint provides aggregated statistics about triage assessments,
    including urgency level distribution, average response times, and
    emergency service utilization.
    
    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        Dict: Triage assessment statistics
        
    Raises:
        HTTPException: If statistics retrieval fails
    """
    try:
        # Check permissions
        if not check_permissions(current_user, ["admin", "healthcare_provider"]):
            raise HTTPException(
                status_code=403,
                detail="Access denied: Insufficient permissions"
            )
        
        # Get basic statistics
        total_assessments = db.query(TriageAssessment).count()
        
        # Get urgency level distribution
        urgency_stats = db.query(
            TriageAssessment.urgency_level,
            db.func.count(TriageAssessment.id)
        ).group_by(TriageAssessment.urgency_level).all()
        
        # Get emergency service utilization
        emergency_count = db.query(TriageAssessment).filter(
            TriageAssessment.emergency_services_needed == True
        ).count()
        
        # Get average risk scores
        avg_risk_score = db.query(
            db.func.avg(TriageAssessment.risk_score)
        ).scalar() or 0.0
        
        # Get recent activity (last 24 hours)
        from datetime import timedelta
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_assessments = db.query(TriageAssessment).filter(
            TriageAssessment.created_at >= recent_cutoff
        ).count()
        
        return {
            "total_assessments": total_assessments,
            "urgency_distribution": dict(urgency_stats),
            "emergency_services_utilization": {
                "count": emergency_count,
                "percentage": (emergency_count / total_assessments * 100) if total_assessments > 0 else 0
            },
            "average_risk_score": round(avg_risk_score, 3),
            "recent_activity_24h": recent_assessments,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve triage stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve triage stats: {str(e)}"
        )
