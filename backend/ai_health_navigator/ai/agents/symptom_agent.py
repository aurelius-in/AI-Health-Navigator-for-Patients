"""
Symptom Analysis Agent for AI Health Navigator.

This agent specializes in analyzing symptoms and providing medical insights
using AI models and medical knowledge bases.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from .base_agent import BaseAgent, AgentContext, AgentResult, AgentPriority
from ..models import SymptomClassifier
from ..llm_service import LLMService
from ...database import SymptomRepository, UserRepository
from ...core.logging import get_logger

logger = get_logger(__name__)


class SymptomAnalysisAgent(BaseAgent):
    """
    Agent for analyzing symptoms and providing medical insights.
    
    This agent combines AI models, LLM analysis, and medical knowledge
    to provide comprehensive symptom analysis.
    """

    def __init__(self):
        super().__init__(
            name="symptom_analysis_agent",
            description="Analyzes symptoms and provides medical insights using AI"
        )
        self.symptom_classifier = None
        self.llm_service = None
        self.medical_knowledge_base = {
            "common_symptoms": [
                "headache", "fever", "cough", "fatigue", "nausea", "dizziness",
                "chest_pain", "shortness_of_breath", "abdominal_pain", "back_pain"
            ],
            "emergency_symptoms": [
                "severe_chest_pain", "difficulty_breathing", "severe_headache",
                "loss_of_consciousness", "severe_bleeding", "paralysis"
            ],
            "symptom_severity_indicators": {
                "mild": ["slight", "minor", "manageable"],
                "moderate": ["noticeable", "interfering", "concerning"],
                "severe": ["intense", "debilitating", "unbearable"]
            }
        }

    async def initialize(self):
        """Initialize the agent with required models and services."""
        try:
            # Initialize symptom classifier
            self.symptom_classifier = SymptomClassifier()
            await self.symptom_classifier.initialize()
            
            # Initialize LLM service
            self.llm_service = LLMService()
            await self.llm_service.initialize()
            
            self.logger.info("SymptomAnalysisAgent initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize SymptomAnalysisAgent: {e}")
            raise

    def validate_input(self, context: AgentContext, **kwargs) -> bool:
        """Validate input parameters for symptom analysis."""
        required_fields = ["symptoms", "severity", "duration"]
        
        for field in required_fields:
            if field not in kwargs:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        symptoms = kwargs.get("symptoms", [])
        if not symptoms or not isinstance(symptoms, list):
            self.logger.error("Symptoms must be a non-empty list")
            return False
        
        severity = kwargs.get("severity")
        if severity not in ["mild", "moderate", "severe"]:
            self.logger.error("Severity must be mild, moderate, or severe")
            return False
        
        return True

    async def execute(self, context: AgentContext, **kwargs) -> AgentResult:
        """Execute symptom analysis."""
        symptoms = kwargs.get("symptoms", [])
        severity = kwargs.get("severity")
        duration = kwargs.get("duration")
        additional_info = kwargs.get("additional_info", "")
        location = kwargs.get("location", "")
        triggers = kwargs.get("triggers", [])
        medications = kwargs.get("medications", [])
        allergies = kwargs.get("allergies", [])

        try:
            # Step 1: AI Model Analysis
            ai_analysis = await self._perform_ai_analysis(symptoms, severity, duration)
            
            # Step 2: LLM Analysis
            llm_analysis = await self._perform_llm_analysis(
                symptoms, severity, duration, additional_info, location, triggers, medications, allergies
            )
            
            # Step 3: Medical Knowledge Integration
            knowledge_analysis = await self._integrate_medical_knowledge(
                symptoms, severity, ai_analysis, llm_analysis
            )
            
            # Step 4: Risk Assessment
            risk_assessment = await self._assess_risk(symptoms, severity, ai_analysis, llm_analysis)
            
            # Step 5: Generate Recommendations
            recommendations = await self._generate_recommendations(
                symptoms, severity, ai_analysis, llm_analysis, risk_assessment
            )

            # Combine all analyses
            combined_analysis = {
                "symptoms": symptoms,
                "severity": severity,
                "duration": duration,
                "ai_analysis": ai_analysis,
                "llm_analysis": llm_analysis,
                "knowledge_analysis": knowledge_analysis,
                "risk_assessment": risk_assessment,
                "recommendations": recommendations,
                "confidence": self._calculate_confidence(ai_analysis, llm_analysis),
                "urgency": self._determine_urgency(risk_assessment, severity),
                "possible_conditions": ai_analysis.get("possible_conditions", []),
                "warnings": risk_assessment.get("warnings", []),
                "next_steps": recommendations.get("next_steps", [])
            }

            return AgentResult(
                success=True,
                data=combined_analysis,
                confidence=combined_analysis["confidence"],
                reasoning=f"Comprehensive symptom analysis completed using AI models and medical knowledge",
                metadata={
                    "analysis_methods": ["ai_model", "llm", "medical_knowledge"],
                    "symptom_count": len(symptoms),
                    "risk_level": risk_assessment.get("risk_level", "unknown")
                },
                execution_time=0.0,  # Will be set by base class
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            self.logger.error(f"Symptom analysis failed: {e}")
            raise

    async def _perform_ai_analysis(self, symptoms: List[str], severity: str, duration: str) -> Dict[str, Any]:
        """Perform AI model-based symptom analysis."""
        try:
            # Use the symptom classifier
            analysis_result = await self.symptom_classifier.analyze_symptoms(
                symptoms=symptoms,
                severity=severity,
                duration=duration
            )
            
            return {
                "possible_conditions": analysis_result.possible_conditions,
                "confidence": analysis_result.confidence,
                "model_used": "symptom_classifier",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return {
                "possible_conditions": [],
                "confidence": 0.0,
                "error": str(e)
            }

    async def _perform_llm_analysis(
        self, symptoms: List[str], severity: str, duration: str,
        additional_info: str, location: str, triggers: List[str],
        medications: List[str], allergies: List[str]
    ) -> Dict[str, Any]:
        """Perform LLM-based symptom analysis."""
        try:
            # Create comprehensive prompt for LLM
            prompt_context = {
                "symptoms": symptoms,
                "severity": severity,
                "duration": duration,
                "additional_info": additional_info,
                "location": location,
                "triggers": triggers,
                "medications": medications,
                "allergies": allergies
            }
            
            # Use LLM service for analysis
            llm_response = await self.llm_service.analyze_symptoms(prompt_context)
            
            return {
                "analysis": llm_response.content,
                "confidence": llm_response.confidence,
                "reasoning": llm_response.reasoning,
                "provider": llm_response.provider,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"LLM analysis failed: {e}")
            return {
                "analysis": "Analysis unavailable",
                "confidence": 0.0,
                "error": str(e)
            }

    async def _integrate_medical_knowledge(
        self, symptoms: List[str], severity: str,
        ai_analysis: Dict[str, Any], llm_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Integrate medical knowledge with AI analysis."""
        try:
            # Check for emergency symptoms
            emergency_symptoms = []
            for symptom in symptoms:
                if any(emergency in symptom.lower() for emergency in self.medical_knowledge_base["emergency_symptoms"]):
                    emergency_symptoms.append(symptom)
            
            # Analyze symptom patterns
            symptom_patterns = self._analyze_symptom_patterns(symptoms)
            
            # Cross-reference with medical knowledge
            medical_insights = {
                "emergency_symptoms_detected": emergency_symptoms,
                "symptom_patterns": symptom_patterns,
                "severity_indicators": self._assess_severity_indicators(severity, symptoms),
                "knowledge_base_version": "1.0",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            return medical_insights
        except Exception as e:
            self.logger.error(f"Medical knowledge integration failed: {e}")
            return {"error": str(e)}

    async def _assess_risk(
        self, symptoms: List[str], severity: str,
        ai_analysis: Dict[str, Any], llm_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risk level based on symptoms and analysis."""
        try:
            risk_factors = []
            risk_level = "low"
            
            # Check for emergency symptoms
            emergency_symptoms = [
                "chest pain", "difficulty breathing", "severe headache",
                "loss of consciousness", "severe bleeding", "paralysis"
            ]
            
            for symptom in symptoms:
                if any(emergency in symptom.lower() for emergency in emergency_symptoms):
                    risk_factors.append(f"Emergency symptom detected: {symptom}")
                    risk_level = "critical"
            
            # Check severity
            if severity == "severe":
                risk_factors.append("High severity symptoms")
                if risk_level != "critical":
                    risk_level = "high"
            elif severity == "moderate":
                risk_factors.append("Moderate severity symptoms")
                if risk_level == "low":
                    risk_level = "moderate"
            
            # Check AI confidence
            ai_confidence = ai_analysis.get("confidence", 0.0)
            if ai_confidence < 0.5:
                risk_factors.append("Low AI confidence - manual review recommended")
            
            warnings = []
            if risk_level == "critical":
                warnings.append("URGENT: Seek immediate medical attention")
            elif risk_level == "high":
                warnings.append("High risk symptoms detected - consult healthcare provider")
            
            return {
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "warnings": warnings,
                "assessment_timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Risk assessment failed: {e}")
            return {
                "risk_level": "unknown",
                "risk_factors": [f"Assessment error: {str(e)}"],
                "warnings": ["Risk assessment unavailable"]
            }

    async def _generate_recommendations(
        self, symptoms: List[str], severity: str,
        ai_analysis: Dict[str, Any], llm_analysis: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized recommendations."""
        try:
            recommendations = []
            next_steps = []
            immediate_actions = []
            
            risk_level = risk_assessment.get("risk_level", "low")
            
            # Immediate actions based on risk level
            if risk_level == "critical":
                immediate_actions.append("Call emergency services immediately")
                immediate_actions.append("Do not drive yourself to the hospital")
            elif risk_level == "high":
                immediate_actions.append("Contact healthcare provider within 24 hours")
                immediate_actions.append("Monitor symptoms closely")
            elif risk_level == "moderate":
                immediate_actions.append("Schedule appointment with healthcare provider")
                immediate_actions.append("Keep symptom diary")
            else:
                immediate_actions.append("Monitor symptoms")
                immediate_actions.append("Consider over-the-counter remedies if appropriate")
            
            # General recommendations
            recommendations.append("Stay hydrated")
            recommendations.append("Get adequate rest")
            recommendations.append("Avoid activities that worsen symptoms")
            
            # Next steps
            next_steps.append("Document symptoms and their progression")
            next_steps.append("Prepare questions for healthcare provider")
            next_steps.append("Gather relevant medical history")
            
            return {
                "immediate_actions": immediate_actions,
                "recommendations": recommendations,
                "next_steps": next_steps,
                "follow_up_timing": self._determine_follow_up_timing(risk_level),
                "generation_timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return {
                "immediate_actions": ["Consult healthcare provider"],
                "recommendations": ["Seek medical advice"],
                "next_steps": ["Contact healthcare provider"],
                "error": str(e)
            }

    def _calculate_confidence(self, ai_analysis: Dict[str, Any], llm_analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence score."""
        ai_confidence = ai_analysis.get("confidence", 0.0)
        llm_confidence = llm_analysis.get("confidence", 0.0)
        
        # Weighted average (AI models typically more reliable for medical analysis)
        return (ai_confidence * 0.7) + (llm_confidence * 0.3)

    def _determine_urgency(self, risk_assessment: Dict[str, Any], severity: str) -> str:
        """Determine urgency level."""
        risk_level = risk_assessment.get("risk_level", "low")
        
        if risk_level == "critical":
            return "immediate"
        elif risk_level == "high" or severity == "severe":
            return "urgent"
        elif risk_level == "moderate" or severity == "moderate":
            return "priority"
        else:
            return "routine"

    def _analyze_symptom_patterns(self, symptoms: List[str]) -> Dict[str, Any]:
        """Analyze patterns in symptoms."""
        patterns = {
            "symptom_count": len(symptoms),
            "body_systems": self._identify_body_systems(symptoms),
            "symptom_clusters": self._identify_symptom_clusters(symptoms)
        }
        return patterns

    def _identify_body_systems(self, symptoms: List[str]) -> List[str]:
        """Identify affected body systems."""
        body_systems = {
            "cardiovascular": ["chest pain", "heart", "blood pressure"],
            "respiratory": ["cough", "breathing", "lungs", "shortness of breath"],
            "neurological": ["headache", "dizziness", "numbness", "seizure"],
            "gastrointestinal": ["nausea", "vomiting", "abdominal pain", "diarrhea"],
            "musculoskeletal": ["back pain", "joint pain", "muscle pain"]
        }
        
        affected_systems = []
        for system, keywords in body_systems.items():
            if any(keyword in " ".join(symptoms).lower() for keyword in keywords):
                affected_systems.append(system)
        
        return affected_systems

    def _identify_symptom_clusters(self, symptoms: List[str]) -> List[str]:
        """Identify symptom clusters."""
        clusters = []
        symptom_text = " ".join(symptoms).lower()
        
        if any(symptom in symptom_text for symptom in ["fever", "cough", "fatigue"]):
            clusters.append("flu_like_symptoms")
        
        if any(symptom in symptom_text for symptom in ["headache", "nausea", "dizziness"]):
            clusters.append("migraine_like_symptoms")
        
        if any(symptom in symptom_text for symptom in ["chest pain", "shortness of breath"]):
            clusters.append("cardiac_symptoms")
        
        return clusters

    def _assess_severity_indicators(self, severity: str, symptoms: List[str]) -> Dict[str, Any]:
        """Assess severity indicators."""
        indicators = self.medical_knowledge_base["symptom_severity_indicators"]
        return {
            "assessed_severity": severity,
            "severity_keywords": indicators.get(severity, []),
            "symptom_intensity": len(symptoms)  # More symptoms might indicate higher severity
        }

    def _determine_follow_up_timing(self, risk_level: str) -> str:
        """Determine appropriate follow-up timing."""
        timing_map = {
            "critical": "immediate",
            "high": "within_24_hours",
            "moderate": "within_week",
            "low": "as_needed"
        }
        return timing_map.get(risk_level, "as_needed")

    def can_handle(self, context: AgentContext, **kwargs) -> bool:
        """Check if this agent can handle the request."""
        return "symptoms" in kwargs and isinstance(kwargs["symptoms"], list)

    def get_provided_capabilities(self) -> List[str]:
        """Get capabilities provided by this agent."""
        return [
            "symptom_analysis",
            "medical_insights",
            "risk_assessment",
            "health_recommendations"
        ]
