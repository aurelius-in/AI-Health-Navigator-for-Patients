"""
Insurance management API routes.

This module provides endpoints for insurance verification, coverage analysis,
cost estimation, and insurance provider management. It integrates with external
insurance APIs and provides intelligent cost optimization recommendations.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...core.security import get_current_user, check_permissions
from ...core.logging import get_logger
from ...database.session import get_db
from ...database.models import User, InsuranceProvider, InsurancePlan, CoverageAnalysis
from ...ai.agents.enhanced_base_agent import AgentContext, AgentPriority
from ...ai.agents.enhanced_agent_orchestrator import EnhancedAgentOrchestrator

logger = get_logger(__name__)
router = APIRouter()


class InsuranceVerificationRequest(BaseModel):
    """Request model for insurance verification."""
    insurance_provider: str = Field(..., description="Insurance provider name")
    member_id: str = Field(..., description="Member ID")
    group_number: Optional[str] = Field(None, description="Group number")
    subscriber_name: str = Field(..., description="Subscriber name")
    subscriber_dob: str = Field(..., description="Subscriber date of birth (YYYY-MM-DD)")
    relationship: str = Field(..., description="Relationship to subscriber")


class CoverageAnalysisRequest(BaseModel):
    """Request model for coverage analysis."""
    insurance_provider: str = Field(..., description="Insurance provider")
    member_id: str = Field(..., description="Member ID")
    procedure_codes: List[str] = Field(..., description="CPT/HCPCS procedure codes")
    diagnosis_codes: List[str] = Field(..., description="ICD-10 diagnosis codes")
    provider_npi: Optional[str] = Field(None, description="Provider NPI number")
    service_date: str = Field(..., description="Service date (YYYY-MM-DD)")
    location: Optional[str] = Field(None, description="Service location")


class CostEstimateRequest(BaseModel):
    """Request model for cost estimation."""
    insurance_provider: str = Field(..., description="Insurance provider")
    member_id: str = Field(..., description="Member ID")
    procedures: List[Dict[str, Any]] = Field(..., description="List of procedures with codes and descriptions")
    provider_id: Optional[str] = Field(None, description="Provider ID")
    facility_type: str = Field(..., description="Facility type (hospital, clinic, etc.)")
    urgency: str = Field(..., description="Urgency level (routine, urgent, emergency)")


class InsuranceVerificationResponse(BaseModel):
    """Response model for insurance verification."""
    is_valid: bool = Field(..., description="Whether insurance is valid")
    member_name: str = Field(..., description="Member name")
    plan_name: str = Field(..., description="Plan name")
    effective_date: str = Field(..., description="Effective date")
    termination_date: Optional[str] = Field(None, description="Termination date")
    coverage_status: str = Field(..., description="Coverage status")
    copay_info: Dict[str, Any] = Field(..., description="Copay information")
    deductible_info: Dict[str, Any] = Field(..., description="Deductible information")
    verification_id: str = Field(..., description="Verification ID")
    timestamp: datetime = Field(..., description="Verification timestamp")


class CoverageAnalysisResponse(BaseModel):
    """Response model for coverage analysis."""
    is_covered: bool = Field(..., description="Whether procedures are covered")
    coverage_percentage: float = Field(..., description="Coverage percentage (0-100)")
    patient_responsibility: float = Field(..., description="Patient responsibility amount")
    insurance_payment: float = Field(..., description="Insurance payment amount")
    prior_authorization_required: bool = Field(..., description="Whether prior authorization is required")
    coverage_details: List[Dict[str, Any]] = Field(..., description="Detailed coverage information")
    exclusions: List[str] = Field(..., description="Coverage exclusions")
    limitations: List[str] = Field(..., description="Coverage limitations")
    analysis_id: str = Field(..., description="Analysis ID")
    timestamp: datetime = Field(..., description="Analysis timestamp")


class CostEstimateResponse(BaseModel):
    """Response model for cost estimation."""
    total_cost: float = Field(..., description="Total estimated cost")
    patient_responsibility: float = Field(..., description="Patient responsibility")
    insurance_coverage: float = Field(..., description="Insurance coverage amount")
    cost_breakdown: List[Dict[str, Any]] = Field(..., description="Detailed cost breakdown")
    savings_opportunities: List[Dict[str, Any]] = Field(..., description="Potential savings opportunities")
    alternative_providers: List[Dict[str, Any]] = Field(..., description="Alternative provider options")
    estimate_id: str = Field(..., description="Estimate ID")
    timestamp: datetime = Field(..., description="Estimate timestamp")


@router.post("/verify", response_model=InsuranceVerificationResponse)
async def verify_insurance(
    request: InsuranceVerificationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify insurance coverage and eligibility.
    
    This endpoint verifies insurance coverage using the EnhancedAgentOrchestrator
    to integrate with external insurance APIs and provide real-time verification.
    
    Args:
        request: Insurance verification request
        background_tasks: FastAPI background tasks for async processing
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        InsuranceVerificationResponse: Insurance verification results
        
    Raises:
        HTTPException: If verification fails or invalid input
    """
    try:
        logger.info(f"Insurance verification requested by user {current_user.id}")
        
        # Create agent context
        context = AgentContext(
            user_id=str(current_user.id),
            session_id=f"insurance_verify_{datetime.utcnow().timestamp()}",
            request_id=f"insurance_verify_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            metadata={
                "verification_type": "insurance_eligibility",
                "provider": request.insurance_provider,
                "has_group_number": bool(request.group_number)
            },
            priority=AgentPriority.MEDIUM
        )
        
        # Initialize enhanced agent orchestrator
        orchestrator = EnhancedAgentOrchestrator()
        await orchestrator.initialize()
        
        # Execute insurance verification workflow
        result = await orchestrator.execute_collaborative_workflow(
            workflow_id=f"insurance_verification_{context.request_id}",
            workflow_type="insurance_verification",
            context=context,
            parameters={
                "insurance_provider": request.insurance_provider,
                "member_id": request.member_id,
                "group_number": request.group_number,
                "subscriber_name": request.subscriber_name,
                "subscriber_dob": request.subscriber_dob,
                "relationship": request.relationship,
                "enable_memory_sharing": True,
                "enable_reasoning_sharing": True,
                "autonomy_level": 0.6
            },
            collaboration_type="collaborative"
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Insurance verification failed: {result.error_message}"
            )
        
        # Extract verification results
        verification_data = result.results.get("insurance_verification", {})
        
        # Create verification record
        verification_record = CoverageAnalysis(
            user_id=current_user.id,
            insurance_provider=request.insurance_provider,
            member_id=request.member_id,
            analysis_type="verification",
            analysis_data=result.results,
            is_covered=verification_data.get("is_valid", False),
            coverage_percentage=100.0 if verification_data.get("is_valid", False) else 0.0,
            patient_responsibility=0.0,
            insurance_payment=0.0
        )
        
        db.add(verification_record)
        db.commit()
        db.refresh(verification_record)
        
        # Log verification for monitoring
        background_tasks.add_task(
            logger.info,
            f"Insurance verification completed for user {current_user.id}: "
            f"provider={request.insurance_provider}, "
            f"valid={verification_data.get('is_valid')}"
        )
        
        return InsuranceVerificationResponse(
            is_valid=verification_data.get("is_valid", False),
            member_name=verification_data.get("member_name", ""),
            plan_name=verification_data.get("plan_name", ""),
            effective_date=verification_data.get("effective_date", ""),
            termination_date=verification_data.get("termination_date"),
            coverage_status=verification_data.get("coverage_status", "unknown"),
            copay_info=verification_data.get("copay_info", {}),
            deductible_info=verification_data.get("deductible_info", {}),
            verification_id=str(verification_record.id),
            timestamp=verification_record.created_at
        )
        
    except Exception as e:
        logger.error(f"Insurance verification failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Insurance verification failed: {str(e)}"
        )


