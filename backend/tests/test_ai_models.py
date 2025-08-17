"""
Tests for AI models and agents.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from ai_health_navigator.ai.models import SymptomClassifier, TriageModel, AIModelManager
from ai_health_navigator.ai.agents import (
    SymptomAnalysisAgent,
    MedicationManagementAgent,
    PreventiveCareAgent,
    MentalHealthAgent,
    AgentOrchestrator,
    AgentContext,
    AgentPriority
)


class TestSymptomClassifier:
    """Test the SymptomClassifier model."""
    
    def test_classify_symptoms(self):
        """Test symptom classification."""
        classifier = SymptomClassifier()
        symptoms = ["headache", "fever", "fatigue"]
        
        with patch.object(classifier, '_predict') as mock_predict:
            mock_predict.return_value = {
                "conditions": ["migraine", "common_cold"],
                "confidence": 0.85,
                "urgency": "low"
            }
            
            result = classifier.classify(symptoms)
            assert "conditions" in result
            assert "confidence" in result
            assert "urgency" in result
    
    def test_classify_empty_symptoms(self):
        """Test classification with empty symptoms."""
        classifier = SymptomClassifier()
        result = classifier.classify([])
        assert result["conditions"] == []
        assert result["confidence"] == 0.0


class TestTriageModel:
    """Test the TriageModel."""
    
    def test_assess_urgency(self):
        """Test triage urgency assessment."""
        model = TriageModel()
        symptoms = ["chest pain", "shortness of breath"]
        patient_info = {"age": 45, "gender": "male"}
        
        with patch.object(model, '_predict') as mock_predict:
            mock_predict.return_value = {
                "urgency_level": "high",
                "recommended_action": "emergency_room",
                "estimated_wait_time": "immediate"
            }
            
            result = model.assess(symptoms, patient_info)
            assert "urgency_level" in result
            assert "recommended_action" in result
            assert "estimated_wait_time" in result
    
    def test_critical_symptoms(self):
        """Test assessment of critical symptoms."""
        model = TriageModel()
        critical_symptoms = ["unconsciousness", "severe bleeding"]
        
        with patch.object(model, '_predict') as mock_predict:
            mock_predict.return_value = {
                "urgency_level": "critical",
                "recommended_action": "call_911",
                "estimated_wait_time": "immediate"
            }
            
            result = model.assess(critical_symptoms, {})
            assert result["urgency_level"] == "critical"


class TestAIModelManager:
    """Test the AI Model Manager."""
    
    def test_analyze_symptoms(self):
        """Test symptom analysis through model manager."""
        manager = AIModelManager()
        
        with patch.object(manager.symptom_classifier, 'classify') as mock_classify:
            mock_classify.return_value = {
                "conditions": ["migraine"],
                "confidence": 0.9,
                "urgency": "low"
            }
            
            result = manager.analyze_symptoms(["headache"])
            assert "conditions" in result
            assert result["confidence"] == 0.9
    
    def test_assess_triage(self):
        """Test triage assessment through model manager."""
        manager = AIModelManager()
        
        with patch.object(manager.triage_model, 'assess') as mock_assess:
            mock_assess.return_value = {
                "urgency_level": "moderate",
                "recommended_action": "urgent_care",
                "estimated_wait_time": "2_hours"
            }
            
            result = manager.assess_triage(["fever"], {"age": 30})
            assert "urgency_level" in result
            assert "recommended_action" in result


class TestSymptomAnalysisAgent:
    """Test the SymptomAnalysisAgent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initialization."""
        agent = SymptomAnalysisAgent()
        await agent.initialize()
        assert agent.status == "ready"
    
    @pytest.mark.asyncio
    async def test_symptom_analysis(self):
        """Test symptom analysis workflow."""
        agent = SymptomAnalysisAgent()
        await agent.initialize()
        
        context = AgentContext(
            user_id="test_user",
            session_id="test_session",
            request_id="test_request",
            timestamp=datetime.utcnow(),
            metadata={},
            priority=AgentPriority.NORMAL
        )
        
        with patch.object(agent, '_analyze_symptoms') as mock_analyze:
            mock_analyze.return_value = {
                "conditions": ["migraine"],
                "confidence": 0.85,
                "recommendations": ["rest", "hydration"]
            }
            
            result = await agent.run(
                context=context,
                symptoms=["headache", "nausea"],
                severity="moderate",
                duration="2 hours"
            )
            
            assert result.success
            assert "conditions" in result.data
            assert "recommendations" in result.data


class TestMedicationManagementAgent:
    """Test the MedicationManagementAgent."""
    
    @pytest.mark.asyncio
    async def test_medication_safety_check(self):
        """Test medication safety analysis."""
        agent = MedicationManagementAgent()
        await agent.initialize()
        
        context = AgentContext(
            user_id="test_user",
            session_id="test_session",
            request_id="test_request",
            timestamp=datetime.utcnow(),
            metadata={},
            priority=AgentPriority.NORMAL
        )
        
        result = await agent.run(
            context=context,
            medications=["warfarin", "aspirin"],
            patient_conditions=["atrial_fibrillation"],
            allergies=["penicillin"]
        )
        
        assert result.success
        assert "interactions" in result.data
        assert "safety_alerts" in result.data


class TestPreventiveCareAgent:
    """Test the PreventiveCareAgent."""
    
    @pytest.mark.asyncio
    async def test_preventive_care_planning(self):
        """Test preventive care planning."""
        agent = PreventiveCareAgent()
        await agent.initialize()
        
        context = AgentContext(
            user_id="test_user",
            session_id="test_session",
            request_id="test_request",
            timestamp=datetime.utcnow(),
            metadata={},
            priority=AgentPriority.NORMAL
        )
        
        result = await agent.run(
            context=context,
            age=45,
            gender="female",
            family_history=["breast_cancer", "diabetes"],
            lifestyle_factors=["sedentary", "smoking"]
        )
        
        assert result.success
        assert "screening_plan" in result.data
        assert "vaccination_schedule" in result.data


class TestMentalHealthAgent:
    """Test the MentalHealthAgent."""
    
    @pytest.mark.asyncio
    async def test_mental_health_assessment(self):
        """Test mental health assessment."""
        agent = MentalHealthAgent()
        await agent.initialize()
        
        context = AgentContext(
            user_id="test_user",
            session_id="test_session",
            request_id="test_request",
            timestamp=datetime.utcnow(),
            metadata={},
            priority=AgentPriority.NORMAL
        )
        
        result = await agent.run(
            context=context,
            symptoms=["sadness", "hopelessness", "fatigue"],
            mood_assessment={"depression_level": 8, "suicidal_thoughts": False},
            current_stressors=["work_stress", "relationship_issues"]
        )
        
        assert result.success
        assert "risk_assessment" in result.data
        assert "support_plan" in result.data
    
    @pytest.mark.asyncio
    async def test_crisis_intervention(self):
        """Test crisis intervention."""
        agent = MentalHealthAgent()
        await agent.initialize()
        
        context = AgentContext(
            user_id="test_user",
            session_id="test_session",
            request_id="test_request",
            timestamp=datetime.utcnow(),
            metadata={},
            priority=AgentPriority.CRITICAL
        )
        
        result = await agent.run(
            context=context,
            symptoms=["suicidal_thoughts", "hopelessness"],
            mood_assessment={"depression_level": 10, "suicidal_thoughts": True},
            crisis_indicators=["suicidal_ideation", "isolation"]
        )
        
        assert result.success
        assert result.data["crisis_risk"] == "high"
        assert "emergency_contacts" in result.data


class TestAgentOrchestrator:
    """Test the AgentOrchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        assert len(orchestrator.agent_registry) > 0
    
    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        """Test sequential workflow execution."""
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        context = AgentContext(
            user_id="test_user",
            session_id="test_session",
            request_id="test_request",
            timestamp=datetime.utcnow(),
            metadata={},
            priority=AgentPriority.NORMAL
        )
        
        workflow = {
            "strategy": "sequential",
            "tasks": [
                {
                    "agent_type": "symptom_analysis",
                    "parameters": {"symptoms": ["headache"]}
                },
                {
                    "agent_type": "medication_management",
                    "parameters": {"medications": ["ibuprofen"]}
                }
            ]
        }
        
        with patch.object(orchestrator, '_execute_agent') as mock_execute:
            mock_execute.return_value = AgentResult(
                success=True,
                data={"test": "data"},
                metadata={},
                timestamp=datetime.utcnow()
            )
            
            result = await orchestrator.execute_workflow(context, workflow)
            assert result.success
            assert len(result.data["results"]) == 2
    
    @pytest.mark.asyncio
    async def test_request_routing(self):
        """Test intelligent request routing."""
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        context = AgentContext(
            user_id="test_user",
            session_id="test_session",
            request_id="test_request",
            timestamp=datetime.utcnow(),
            metadata={},
            priority=AgentPriority.NORMAL
        )
        
        # Test routing to symptom analysis
        request_data = {"symptoms": ["headache", "fever"]}
        tasks = orchestrator.route_request(context, request_data)
        assert len(tasks) > 0
        assert any(task.agent_type.__name__ == "SymptomAnalysisAgent" for task in tasks)
        
        # Test routing to medication management
        request_data = {"medications": ["warfarin", "aspirin"]}
        tasks = orchestrator.route_request(context, request_data)
        assert len(tasks) > 0
        assert any(task.agent_type.__name__ == "MedicationManagementAgent" for task in tasks)
