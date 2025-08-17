#!/usr/bin/env python3
"""
Medical data loading script for AI Health Navigator.

This script loads medical ontologies, ICD-10 codes, drug databases, and other medical knowledge.
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from ai_health_navigator.core.config import settings
from ai_health_navigator.core.logging import get_logger

logger = get_logger(__name__)


# Sample medical data - in a real implementation, this would come from external sources
ICD10_CODES = {
    "I10": {
        "code": "I10",
        "description": "Essential (primary) hypertension",
        "category": "Diseases of the circulatory system",
        "severity": "moderate"
    },
    "E11": {
        "code": "E11",
        "description": "Type 2 diabetes mellitus",
        "category": "Endocrine, nutritional and metabolic diseases",
        "severity": "moderate"
    },
    "J44": {
        "code": "J44",
        "description": "Other chronic obstructive pulmonary disease",
        "category": "Diseases of the respiratory system",
        "severity": "moderate"
    },
    "F32": {
        "code": "F32",
        "description": "Depressive episode",
        "category": "Mental, Behavioral and Neurodevelopmental disorders",
        "severity": "moderate"
    },
    "G43": {
        "code": "G43",
        "description": "Migraine",
        "category": "Diseases of the nervous system",
        "severity": "mild"
    }
}

DRUG_DATABASE = {
    "warfarin": {
        "name": "Warfarin",
        "generic_name": "warfarin",
        "drug_class": "anticoagulant",
        "indications": ["atrial_fibrillation", "deep_vein_thrombosis", "pulmonary_embolism"],
        "contraindications": ["pregnancy", "active_bleeding", "severe_liver_disease"],
        "side_effects": ["bleeding", "bruising", "nausea"],
        "interactions": ["aspirin", "ibuprofen", "alcohol"]
    },
    "metformin": {
        "name": "Metformin",
        "generic_name": "metformin",
        "drug_class": "biguanide",
        "indications": ["type_2_diabetes"],
        "contraindications": ["severe_kidney_disease", "metabolic_acidosis"],
        "side_effects": ["nausea", "diarrhea", "stomach_upset"],
        "interactions": ["alcohol", "furosemide"]
    },
    "aspirin": {
        "name": "Aspirin",
        "generic_name": "acetylsalicylic_acid",
        "drug_class": "nsaid",
        "indications": ["pain", "fever", "inflammation", "heart_attack_prevention"],
        "contraindications": ["active_bleeding", "stomach_ulcers", "allergy_to_aspirin"],
        "side_effects": ["stomach_irritation", "bleeding", "ringing_in_ears"],
        "interactions": ["warfarin", "ibuprofen", "alcohol"]
    }
}

SYMPTOM_CONDITION_MAPPING = {
    "headache": {
        "conditions": ["migraine", "tension_headache", "cluster_headache", "sinusitis"],
        "urgency_levels": {
            "mild": "low",
            "moderate": "low",
            "severe": "high"
        },
        "red_flags": ["sudden_severe_headache", "headache_with_neck_stiffness", "headache_with_fever"]
    },
    "chest_pain": {
        "conditions": ["angina", "heart_attack", "costochondritis", "anxiety"],
        "urgency_levels": {
            "mild": "medium",
            "moderate": "high",
            "severe": "critical"
        },
        "red_flags": ["crushing_chest_pain", "pain_radiating_to_arm", "shortness_of_breath"]
    },
    "shortness_of_breath": {
        "conditions": ["asthma", "copd", "pneumonia", "heart_failure", "anxiety"],
        "urgency_levels": {
            "mild": "medium",
            "moderate": "high",
            "severe": "critical"
        },
        "red_flags": ["sudden_onset", "chest_pain", "blue_lips"]
    }
}

PREVENTIVE_CARE_GUIDELINES = {
    "adult_screening": {
        "blood_pressure": {
            "frequency": "annually",
            "age_start": 18,
            "age_end": None,
            "risk_factors": ["obesity", "family_history", "smoking"]
        },
        "cholesterol": {
            "frequency": "every_5_years",
            "age_start": 20,
            "age_end": None,
            "risk_factors": ["diabetes", "family_history", "smoking"]
        },
        "diabetes": {
            "frequency": "every_3_years",
            "age_start": 45,
            "age_end": None,
            "risk_factors": ["obesity", "family_history", "gestational_diabetes"]
        },
        "colorectal_cancer": {
            "frequency": "every_10_years",
            "age_start": 50,
            "age_end": 75,
            "risk_factors": ["family_history", "inflammatory_bowel_disease"]
        }
    },
    "vaccinations": {
        "flu": {
            "frequency": "annually",
            "age_start": 6,
            "age_end": None,
            "high_risk_groups": ["elderly", "pregnant_women", "chronic_conditions"]
        },
        "tdap": {
            "frequency": "every_10_years",
            "age_start": 11,
            "age_end": None,
            "special_cases": ["pregnancy"]
        },
        "pneumonia": {
            "frequency": "once_or_twice",
            "age_start": 65,
            "age_end": None,
            "high_risk_groups": ["smokers", "chronic_conditions"]
        }
    }
}


def load_icd10_codes() -> Dict[str, Any]:
    """Load ICD-10 codes into the system."""
    logger.info("Loading ICD-10 codes...")
    # In a real implementation, this would load from a database or API
    return ICD10_CODES


def load_drug_database() -> Dict[str, Any]:
    """Load drug database into the system."""
    logger.info("Loading drug database...")
    # In a real implementation, this would load from FDA API or similar
    return DRUG_DATABASE


def load_symptom_mappings() -> Dict[str, Any]:
    """Load symptom-condition mappings."""
    logger.info("Loading symptom-condition mappings...")
    return SYMPTOM_CONDITION_MAPPING


def load_preventive_guidelines() -> Dict[str, Any]:
    """Load preventive care guidelines."""
    logger.info("Loading preventive care guidelines...")
    return PREVENTIVE_CARE_GUIDELINES


def save_to_json(data: Dict[str, Any], filename: str):
    """Save data to JSON file for caching."""
    data_dir = Path(backend_dir) / "data"
    data_dir.mkdir(exist_ok=True)
    
    filepath = data_dir / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved {filename} to {filepath}")


def main():
    """Main function to load all medical data."""
    logger.info("Starting medical data loading...")
    
    try:
        # Load all medical data
        icd10_data = load_icd10_codes()
        drug_data = load_drug_database()
        symptom_data = load_symptom_mappings()
        preventive_data = load_preventive_guidelines()
        
        # Save to JSON files for caching
        save_to_json(icd10_data, "icd10_codes.json")
        save_to_json(drug_data, "drug_database.json")
        save_to_json(symptom_data, "symptom_mappings.json")
        save_to_json(preventive_data, "preventive_guidelines.json")
        
        # Create a combined medical knowledge base
        medical_knowledge = {
            "icd10_codes": icd10_data,
            "drug_database": drug_data,
            "symptom_mappings": symptom_data,
            "preventive_guidelines": preventive_data,
            "loaded_at": str(asyncio.get_event_loop().time())
        }
        
        save_to_json(medical_knowledge, "medical_knowledge_base.json")
        
        logger.info("Medical data loading completed successfully!")
        logger.info(f"Loaded {len(icd10_data)} ICD-10 codes")
        logger.info(f"Loaded {len(drug_data)} drugs")
        logger.info(f"Loaded {len(symptom_data)} symptom mappings")
        logger.info(f"Loaded preventive care guidelines for {len(preventive_data)} categories")
        
    except Exception as e:
        logger.error(f"Medical data loading failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
