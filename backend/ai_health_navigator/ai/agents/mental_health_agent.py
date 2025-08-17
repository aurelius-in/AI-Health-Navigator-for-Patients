"""
Mental Health Support Agent for AI Health Navigator.

This agent specializes in mental health assessment, crisis intervention,
and providing discreet mental health support and resources.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from .base_agent import BaseAgent, AgentContext, AgentResult, AgentPriority
from ...core.logging import get_logger

logger = get_logger(__name__)


class MentalHealthAgent(BaseAgent):
    """
    Agent for mental health support and crisis intervention.
    
    This agent provides discreet mental health assessment, crisis detection,
    and connects users with appropriate mental health resources and providers.
    """

    def __init__(self):
        super().__init__(
            name="mental_health_agent",
            description="Provides mental health support, crisis intervention, and resource connection"
        )
        self.crisis_keywords = [
            "suicide", "kill myself", "want to die", "end it all", "no reason to live",
            "better off dead", "hurt myself", "self-harm", "cutting", "overdose"
        ]
        
        self.mental_health_conditions = {
            "depression": {
                "symptoms": ["sadness", "hopelessness", "fatigue", "sleep_changes", "appetite_changes"],
                "severity_levels": ["mild", "moderate", "severe"],
                "risk_factors": ["family_history", "trauma", "chronic_illness"]
            },
            "anxiety": {
                "symptoms": ["worry", "panic", "restlessness", "irritability", "concentration_issues"],
                "severity_levels": ["mild", "moderate", "severe"],
                "risk_factors": ["stress", "trauma", "genetics"]
            },
            "ptsd": {
                "symptoms": ["flashbacks", "nightmares", "hypervigilance", "avoidance", "mood_changes"],
                "severity_levels": ["mild", "moderate", "severe"],
                "risk_factors": ["trauma", "combat", "abuse"]
            },
            "bipolar": {
                "symptoms": ["mood_swings", "mania", "depression", "impulsivity", "sleep_changes"],
                "severity_levels": ["mild", "moderate", "severe"],
                "risk_factors": ["family_history", "stress", "substance_use"]
            }
        }
        
        self.crisis_resources = {
            "national_suicide_prevention": "988",
            "crisis_text_line": "Text HOME to 741741",
            "veterans_crisis_line": "1-800-273-8255",
            "emergency_services": "911"
        }

    def validate_input(self, context: AgentContext, **kwargs) -> bool:
        """Validate input parameters for mental health assessment."""
        if "symptoms" not in kwargs and "mood_assessment" not in kwargs:
            self.logger.error("Missing symptoms or mood_assessment parameter")
            return False
        
        return True

    async def execute(self, context: AgentContext, **kwargs) -> AgentResult:
        """Execute mental health assessment and support."""
        symptoms = kwargs.get("symptoms", [])
        mood_assessment = kwargs.get("mood_assessment", {})
        current_stressors = kwargs.get("current_stressors", [])
        sleep_quality = kwargs.get("sleep_quality", "unknown")
        social_support = kwargs.get("social_support", "unknown")
        previous_mental_health = kwargs.get("previous_mental_health", [])
        crisis_indicators = kwargs.get("crisis_indicators", [])

        try:
            # Step 1: Crisis Assessment
            crisis_assessment = await self._assess_crisis_risk(
                symptoms, mood_assessment, crisis_indicators
            )
            
            # Step 2: Mental Health Assessment
            mental_health_assessment = await self._assess_mental_health(
                symptoms, mood_assessment, current_stressors, sleep_quality, social_support
            )
            
            # Step 3: Generate Support Plan
            support_plan = await self._generate_support_plan(
                crisis_assessment, mental_health_assessment, social_support
            )
            
            # Step 4: Resource Recommendations
            resource_recommendations = await self._recommend_resources(
                mental_health_assessment, support_plan, context
            )
            
            # Step 5: Safety Planning (if needed)
            safety_plan = await self._create_safety_plan(crisis_assessment, context)

            # Combine all analyses
            mental_health_analysis = {
                "crisis_assessment": crisis_assessment,
                "mental_health_assessment": mental_health_assessment,
                "support_plan": support_plan,
                "resource_recommendations": resource_recommendations,
                "safety_plan": safety_plan,
                "urgency_level": self._determine_urgency_level(crisis_assessment, mental_health_assessment),
                "recommendations": self._generate_recommendations(
                    crisis_assessment, mental_health_assessment, support_plan
                )
            }

            return AgentResult(
                success=True,
                data=mental_health_analysis,
                confidence=0.80,
                reasoning=f"Comprehensive mental health assessment completed with {mental_health_analysis['urgency_level']} urgency",
                metadata={
                    "crisis_risk": crisis_assessment.get("risk_level", "low"),
                    "mental_health_conditions": len(mental_health_assessment.get("potential_conditions", [])),
                    "support_level": support_plan.get("support_level", "self_help")
                },
                execution_time=0.0,
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            self.logger.error(f"Mental health assessment failed: {e}")
            raise

    async def _assess_crisis_risk(
        self, symptoms: List[str], mood_assessment: Dict[str, Any], 
        crisis_indicators: List[str]
    ) -> Dict[str, Any]:
        """Assess crisis risk and provide immediate intervention if needed."""
        crisis_assessment = {
            "risk_level": "low",
            "crisis_indicators": [],
            "immediate_actions": [],
            "safety_concerns": [],
            "emergency_contacts": []
        }
        
        risk_score = 0
        
        # Check for crisis keywords in symptoms
        symptom_text = " ".join(symptoms).lower()
        for keyword in self.crisis_keywords:
            if keyword in symptom_text:
                risk_score += 5
                crisis_assessment["crisis_indicators"].append(f"Crisis keyword detected: {keyword}")
        
        # Check mood assessment
        if mood_assessment.get("suicidal_thoughts", False):
            risk_score += 10
            crisis_assessment["crisis_indicators"].append("Suicidal thoughts reported")
        
        if mood_assessment.get("hopelessness", 0) > 8:
            risk_score += 3
            crisis_assessment["crisis_indicators"].append("High hopelessness level")
        
        if mood_assessment.get("isolation", 0) > 8:
            risk_score += 2
            crisis_assessment["crisis_indicators"].append("High isolation level")
        
        # Check crisis indicators
        for indicator in crisis_indicators:
            if indicator in ["suicidal_ideation", "self_harm", "psychosis"]:
                risk_score += 8
                crisis_assessment["crisis_indicators"].append(f"Critical indicator: {indicator}")
        
        # Determine risk level
        if risk_score >= 10:
            crisis_assessment["risk_level"] = "critical"
            crisis_assessment["immediate_actions"].extend([
                "Call emergency services (911) immediately",
                "Contact National Suicide Prevention Lifeline (988)",
                "Go to nearest emergency room",
                "Do not leave the person alone"
            ])
            crisis_assessment["emergency_contacts"] = [
                {"name": "Emergency Services", "number": "911"},
                {"name": "National Suicide Prevention", "number": "988"},
                {"name": "Crisis Text Line", "number": "Text HOME to 741741"}
            ]
        elif risk_score >= 5:
            crisis_assessment["risk_level"] = "high"
            crisis_assessment["immediate_actions"].extend([
                "Contact mental health professional within 24 hours",
                "Call crisis hotline for support",
                "Create safety plan",
                "Increase social support"
            ])
        elif risk_score >= 2:
            crisis_assessment["risk_level"] = "moderate"
            crisis_assessment["immediate_actions"].extend([
                "Schedule appointment with mental health professional",
                "Practice self-care strategies",
                "Reach out to trusted friends or family"
            ])
        else:
            crisis_assessment["risk_level"] = "low"
            crisis_assessment["immediate_actions"].extend([
                "Continue monitoring mental health",
                "Practice preventive self-care",
                "Maintain social connections"
            ])
        
        return crisis_assessment

    async def _assess_mental_health(
        self, symptoms: List[str], mood_assessment: Dict[str, Any],
        current_stressors: List[str], sleep_quality: str, social_support: str
    ) -> Dict[str, Any]:
        """Assess mental health conditions and severity."""
        mental_health_assessment = {
            "potential_conditions": [],
            "severity_levels": {},
            "risk_factors": [],
            "protective_factors": [],
            "recommendations": []
        }
        
        # Analyze symptoms for potential conditions
        for condition, criteria in self.mental_health_conditions.items():
            condition_symptoms = criteria["symptoms"]
            matching_symptoms = [s for s in symptoms if any(cs in s.lower() for cs in condition_symptoms)]
            
            if len(matching_symptoms) >= 3:  # Threshold for potential diagnosis
                mental_health_assessment["potential_conditions"].append({
                    "condition": condition,
                    "matching_symptoms": matching_symptoms,
                    "confidence": min(len(matching_symptoms) / len(condition_symptoms), 1.0)
                })
        
        # Assess severity based on mood assessment
        for condition_info in mental_health_assessment["potential_conditions"]:
            condition = condition_info["condition"]
            severity = self._assess_severity(condition, mood_assessment, symptoms)
            mental_health_assessment["severity_levels"][condition] = severity
        
        # Identify risk factors
        risk_factors = []
        if sleep_quality in ["poor", "very_poor"]:
            risk_factors.append("Poor sleep quality")
        if social_support in ["low", "none"]:
            risk_factors.append("Limited social support")
        if current_stressors:
            risk_factors.extend([f"Current stressor: {stressor}" for stressor in current_stressors])
        
        mental_health_assessment["risk_factors"] = risk_factors
        
        # Identify protective factors
        protective_factors = []
        if sleep_quality in ["good", "excellent"]:
            protective_factors.append("Good sleep quality")
        if social_support in ["high", "excellent"]:
            protective_factors.append("Strong social support")
        if mood_assessment.get("coping_skills", 0) > 6:
            protective_factors.append("Good coping skills")
        
        mental_health_assessment["protective_factors"] = protective_factors
        
        return mental_health_assessment

    async def _generate_support_plan(
        self, crisis_assessment: Dict[str, Any], mental_health_assessment: Dict[str, Any],
        social_support: str
    ) -> Dict[str, Any]:
        """Generate personalized mental health support plan."""
        support_plan = {
            "support_level": "self_help",
            "immediate_strategies": [],
            "long_term_plan": [],
            "professional_services": [],
            "self_care_activities": [],
            "support_network": []
        }
        
        crisis_risk = crisis_assessment.get("risk_level", "low")
        
        if crisis_risk == "critical":
            support_plan["support_level"] = "emergency"
            support_plan["immediate_strategies"] = [
                "Emergency intervention required",
                "Immediate professional evaluation",
                "Safety planning",
                "24/7 crisis support"
            ]
        elif crisis_risk == "high":
            support_plan["support_level"] = "intensive"
            support_plan["immediate_strategies"] = [
                "Professional mental health evaluation within 24 hours",
                "Crisis intervention services",
                "Safety planning",
                "Increased monitoring"
            ]
            support_plan["professional_services"] = [
                "Psychiatrist evaluation",
                "Therapy sessions (2-3 times per week)",
                "Crisis intervention program",
                "Medication management"
            ]
        elif crisis_risk == "moderate":
            support_plan["support_level"] = "professional"
            support_plan["immediate_strategies"] = [
                "Schedule mental health evaluation",
                "Begin therapy program",
                "Develop coping strategies",
                "Monitor symptoms"
            ]
            support_plan["professional_services"] = [
                "Therapy sessions (weekly)",
                "Psychiatric evaluation",
                "Support groups",
                "Medication consultation if needed"
            ]
        else:
            support_plan["support_level"] = "self_help"
            support_plan["immediate_strategies"] = [
                "Self-care practices",
                "Stress management techniques",
                "Social connection activities",
                "Regular exercise and sleep"
            ]
        
        # Add self-care activities
        support_plan["self_care_activities"] = [
            "Mindfulness meditation",
            "Regular exercise",
            "Healthy sleep hygiene",
            "Creative activities",
            "Nature walks",
            "Journaling",
            "Deep breathing exercises"
        ]
        
        # Add support network recommendations
        if social_support in ["low", "none"]:
            support_plan["support_network"] = [
                "Join support groups",
                "Connect with mental health organizations",
                "Build relationships with trusted individuals",
                "Consider peer support programs"
            ]
        
        return support_plan

    async def _recommend_resources(
        self, mental_health_assessment: Dict[str, Any], support_plan: Dict[str, Any],
        context: AgentContext
    ) -> Dict[str, Any]:
        """Recommend mental health resources and providers."""
        resource_recommendations = {
            "crisis_resources": [],
            "professional_services": [],
            "support_groups": [],
            "educational_resources": [],
            "apps_and_tools": []
        }
        
        # Crisis resources
        resource_recommendations["crisis_resources"] = [
            {"name": "National Suicide Prevention Lifeline", "number": "988", "available": "24/7"},
            {"name": "Crisis Text Line", "number": "Text HOME to 741741", "available": "24/7"},
            {"name": "Emergency Services", "number": "911", "available": "24/7"}
        ]
        
        # Professional services based on conditions
        conditions = [c["condition"] for c in mental_health_assessment.get("potential_conditions", [])]
        
        if "depression" in conditions:
            resource_recommendations["professional_services"].extend([
                "Depression specialist",
                "Cognitive Behavioral Therapy (CBT)",
                "Interpersonal Therapy (IPT)",
                "Medication management"
            ])
        
        if "anxiety" in conditions:
            resource_recommendations["professional_services"].extend([
                "Anxiety specialist",
                "Exposure therapy",
                "Mindfulness-based therapy",
                "Anti-anxiety medication consultation"
            ])
        
        if "ptsd" in conditions:
            resource_recommendations["professional_services"].extend([
                "Trauma specialist",
                "EMDR therapy",
                "Prolonged Exposure therapy",
                "Trauma-focused CBT"
            ])
        
        # Support groups
        resource_recommendations["support_groups"] = [
            "NAMI (National Alliance on Mental Illness) support groups",
            "Depression and Bipolar Support Alliance",
            "Anxiety and Depression Association of America",
            "Online peer support communities"
        ]
        
        # Educational resources
        resource_recommendations["educational_resources"] = [
            "MentalHealth.gov",
            "National Institute of Mental Health",
            "Psychology Today articles",
            "Mental health podcasts and videos"
        ]
        
        # Apps and tools
        resource_recommendations["apps_and_tools"] = [
            "Headspace (meditation)",
            "Calm (relaxation)",
            "Mood tracking apps",
            "Crisis safety planning apps",
            "Therapy apps (Talkspace, BetterHelp)"
        ]
        
        return resource_recommendations

    async def _create_safety_plan(self, crisis_assessment: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Create safety plan for crisis situations."""
        safety_plan = {
            "warning_signs": [],
            "coping_strategies": [],
            "distractions": [],
            "people_to_contact": [],
            "professional_contacts": [],
            "safe_places": [],
            "emergency_plan": []
        }
        
        if crisis_assessment.get("risk_level") in ["high", "critical"]:
            safety_plan["warning_signs"] = [
                "Increased isolation",
                "Changes in sleep or appetite",
                "Giving away possessions",
                "Talking about death or suicide",
                "Increased substance use",
                "Extreme mood swings"
            ]
            
            safety_plan["coping_strategies"] = [
                "Deep breathing exercises",
                "Grounding techniques (5-4-3-2-1 method)",
                "Call a trusted friend or family member",
                "Write in a journal",
                "Take a walk or exercise",
                "Listen to calming music"
            ]
            
            safety_plan["distractions"] = [
                "Watch a favorite movie or TV show",
                "Read a book",
                "Play with a pet",
                "Cook or bake something",
                "Do a puzzle or craft",
                "Listen to podcasts"
            ]
            
            safety_plan["people_to_contact"] = [
                "Trusted family member",
                "Close friend",
                "Mental health professional",
                "Crisis hotline"
            ]
            
            safety_plan["professional_contacts"] = [
                {"name": "National Suicide Prevention", "number": "988"},
                {"name": "Crisis Text Line", "number": "Text HOME to 741741"},
                {"name": "Emergency Services", "number": "911"}
            ]
            
            safety_plan["safe_places"] = [
                "Emergency room",
                "Mental health crisis center",
                "Trusted friend's home",
                "Public place with people around"
            ]
            
            safety_plan["emergency_plan"] = [
                "If in immediate danger, call 911",
                "Go to nearest emergency room",
                "Contact crisis hotline",
                "Stay with a trusted person",
                "Remove access to harmful items"
            ]
        
        return safety_plan

    def _assess_severity(self, condition: str, mood_assessment: Dict[str, Any], symptoms: List[str]) -> str:
        """Assess severity of mental health condition."""
        severity_score = 0
        
        # Base severity from mood assessment
        if condition == "depression":
            severity_score += mood_assessment.get("depression_level", 0)
        elif condition == "anxiety":
            severity_score += mood_assessment.get("anxiety_level", 0)
        
        # Additional severity from symptoms
        severity_score += len(symptoms) * 0.5
        
        # Determine severity level
        if severity_score >= 8:
            return "severe"
        elif severity_score >= 5:
            return "moderate"
        else:
            return "mild"

    def _determine_urgency_level(
        self, crisis_assessment: Dict[str, Any], mental_health_assessment: Dict[str, Any]
    ) -> str:
        """Determine overall urgency level for mental health support."""
        crisis_risk = crisis_assessment.get("risk_level", "low")
        
        if crisis_risk == "critical":
            return "immediate"
        elif crisis_risk == "high":
            return "urgent"
        elif crisis_risk == "moderate":
            return "priority"
        else:
            return "routine"

    def _generate_recommendations(
        self, crisis_assessment: Dict[str, Any], mental_health_assessment: Dict[str, Any],
        support_plan: Dict[str, Any]
    ) -> List[str]:
        """Generate mental health recommendations."""
        recommendations = []
        
        crisis_risk = crisis_assessment.get("risk_level", "low")
        
        if crisis_risk == "critical":
            recommendations.append("URGENT: Immediate crisis intervention required")
            recommendations.append("Call emergency services or crisis hotline immediately")
        elif crisis_risk == "high":
            recommendations.append("High-risk situation - seek professional help within 24 hours")
            recommendations.append("Create safety plan and increase monitoring")
        elif crisis_risk == "moderate":
            recommendations.append("Schedule mental health evaluation soon")
            recommendations.append("Begin self-care practices and stress management")
        else:
            recommendations.append("Continue monitoring mental health")
            recommendations.append("Practice preventive self-care and maintain social connections")
        
        # Add condition-specific recommendations
        conditions = mental_health_assessment.get("potential_conditions", [])
        for condition_info in conditions:
            condition = condition_info["condition"]
            severity = mental_health_assessment["severity_levels"].get(condition, "mild")
            recommendations.append(f"Consider {condition} treatment - severity: {severity}")
        
        return recommendations

    def can_handle(self, context: AgentContext, **kwargs) -> bool:
        """Check if this agent can handle the request."""
        return ("symptoms" in kwargs or "mood_assessment" in kwargs or 
                "crisis_indicators" in kwargs)

    def get_provided_capabilities(self) -> List[str]:
        """Get capabilities provided by this agent."""
        return [
            "mental_health_assessment",
            "crisis_intervention",
            "safety_planning",
            "resource_recommendations",
            "support_planning",
            "crisis_detection"
        ]
