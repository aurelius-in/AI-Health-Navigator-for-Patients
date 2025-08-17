"""
Repository classes for data access.

This module implements the repository pattern for clean data access layer.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime, timedelta
import logging

from .models import (
    User, SymptomAnalysis, TriageAssessment, HealthcareProvider,
    InsuranceProvider, HealthRecord, Notification, AuditLog,
    UserRole, SeverityLevel, UrgencyLevel, RecordType, RecordStatus
)

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository class with common CRUD operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add(self, entity):
        """Add an entity to the session."""
        self.session.add(entity)
        return entity
    
    def commit(self):
        """Commit the current transaction."""
        self.session.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()
    
    def refresh(self, entity):
        """Refresh an entity from the database."""
        self.session.refresh(entity)
        return entity


class UserRepository(BaseRepository):
    """Repository for user operations."""
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        user = User(**user_data)
        self.add(user)
        self.commit()
        return user
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.session.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.session.query(User).filter(User.email == email).first()
    
    def get_active_users(self) -> List[User]:
        """Get all active users."""
        return self.session.query(User).filter(User.is_active == True).all()
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user information."""
        user = self.get_by_id(user_id)
        if user:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            self.commit()
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Soft delete a user."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            user.updated_at = datetime.utcnow()
            self.commit()
            return True
        return False
    
    def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get users by role."""
        return self.session.query(User).filter(
            and_(User.role == role, User.is_active == True)
        ).all()


class SymptomRepository(BaseRepository):
    """Repository for symptom analysis operations."""
    
    def create_analysis(self, analysis_data: Dict[str, Any]) -> SymptomAnalysis:
        """Create a new symptom analysis."""
        analysis = SymptomAnalysis(**analysis_data)
        self.add(analysis)
        self.commit()
        return analysis
    
    def get_by_id(self, analysis_id: str) -> Optional[SymptomAnalysis]:
        """Get symptom analysis by ID."""
        return self.session.query(SymptomAnalysis).filter(
            SymptomAnalysis.id == analysis_id
        ).first()
    
    def get_by_user_id(self, user_id: str, limit: int = 50, offset: int = 0) -> List[SymptomAnalysis]:
        """Get symptom analyses for a user."""
        return self.session.query(SymptomAnalysis).filter(
            SymptomAnalysis.user_id == user_id
        ).order_by(desc(SymptomAnalysis.created_at)).limit(limit).offset(offset).all()
    
    def get_by_severity(self, severity: SeverityLevel, limit: int = 50) -> List[SymptomAnalysis]:
        """Get symptom analyses by severity level."""
        return self.session.query(SymptomAnalysis).filter(
            SymptomAnalysis.severity == severity
        ).order_by(desc(SymptomAnalysis.created_at)).limit(limit).all()
    
    def get_recent_analyses(self, days: int = 7) -> List[SymptomAnalysis]:
        """Get recent symptom analyses."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.session.query(SymptomAnalysis).filter(
            SymptomAnalysis.created_at >= cutoff_date
        ).order_by(desc(SymptomAnalysis.created_at)).all()
    
    def update_analysis(self, analysis_id: str, update_data: Dict[str, Any]) -> Optional[SymptomAnalysis]:
        """Update symptom analysis."""
        analysis = self.get_by_id(analysis_id)
        if analysis:
            for key, value in update_data.items():
                if hasattr(analysis, key):
                    setattr(analysis, key, value)
            analysis.updated_at = datetime.utcnow()
            self.commit()
        return analysis


class TriageRepository(BaseRepository):
    """Repository for triage assessment operations."""
    
    def create_assessment(self, assessment_data: Dict[str, Any]) -> TriageAssessment:
        """Create a new triage assessment."""
        assessment = TriageAssessment(**assessment_data)
        self.add(assessment)
        self.commit()
        return assessment
    
    def get_by_id(self, assessment_id: str) -> Optional[TriageAssessment]:
        """Get triage assessment by ID."""
        return self.session.query(TriageAssessment).filter(
            TriageAssessment.id == assessment_id
        ).first()
    
    def get_by_user_id(self, user_id: str, limit: int = 50, offset: int = 0) -> List[TriageAssessment]:
        """Get triage assessments for a user."""
        return self.session.query(TriageAssessment).filter(
            TriageAssessment.user_id == user_id
        ).order_by(desc(TriageAssessment.created_at)).limit(limit).offset(offset).all()
    
    def get_by_urgency(self, urgency: UrgencyLevel, limit: int = 50) -> List[TriageAssessment]:
        """Get triage assessments by urgency level."""
        return self.session.query(TriageAssessment).filter(
            TriageAssessment.urgency == urgency
        ).order_by(desc(TriageAssessment.created_at)).limit(limit).all()
    
    def get_emergency_assessments(self, limit: int = 20) -> List[TriageAssessment]:
        """Get emergency level assessments."""
        return self.session.query(TriageAssessment).filter(
            or_(
                TriageAssessment.urgency == UrgencyLevel.IMMEDIATE,
                TriageAssessment.urgency == UrgencyLevel.EMERGENCY
            )
        ).order_by(desc(TriageAssessment.created_at)).limit(limit).all()


