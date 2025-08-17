#!/usr/bin/env python3
"""
Database setup script for AI Health Navigator.

This script initializes the database schema and creates sample data for development.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ai_health_navigator.database.models import Base
from ai_health_navigator.database.repositories import (
    UserRepository,
    HealthcareProviderRepository,
    InsuranceProviderRepository
)
from ai_health_navigator.core.config import settings
from ai_health_navigator.core.logging import get_logger

logger = get_logger(__name__)


def create_sample_data(session):
    """Create sample data for development."""
    logger.info("Creating sample data...")
    
    # Create sample users
    user_repo = UserRepository(session)
    sample_users = [
        {
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-15",
            "phone": "+1234567890",
            "is_active": True
        },
        {
            "email": "jane.smith@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "1985-05-20",
            "phone": "+1234567891",
            "is_active": True
        }
    ]
    
    for user_data in sample_users:
        try:
            user_repo.create(user_data)
            logger.info(f"Created user: {user_data['email']}")
        except Exception as e:
            logger.warning(f"User {user_data['email']} already exists: {e}")
    
    # Create sample healthcare providers
    provider_repo = HealthcareProviderRepository(session)
    sample_providers = [
        {
            "name": "Dr. Sarah Johnson",
            "specialty": "Cardiology",
            "location": "New York, NY",
            "phone": "+1234567892",
            "email": "sarah.johnson@healthcare.com",
            "accepting_patients": True,
            "insurance_accepted": ["blue_cross", "aetna"]
        },
        {
            "name": "Dr. Michael Chen",
            "specialty": "Neurology",
            "location": "Los Angeles, CA",
            "phone": "+1234567893",
            "email": "michael.chen@healthcare.com",
            "accepting_patients": True,
            "insurance_accepted": ["blue_cross", "cigna"]
        },
        {
            "name": "Dr. Emily Rodriguez",
            "specialty": "Primary Care",
            "location": "Chicago, IL",
            "phone": "+1234567894",
            "email": "emily.rodriguez@healthcare.com",
            "accepting_patients": True,
            "insurance_accepted": ["aetna", "humana"]
        }
    ]
    
    for provider_data in sample_providers:
        try:
            provider_repo.create(provider_data)
            logger.info(f"Created provider: {provider_data['name']}")
        except Exception as e:
            logger.warning(f"Provider {provider_data['name']} already exists: {e}")
    
    # Create sample insurance providers
    insurance_repo = InsuranceProviderRepository(session)
    sample_insurance = [
        {
            "name": "Blue Cross Blue Shield",
            "plan_type": "PPO",
            "coverage_level": "comprehensive",
            "network_size": "national"
        },
        {
            "name": "Aetna",
            "plan_type": "HMO",
            "coverage_level": "standard",
            "network_size": "national"
        },
        {
            "name": "Cigna",
            "plan_type": "PPO",
            "coverage_level": "comprehensive",
            "network_size": "national"
        }
    ]
    
    for insurance_data in sample_insurance:
        try:
            insurance_repo.create(insurance_data)
            logger.info(f"Created insurance provider: {insurance_data['name']}")
        except Exception as e:
            logger.warning(f"Insurance provider {insurance_data['name']} already exists: {e}")


def main():
    """Main setup function."""
    logger.info("Starting database setup...")
    
    try:
        # Create database engine
        engine = create_engine(settings.database.url)
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        try:
            # Create sample data
            create_sample_data(session)
            session.commit()
            logger.info("Sample data created successfully")
            
        except Exception as e:
            logger.error(f"Error creating sample data: {e}")
            session.rollback()
            raise
        finally:
            session.close()
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
