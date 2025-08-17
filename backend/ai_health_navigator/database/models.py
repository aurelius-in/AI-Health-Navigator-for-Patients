"""
Database models for AI Health Navigator.

This module contains all SQLAlchemy ORM models for the healthcare application.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User roles in the system."""
    PATIENT = "patient"
    PROVIDER = "provider"
    ADMIN = "admin"


class UrgencyLevel(str, enum.Enum):
    """Triage urgency levels."""
    IMMEDIATE = "immediate"
    EMERGENCY = "emergency"
    URGENT = "urgent"
    PRIORITY = "priority"
    ROUTINE = "routine"


class SeverityLevel(str, enum.Enum):
    """Symptom severity levels."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class RecordType(str, enum.Enum):
    """Health record types."""
    SYMPTOM = "symptom"
    DIAGNOSIS = "diagnosis"
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    LAB = "lab"
    IMAGING = "imaging"


class RecordStatus(str, enum.Enum):
    """Health record status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ONGOING = "ongoing"


class NotificationType(str, enum.Enum):
    """Notification types."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class User(Base):
    """User model for patients and healthcare providers."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.PATIENT)
    
    # Emergency contact
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(200))
    emergency_contact_relationship: Mapped[Optional[str]] = mapped_column(String(100))
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    emergency_contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Insurance information
    insurance_provider: Mapped[Optional[str]] = mapped_column(String(200))
    insurance_member_id: Mapped[Optional[str]] = mapped_column(String(100))
    insurance_group_number: Mapped[Optional[str]] = mapped_column(String(100))
    insurance_plan_type: Mapped[Optional[str]] = mapped_column(String(100))
    insurance_effective_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    insurance_expiration_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Preferences (stored as JSON)
    preferences: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    symptom_analyses: Mapped[List["SymptomAnalysis"]] = relationship("SymptomAnalysis", back_populates="user")
    triage_assessments: Mapped[List["TriageAssessment"]] = relationship("TriageAssessment", back_populates="user")
    health_records: Mapped[List["HealthRecord"]] = relationship("HealthRecord", back_populates="user")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user")


class SymptomAnalysis(Base):
    """Symptom analysis results."""
    __tablename__ = "symptom_analyses"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    symptoms: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    severity: Mapped[SeverityLevel] = mapped_column(Enum(SeverityLevel), nullable=False)
    duration: Mapped[str] = mapped_column(String(100), nullable=False)
    additional_info: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    triggers: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    medications: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    allergies: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # Analysis results (stored as JSON)
    possible_conditions: Mapped[Optional[List[dict]]] = mapped_column(ARRAY(JSON))
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    urgency: Mapped[Optional[str]] = mapped_column(String(50))
    recommendations: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    warnings: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    next_steps: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # AI insights
    ai_model: Mapped[Optional[str]] = mapped_column(String(100))
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float)
    ai_reasoning: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="symptom_analyses")


class TriageAssessment(Base):
    """Triage assessment results."""
    __tablename__ = "triage_assessments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    symptoms: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    
    # Vital signs (stored as JSON)
    vital_signs: Mapped[Optional[dict]] = mapped_column(JSON)
    pain_level: Mapped[int] = mapped_column(Integer, nullable=False)
    consciousness: Mapped[str] = mapped_column(String(50), nullable=False)
    breathing: Mapped[str] = mapped_column(String(50), nullable=False)
    bleeding: Mapped[Optional[str]] = mapped_column(String(50))
    trauma: Mapped[Optional[bool]] = mapped_column(Boolean)
    pregnancy: Mapped[Optional[bool]] = mapped_column(Boolean)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Assessment results
    urgency: Mapped[UrgencyLevel] = mapped_column(Enum(UrgencyLevel), nullable=False)
    estimated_wait_time: Mapped[str] = mapped_column(String(100), nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    risk_factors: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    vital_signs_status: Mapped[Optional[str]] = mapped_column(String(50))
    
    # AI assessment
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float)
    ai_reasoning: Mapped[Optional[str]] = mapped_column(Text)
    ai_model: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="triage_assessments")


class HealthcareProvider(Base):
    """Healthcare provider information."""
    __tablename__ = "healthcare_providers"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)  # physician, nurse, specialist, etc.
    specialty: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    credentials: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    
    # Location
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(20), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    
    # Contact information
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    fax: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Availability (stored as JSON)
    availability: Mapped[Optional[List[dict]]] = mapped_column(ARRAY(JSON))
    insurance_accepted: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    languages: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    
    # Ratings and verification
    rating: Mapped[Optional[float]] = mapped_column(Float)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    accepting_patients: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class InsuranceProvider(Base):
    """Insurance provider information."""
    __tablename__ = "insurance_providers"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)  # private, medicare, medicaid, etc.
    
    # Coverage information (stored as JSON)
    coverage: Mapped[dict] = mapped_column(JSON, nullable=False)
    network: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Contact information
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    website: Mapped[str] = mapped_column(String(500), nullable=False)
    claims_address: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class HealthRecord(Base):
    """Health record entries."""
    __tablename__ = "health_records"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type: Mapped[RecordType] = mapped_column(Enum(RecordType), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(200))
    location: Mapped[Optional[str]] = mapped_column(String(500))
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    severity: Mapped[Optional[SeverityLevel]] = mapped_column(Enum(SeverityLevel))
    status: Mapped[RecordStatus] = mapped_column(Enum(RecordStatus), default=RecordStatus.ACTIVE)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Attachments (file paths/URLs stored as JSON)
    attachments: Mapped[Optional[List[dict]]] = mapped_column(ARRAY(JSON))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="health_records")


class Notification(Base):
    """User notifications."""
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    action_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")


class AuditLog(Base):
    """Audit log for HIPAA compliance."""
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100))
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User")
