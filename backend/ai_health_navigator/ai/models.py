"""
Advanced AI models for healthcare analysis and decision support.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class SymptomAnalysis(BaseModel):
    """Result of symptom analysis."""
    
    primary_symptoms: List[str] = Field(description="Identified primary symptoms")
    secondary_symptoms: List[str] = Field(description="Related secondary symptoms")
    confidence_score: float = Field(description="Confidence in symptom identification")
    medical_conditions: List[Dict[str, Any]] = Field(description="Possible medical conditions")
    urgency_level: str = Field(description="Urgency level: low, medium, high, emergency")
    recommended_care: str = Field(description="Recommended type of care")
    reasoning: str = Field(description="AI reasoning for the assessment")


class TriageAssessment(BaseModel):
    """Triage assessment result."""
    
    urgency_score: float = Field(description="Urgency score (0-1)")
    urgency_level: str = Field(description="Urgency classification")
    recommended_action: str = Field(description="Recommended immediate action")
    time_to_care: str = Field(description="Recommended time to seek care")
    risk_factors: List[str] = Field(description="Identified risk factors")
    contraindications: List[str] = Field(description="Any contraindications")


class MedicalCondition(BaseModel):
    """Medical condition information."""
    
    icd10_code: str = Field(description="ICD-10 code")
    name: str = Field(description="Condition name")
    probability: float = Field(description="Probability score")
    symptoms: List[str] = Field(description="Associated symptoms")
    severity: str = Field(description="Condition severity")
    treatment_options: List[str] = Field(description="Treatment options")


class BaseAIModel(ABC):
    """Base class for AI models."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.logger = get_logger(f"{self.__class__.__name__}.{model_name}")
    
    @abstractmethod
    async def predict(self, input_data: Any) -> Any:
        """Make prediction with the model."""
        pass
    
    @abstractmethod
    async def load_model(self) -> None:
        """Load the model."""
        pass


