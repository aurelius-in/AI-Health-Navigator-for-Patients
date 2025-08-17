"""
API tests for AI Health Navigator endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestHealthEndpoints:
    """Test health check and monitoring endpoints."""
    
    def test_health_check(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_metrics_endpoint(self, client: TestClient):
        """Test the metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestSymptomAnalysis:
    """Test symptom analysis endpoints."""
    
    def test_analyze_symptoms_success(self, client: TestClient, sample_symptom_data):
        """Test successful symptom analysis."""
        with patch('ai_health_navigator.ai.models.model_manager.analyze_symptoms') as mock_analyze:
            mock_analyze.return_value = {
                "analysis_id": "test-123",
                "conditions": ["migraine", "tension headache"],
                "confidence": 0.85,
                "recommendations": ["rest", "hydration"],
                "urgency": "low"
            }
            
            response = client.post("/api/v1/symptoms/analyze", json=sample_symptom_data)
            assert response.status_code == 200
            data = response.json()
            assert "analysis_id" in data
            assert "conditions" in data
            assert "confidence" in data
    
    def test_analyze_symptoms_invalid_data(self, client: TestClient):
        """Test symptom analysis with invalid data."""
        invalid_data = {"symptoms": []}  # Empty symptoms list
        response = client.post("/api/v1/symptoms/analyze", json=invalid_data)
        assert response.status_code == 422
    
    def test_batch_analysis(self, client: TestClient):
        """Test batch symptom analysis."""
        batch_data = {
            "analyses": [
                {"symptoms": ["headache"], "severity": "mild"},
                {"symptoms": ["fever", "cough"], "severity": "moderate"}
            ]
        }
        
        with patch('ai_health_navigator.ai.models.model_manager.analyze_symptoms_batch') as mock_batch:
            mock_batch.return_value = [
                {"analysis_id": "batch-1", "conditions": ["tension headache"]},
                {"analysis_id": "batch-2", "conditions": ["common cold"]}
            ]
            
            response = client.post("/api/v1/symptoms/batch", json=batch_data)
            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == 2


class TestTriageAssessment:
    """Test triage assessment endpoints."""
    
    def test_triage_assessment_success(self, client: TestClient, sample_triage_data):
        """Test successful triage assessment."""
        with patch('ai_health_navigator.ai.models.model_manager.assess_triage') as mock_triage:
            mock_triage.return_value = {
                "triage_id": "triage-123",
                "urgency_level": "high",
                "recommended_action": "emergency_room",
                "estimated_wait_time": "immediate",
                "risk_factors": ["chest pain", "age > 40"]
            }
            
            response = client.post("/api/v1/triage/assess", json=sample_triage_data)
            assert response.status_code == 200
            data = response.json()
            assert "urgency_level" in data
            assert "recommended_action" in data
    
    def test_triage_assessment_critical(self, client: TestClient):
        """Test triage assessment for critical symptoms."""
        critical_data = {
            "symptoms": ["unconsciousness", "severe bleeding"],
            "severity": "critical",
            "duration": "5 minutes",
            "age": 30,
            "gender": "female"
        }
        
        with patch('ai_health_navigator.ai.models.model_manager.assess_triage') as mock_triage:
            mock_triage.return_value = {
                "triage_id": "critical-123",
                "urgency_level": "critical",
                "recommended_action": "call_911",
                "estimated_wait_time": "immediate",
                "risk_factors": ["life_threatening"]
            }
            
            response = client.post("/api/v1/triage/assess", json=critical_data)
            assert response.status_code == 200
            data = response.json()
            assert data["urgency_level"] == "critical"


class TestAgentEndpoints:
    """Test AI agent endpoints."""
    
    def test_agent_health(self, client: TestClient):
        """Test agent health endpoint."""
        response = client.get("/api/v1/agents/health")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "overall_status" in data
    
    def test_agent_stats(self, client: TestClient):
        """Test agent statistics endpoint."""
        response = client.get("/api/v1/agents/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "success_rate" in data
    
    def test_comprehensive_assessment(self, client: TestClient):
        """Test comprehensive health assessment endpoint."""
        assessment_data = {
            "symptoms": ["fatigue", "weight_loss"],
            "medications": ["metformin"],
            "age": 55,
            "gender": "female",
            "family_history": ["diabetes"],
            "mood_assessment": {"depression_level": 3}
        }
        
        with patch('ai_health_navigator.ai.agents.agent_orchestrator.AgentOrchestrator.execute_workflow') as mock_execute:
            mock_execute.return_value = {
                "workflow_id": "comp-123",
                "results": {
                    "symptom_analysis": {"conditions": ["diabetes"]},
                    "medication_management": {"interactions": []},
                    "preventive_care": {"recommendations": ["blood_sugar_test"]},
                    "mental_health": {"risk_level": "low"}
                },
                "overall_health_score": 75,
                "risk_level": "moderate"
            }
            
            response = client.post("/api/v1/agents/comprehensive-assessment", json=assessment_data)
            assert response.status_code == 200
            data = response.json()
            assert "workflow_id" in data
            assert "overall_health_score" in data
            assert "results" in data


class TestProviderEndpoints:
    """Test healthcare provider endpoints."""
    
    def test_search_providers(self, client: TestClient):
        """Test provider search endpoint."""
        search_params = {
            "specialty": "cardiology",
            "location": "New York, NY",
            "insurance": "blue_cross"
        }
        
        response = client.get("/api/v1/providers/search", params=search_params)
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], list)
    
    def test_provider_details(self, client: TestClient):
        """Test provider details endpoint."""
        provider_id = "provider-123"
        response = client.get(f"/api/v1/providers/{provider_id}")
        assert response.status_code == 200
        data = response.json()
        assert "provider_id" in data
        assert "name" in data


class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_user(self, client: TestClient, sample_user_data):
        """Test user registration."""
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert "email" in data
    
    def test_login_user(self, client: TestClient):
        """Test user login."""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
