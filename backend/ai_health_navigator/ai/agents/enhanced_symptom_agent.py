"""
Enhanced Symptom Analysis Agent with Advanced Agentic AI Capabilities.

This agent specializes in analyzing symptoms using advanced AI capabilities
including memory, reasoning, planning, and autonomous decision-making.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import json

from .enhanced_base_agent import EnhancedBaseAgent, AgentContext, AgentResult, AgentPriority, AgentMemoryType, ReasoningType, MemoryItem
from ..models import SymptomClassifier
from ..llm_service import LLMService
from ...database import SymptomRepository, UserRepository
from ...core.logging import get_logger

logger = get_logger(__name__)


class EnhancedSymptomAnalysisAgent(EnhancedBaseAgent):
    """
    Enhanced agent for analyzing symptoms with advanced agentic capabilities.
    
    This agent combines AI models, LLM analysis, medical knowledge,
    memory systems, advanced reasoning, and autonomous decision-making
    to provide comprehensive symptom analysis.
    """

    def __init__(self):
        super().__init__(
            name="enhanced_symptom_analysis_agent",
            description="Advanced symptom analysis with memory, reasoning, and autonomous capabilities"
        )
        
        # Medical knowledge bases
        self.medical_knowledge_base = {
            "symptom_patterns": {
                "cardiac": ["chest_pain", "shortness_of_breath", "palpitations", "fatigue"],
                "respiratory": ["cough", "wheezing", "chest_tightness", "sputum"],
                "neurological": ["headache", "dizziness", "numbness", "seizures"],
                "gastrointestinal": ["abdominal_pain", "nausea", "vomiting", "diarrhea"],
                "musculoskeletal": ["joint_pain", "back_pain", "stiffness", "swelling"]
            },
            "emergency_patterns": {
                "heart_attack": ["severe_chest_pain", "shortness_of_breath", "sweating", "nausea"],
                "stroke": ["sudden_headache", "weakness", "speech_problems", "vision_changes"],
                "severe_infection": ["high_fever", "chills", "rapid_breathing", "confusion"]
            },
            "risk_factors": {
                "age": {"elderly": 65, "young": 18},
                "comorbidities": ["diabetes", "hypertension", "heart_disease"],
                "lifestyle": ["smoking", "obesity", "sedentary"]
            }
        }
        
        # Initialize specialized components
        self.symptom_classifier = None
        self.llm_service = None
        self.symptom_repository = None
        self.user_repository = None

    async def initialize(self):
        """Initialize the enhanced symptom analysis agent."""
        await super().initialize()
        
        # Initialize medical components
        self.symptom_classifier = SymptomClassifier()
        await self.symptom_classifier.initialize()
        
        self.llm_service = LLMService()
        await self.llm_service.initialize()
        
        # Initialize repositories
        self.symptom_repository = SymptomRepository()
        self.user_repository = UserRepository()
        
        # Load medical knowledge into semantic memory
        await self._load_medical_knowledge()
        
        self.logger.info("Enhanced SymptomAnalysisAgent initialized with advanced capabilities")

    async def _load_medical_knowledge(self):
        """Load medical knowledge into semantic memory."""
        self.semantic_memory.update({
            "medical_patterns": self.medical_knowledge_base["symptom_patterns"],
            "emergency_patterns": self.medical_knowledge_base["emergency_patterns"],
            "risk_factors": self.medical_knowledge_base["risk_factors"],
            "medical_rules": self._generate_medical_rules(),
            "diagnostic_criteria": self._load_diagnostic_criteria()
        })

    def _generate_medical_rules(self) -> Dict[str, Any]:
        """Generate medical reasoning rules."""
        return {
            "emergency_rule": {
                "condition": "emergency_symptoms_present",
                "action": "immediate_medical_attention",
                "confidence": 0.95,
                "priority": "critical"
            },
            "pattern_rule": {
                "condition": "symptom_pattern_matches",
                "action": "suggest_differential_diagnosis",
                "confidence": 0.85,
                "priority": "high"
            },
            "risk_rule": {
                "condition": "high_risk_factors_present",
                "action": "escalate_assessment",
                "confidence": 0.80,
                "priority": "moderate"
            }
        }

    def _load_diagnostic_criteria(self) -> Dict[str, Any]:
        """Load diagnostic criteria for common conditions."""
        return {
            "migraine": {
                "required_symptoms": ["headache"],
                "supporting_symptoms": ["nausea", "light_sensitivity", "aura"],
                "duration": "4-72_hours",
                "frequency": "recurrent"
            },
            "pneumonia": {
                "required_symptoms": ["cough", "fever"],
                "supporting_symptoms": ["chest_pain", "shortness_of_breath", "fatigue"],
                "duration": "days_to_weeks",
                "severity": "moderate_to_severe"
            }
        }

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

    # Implement abstract methods from EnhancedBaseAgent
    def _extract_context_patterns(self, context: AgentContext, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract patterns from the current context."""
        patterns = {
            "symptom_pattern": self._identify_symptom_pattern(kwargs.get("symptoms", [])),
            "severity_pattern": self._analyze_severity_pattern(kwargs.get("severity", "mild")),
            "temporal_pattern": self._analyze_temporal_pattern(kwargs.get("duration", "")),
            "user_pattern": self._extract_user_pattern(context.user_id),
            "context_pattern": {
                "time_of_day": context.timestamp.hour,
                "day_of_week": context.timestamp.weekday(),
                "priority": context.priority.value
            }
        }
        return patterns

    async def _build_situation_model(self, context: AgentContext, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Build a model of the current situation."""
        # Get user profile
        user_profile = await self._get_user_profile(context.user_id)
        
        # Build situation model
        situation_model = {
            "patient_context": {
                "age": user_profile.get("age", 0),
                "gender": user_profile.get("gender", "unknown"),
                "medical_history": user_profile.get("medical_history", []),
                "medications": user_profile.get("medications", []),
                "allergies": user_profile.get("allergies", [])
            },
            "symptom_context": {
                "symptoms": kwargs.get("symptoms", []),
                "severity": kwargs.get("severity", "mild"),
                "duration": kwargs.get("duration", ""),
                "location": kwargs.get("location", ""),
                "triggers": kwargs.get("triggers", [])
            },
            "environmental_context": {
                "season": self._determine_season(context.timestamp),
                "time_of_day": context.timestamp.hour,
                "urgency": context.priority.value
            }
        }
        return situation_model

    def _calculate_memory_relevance(self, memory: MemoryItem, context: AgentContext, kwargs: Dict[str, Any]) -> float:
        """Calculate the relevance of a memory to the current context."""
        relevance_score = 0.0
        
        # Check if memory contains similar symptoms
        if "symptoms" in memory.content:
            memory_symptoms = memory.content.get("symptoms", [])
            current_symptoms = kwargs.get("symptoms", [])
            
            # Calculate symptom similarity
            symptom_overlap = len(set(memory_symptoms) & set(current_symptoms))
            if symptom_overlap > 0:
                relevance_score += 0.4 * (symptom_overlap / max(len(memory_symptoms), len(current_symptoms)))
        
        # Check if memory is from same user
        if memory.content.get("user_id") == context.user_id:
            relevance_score += 0.3
        
        # Check temporal relevance (more recent = more relevant)
        time_diff = datetime.utcnow() - memory.timestamp
        if time_diff.days < 30:  # Within last month
            relevance_score += 0.2
        elif time_diff.days < 90:  # Within last 3 months
            relevance_score += 0.1
        
        # Check severity relevance
        if memory.content.get("severity") == kwargs.get("severity"):
            relevance_score += 0.1
        
        return min(1.0, relevance_score)

    def _identify_patterns(self, context: AgentContext, kwargs: Dict[str, Any], result: AgentResult) -> List[Dict[str, Any]]:
        """Identify patterns in the current experience."""
        patterns = []
        
        # Symptom pattern recognition
        symptom_pattern = self._identify_symptom_pattern(kwargs.get("symptoms", []))
        if symptom_pattern:
            patterns.append({
                "pattern": "symptom_cluster",
                "knowledge": {"cluster_type": symptom_pattern, "confidence": 0.8},
                "confidence": 0.8,
                "applicability": ["diagnosis", "treatment", "prevention"]
            })
        
        # Risk pattern recognition
        risk_pattern = self._identify_risk_pattern(context, kwargs)
        if risk_pattern:
            patterns.append({
                "pattern": "risk_assessment",
                "knowledge": {"risk_factors": risk_pattern, "severity": "high"},
                "confidence": 0.7,
                "applicability": ["screening", "prevention", "monitoring"]
            })
        
        # Temporal pattern recognition
        temporal_pattern = self._identify_temporal_pattern(kwargs.get("duration", ""))
        if temporal_pattern:
            patterns.append({
                "pattern": "temporal_characteristics",
                "knowledge": {"duration_type": temporal_pattern, "urgency": "moderate"},
                "confidence": 0.6,
                "applicability": ["diagnosis", "treatment_timing"]
            })
        
        return patterns

    def _extract_semantic_knowledge(self, context: AgentContext, kwargs: Dict[str, Any], result: AgentResult) -> Dict[str, Any]:
        """Extract semantic knowledge from the current experience."""
        knowledge = {}
        
        # Extract symptom-diagnosis associations
        if result.success and "possible_conditions" in result.data:
            conditions = result.data["possible_conditions"]
            symptoms = kwargs.get("symptoms", [])
            
            for condition in conditions:
                condition_name = condition.get("condition", "")
                if condition_name and symptoms:
                    knowledge[f"symptom_condition_association_{condition_name}"] = {
                        "symptoms": symptoms,
                        "condition": condition_name,
                        "confidence": condition.get("confidence", 0.0),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        
        # Extract severity patterns
        severity = kwargs.get("severity", "mild")
        if severity != "mild":
            knowledge[f"severity_pattern_{severity}"] = {
                "symptoms": kwargs.get("symptoms", []),
                "severity": severity,
                "outcome": result.success,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return knowledge

    # Specialized medical reasoning methods
    async def _deductive_reasoning(self, context: AgentContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform medical deductive reasoning."""
        # Apply medical rules to symptoms
        rules = self.semantic_memory.get("medical_rules", {})
        symptoms = input_data.get("symptoms", [])
        severity = input_data.get("severity", "mild")
        
        conclusions = []
        confidence = 0.0
        
        # Check emergency rule
        if self._check_emergency_symptoms(symptoms):
            conclusions.append({
                "rule": "emergency_rule",
                "conclusion": "immediate_medical_attention_required",
                "confidence": 0.95,
                "reasoning": "Emergency symptoms detected"
            })
            confidence = 0.95
        
        # Check pattern rule
        pattern_match = self._check_symptom_pattern(symptoms)
        if pattern_match:
            conclusions.append({
                "rule": "pattern_rule",
                "conclusion": f"pattern_matches_{pattern_match}",
                "confidence": 0.85,
                "reasoning": f"Symptom pattern matches {pattern_match}"
            })
            confidence = max(confidence, 0.85)
        
        # Check risk rule
        risk_factors = self._assess_risk_factors(context, input_data)
        if risk_factors.get("high_risk"):
            conclusions.append({
                "rule": "risk_rule",
                "conclusion": "escalate_assessment",
                "confidence": 0.80,
                "reasoning": "High risk factors present"
            })
            confidence = max(confidence, 0.80)
        
        return {
            "conclusion": conclusions,
            "confidence": confidence,
            "process": f"Applied {len(conclusions)} medical rules"
        }

    async def _inductive_reasoning(self, context: AgentContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform medical inductive reasoning."""
        # Look for patterns in symptom data
        symptoms = input_data.get("symptoms", [])
        user_id = context.user_id
        
        # Get historical data for this user
        historical_data = await self._get_user_symptom_history(user_id)
        
        # Identify patterns
        patterns = []
        
        # Symptom frequency pattern
        symptom_frequency = self._analyze_symptom_frequency(symptoms, historical_data)
        if symptom_frequency.get("recurring"):
            patterns.append({
                "type": "recurring_symptoms",
                "strength": 0.8,
                "implication": "chronic_condition_possible"
            })
        
        # Seasonal pattern
        seasonal_pattern = self._analyze_seasonal_pattern(symptoms, historical_data)
        if seasonal_pattern.get("seasonal"):
            patterns.append({
                "type": "seasonal_pattern",
                "strength": 0.7,
                "implication": "allergic_or_seasonal_condition"
            })
        
        # Time-of-day pattern
        temporal_pattern = self._analyze_temporal_pattern(input_data.get("duration", ""))
        if temporal_pattern.get("pattern"):
            patterns.append({
                "type": "temporal_pattern",
                "strength": 0.6,
                "implication": temporal_pattern.get("implication", "unknown")
            })
        
        # Generate hypotheses
        hypotheses = []
        for pattern in patterns:
            hypothesis = self._generate_medical_hypothesis(pattern, symptoms)
            hypotheses.append(hypothesis)
        
        confidence = sum(p.get("strength", 0.0) for p in patterns) / len(patterns) if patterns else 0.0
        
        return {
            "conclusion": hypotheses,
            "confidence": confidence,
            "process": f"Generated {len(hypotheses)} hypotheses from {len(patterns)} patterns"
        }

    async def _abductive_reasoning(self, context: AgentContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform medical abductive reasoning (best explanation)."""
        symptoms = input_data.get("symptoms", [])
        severity = input_data.get("severity", "mild")
        
        # Find possible explanations for the symptoms
        explanations = []
        
        # Check against diagnostic criteria
        diagnostic_criteria = self.semantic_memory.get("diagnostic_criteria", {})
        for condition, criteria in diagnostic_criteria.items():
            match_score = self._calculate_diagnostic_match(symptoms, criteria)
            if match_score > 0.5:  # Threshold for consideration
                explanations.append({
                    "condition": condition,
                    "match_score": match_score,
                    "confidence": match_score * 0.9,
                    "reasoning": f"Matches {condition} criteria"
                })
        
        # Check emergency patterns
        emergency_patterns = self.medical_knowledge_base["emergency_patterns"]
        for emergency, pattern in emergency_patterns.items():
            if self._check_pattern_match(symptoms, pattern):
                explanations.append({
                    "condition": emergency,
                    "match_score": 0.9,
                    "confidence": 0.9,
                    "reasoning": f"Matches emergency pattern: {emergency}"
                })
        
        # Select best explanation
        if explanations:
            best_explanation = max(explanations, key=lambda x: x["confidence"])
        else:
            best_explanation = {
                "condition": "unknown",
                "match_score": 0.0,
                "confidence": 0.0,
                "reasoning": "No clear diagnostic match"
            }
        
        return {
            "conclusion": [best_explanation],
            "confidence": best_explanation["confidence"],
            "process": f"Found best explanation from {len(explanations)} possibilities"
        }

    # Helper methods for medical reasoning
    def _identify_symptom_pattern(self, symptoms: List[str]) -> Optional[str]:
        """Identify the pattern of symptoms."""
        symptom_text = " ".join(symptoms).lower()
        
        for pattern_name, pattern_symptoms in self.medical_knowledge_base["symptom_patterns"].items():
            pattern_matches = sum(1 for symptom in pattern_symptoms if symptom in symptom_text)
            if pattern_matches >= 2:  # At least 2 symptoms match
                return pattern_name
        
        return None

    def _check_emergency_symptoms(self, symptoms: List[str]) -> bool:
        """Check if symptoms indicate an emergency."""
        symptom_text = " ".join(symptoms).lower()
        
        for emergency, pattern in self.medical_knowledge_base["emergency_patterns"].items():
            if self._check_pattern_match(symptoms, pattern):
                return True
        
        return False

    def _check_symptom_pattern(self, symptoms: List[str]) -> Optional[str]:
        """Check if symptoms match a known pattern."""
        return self._identify_symptom_pattern(symptoms)

    def _assess_risk_factors(self, context: AgentContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk factors for the current situation."""
        risk_factors = self.medical_knowledge_base["risk_factors"]
        user_profile = self.user_profiles.get(context.user_id, {})
        
        risk_assessment = {
            "high_risk": False,
            "risk_factors": [],
            "risk_score": 0.0
        }
        
        # Check age risk
        user_age = user_profile.get("age", 0)
        if user_age >= risk_factors["age"]["elderly"]:
            risk_assessment["risk_factors"].append("elderly_age")
            risk_assessment["risk_score"] += 0.3
        
        # Check comorbidities
        user_conditions = user_profile.get("medical_history", [])
        for condition in risk_factors["comorbidities"]:
            if condition in user_conditions:
                risk_assessment["risk_factors"].append(condition)
                risk_assessment["risk_score"] += 0.2
        
        # Check severity
        severity = input_data.get("severity", "mild")
        if severity == "severe":
            risk_assessment["risk_score"] += 0.4
        
        risk_assessment["high_risk"] = risk_assessment["risk_score"] >= 0.5
        
        return risk_assessment

    def _analyze_severity_pattern(self, severity: str) -> Dict[str, Any]:
        """Analyze the severity pattern."""
        severity_levels = {"mild": 1, "moderate": 2, "severe": 3}
        return {
            "level": severity_levels.get(severity, 1),
            "urgency": "high" if severity == "severe" else "moderate" if severity == "moderate" else "low"
        }

    def _analyze_temporal_pattern(self, duration: str) -> Dict[str, Any]:
        """Analyze temporal patterns in symptoms."""
        duration_lower = duration.lower()
        
        if "hours" in duration_lower or "acute" in duration_lower:
            return {"pattern": "acute", "urgency": "high", "implication": "recent_onset"}
        elif "days" in duration_lower:
            return {"pattern": "subacute", "urgency": "moderate", "implication": "developing_condition"}
        elif "weeks" in duration_lower or "months" in duration_lower:
            return {"pattern": "chronic", "urgency": "low", "implication": "long_term_condition"}
        else:
            return {"pattern": "unknown", "urgency": "moderate", "implication": "unknown"}

    def _extract_user_pattern(self, user_id: str) -> Dict[str, Any]:
        """Extract patterns specific to the user."""
        user_profile = self.user_profiles.get(user_id, {})
        return {
            "age_group": self._categorize_age(user_profile.get("age", 0)),
            "gender": user_profile.get("gender", "unknown"),
            "has_chronic_conditions": len(user_profile.get("medical_history", [])) > 0,
            "medication_count": len(user_profile.get("medications", []))
        }

    def _categorize_age(self, age: int) -> str:
        """Categorize age into groups."""
        if age < 18:
            return "pediatric"
        elif age < 65:
            return "adult"
        else:
            return "elderly"

    def _determine_season(self, timestamp: datetime) -> str:
        """Determine the season from timestamp."""
        month = timestamp.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"

    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile from database."""
        try:
            # This would typically fetch from database
            # For now, return from memory
            return self.user_profiles.get(user_id, {})
        except Exception as e:
            self.logger.error(f"Failed to get user profile: {e}")
            return {}

    async def _get_user_symptom_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's symptom history."""
        try:
            # This would typically fetch from database
            # For now, return from episodic memory
            user_memories = [m for m in self.episodic_memory if m.content.get("user_id") == user_id]
            return [m.content for m in user_memories]
        except Exception as e:
            self.logger.error(f"Failed to get symptom history: {e}")
            return []

    def _analyze_symptom_frequency(self, current_symptoms: List[str], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze symptom frequency patterns."""
        symptom_counts = {}
        
        for record in historical_data:
            symptoms = record.get("symptoms", [])
            for symptom in symptoms:
                symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
        
        recurring_symptoms = [s for s in current_symptoms if symptom_counts.get(s, 0) > 2]
        
        return {
            "recurring": len(recurring_symptoms) > 0,
            "recurring_symptoms": recurring_symptoms,
            "frequency_data": symptom_counts
        }

    def _analyze_seasonal_pattern(self, current_symptoms: List[str], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze seasonal patterns in symptoms."""
        # This would analyze historical data for seasonal patterns
        # For now, return a simple analysis
        return {
            "seasonal": False,
            "season": "unknown"
        }

    def _generate_medical_hypothesis(self, pattern: Dict[str, Any], symptoms: List[str]) -> Dict[str, Any]:
        """Generate a medical hypothesis from a pattern."""
        return {
            "hypothesis": f"Pattern: {pattern['type']}",
            "confidence": pattern.get("strength", 0.0),
            "implication": pattern.get("implication", "unknown"),
            "supporting_evidence": symptoms
        }

    def _calculate_diagnostic_match(self, symptoms: List[str], criteria: Dict[str, Any]) -> float:
        """Calculate how well symptoms match diagnostic criteria."""
        required_symptoms = criteria.get("required_symptoms", [])
        supporting_symptoms = criteria.get("supporting_symptoms", [])
        
        # Check required symptoms
        required_matches = sum(1 for req in required_symptoms if any(req in s.lower() for s in symptoms))
        required_score = required_matches / len(required_symptoms) if required_symptoms else 0.0
        
        # Check supporting symptoms
        supporting_matches = sum(1 for sup in supporting_symptoms if any(sup in s.lower() for s in symptoms))
        supporting_score = supporting_matches / len(supporting_symptoms) if supporting_symptoms else 0.0
        
        # Weighted score (required symptoms more important)
        total_score = (required_score * 0.7) + (supporting_score * 0.3)
        
        return total_score

    def _check_pattern_match(self, symptoms: List[str], pattern: List[str]) -> bool:
        """Check if symptoms match a pattern."""
        symptom_text = " ".join(symptoms).lower()
        pattern_matches = sum(1 for p in pattern if p in symptom_text)
        return pattern_matches >= len(pattern) * 0.7  # 70% match threshold

    def can_handle(self, context: AgentContext, **kwargs) -> bool:
        """Check if this agent can handle the request."""
        return "symptoms" in kwargs and isinstance(kwargs["symptoms"], list)

    def get_provided_capabilities(self) -> List[str]:
        """Get capabilities provided by this agent."""
        return [
            "advanced_symptom_analysis",
            "medical_reasoning",
            "pattern_recognition",
            "risk_assessment",
            "autonomous_diagnosis",
            "memory_based_analysis",
            "context_aware_assessment"
        ]