class SymptomClassifier(BaseAIModel):
    """Advanced symptom classification model."""
    
    def __init__(self):
        super().__init__("symptom_classifier")
        self.model = None
        self.tokenizer = None
        self.vectorizer = None
        self.classifier = None
        self.embedding_model = None
        self.symptom_embeddings = None
        
    async def load_model(self) -> None:
        """Load the symptom classification model."""
        try:
            # Load transformer model for symptom classification
            model_name = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name, num_labels=100  # Adjust based on symptom categories
            )
            
            # Load TF-IDF vectorizer for traditional ML approach
            self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 3))
            
            # Load sentence transformer for semantic similarity
            self.embedding_model = SentenceTransformer(settings.ml_models.embedding_model)
            
            # Load traditional classifier
            self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            
            self.logger.info("Symptom classifier model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load symptom classifier: {e}")
            raise
    
    async def predict(self, symptoms_text: str) -> SymptomAnalysis:
        """Analyze symptoms and provide comprehensive assessment."""
        try:
            # Multi-modal analysis
            transformer_result = await self._transformer_analysis(symptoms_text)
            ml_result = await self._ml_analysis(symptoms_text)
            semantic_result = await self._semantic_analysis(symptoms_text)
            
            # Combine results using ensemble approach
            combined_result = self._ensemble_results(
                transformer_result, ml_result, semantic_result
            )
            
            return combined_result
            
        except Exception as e:
            self.logger.error(f"Symptom analysis failed: {e}")
            raise
    
    async def _transformer_analysis(self, text: str) -> Dict[str, Any]:
        """Analyze symptoms using transformer model."""
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512,
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)
            
        return {
            "probabilities": probabilities.numpy(),
            "confidence": float(torch.max(probabilities)),
            "method": "transformer"
        }
    
    async def _ml_analysis(self, text: str) -> Dict[str, Any]:
        """Analyze symptoms using traditional ML."""
        # This would be trained on historical symptom data
        features = self.vectorizer.transform([text])
        prediction = self.classifier.predict_proba(features)
        
        return {
            "probabilities": prediction,
            "confidence": float(np.max(prediction)),
            "method": "ml"
        }
    
    async def _semantic_analysis(self, text: str) -> Dict[str, Any]:
        """Analyze symptoms using semantic similarity."""
        text_embedding = self.embedding_model.encode([text])
        
        # Compare with symptom database embeddings
        similarities = self._calculate_similarities(text_embedding)
        
        return {
            "similarities": similarities,
            "confidence": float(np.max(similarities)),
            "method": "semantic"
        }
    
    def _calculate_similarities(self, text_embedding: np.ndarray) -> np.ndarray:
        """Calculate similarities with symptom database."""
        # This would compare with pre-computed symptom embeddings
        # For now, return dummy similarities
        return np.random.random(100)
    
    def _ensemble_results(
        self, 
        transformer_result: Dict[str, Any],
        ml_result: Dict[str, Any], 
        semantic_result: Dict[str, Any]
    ) -> SymptomAnalysis:
        """Combine results from different models using ensemble approach."""
        
        # Weighted ensemble (can be optimized based on model performance)
        weights = {"transformer": 0.5, "ml": 0.3, "semantic": 0.2}
        
        # Combine confidence scores
        total_confidence = (
            transformer_result["confidence"] * weights["transformer"] +
            ml_result["confidence"] * weights["ml"] +
            semantic_result["confidence"] * weights["semantic"]
        )
        
        # Extract primary symptoms (top predictions)
        primary_symptoms = self._extract_primary_symptoms(
            transformer_result, ml_result, semantic_result
        )
        
        # Determine urgency level
        urgency_level = self._determine_urgency_level(total_confidence, primary_symptoms)
        
        # Generate medical conditions
        medical_conditions = self._generate_medical_conditions(primary_symptoms)
        
        return SymptomAnalysis(
            primary_symptoms=primary_symptoms,
            secondary_symptoms=self._extract_secondary_symptoms(primary_symptoms),
            confidence_score=total_confidence,
            medical_conditions=medical_conditions,
            urgency_level=urgency_level,
            recommended_care=self._recommend_care(urgency_level),
            reasoning=self._generate_reasoning(primary_symptoms, medical_conditions)
        )
    
    def _extract_primary_symptoms(
        self, 
        transformer_result: Dict[str, Any],
        ml_result: Dict[str, Any], 
        semantic_result: Dict[str, Any]
    ) -> List[str]:
        """Extract primary symptoms from model results."""
        # This would map model outputs to actual symptom names
        # For now, return dummy symptoms
        return ["fever", "cough", "fatigue"]
    
    def _extract_secondary_symptoms(self, primary_symptoms: List[str]) -> List[str]:
        """Extract related secondary symptoms."""
        # This would use medical knowledge graph to find related symptoms
        symptom_relations = {
            "fever": ["chills", "sweating", "headache"],
            "cough": ["sore throat", "chest pain", "shortness of breath"],
            "fatigue": ["weakness", "dizziness", "loss of appetite"]
        }
        
        secondary = []
        for symptom in primary_symptoms:
            if symptom in symptom_relations:
                secondary.extend(symptom_relations[symptom])
        
        return list(set(secondary))
    
    def _determine_urgency_level(self, confidence: float, symptoms: List[str]) -> str:
        """Determine urgency level based on symptoms and confidence."""
        # Emergency symptoms
        emergency_symptoms = ["chest pain", "severe bleeding", "unconsciousness", "seizure"]
        
        if any(symptom in symptoms for symptom in emergency_symptoms):
            return "emergency"
        
        # High urgency symptoms
        high_urgency = ["high fever", "severe pain", "difficulty breathing"]
        if any(symptom in symptoms for symptom in high_urgency):
            return "high"
        
        # Medium urgency
        if confidence > 0.7:
            return "medium"
        
        return "low"
    
    def _generate_medical_conditions(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        """Generate possible medical conditions."""
        # This would use medical knowledge base to map symptoms to conditions
        condition_mapping = {
            "fever": [{"icd10_code": "R50.9", "name": "Fever, unspecified", "probability": 0.8}],
            "cough": [{"icd10_code": "R05.9", "name": "Cough, unspecified", "probability": 0.7}],
            "fatigue": [{"icd10_code": "R53.83", "name": "Other fatigue", "probability": 0.6}]
        }
        
        conditions = []
        for symptom in symptoms:
            if symptom in condition_mapping:
                conditions.extend(condition_mapping[symptom])
        
        return conditions
    
    def _recommend_care(self, urgency_level: str) -> str:
        """Recommend appropriate care based on urgency."""
        care_mapping = {
            "emergency": "Emergency room immediately",
            "high": "Urgent care or emergency room within 2 hours",
            "medium": "Primary care physician within 24 hours",
            "low": "Primary care physician within 1 week"
        }
        return care_mapping.get(urgency_level, "Consult healthcare provider")
    
    def _generate_reasoning(self, symptoms: List[str], conditions: List[Dict[str, Any]]) -> str:
        """Generate AI reasoning for the assessment."""
        return f"Based on the symptoms {', '.join(symptoms)}, the AI identified {len(conditions)} possible conditions with varying probabilities. The assessment considers symptom patterns, severity indicators, and medical knowledge to provide appropriate care recommendations."


class TriageModel(BaseAIModel):
    """Advanced triage assessment model."""
    
    def __init__(self):
        super().__init__("triage_model")
        self.model = None
        self.risk_calculator = None
        
    async def load_model(self) -> None:
        """Load the triage model."""
        try:
            # Load pre-trained triage model
            self.model = pipeline(
                "text-classification",
                model="microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract",
                return_all_scores=True
            )
            
            self.logger.info("Triage model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load triage model: {e}")
            raise
    
    async def predict(self, symptoms_analysis: SymptomAnalysis) -> TriageAssessment:
        """Generate triage assessment."""
        try:
            # Combine symptoms and context
            input_text = f"{' '.join(symptoms_analysis.primary_symptoms)} {symptoms_analysis.reasoning}"
            
            # Get model prediction
            prediction = self.model(input_text)
            
            # Calculate urgency score
            urgency_score = self._calculate_urgency_score(prediction, symptoms_analysis)
            
            # Determine urgency level
            urgency_level = self._classify_urgency(urgency_score)
            
            # Generate assessment
            return TriageAssessment(
                urgency_score=urgency_score,
                urgency_level=urgency_level,
                recommended_action=self._get_recommended_action(urgency_level),
                time_to_care=self._get_time_to_care(urgency_level),
                risk_factors=self._identify_risk_factors(symptoms_analysis),
                contraindications=self._identify_contraindications(symptoms_analysis)
            )
            
        except Exception as e:
            self.logger.error(f"Triage assessment failed: {e}")
            raise
    
    def _calculate_urgency_score(self, prediction: List[Dict], symptoms_analysis: SymptomAnalysis) -> float:
        """Calculate urgency score from model prediction."""
        # Extract confidence scores and weight them
        scores = [p["score"] for p in prediction]
        base_score = np.mean(scores)
        
        # Adjust based on symptom severity
        severity_multiplier = {
            "emergency": 1.5,
            "high": 1.2,
            "medium": 1.0,
            "low": 0.8
        }
        
        multiplier = severity_multiplier.get(symptoms_analysis.urgency_level, 1.0)
        return min(1.0, base_score * multiplier)
    
    def _classify_urgency(self, urgency_score: float) -> str:
        """Classify urgency level based on score."""
        if urgency_score >= 0.8:
            return "emergency"
        elif urgency_score >= 0.6:
            return "high"
        elif urgency_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _get_recommended_action(self, urgency_level: str) -> str:
        """Get recommended immediate action."""
        actions = {
            "emergency": "Call 911 or go to emergency room immediately",
            "high": "Seek urgent medical attention within 2 hours",
            "medium": "Schedule appointment with healthcare provider within 24 hours",
            "low": "Monitor symptoms and consult provider if they worsen"
        }
        return actions.get(urgency_level, "Consult healthcare provider")
    
    def _get_time_to_care(self, urgency_level: str) -> str:
        """Get recommended time to seek care."""
        times = {
            "emergency": "Immediately",
            "high": "Within 2 hours",
            "medium": "Within 24 hours",
            "low": "Within 1 week"
        }
        return times.get(urgency_level, "As soon as possible")
    
    def _identify_risk_factors(self, symptoms_analysis: SymptomAnalysis) -> List[str]:
        """Identify potential risk factors."""
        # This would analyze symptoms against known risk factors
        risk_factors = []
        
        if "chest pain" in symptoms_analysis.primary_symptoms:
            risk_factors.append("Cardiovascular risk")
        
        if "fever" in symptoms_analysis.primary_symptoms:
            risk_factors.append("Infection risk")
        
        return risk_factors
    
    def _identify_contraindications(self, symptoms_analysis: SymptomAnalysis) -> List[str]:
        """Identify potential contraindications."""
        # This would check for contraindications based on symptoms
        contraindications = []
        
        # Add logic to identify contraindications
        return contraindications


class AIModelManager:
    """Manages all AI models in the system."""
    
    def __init__(self):
        self.models: Dict[str, BaseAIModel] = {}
        self.logger = get_logger("AIModelManager")
    
    async def initialize_models(self) -> None:
        """Initialize all AI models."""
        try:
            # Initialize symptom classifier
            symptom_classifier = SymptomClassifier()
            await symptom_classifier.load_model()
            self.models["symptom_classifier"] = symptom_classifier
            
            # Initialize triage model
            triage_model = TriageModel()
            await triage_model.load_model()
            self.models["triage_model"] = triage_model
            
            self.logger.info("All AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {e}")
            raise
    
    def get_model(self, model_name: str) -> BaseAIModel:
        """Get a specific model by name."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        return self.models[model_name]
    
    async def analyze_symptoms(self, symptoms_text: str) -> SymptomAnalysis:
        """Analyze symptoms using the symptom classifier."""
        classifier = self.get_model("symptom_classifier")
        return await classifier.predict(symptoms_text)
    
    async def assess_triage(self, symptoms_analysis: SymptomAnalysis) -> TriageAssessment:
        """Assess triage using the triage model."""
        triage_model = self.get_model("triage_model")
        return await triage_model.predict(symptoms_analysis)


# Global model manager instance
model_manager = AIModelManager()
