"""
Healthcare provider management API routes.

This module provides endpoints for healthcare provider search, matching, and management.
It integrates with the EnhancedProviderMatchingAgent for intelligent provider recommendations
based on patient needs, location, and preferences.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from ...core.security import get_current_user, check_permissions
from ...core.logging import get_logger
from ...database.session import get_db
from ...database.models import User, HealthcareProvider, ProviderSpecialty, ProviderReview
from ...ai.agents.enhanced_base_agent import AgentContext, AgentPriority
from ...ai.agents.enhanced_agent_orchestrator import EnhancedAgentOrchestrator

logger = get_logger(__name__)
router = APIRouter()


class ProviderSearchRequest(BaseModel):
    """Request model for provider search."""
    location: Optional[str] = Field(None, description="Location (city, state, or zip code)")
    specialty: Optional[str] = Field(None, description="Medical specialty")
    insurance: Optional[str] = Field(None, description="Insurance provider")
    availability: Optional[str] = Field(None, description="Required availability (weekdays, weekends, etc.)")
    languages: Optional[List[str]] = Field(None, description="Preferred languages")
    gender: Optional[str] = Field(None, description="Preferred provider gender")
    rating_min: Optional[float] = Field(None, description="Minimum rating (1-5)")
    distance_max: Optional[float] = Field(None, description="Maximum distance in miles")
    conditions: Optional[List[str]] = Field(None, description="Specific medical conditions")
    urgency: Optional[str] = Field(None, description="Urgency level (routine, urgent, emergency)")


class ProviderResponse(BaseModel):
    """Response model for healthcare provider."""
    id: str = Field(..., description="Provider ID")
    name: str = Field(..., description="Provider name")
    specialty: str = Field(..., description="Medical specialty")
    location: Dict[str, Any] = Field(..., description="Location information")
    contact_info: Dict[str, Any] = Field(..., description="Contact information")
    availability: Dict[str, Any] = Field(..., description="Availability schedule")
    insurance_accepted: List[str] = Field(..., description="Accepted insurance providers")
    languages: List[str] = Field(..., description="Languages spoken")
    rating: float = Field(..., description="Average rating (1-5)")
    review_count: int = Field(..., description="Number of reviews")
    experience_years: int = Field(..., description="Years of experience")
    education: List[str] = Field(..., description="Education and credentials")
    certifications: List[str] = Field(..., description="Professional certifications")
    match_score: float = Field(..., description="Match score for current search (0-1)")
    distance_miles: Optional[float] = Field(None, description="Distance from search location")


class ProviderSearchResponse(BaseModel):
    """Response model for provider search results."""
    providers: List[ProviderResponse] = Field(..., description="List of matching providers")
    total_count: int = Field(..., description="Total number of matching providers")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    search_metadata: Dict[str, Any] = Field(..., description="Search metadata and filters applied")


class ProviderDetailResponse(BaseModel):
    """Response model for detailed provider information."""
    provider: ProviderResponse = Field(..., description="Provider information")
    reviews: List[Dict[str, Any]] = Field(..., description="Recent reviews")
    availability_slots: List[Dict[str, Any]] = Field(..., description="Available appointment slots")
    specialties: List[str] = Field(..., description="All specialties")
    procedures: List[str] = Field(..., description="Procedures performed")
    hospital_affiliations: List[str] = Field(..., description="Hospital affiliations")
    research_interests: List[str] = Field(..., description="Research interests")
    publications: List[Dict[str, Any]] = Field(..., description="Recent publications")


@router.post("/search", response_model=ProviderSearchResponse)
async def search_providers(
    request: ProviderSearchRequest,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for healthcare providers.
    
    This endpoint provides intelligent provider search using the EnhancedProviderMatchingAgent.
    It considers patient needs, location, insurance, and preferences to find the best matches.
    
    Args:
        request: Provider search criteria
        page: Page number for pagination
        page_size: Number of items per page
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        ProviderSearchResponse: Paginated list of matching providers
        
    Raises:
        HTTPException: If search fails or invalid input
    """
    try:
        logger.info(f"Provider search requested by user {current_user.id}")
        
        # Create agent context
        context = AgentContext(
            user_id=str(current_user.id),
            session_id=f"provider_search_{datetime.utcnow().timestamp()}",
            request_id=f"provider_search_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            metadata={
                "search_type": "provider_matching",
                "has_location": bool(request.location),
                "has_specialty": bool(request.specialty),
                "has_insurance": bool(request.insurance)
            },
            priority=AgentPriority.MEDIUM
        )
        
        # Initialize enhanced agent orchestrator
        orchestrator = EnhancedAgentOrchestrator()
        await orchestrator.initialize()
        
        # Execute provider matching workflow
        result = await orchestrator.execute_collaborative_workflow(
            workflow_id=f"provider_search_{context.request_id}",
            workflow_type="provider_matching",
            context=context,
            parameters={
                "location": request.location,
                "specialty": request.specialty,
                "insurance": request.insurance,
                "availability": request.availability,
                "languages": request.languages or [],
                "gender": request.gender,
                "rating_min": request.rating_min,
                "distance_max": request.distance_max,
                "conditions": request.conditions or [],
                "urgency": request.urgency,
                "enable_memory_sharing": True,
                "enable_reasoning_sharing": True,
                "autonomy_level": 0.7
            },
            collaboration_type="collaborative"
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Provider search failed: {result.error_message}"
            )
        
        # Extract provider recommendations
        provider_recommendations = result.results.get("provider_recommendations", [])
        
        # Get provider IDs from recommendations
        provider_ids = [rec.get("provider_id") for rec in provider_recommendations if rec.get("provider_id")]
        
        # Query providers from database
        providers_query = db.query(HealthcareProvider)
        
        if provider_ids:
            # Filter by recommended providers
            providers_query = providers_query.filter(HealthcareProvider.id.in_(provider_ids))
        else:
            # Fallback to basic search if no AI recommendations
            if request.specialty:
                providers_query = providers_query.join(ProviderSpecialty).filter(
                    ProviderSpecialty.specialty_name.ilike(f"%{request.specialty}%")
                )
            
            if request.location:
                providers_query = providers_query.filter(
                    or_(
                        HealthcareProvider.city.ilike(f"%{request.location}%"),
                        HealthcareProvider.state.ilike(f"%{request.location}%"),
                        HealthcareProvider.zip_code.ilike(f"%{request.location}%")
                    )
                )
        
        # Apply additional filters
        if request.rating_min:
            providers_query = providers_query.filter(HealthcareProvider.rating >= request.rating_min)
        
        # Get total count and paginate
        total_count = providers_query.count()
        offset = (page - 1) * page_size
        providers = providers_query.offset(offset).limit(page_size).all()
        
        # Convert to response format
        provider_list = []
        for provider in providers:
            # Find matching recommendation for score
            match_score = 0.5  # Default score
            for rec in provider_recommendations:
                if rec.get("provider_id") == str(provider.id):
                    match_score = rec.get("match_score", 0.5)
                    break
            
            provider_list.append(ProviderResponse(
                id=str(provider.id),
                name=provider.name,
                specialty=provider.primary_specialty,
                location={
                    "address": provider.address,
                    "city": provider.city,
                    "state": provider.state,
                    "zip_code": provider.zip_code,
                    "coordinates": {
                        "lat": provider.latitude,
                        "lng": provider.longitude
                    } if provider.latitude and provider.longitude else None
                },
                contact_info={
                    "phone": provider.phone,
                    "email": provider.email,
                    "website": provider.website
                },
                availability=provider.availability_schedule or {},
                insurance_accepted=provider.insurance_accepted or [],
                languages=provider.languages or [],
                rating=provider.rating or 0.0,
                review_count=provider.review_count or 0,
                experience_years=provider.experience_years or 0,
                education=provider.education or [],
                certifications=provider.certifications or [],
                match_score=match_score,
                distance_miles=None  # Would be calculated based on location
            ))
        
        return ProviderSearchResponse(
            providers=provider_list,
            total_count=total_count,
            page=page,
            page_size=page_size,
            search_metadata={
                "filters_applied": request.dict(exclude_none=True),
                "ai_recommendations_used": bool(provider_ids),
                "search_timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Provider search failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Provider search failed: {str(e)}"
        )


@router.get("/{provider_id}", response_model=ProviderDetailResponse)
async def get_provider_details(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a healthcare provider.
    
    This endpoint provides comprehensive information about a specific provider,
    including reviews, availability, specialties, and professional background.
    
    Args:
        provider_id: ID of the provider
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        ProviderDetailResponse: Detailed provider information
        
    Raises:
        HTTPException: If provider not found or access denied
    """
    try:
        # Get provider
        provider = db.query(HealthcareProvider).filter(
            HealthcareProvider.id == provider_id
        ).first()
        
        if not provider:
            raise HTTPException(
                status_code=404,
                detail="Provider not found"
            )
        
        # Get recent reviews
        reviews = db.query(ProviderReview).filter(
            ProviderReview.provider_id == provider_id
        ).order_by(ProviderReview.created_at.desc()).limit(10).all()
        
        review_list = []
        for review in reviews:
            review_list.append({
                "id": str(review.id),
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.isoformat(),
                "user_name": review.user_name or "Anonymous"
            })
        
        # Get all specialties
        specialties = db.query(ProviderSpecialty).filter(
            ProviderSpecialty.provider_id == provider_id
        ).all()
        
        specialty_list = [spec.specialty_name for spec in specialties]
        
        # Create provider response
        provider_response = ProviderResponse(
            id=str(provider.id),
            name=provider.name,
            specialty=provider.primary_specialty,
            location={
                "address": provider.address,
                "city": provider.city,
                "state": provider.state,
                "zip_code": provider.zip_code,
                "coordinates": {
                    "lat": provider.latitude,
                    "lng": provider.longitude
                } if provider.latitude and provider.longitude else None
            },
            contact_info={
                "phone": provider.phone,
                "email": provider.email,
                "website": provider.website
            },
            availability=provider.availability_schedule or {},
            insurance_accepted=provider.insurance_accepted or [],
            languages=provider.languages or [],
            rating=provider.rating or 0.0,
            review_count=provider.review_count or 0,
            experience_years=provider.experience_years or 0,
            education=provider.education or [],
            certifications=provider.certifications or [],
            match_score=1.0,  # Perfect match for specific provider
            distance_miles=None
        )
        
        return ProviderDetailResponse(
            provider=provider_response,
            reviews=review_list,
            availability_slots=[],  # Would be populated from scheduling system
            specialties=specialty_list,
            procedures=provider.procedures or [],
            hospital_affiliations=provider.hospital_affiliations or [],
            research_interests=provider.research_interests or [],
            publications=provider.publications or []
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get provider details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get provider details: {str(e)}"
        )


@router.get("/specialties/list")
async def get_specialties(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of available medical specialties.
    
    This endpoint provides a comprehensive list of medical specialties
    available in the system for provider search and filtering.
    
    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        List: Available medical specialties
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Get unique specialties
        specialties = db.query(ProviderSpecialty.specialty_name).distinct().all()
        
        specialty_list = [spec.specialty_name for spec in specialties]
        
        return {
            "specialties": sorted(specialty_list),
            "total_count": len(specialty_list),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get specialties: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get specialties: {str(e)}"
        )


@router.get("/stats/overview")
async def get_provider_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get provider statistics overview.
    
    This endpoint provides aggregated statistics about healthcare providers,
    including specialty distribution, average ratings, and geographic coverage.
    
    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        Dict: Provider statistics
        
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
        total_providers = db.query(HealthcareProvider).count()
        
        # Get specialty distribution
        specialty_stats = db.query(
            ProviderSpecialty.specialty_name,
            db.func.count(ProviderSpecialty.provider_id)
        ).group_by(ProviderSpecialty.specialty_name).all()
        
        # Get average rating
        avg_rating = db.query(
            db.func.avg(HealthcareProvider.rating)
        ).scalar() or 0.0
        
        # Get geographic distribution
        state_stats = db.query(
            HealthcareProvider.state,
            db.func.count(HealthcareProvider.id)
        ).group_by(HealthcareProvider.state).all()
        
        return {
            "total_providers": total_providers,
            "specialty_distribution": dict(specialty_stats),
            "average_rating": round(avg_rating, 2),
            "geographic_distribution": dict(state_stats),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get provider stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get provider stats: {str(e)}"
        )