@router.post("/analyze-coverage", response_model=CoverageAnalysisResponse)
async def analyze_coverage(
    request: CoverageAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze insurance coverage for specific procedures.
    
    This endpoint analyzes insurance coverage for specific procedures using
    the EnhancedAgentOrchestrator to determine coverage, patient responsibility,
    and authorization requirements.
    
    Args:
        request: Coverage analysis request
        background_tasks: FastAPI background tasks for async processing
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        CoverageAnalysisResponse: Coverage analysis results
        
    Raises:
        HTTPException: If analysis fails or invalid input
    """
    try:
        logger.info(f"Coverage analysis requested by user {current_user.id}")
        
        # Create agent context
        context = AgentContext(
            user_id=str(current_user.id),
            session_id=f"coverage_analysis_{datetime.utcnow().timestamp()}",
            request_id=f"coverage_analysis_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            metadata={
                "analysis_type": "procedure_coverage",
                "procedure_count": len(request.procedure_codes),
                "diagnosis_count": len(request.diagnosis_codes)
            },
            priority=AgentPriority.MEDIUM
        )
        
        # Initialize enhanced agent orchestrator
        orchestrator = EnhancedAgentOrchestrator()
        await orchestrator.initialize()
        
        # Execute coverage analysis workflow
        result = await orchestrator.execute_collaborative_workflow(
            workflow_id=f"coverage_analysis_{context.request_id}",
            workflow_type="coverage_analysis",
            context=context,
            parameters={
                "insurance_provider": request.insurance_provider,
                "member_id": request.member_id,
                "procedure_codes": request.procedure_codes,
                "diagnosis_codes": request.diagnosis_codes,
                "provider_npi": request.provider_npi,
                "service_date": request.service_date,
                "location": request.location,
                "enable_memory_sharing": True,
                "enable_reasoning_sharing": True,
                "autonomy_level": 0.7
            },
            collaboration_type="collaborative"
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Coverage analysis failed: {result.error_message}"
            )
        
        # Extract analysis results
        analysis_data = result.results.get("coverage_analysis", {})
        
        # Create analysis record
        analysis_record = CoverageAnalysis(
            user_id=current_user.id,
            insurance_provider=request.insurance_provider,
            member_id=request.member_id,
            analysis_type="coverage_analysis",
            analysis_data=result.results,
            is_covered=analysis_data.get("is_covered", False),
            coverage_percentage=analysis_data.get("coverage_percentage", 0.0),
            patient_responsibility=analysis_data.get("patient_responsibility", 0.0),
            insurance_payment=analysis_data.get("insurance_payment", 0.0)
        )
        
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)
        
        # Log analysis for monitoring
        background_tasks.add_task(
            logger.info,
            f"Coverage analysis completed for user {current_user.id}: "
            f"covered={analysis_data.get('is_covered')}, "
            f"coverage_percentage={analysis_data.get('coverage_percentage')}%"
        )
        
        return CoverageAnalysisResponse(
            is_covered=analysis_data.get("is_covered", False),
            coverage_percentage=analysis_data.get("coverage_percentage", 0.0),
            patient_responsibility=analysis_data.get("patient_responsibility", 0.0),
            insurance_payment=analysis_data.get("insurance_payment", 0.0),
            prior_authorization_required=analysis_data.get("prior_authorization_required", False),
            coverage_details=analysis_data.get("coverage_details", []),
            exclusions=analysis_data.get("exclusions", []),
            limitations=analysis_data.get("limitations", []),
            analysis_id=str(analysis_record.id),
            timestamp=analysis_record.created_at
        )
        
    except Exception as e:
        logger.error(f"Coverage analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Coverage analysis failed: {str(e)}"
        )


@router.post("/estimate-cost", response_model=CostEstimateResponse)
async def estimate_cost(
    request: CostEstimateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Estimate healthcare costs and patient responsibility.
    
    This endpoint provides cost estimation using the EnhancedAgentOrchestrator
    to analyze costs, identify savings opportunities, and suggest alternatives.
    
    Args:
        request: Cost estimation request
        background_tasks: FastAPI background tasks for async processing
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        CostEstimateResponse: Cost estimation results
        
    Raises:
        HTTPException: If estimation fails or invalid input
    """
    try:
        logger.info(f"Cost estimation requested by user {current_user.id}")
        
        # Create agent context
        context = AgentContext(
            user_id=str(current_user.id),
            session_id=f"cost_estimate_{datetime.utcnow().timestamp()}",
            request_id=f"cost_estimate_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            metadata={
                "estimate_type": "procedure_cost",
                "procedure_count": len(request.procedures),
                "facility_type": request.facility_type,
                "urgency": request.urgency
            },
            priority=AgentPriority.MEDIUM
        )
        
        # Initialize enhanced agent orchestrator
        orchestrator = EnhancedAgentOrchestrator()
        await orchestrator.initialize()
        
        # Execute cost estimation workflow
        result = await orchestrator.execute_collaborative_workflow(
            workflow_id=f"cost_estimation_{context.request_id}",
            workflow_type="cost_estimation",
            context=context,
            parameters={
                "insurance_provider": request.insurance_provider,
                "member_id": request.member_id,
                "procedures": request.procedures,
                "provider_id": request.provider_id,
                "facility_type": request.facility_type,
                "urgency": request.urgency,
                "enable_memory_sharing": True,
                "enable_reasoning_sharing": True,
                "autonomy_level": 0.8
            },
            collaboration_type="collaborative"
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Cost estimation failed: {result.error_message}"
            )
        
        # Extract estimation results
        estimate_data = result.results.get("cost_estimation", {})
        
        # Create estimation record
        estimation_record = CoverageAnalysis(
            user_id=current_user.id,
            insurance_provider=request.insurance_provider,
            member_id=request.member_id,
            analysis_type="cost_estimation",
            analysis_data=result.results,
            is_covered=True,  # Cost estimation assumes coverage
            coverage_percentage=100.0,
            patient_responsibility=estimate_data.get("patient_responsibility", 0.0),
            insurance_payment=estimate_data.get("insurance_coverage", 0.0)
        )
        
        db.add(estimation_record)
        db.commit()
        db.refresh(estimation_record)
        
        # Log estimation for monitoring
        background_tasks.add_task(
            logger.info,
            f"Cost estimation completed for user {current_user.id}: "
            f"total_cost=${estimate_data.get('total_cost', 0):.2f}, "
            f"patient_responsibility=${estimate_data.get('patient_responsibility', 0):.2f}"
        )
        
        return CostEstimateResponse(
            total_cost=estimate_data.get("total_cost", 0.0),
            patient_responsibility=estimate_data.get("patient_responsibility", 0.0),
            insurance_coverage=estimate_data.get("insurance_coverage", 0.0),
            cost_breakdown=estimate_data.get("cost_breakdown", []),
            savings_opportunities=estimate_data.get("savings_opportunities", []),
            alternative_providers=estimate_data.get("alternative_providers", []),
            estimate_id=str(estimation_record.id),
            timestamp=estimation_record.created_at
        )
        
    except Exception as e:
        logger.error(f"Cost estimation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Cost estimation failed: {str(e)}"
        )


