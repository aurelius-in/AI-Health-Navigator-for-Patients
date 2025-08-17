"""
Medication Management Agent for AI Health Navigator.

This agent specializes in medication safety, interaction checking, and adherence monitoring.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from .base_agent import BaseAgent, AgentContext, AgentResult, AgentPriority
from ...core.logging import get_logger

logger = get_logger(__name__)


class MedicationManagementAgent(BaseAgent):
    """
    Agent for medication management and safety.
    
    This agent handles medication interactions, adherence monitoring,
    side effect analysis, and safety recommendations.
    """

    def __init__(self):
        super().__init__(
            name="medication_management_agent",
            description="Manages medication safety, interactions, and adherence"
        )
        self.medication_database = {
            "interactions": {
                "warfarin": ["aspirin", "ibuprofen", "vitamin_k"],
                "metformin": ["alcohol", "furosemide"],
                "lisinopril": ["potassium", "lithium"],
                "atorvastatin": ["grapefruit", "cyclosporine"],
                "metoprolol": ["verapamil", "diltiazem"]
            },
            "side_effects": {
                "warfarin": ["bleeding", "bruising", "nausea"],
                "metformin": ["diarrhea", "nausea", "stomach_upset"],
                "lisinopril": ["cough", "dizziness", "fatigue"],
                "atorvastatin": ["muscle_pain", "liver_problems", "headache"],
                "metoprolol": ["fatigue", "dizziness", "cold_hands"]
            },
            "contraindications": {
                "warfarin": ["pregnancy", "bleeding_disorders"],
                "metformin": ["kidney_disease", "heart_failure"],
                "lisinopril": ["pregnancy", "angioedema_history"],
                "atorvastatin": ["liver_disease", "pregnancy"],
                "metoprolol": ["heart_block", "severe_asthma"]
            }
        }

    def validate_input(self, context: AgentContext, **kwargs) -> bool:
        """Validate input parameters for medication management."""
        if "medications" not in kwargs:
            self.logger.error("Missing medications parameter")
            return False
        
        medications = kwargs.get("medications", [])
        if not isinstance(medications, list):
            self.logger.error("Medications must be a list")
            return False
        
        return True

    async def execute(self, context: AgentContext, **kwargs) -> AgentResult:
        """Execute medication management analysis."""
        medications = kwargs.get("medications", [])
        patient_conditions = kwargs.get("patient_conditions", [])
        allergies = kwargs.get("allergies", [])
        age = kwargs.get("age", 0)
        weight = kwargs.get("weight", 0)
        kidney_function = kwargs.get("kidney_function", "normal")
        liver_function = kwargs.get("liver_function", "normal")

        try:
            # Step 1: Check for drug interactions
            interactions = await self._check_drug_interactions(medications)
            
            # Step 2: Analyze side effects
            side_effects = await self._analyze_side_effects(medications, patient_conditions)
            
            # Step 3: Check contraindications
            contraindications = await self._check_contraindications(
                medications, patient_conditions, age, kidney_function, liver_function
            )
            
            # Step 4: Generate dosing recommendations
            dosing_recommendations = await self._generate_dosing_recommendations(
                medications, age, weight, kidney_function, liver_function
            )
            
            # Step 5: Create adherence plan
            adherence_plan = await self._create_adherence_plan(medications, context)

            # Combine all analyses
            medication_analysis = {
                "medications": medications,
                "interactions": interactions,
                "side_effects": side_effects,
                "contraindications": contraindications,
                "dosing_recommendations": dosing_recommendations,
                "adherence_plan": adherence_plan,
                "safety_score": self._calculate_safety_score(interactions, contraindications),
                "risk_level": self._determine_risk_level(interactions, contraindications),
                "recommendations": self._generate_recommendations(
                    interactions, contraindications, side_effects
                )
            }

            return AgentResult(
                success=True,
                data=medication_analysis,
                confidence=0.85,
                reasoning=f"Comprehensive medication analysis completed for {len(medications)} medications",
                metadata={
                    "medication_count": len(medications),
                    "interaction_count": len(interactions.get("critical", [])),
                    "contraindication_count": len(contraindications.get("critical", [])),
                    "safety_score": medication_analysis["safety_score"]
                },
                execution_time=0.0,
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            self.logger.error(f"Medication analysis failed: {e}")
            raise

    async def _check_drug_interactions(self, medications: List[str]) -> Dict[str, Any]:
        """Check for drug-drug interactions."""
        interactions = {
            "critical": [],
            "moderate": [],
            "minor": [],
            "recommendations": []
        }
        
        for i, med1 in enumerate(medications):
            for j, med2 in enumerate(medications):
                if i != j:
                    # Check known interactions
                    if med1.lower() in self.medication_database["interactions"]:
                        if med2.lower() in self.medication_database["interactions"][med1.lower()]:
                            interactions["critical"].append({
                                "medication1": med1,
                                "medication2": med2,
                                "severity": "critical",
                                "description": f"Critical interaction between {med1} and {med2}",
                                "recommendation": "Consult healthcare provider immediately"
                            })
        
        return interactions

    async def _analyze_side_effects(self, medications: List[str], conditions: List[str]) -> Dict[str, Any]:
        """Analyze potential side effects."""
        side_effects = {
            "common": [],
            "serious": [],
            "monitoring_needed": [],
            "recommendations": []
        }
        
        for medication in medications:
            med_lower = medication.lower()
            if med_lower in self.medication_database["side_effects"]:
                effects = self.medication_database["side_effects"][med_lower]
                side_effects["common"].extend([
                    {"medication": medication, "effect": effect}
                    for effect in effects
                ])
        
        return side_effects

    async def _check_contraindications(
        self, medications: List[str], conditions: List[str], 
        age: int, kidney_function: str, liver_function: str
    ) -> Dict[str, Any]:
        """Check for contraindications."""
        contraindications = {
            "critical": [],
            "moderate": [],
            "minor": [],
            "recommendations": []
        }
        
        for medication in medications:
            med_lower = medication.lower()
            if med_lower in self.medication_database["contraindications"]:
                contraindicated_conditions = self.medication_database["contraindications"][med_lower]
                
                for condition in conditions:
                    if condition.lower() in contraindicated_conditions:
                        contraindications["critical"].append({
                            "medication": medication,
                            "condition": condition,
                            "severity": "critical",
                            "description": f"{medication} is contraindicated in {condition}",
                            "recommendation": "Discontinue medication and consult healthcare provider"
                        })
        
        return contraindications

    async def _generate_dosing_recommendations(
        self, medications: List[str], age: int, weight: float,
        kidney_function: str, liver_function: str
    ) -> Dict[str, Any]:
        """Generate personalized dosing recommendations."""
        recommendations = {
            "dosing_schedule": {},
            "monitoring_requirements": {},
            "adjustments_needed": []
        }
        
        for medication in medications:
            # Generate dosing schedule based on medication type
            if "warfarin" in medication.lower():
                recommendations["dosing_schedule"][medication] = {
                    "frequency": "daily",
                    "timing": "evening",
                    "monitoring": "INR every 2-4 weeks"
                }
            elif "metformin" in medication.lower():
                recommendations["dosing_schedule"][medication] = {
                    "frequency": "twice_daily",
                    "timing": "with_meals",
                    "monitoring": "kidney_function every 3-6 months"
                }
            else:
                recommendations["dosing_schedule"][medication] = {
                    "frequency": "daily",
                    "timing": "morning",
                    "monitoring": "as_prescribed"
                }
        
        return recommendations

    async def _create_adherence_plan(self, medications: List[str], context: AgentContext) -> Dict[str, Any]:
        """Create medication adherence plan."""
        adherence_plan = {
            "reminder_schedule": {},
            "adherence_strategies": [],
            "monitoring_plan": {},
            "support_resources": []
        }
        
        for medication in medications:
            adherence_plan["reminder_schedule"][medication] = {
                "frequency": "daily",
                "times": ["08:00", "20:00"],
                "method": "app_notification"
            }
        
        adherence_plan["adherence_strategies"] = [
            "Use pill organizer",
            "Set phone reminders",
            "Take medications at same time daily",
            "Keep medications visible",
            "Use medication tracking app"
        ]
        
        adherence_plan["support_resources"] = [
            "Medication reminder apps",
            "Pill organizers",
            "Pharmacy consultation",
            "Healthcare provider support"
        ]
        
        return adherence_plan

    def _calculate_safety_score(self, interactions: Dict[str, Any], contraindications: Dict[str, Any]) -> float:
        """Calculate medication safety score (0-100)."""
        base_score = 100.0
        
        # Deduct points for interactions
        critical_interactions = len(interactions.get("critical", []))
        moderate_interactions = len(interactions.get("moderate", []))
        
        base_score -= (critical_interactions * 20)
        base_score -= (moderate_interactions * 10)
        
        # Deduct points for contraindications
        critical_contraindications = len(contraindications.get("critical", []))
        moderate_contraindications = len(contraindications.get("moderate", []))
        
        base_score -= (critical_contraindications * 25)
        base_score -= (moderate_contraindications * 15)
        
        return max(0.0, min(100.0, base_score))

    def _determine_risk_level(self, interactions: Dict[str, Any], contraindications: Dict[str, Any]) -> str:
        """Determine overall medication risk level."""
        critical_count = len(interactions.get("critical", [])) + len(contraindications.get("critical", []))
        moderate_count = len(interactions.get("moderate", [])) + len(contraindications.get("moderate", []))
        
        if critical_count > 0:
            return "critical"
        elif moderate_count > 2:
            return "high"
        elif moderate_count > 0:
            return "moderate"
        else:
            return "low"

    def _generate_recommendations(
        self, interactions: Dict[str, Any], contraindications: Dict[str, Any], 
        side_effects: Dict[str, Any]
    ) -> List[str]:
        """Generate medication recommendations."""
        recommendations = []
        
        # Critical interactions
        if interactions.get("critical"):
            recommendations.append("URGENT: Critical drug interactions detected. Consult healthcare provider immediately.")
        
        # Critical contraindications
        if contraindications.get("critical"):
            recommendations.append("URGENT: Critical contraindications detected. Discontinue medication and seek medical attention.")
        
        # General recommendations
        recommendations.extend([
            "Review medications with healthcare provider regularly",
            "Report any new side effects immediately",
            "Keep updated medication list",
            "Use one pharmacy for all prescriptions",
            "Ask about generic alternatives to reduce costs"
        ])
        
        return recommendations

    def can_handle(self, context: AgentContext, **kwargs) -> bool:
        """Check if this agent can handle the request."""
        return "medications" in kwargs and isinstance(kwargs["medications"], list)

    def get_provided_capabilities(self) -> List[str]:
        """Get capabilities provided by this agent."""
        return [
            "medication_safety",
            "drug_interaction_checking",
            "side_effect_analysis",
            "contraindication_screening",
            "dosing_recommendations",
            "adherence_monitoring"
        ]
