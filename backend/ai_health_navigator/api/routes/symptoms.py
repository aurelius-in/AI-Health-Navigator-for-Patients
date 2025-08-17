"""
Symptom analysis API routes.
"""

import time
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, Field

from ...core.logging import get_logger, HealthNavigatorLogger
from ...ai.models import model_manager, SymptomAnalysis
from ...ai.llm_service import llm_service

logger = get_logger(__name__)
health_logger = HealthNavigatorLogger("SymptomsAPI")

router = APIRouter()


class SymptomRequest(BaseModel):
    """Symptom analysis request."""
    
    symptoms: str = Field(..., description="Patient symptoms description", min_length=10)
    age: Optional[int] = Field(None, description="Patient age", ge=0, le=120)
    gender: Optional[str] = Field(None, description="Patient gender")
    duration: Optional[str] = Field(None, description="Symptom duration")
    severity: Optional[str] = Field(None, description="Symptom severity")
    language: Optional[str] = Field(default="en", description="Language code")
    include_llm_analysis: bool = Field(default=True, description="Include LLM analysis")
    provider: Optional[str] = Field(None, description="Preferred LLM provider")


class SymptomResponse(BaseModel):
    """Symptom analysis response."""
    
    request_id: str = Field(description="Unique request identifier")
    symptoms_analysis: SymptomAnalysis = Field(description="AI symptom analysis")
    llm_analysis: Optional[Dict[str, Any]] = Field(description="LLM analysis if requested")
    processing_time: float = Field(description="Processing time in seconds")
    confidence: float = Field(description="Overall confidence score")
    recommendations: Dict[str, Any] = Field(description="Care recommendations")
    warnings: List[str] = Field(description="Important warnings")
    next_steps: List[str] = Field(description="Recommended next steps")


class BatchSymptomRequest(BaseModel):
    """Batch symptom analysis request."""
    
    requests: List[SymptomRequest] = Field(..., description="List of symptom requests", max_items=10)
    priority: str = Field(default="normal", description="Processing priority")


class BatchSymptomResponse(BaseModel):
    """Batch symptom analysis response."""
    
    batch_id: str = Field(description="Batch identifier")
    results: List[SymptomResponse] = Field(description="Analysis results")
    processing_time: float = Field(description="Total processing time")
    success_count: int = Field(description="Number of successful analyses")
    error_count: int = Field(description="Number of failed analyses")


async def get_current_user(request: Request):
    """Get current authenticated user."""
    # Placeholder for authentication
    return {"id": "user_123", "email": "user@example.com"}


