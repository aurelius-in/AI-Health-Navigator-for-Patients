"""
Advanced LLM service for healthcare applications with multi-provider support.
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import openai
from anthropic import Anthropic
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class LLMResponse(BaseModel):
    """Standardized LLM response."""
    
    content: str = Field(description="Generated content")
    model: str = Field(description="Model used")
    provider: str = Field(description="LLM provider")
    tokens_used: Optional[int] = Field(description="Tokens consumed")
    confidence: Optional[float] = Field(description="Confidence score")
    reasoning: Optional[str] = Field(description="Model reasoning")


class PromptTemplate(BaseModel):
    """Healthcare-specific prompt template."""
    
    name: str = Field(description="Template name")
    system_prompt: str = Field(description="System prompt")
    human_prompt: str = Field(description="Human prompt template")
    variables: List[str] = Field(description="Template variables")
    temperature: float = Field(default=0.1, description="Temperature setting")
    max_tokens: int = Field(default=2000, description="Maximum tokens")


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.logger = get_logger(f"LLMProvider.{provider_name}")
    
    @abstractmethod
    async def generate_response(self, messages: List[BaseMessage], **kwargs) -> LLMResponse:
        """Generate response from the LLM."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self):
        super().__init__("openai")
        self.client = None
        self.chat_model = None
        
    async def initialize(self) -> None:
        """Initialize OpenAI client."""
        try:
            if not settings.llm.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            
            openai.api_key = settings.llm.openai_api_key
            self.client = openai.AsyncOpenAI(api_key=settings.llm.openai_api_key)
            
            # Initialize LangChain chat model
            self.chat_model = ChatOpenAI(
                model_name=settings.llm.default_model,
                temperature=settings.llm.temperature,
                max_tokens=settings.llm.max_tokens,
                openai_api_key=settings.llm.openai_api_key
            )
            
            self.logger.info("OpenAI provider initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI provider: {e}")
            raise
    
    async def generate_response(self, messages: List[BaseMessage], **kwargs) -> LLMResponse:
        """Generate response using OpenAI."""
        try:
            # Convert LangChain messages to OpenAI format
            openai_messages = []
            for message in messages:
                if isinstance(message, SystemMessage):
                    openai_messages.append({"role": "system", "content": message.content})
                elif isinstance(message, HumanMessage):
                    openai_messages.append({"role": "user", "content": message.content})
                else:
                    openai_messages.append({"role": "assistant", "content": message.content})
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=settings.llm.default_model,
                messages=openai_messages,
                temperature=kwargs.get("temperature", settings.llm.temperature),
                max_tokens=kwargs.get("max_tokens", settings.llm.max_tokens),
                **kwargs
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider="openai",
                tokens_used=response.usage.total_tokens if response.usage else None,
                confidence=kwargs.get("confidence", 0.9)
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI response generation failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check OpenAI health."""
        try:
            await self.client.models.list()
            return True
        except Exception as e:
            self.logger.error(f"OpenAI health check failed: {e}")
            return False


class AnthropicProvider(BaseLLMProvider):
    """Anthropic LLM provider."""
    
    def __init__(self):
        super().__init__("anthropic")
        self.client = None
        self.chat_model = None
        
    async def initialize(self) -> None:
        """Initialize Anthropic client."""
        try:
            if not settings.llm.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            
            self.client = Anthropic(api_key=settings.llm.anthropic_api_key)
            
            # Initialize LangChain chat model
            self.chat_model = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                temperature=settings.llm.temperature,
                max_tokens=settings.llm.max_tokens,
                anthropic_api_key=settings.llm.anthropic_api_key
            )
            
            self.logger.info("Anthropic provider initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Anthropic provider: {e}")
            raise
    
    async def generate_response(self, messages: List[BaseMessage], **kwargs) -> LLMResponse:
        """Generate response using Anthropic."""
        try:
            # Convert messages to Anthropic format
            system_message = ""
            user_message = ""
            
            for message in messages:
                if isinstance(message, SystemMessage):
                    system_message = message.content
                elif isinstance(message, HumanMessage):
                    user_message = message.content
            
            # Generate response
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=kwargs.get("max_tokens", settings.llm.max_tokens),
                temperature=kwargs.get("temperature", settings.llm.temperature),
                system=system_message,
                messages=[{"role": "user", "content": user_message}],
                **kwargs
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=response.model,
                provider="anthropic",
                tokens_used=response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
                confidence=kwargs.get("confidence", 0.9)
            )
            
        except Exception as e:
            self.logger.error(f"Anthropic response generation failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Anthropic health."""
        try:
            # Simple health check
            await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            self.logger.error(f"Anthropic health check failed: {e}")
            return False