@router.get("/providers/list")
async def get_insurance_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of supported insurance providers.
    
    This endpoint provides a comprehensive list of insurance providers
    supported by the system for verification and analysis.
    
    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        List: Supported insurance providers
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Get insurance providers
        providers = db.query(InsuranceProvider).all()
        
        provider_list = []
        for provider in providers:
            provider_list.append({
                "id": str(provider.id),
                "name": provider.name,
                "type": provider.type,
                "website": provider.website,
                "phone": provider.phone,
                "supported_features": provider.supported_features or []
            })
        
        return {
            "providers": provider_list,
            "total_count": len(provider_list),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get insurance providers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get insurance providers: {str(e)}"
        )


@router.get("/history/{user_id}")
async def get_insurance_history(
    user_id: str,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get insurance analysis history for a user.
    
    This endpoint retrieves the history of insurance verifications, coverage
    analyses, and cost estimations for a specific user.
    
    Args:
        user_id: ID of the user whose history to retrieve
        page: Page number for pagination
        page_size: Number of items per page
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        Dict: Paginated insurance history
        
    Raises:
        HTTPException: If access denied or retrieval fails
    """
    try:
        # Check permissions
        if str(current_user.id) != user_id and not check_permissions(current_user, ["admin", "healthcare_provider"]):
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only view your own insurance history"
            )
        
        # Calculate offset for pagination
        offset = (page - 1) * page_size
        
        # Query insurance analyses
        analyses_query = db.query(CoverageAnalysis).filter(
            CoverageAnalysis.user_id == user_id
        ).order_by(CoverageAnalysis.created_at.desc())
        
        total_count = analyses_query.count()
        analyses = analyses_query.offset(offset).limit(page_size).all()
        
        # Convert to response format
        analysis_list = []
        for analysis in analyses:
            analysis_list.append({
                "id": str(analysis.id),
                "insurance_provider": analysis.insurance_provider,
                "analysis_type": analysis.analysis_type,
                "is_covered": analysis.is_covered,
                "coverage_percentage": analysis.coverage_percentage,
                "patient_responsibility": analysis.patient_responsibility,
                "insurance_payment": analysis.insurance_payment,
                "created_at": analysis.created_at.isoformat()
            })
        
        return {
            "analyses": analysis_list,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve insurance history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve insurance history: {str(e)}"
        )