@router.post("/analyze", response_model=SymptomResponse)
async def analyze_symptoms(
    request: SymptomRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    http_request: Request = None
):
    """
    Analyze patient symptoms using advanced AI models.
    
    This endpoint provides comprehensive symptom analysis using:
    - Multi-modal AI models (transformer, ML, semantic)
    - Large Language Models for reasoning
    - Medical knowledge base integration
    - Risk assessment and triage recommendations
    """
    start_time = time.time()
    request_id = f"sym_{int(start_time * 1000)}"
    
    try:
        # Log the request
        health_logger.log_symptom_check(
            user_id=current_user["id"],
            symptoms=request.symptoms,
            confidence=0.0,  # Will be updated after analysis
            request_id=request_id
        )
        
        # Perform AI symptom analysis
        symptoms_analysis = await model_manager.analyze_symptoms(request.symptoms)
        
        # Perform LLM analysis if requested
        llm_analysis = None
        if request.include_llm_analysis:
            try:
                llm_response = await llm_service.analyze_symptoms(
                    symptoms=request.symptoms,
                    age=request.age,
                    gender=request.gender,
                    duration=request.duration,
                    severity=request.severity,
                    provider=request.provider
                )
                
                llm_analysis = {
                    "content": llm_response.content,
                    "model": llm_response.model,
                    "provider": llm_response.provider,
                    "tokens_used": llm_response.tokens_used,
                    "confidence": llm_response.confidence
                }
            except Exception as e:
                logger.warning(f"LLM analysis failed: {e}")
                llm_analysis = {"error": str(e)}
        
        # Calculate overall confidence
        overall_confidence = symptoms_analysis.confidence_score
        if llm_analysis and llm_analysis.get("confidence"):
            overall_confidence = (overall_confidence + llm_analysis["confidence"]) / 2
        
        # Generate recommendations
        recommendations = generate_recommendations(symptoms_analysis, llm_analysis)
        
        # Generate warnings
        warnings = generate_warnings(symptoms_analysis)
        
        # Generate next steps
        next_steps = generate_next_steps(symptoms_analysis, recommendations)
        
        processing_time = time.time() - start_time
        
        # Log successful analysis
        health_logger.log_symptom_check(
            user_id=current_user["id"],
            symptoms=request.symptoms,
            confidence=overall_confidence,
            request_id=request_id,
            processing_time=processing_time
        )
        
        # Add background task for analytics
        background_tasks.add_task(
            log_analytics,
            request_id=request_id,
            user_id=current_user["id"],
            symptoms_analysis=symptoms_analysis,
            processing_time=processing_time
        )
        
        return SymptomResponse(
            request_id=request_id,
            symptoms_analysis=symptoms_analysis,
            llm_analysis=llm_analysis,
            processing_time=processing_time,
            confidence=overall_confidence,
            recommendations=recommendations,
            warnings=warnings,
            next_steps=next_steps
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        health_logger.log_error(e, {
            "request_id": request_id,
            "user_id": current_user["id"],
            "processing_time": processing_time
        })
        raise HTTPException(status_code=500, detail=f"Symptom analysis failed: {str(e)}")


@router.post("/analyze/batch", response_model=BatchSymptomResponse)
async def analyze_symptoms_batch(
    request: BatchSymptomRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Analyze multiple symptom requests in batch.
    
    Useful for processing multiple patients or scenarios efficiently.
    """
    start_time = time.time()
    batch_id = f"batch_{int(start_time * 1000)}"
    
    results = []
    success_count = 0
    error_count = 0
    
    for i, symptom_request in enumerate(request.requests):
        try:
            # Create individual request
            individual_request = SymptomRequest(**symptom_request.dict())
            
            # Analyze symptoms
            result = await analyze_symptoms(
                request=individual_request,
                background_tasks=BackgroundTasks(),
                current_user=current_user
            )
            
            results.append(result)
            success_count += 1
            
        except Exception as e:
            logger.error(f"Batch analysis failed for request {i}: {e}")
            error_count += 1
            
            # Add error result
            results.append(SymptomResponse(
                request_id=f"error_{i}",
                symptoms_analysis=SymptomAnalysis(
                    primary_symptoms=[],
                    secondary_symptoms=[],
                    confidence_score=0.0,
                    medical_conditions=[],
                    urgency_level="unknown",
                    recommended_care="Error occurred",
                    reasoning=f"Analysis failed: {str(e)}"
                ),
                processing_time=0.0,
                confidence=0.0,
                recommendations={"error": str(e)},
                warnings=["Analysis failed"],
                next_steps=["Contact support"]
            ))
    
    processing_time = time.time() - start_time
    
    return BatchSymptomResponse(
        batch_id=batch_id,
        results=results,
        processing_time=processing_time,
        success_count=success_count,
        error_count=error_count
    )


@router.get("/history/{user_id}")
async def get_symptom_history(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get symptom analysis history for a user.
    
    Returns previous symptom analyses with timestamps and outcomes.
    """
    # This would query a database for historical data
    # For now, return mock data
    return {
        "user_id": user_id,
        "analyses": [
            {
                "request_id": f"hist_{i}",
                "timestamp": "2024-01-01T12:00:00Z",
                "symptoms": "fever, cough",
                "urgency_level": "medium",
                "confidence": 0.85
            }
            for i in range(limit)
        ],
        "total_count": 100,
        "limit": limit,
        "offset": offset
    }


@router.get("/conditions")
async def get_medical_conditions(
    query: Optional[str] = None,
    limit: int = 20
):
    """
    Search medical conditions database.
    
    Returns matching medical conditions with ICD-10 codes and descriptions.
    """
    # This would query a medical conditions database
    # For now, return mock data
    conditions = [
        {
            "icd10_code": "R50.9",
            "name": "Fever, unspecified",
            "description": "Elevated body temperature",
            "symptoms": ["fever", "chills", "sweating"]
        },
        {
            "icd10_code": "R05.9",
            "name": "Cough, unspecified",
            "description": "Sudden expulsion of air from the lungs",
            "symptoms": ["cough", "sore throat", "chest discomfort"]
        }
    ]
    
    if query:
        conditions = [c for c in conditions if query.lower() in c["name"].lower()]
    
    return {
        "conditions": conditions[:limit],
        "total_count": len(conditions),
        "query": query
    }


def generate_recommendations(
    symptoms_analysis: SymptomAnalysis,
    llm_analysis: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate care recommendations based on analysis."""
    recommendations = {
        "immediate_action": symptoms_analysis.recommended_care,
        "care_level": symptoms_analysis.urgency_level,
        "providers": [],
        "medications": [],
        "lifestyle": [],
        "monitoring": []
    }
    
    # Add provider recommendations based on urgency
    if symptoms_analysis.urgency_level == "emergency":
        recommendations["providers"].append("Emergency Room")
    elif symptoms_analysis.urgency_level == "high":
        recommendations["providers"].extend(["Urgent Care", "Emergency Room"])
    elif symptoms_analysis.urgency_level == "medium":
        recommendations["providers"].append("Primary Care Physician")
    else:
        recommendations["providers"].append("Primary Care Physician")
    
    # Add monitoring recommendations
    if "fever" in symptoms_analysis.primary_symptoms:
        recommendations["monitoring"].append("Monitor temperature every 4 hours")
    
    if "cough" in symptoms_analysis.primary_symptoms:
        recommendations["lifestyle"].append("Stay hydrated and rest")
    
    return recommendations


def generate_warnings(symptoms_analysis: SymptomAnalysis) -> List[str]:
    """Generate warnings based on symptoms."""
    warnings = []
    
    # Emergency symptoms
    emergency_symptoms = ["chest pain", "severe bleeding", "unconsciousness"]
    if any(symptom in symptoms_analysis.primary_symptoms for symptom in emergency_symptoms):
        warnings.append("Seek immediate emergency medical attention")
    
    # High urgency symptoms
    if symptoms_analysis.urgency_level == "high":
        warnings.append("Urgent medical attention recommended within 2 hours")
    
    # Age-related warnings
    warnings.append("This analysis is for informational purposes only and should not replace professional medical advice")
    
    return warnings


def generate_next_steps(
    symptoms_analysis: SymptomAnalysis,
    recommendations: Dict[str, Any]
) -> List[str]:
    """Generate next steps for the patient."""
    next_steps = []
    
    # Immediate action
    next_steps.append(f"Follow recommended care: {symptoms_analysis.recommended_care}")
    
    # Provider contact
    if recommendations["providers"]:
        next_steps.append(f"Contact {recommendations['providers'][0]} for appointment")
    
    # Monitoring
    if recommendations["monitoring"]:
        next_steps.extend(recommendations["monitoring"])
    
    # Follow-up
    next_steps.append("Monitor symptoms and seek care if they worsen")
    
    return next_steps


async def log_analytics(
    request_id: str,
    user_id: str,
    symptoms_analysis: SymptomAnalysis,
    processing_time: float
):
    """Log analytics data for the symptom analysis."""
    try:
        # This would send analytics data to a monitoring system
        logger.info(
            "Analytics logged",
            request_id=request_id,
            user_id=user_id,
            urgency_level=symptoms_analysis.urgency_level,
            confidence=symptoms_analysis.confidence_score,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Failed to log analytics: {e}")