class HealthcarePromptTemplates:
    """Healthcare-specific prompt templates."""
    
    @staticmethod
    def get_symptom_analysis_template() -> PromptTemplate:
        """Get symptom analysis prompt template."""
        return PromptTemplate(
            name="symptom_analysis",
            system_prompt="""You are an advanced AI medical assistant with expertise in symptom analysis and triage. 
            Your role is to analyze patient symptoms and provide evidence-based assessments.
            
            Guidelines:
            - Always prioritize patient safety
            - Be thorough but concise
            - Consider differential diagnoses
            - Provide clear recommendations
            - Include confidence levels
            - Mention when immediate medical attention is needed
            
            Remember: This is for informational purposes only and should not replace professional medical advice.""",
            human_prompt="""Please analyze the following symptoms and provide a comprehensive assessment:

Symptoms: {symptoms}
Patient Age: {age}
Patient Gender: {gender}
Duration: {duration}
Severity: {severity}

Please provide:
1. Primary symptoms identified
2. Possible medical conditions (with probabilities)
3. Urgency level assessment
4. Recommended next steps
5. Any red flags or warning signs
6. Confidence in your assessment""",
            variables=["symptoms", "age", "gender", "duration", "severity"],
            temperature=0.1
        )
    
    @staticmethod
    def get_triage_assessment_template() -> PromptTemplate:
        """Get triage assessment prompt template."""
        return PromptTemplate(
            name="triage_assessment",
            system_prompt="""You are an expert triage nurse with years of experience in emergency medicine.
            Your task is to assess the urgency of medical situations and provide appropriate care recommendations.
            
            Urgency Levels:
            - Emergency: Immediate medical attention required (call 911)
            - High: Urgent care needed within 2 hours
            - Medium: Medical attention needed within 24 hours
            - Low: Routine care or monitoring
            
            Always err on the side of caution when in doubt.""",
            human_prompt="""Based on the following symptom analysis, provide a triage assessment:

Symptom Analysis: {symptom_analysis}
Patient Context: {patient_context}
Risk Factors: {risk_factors}

Please provide:
1. Urgency level classification
2. Recommended immediate action
3. Time frame for seeking care
4. Risk factors to consider
5. Any contraindications or warnings""",
            variables=["symptom_analysis", "patient_context", "risk_factors"],
            temperature=0.1
        )
    
    @staticmethod
    def get_provider_recommendation_template() -> PromptTemplate:
        """Get provider recommendation prompt template."""
        return PromptTemplate(
            name="provider_recommendation",
            system_prompt="""You are a healthcare navigation specialist helping patients find the right providers.
            Consider factors like specialization, location, insurance, and patient preferences.
            
            Provider Types:
            - Primary Care Physician (PCP)
            - Specialists (Cardiology, Neurology, etc.)
            - Urgent Care
            - Emergency Room
            - Telemedicine""",
            human_prompt="""Based on the patient's needs, recommend appropriate healthcare providers:

Patient Needs: {patient_needs}
Location: {location}
Insurance: {insurance}
Preferences: {preferences}

Please provide:
1. Recommended provider types
2. Specific considerations for each type
3. When to see each type
4. Questions to ask providers
5. Preparation tips""",
            variables=["patient_needs", "location", "insurance", "preferences"],
            temperature=0.2
        )
    
    @staticmethod
    def get_insurance_guidance_template() -> PromptTemplate:
        """Get insurance guidance prompt template."""
        return PromptTemplate(
            name="insurance_guidance",
            system_prompt="""You are an insurance specialist helping patients understand their coverage.
            Provide clear, actionable guidance on insurance matters.
            
            Key Areas:
            - Coverage verification
            - Pre-authorization requirements
            - Cost estimates
            - Appeal processes
            - Network considerations""",
            human_prompt="""Help the patient understand their insurance coverage for the following:

Service/Procedure: {service}
Insurance Plan: {insurance_plan}
Provider: {provider}
Patient Questions: {questions}

Please provide:
1. Coverage status
2. Estimated costs
3. Pre-authorization requirements
4. Alternative options if not covered
5. Next steps for the patient""",
            variables=["service", "insurance_plan", "provider", "questions"],
            temperature=0.1
        )