class ProviderRepository(BaseRepository):
    """Repository for healthcare provider operations."""
    
    def create_provider(self, provider_data: Dict[str, Any]) -> HealthcareProvider:
        """Create a new healthcare provider."""
        provider = HealthcareProvider(**provider_data)
        self.add(provider)
        self.commit()
        return provider
    
    def get_by_id(self, provider_id: str) -> Optional[HealthcareProvider]:
        """Get provider by ID."""
        return self.session.query(HealthcareProvider).filter(
            HealthcareProvider.id == provider_id
        ).first()
    
    def get_all_active(self) -> List[HealthcareProvider]:
        """Get all active providers."""
        return self.session.query(HealthcareProvider).filter(
            HealthcareProvider.is_active == True
        ).all()
    
    def search_providers(
        self,
        location: Optional[str] = None,
        specialty: Optional[List[str]] = None,
        insurance: Optional[List[str]] = None,
        rating_min: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[HealthcareProvider]:
        """Search providers with filters."""
        query = self.session.query(HealthcareProvider).filter(
            HealthcareProvider.is_active == True
        )
        
        if location:
            query = query.filter(
                or_(
                    HealthcareProvider.city.ilike(f"%{location}%"),
                    HealthcareProvider.state.ilike(f"%{location}%")
                )
            )
        
        if specialty:
            for spec in specialty:
                query = query.filter(HealthcareProvider.specialty.contains([spec]))
        
        if insurance:
            for ins in insurance:
                query = query.filter(HealthcareProvider.insurance_accepted.contains([ins]))
        
        if rating_min is not None:
            query = query.filter(HealthcareProvider.rating >= rating_min)
        
        return query.order_by(desc(HealthcareProvider.rating)).limit(limit).offset(offset).all()
    
    def get_by_specialty(self, specialty: str, limit: int = 50) -> List[HealthcareProvider]:
        """Get providers by specialty."""
        return self.session.query(HealthcareProvider).filter(
            and_(
                HealthcareProvider.is_active == True,
                HealthcareProvider.specialty.contains([specialty])
            )
        ).order_by(desc(HealthcareProvider.rating)).limit(limit).all()
    
    def update_provider(self, provider_id: str, update_data: Dict[str, Any]) -> Optional[HealthcareProvider]:
        """Update provider information."""
        provider = self.get_by_id(provider_id)
        if provider:
            for key, value in update_data.items():
                if hasattr(provider, key):
                    setattr(provider, key, value)
            provider.updated_at = datetime.utcnow()
            self.commit()
        return provider


class InsuranceRepository(BaseRepository):
    """Repository for insurance provider operations."""
    
    def create_provider(self, provider_data: Dict[str, Any]) -> InsuranceProvider:
        """Create a new insurance provider."""
        provider = InsuranceProvider(**provider_data)
        self.add(provider)
        self.commit()
        return provider
    
    def get_by_id(self, provider_id: str) -> Optional[InsuranceProvider]:
        """Get insurance provider by ID."""
        return self.session.query(InsuranceProvider).filter(
            InsuranceProvider.id == provider_id
        ).first()
    
    def get_all_active(self) -> List[InsuranceProvider]:
        """Get all active insurance providers."""
        return self.session.query(InsuranceProvider).filter(
            InsuranceProvider.is_active == True
        ).all()
    
    def get_by_type(self, provider_type: str) -> List[InsuranceProvider]:
        """Get insurance providers by type."""
        return self.session.query(InsuranceProvider).filter(
            and_(
                InsuranceProvider.type == provider_type,
                InsuranceProvider.is_active == True
            )
        ).all()


class HealthRecordRepository(BaseRepository):
    """Repository for health record operations."""
    
    def create_record(self, record_data: Dict[str, Any]) -> HealthRecord:
        """Create a new health record."""
        record = HealthRecord(**record_data)
        self.add(record)
        self.commit()
        return record
    
    def get_by_id(self, record_id: str) -> Optional[HealthRecord]:
        """Get health record by ID."""
        return self.session.query(HealthRecord).filter(
            HealthRecord.id == record_id
        ).first()
    
    def get_by_user_id(self, user_id: str, limit: int = 50, offset: int = 0) -> List[HealthRecord]:
        """Get health records for a user."""
        return self.session.query(HealthRecord).filter(
            HealthRecord.user_id == user_id
        ).order_by(desc(HealthRecord.date)).limit(limit).offset(offset).all()
    
    def get_by_type(self, user_id: str, record_type: RecordType, limit: int = 50) -> List[HealthRecord]:
        """Get health records by type for a user."""
        return self.session.query(HealthRecord).filter(
            and_(
                HealthRecord.user_id == user_id,
                HealthRecord.type == record_type
            )
        ).order_by(desc(HealthRecord.date)).limit(limit).all()
    
    def get_by_status(self, user_id: str, status: RecordStatus, limit: int = 50) -> List[HealthRecord]:
        """Get health records by status for a user."""
        return self.session.query(HealthRecord).filter(
            and_(
                HealthRecord.user_id == user_id,
                HealthRecord.status == status
            )
        ).order_by(desc(HealthRecord.date)).limit(limit).all()
    
    def update_record(self, record_id: str, update_data: Dict[str, Any]) -> Optional[HealthRecord]:
        """Update health record."""
        record = self.get_by_id(record_id)
        if record:
            for key, value in update_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            record.updated_at = datetime.utcnow()
            self.commit()
        return record
    
    def delete_record(self, record_id: str) -> bool:
        """Delete a health record."""
        record = self.get_by_id(record_id)
        if record:
            self.session.delete(record)
            self.commit()
            return True
        return False


class NotificationRepository(BaseRepository):
    """Repository for notification operations."""
    
    def create_notification(self, notification_data: Dict[str, Any]) -> Notification:
        """Create a new notification."""
        notification = Notification(**notification_data)
        self.add(notification)
        self.commit()
        return notification
    
    def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        return self.session.query(Notification).filter(
            Notification.id == notification_id
        ).first()
    
    def get_by_user_id(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Notification]:
        """Get notifications for a user."""
        return self.session.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(desc(Notification.created_at)).limit(limit).offset(offset).all()
    
    def get_unread_by_user_id(self, user_id: str, limit: int = 50) -> List[Notification]:
        """Get unread notifications for a user."""
        return self.session.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.read == False
            )
        ).order_by(desc(Notification.created_at)).limit(limit).all()
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        notification = self.get_by_id(notification_id)
        if notification:
            notification.read = True
            notification.updated_at = datetime.utcnow()
            self.commit()
            return True
        return False
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        result = self.session.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.read == False
            )
        ).update({
            Notification.read: True,
            Notification.updated_at: datetime.utcnow()
        })
        self.commit()
        return result
    
    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification."""
        notification = self.get_by_id(notification_id)
        if notification:
            self.session.delete(notification)
            self.commit()
            return True
        return False


class AuditRepository(BaseRepository):
    """Repository for audit log operations."""
    
    def create_audit_log(self, audit_data: Dict[str, Any]) -> AuditLog:
        """Create a new audit log entry."""
        audit_log = AuditLog(**audit_data)
        self.add(audit_log)
        self.commit()
        return audit_log
    
    def get_by_user_id(self, user_id: str, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a user."""
        return self.session.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(desc(AuditLog.created_at)).limit(limit).all()
    
    def get_by_action(self, action: str, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by action."""
        return self.session.query(AuditLog).filter(
            AuditLog.action == action
        ).order_by(desc(AuditLog.created_at)).limit(limit).all()
    
    def get_recent_logs(self, days: int = 30, limit: int = 1000) -> List[AuditLog]:
        """Get recent audit logs."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.session.query(AuditLog).filter(
            AuditLog.created_at >= cutoff_date
        ).order_by(desc(AuditLog.created_at)).limit(limit).all()