class LLMService:
    """Main LLM service orchestrating multiple providers."""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider = "openai"
        self.logger = get_logger("LLMService")
        self.prompt_templates = HealthcarePromptTemplates()
    
    async def initialize(self) -> None:
        """Initialize all LLM providers."""
        try:
            # Initialize OpenAI
            if settings.llm.openai_api_key:
                openai_provider = OpenAIProvider()
                await openai_provider.initialize()
                self.providers["openai"] = openai_provider
            
            # Initialize Anthropic
            if settings.llm.anthropic_api_key:
                anthropic_provider = AnthropicProvider()
                await anthropic_provider.initialize()
                self.providers["anthropic"] = anthropic_provider
            
            self.logger.info(f"LLM service initialized with providers: {list(self.providers.keys())}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM service: {e}")
            raise
    
    async def generate_response(
        self, 
        prompt_template: PromptTemplate, 
        variables: Dict[str, Any], 
        provider: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using specified template and provider."""
        try:
            # Select provider
            selected_provider = provider or self.default_provider
            if selected_provider not in self.providers:
                raise ValueError(f"Provider {selected_provider} not available")
            
            # Format prompt
            messages = self._format_prompt(prompt_template, variables)
            
            # Generate response
            response = await self.providers[selected_provider].generate_response(
                messages,
                temperature=prompt_template.temperature,
                max_tokens=prompt_template.max_tokens,
                **kwargs
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            raise
    
    def _format_prompt(self, template: PromptTemplate, variables: Dict[str, Any]) -> List[BaseMessage]:
        """Format prompt template with variables."""
        try:
            # Format system prompt
            system_content = template.system_prompt
            
            # Format human prompt
            human_content = template.human_prompt.format(**variables)
            
            return [
                SystemMessage(content=system_content),
                HumanMessage(content=human_content)
            ]
            
        except KeyError as e:
            raise ValueError(f"Missing required variable: {e}")
    
    async def analyze_symptoms(
        self, 
        symptoms: str, 
        age: Optional[int] = None,
        gender: Optional[str] = None,
        duration: Optional[str] = None,
        severity: Optional[str] = None,
        provider: Optional[str] = None
    ) -> LLMResponse:
        """Analyze symptoms using LLM."""
        template = self.prompt_templates.get_symptom_analysis_template()
        
        variables = {
            "symptoms": symptoms,
            "age": age or "Not specified",
            "gender": gender or "Not specified",
            "duration": duration or "Not specified",
            "severity": severity or "Not specified"
        }
        
        return await self.generate_response(template, variables, provider)
    
    async def assess_triage(
        self, 
        symptom_analysis: str,
        patient_context: Optional[str] = None,
        risk_factors: Optional[str] = None,
        provider: Optional[str] = None
    ) -> LLMResponse:
        """Assess triage using LLM."""
        template = self.prompt_templates.get_triage_assessment_template()
        
        variables = {
            "symptom_analysis": symptom_analysis,
            "patient_context": patient_context or "Not specified",
            "risk_factors": risk_factors or "None identified"
        }
        
        return await self.generate_response(template, variables, provider)
    
    async def recommend_providers(
        self,
        patient_needs: str,
        location: Optional[str] = None,
        insurance: Optional[str] = None,
        preferences: Optional[str] = None,
        provider: Optional[str] = None
    ) -> LLMResponse:
        """Recommend healthcare providers using LLM."""
        template = self.prompt_templates.get_provider_recommendation_template()
        
        variables = {
            "patient_needs": patient_needs,
            "location": location or "Not specified",
            "insurance": insurance or "Not specified",
            "preferences": preferences or "None"
        }
        
        return await self.generate_response(template, variables, provider)
    
    async def provide_insurance_guidance(
        self,
        service: str,
        insurance_plan: Optional[str] = None,
        provider: Optional[str] = None,
        questions: Optional[str] = None,
        llm_provider: Optional[str] = None
    ) -> LLMResponse:
        """Provide insurance guidance using LLM."""
        template = self.prompt_templates.get_insurance_guidance_template()
        
        variables = {
            "service": service,
            "insurance_plan": insurance_plan or "Not specified",
            "provider": provider or "Not specified",
            "questions": questions or "General coverage questions"
        }
        
        return await self.generate_response(template, variables, llm_provider)
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all providers."""
        health_status = {}
        for name, provider in self.providers.items():
            health_status[name] = await provider.health_check()
        return health_status


# Global LLM service instance
llm_service = LLMService()
