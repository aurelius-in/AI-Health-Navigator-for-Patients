"""
Preventive Care Agent for AI Health Navigator.

This agent specializes in preventive health planning, screening recommendations,
and wellness guidance based on age, risk factors, and family history.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from .base_agent import BaseAgent, AgentContext, AgentResult, AgentPriority
from ...core.logging import get_logger

logger = get_logger(__name__)


class PreventiveCareAgent(BaseAgent):
    """
    Agent for preventive care planning and recommendations.
    
    This agent provides personalized preventive care recommendations,
    screening schedules, and wellness guidance based on individual
    risk factors and demographics.
    """

    def __init__(self):
        super().__init__(
            name="preventive_care_agent",
            description="Provides personalized preventive care recommendations and wellness guidance"
        )
        self.screening_guidelines = {
            "general_population": {
                "blood_pressure": {"frequency": "annual", "age_start": 18},
                "cholesterol": {"frequency": "every_5_years", "age_start": 20},
                "diabetes": {"frequency": "every_3_years", "age_start": 45},
                "colorectal_cancer": {"frequency": "every_10_years", "age_start": 45},
                "breast_cancer": {"frequency": "every_2_years", "age_start": 50},
                "prostate_cancer": {"frequency": "annual", "age_start": 55},
                "osteoporosis": {"frequency": "every_2_years", "age_start": 65}
            },
            "high_risk_factors": {
                "family_history": {
                    "breast_cancer": {"frequency": "annual", "age_start": 40},
                    "colorectal_cancer": {"frequency": "every_5_years", "age_start": 40},
                    "diabetes": {"frequency": "annual", "age_start": 35}
                },
                "lifestyle": {
                    "smoking": {"lung_cancer": {"frequency": "annual", "age_start": 55}},
                    "obesity": {"diabetes": {"frequency": "annual", "age_start": 35}},
                    "sedentary": {"cardiovascular": {"frequency": "annual", "age_start": 30}}
                }
            }
        }
        
        self.vaccination_schedule = {
            "adults": {
                "flu": {"frequency": "annual", "age_start": 18},
                "tdap": {"frequency": "every_10_years", "age_start": 18},
                "covid_19": {"frequency": "as_recommended", "age_start": 18},
                "shingles": {"frequency": "once", "age_start": 50},
                "pneumonia": {"frequency": "once", "age_start": 65}
            },
            "children": {
                "mmr": {"frequency": "schedule", "age_start": 12},
                "varicella": {"frequency": "schedule", "age_start": 12},
                "hepatitis_b": {"frequency": "schedule", "age_start": 0}
            }
        }

    def validate_input(self, context: AgentContext, **kwargs) -> bool:
        """Validate input parameters for preventive care planning."""
        required_fields = ["age", "gender"]
        
        for field in required_fields:
            if field not in kwargs:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        age = kwargs.get("age", 0)
        if not isinstance(age, int) or age < 0 or age > 120:
            self.logger.error("Age must be a valid integer between 0 and 120")
            return False
        
        return True

    async def execute(self, context: AgentContext, **kwargs) -> AgentResult:
        """Execute preventive care planning."""
        age = kwargs.get("age", 0)
        gender = kwargs.get("gender", "unknown")
        family_history = kwargs.get("family_history", [])
        lifestyle_factors = kwargs.get("lifestyle_factors", [])
        current_conditions = kwargs.get("current_conditions", [])
        last_screenings = kwargs.get("last_screenings", {})
        insurance_coverage = kwargs.get("insurance_coverage", "standard")

        try:
            # Step 1: Generate screening recommendations
            screening_plan = await self._generate_screening_plan(
                age, gender, family_history, lifestyle_factors, last_screenings
            )
            
            # Step 2: Create vaccination schedule
            vaccination_plan = await self._create_vaccination_plan(age, gender)
            
            # Step 3: Develop wellness recommendations
            wellness_plan = await self._develop_wellness_plan(
                age, gender, lifestyle_factors, current_conditions
            )
            
            # Step 4: Assess risk factors
            risk_assessment = await self._assess_risk_factors(
                age, gender, family_history, lifestyle_factors, current_conditions
            )
            
            # Step 5: Create preventive care calendar
            care_calendar = await self._create_care_calendar(
                screening_plan, vaccination_plan, wellness_plan
            )

            # Combine all analyses
            preventive_care_plan = {
                "age": age,
                "gender": gender,
                "screening_plan": screening_plan,
                "vaccination_plan": vaccination_plan,
                "wellness_plan": wellness_plan,
                "risk_assessment": risk_assessment,
                "care_calendar": care_calendar,
                "priority_recommendations": self._generate_priority_recommendations(
                    screening_plan, risk_assessment
                ),
                "cost_estimates": self._estimate_costs(
                    screening_plan, vaccination_plan, insurance_coverage
                )
            }

            return AgentResult(
                success=True,
                data=preventive_care_plan,
                confidence=0.90,
                reasoning=f"Comprehensive preventive care plan created for {age}-year-old {gender}",
                metadata={
                    "age_group": self._get_age_group(age),
                    "risk_level": risk_assessment.get("overall_risk", "low"),
                    "screening_count": len(screening_plan.get("recommended", [])),
                    "vaccination_count": len(vaccination_plan.get("recommended", []))
                },
                execution_time=0.0,
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            self.logger.error(f"Preventive care planning failed: {e}")
            raise

    async def _generate_screening_plan(
        self, age: int, gender: str, family_history: List[str],
        lifestyle_factors: List[str], last_screenings: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate personalized screening recommendations."""
        screening_plan = {
            "recommended": [],
            "overdue": [],
            "upcoming": [],
            "not_needed": []
        }
        
        # Get base recommendations for age and gender
        base_screenings = self._get_base_screenings(age, gender)
        
        # Add high-risk screenings based on family history
        high_risk_screenings = self._get_high_risk_screenings(family_history, age)
        
        # Add lifestyle-based screenings
        lifestyle_screenings = self._get_lifestyle_screenings(lifestyle_factors, age)
        
        all_screenings = base_screenings + high_risk_screenings + lifestyle_screenings
        
        # Categorize screenings based on last screening dates
        for screening in all_screenings:
            screening_name = screening["name"]
            frequency = screening["frequency"]
            last_screening_date = last_screenings.get(screening_name)
            
            if last_screening_date:
                last_date = datetime.strptime(last_screening_date, "%Y-%m-%d")
                next_due = self._calculate_next_due_date(last_date, frequency)
                
                if next_due <= datetime.now():
                    screening["status"] = "overdue"
                    screening["next_due"] = next_due.strftime("%Y-%m-%d")
                    screening_plan["overdue"].append(screening)
                elif next_due <= datetime.now() + timedelta(days=90):
                    screening["status"] = "upcoming"
                    screening["next_due"] = next_due.strftime("%Y-%m-%d")
                    screening_plan["upcoming"].append(screening)
                else:
                    screening["status"] = "not_needed"
                    screening["next_due"] = next_due.strftime("%Y-%m-%d")
                    screening_plan["not_needed"].append(screening)
            else:
                screening["status"] = "recommended"
                screening["next_due"] = "asap"
                screening_plan["recommended"].append(screening)
        
        return screening_plan

    async def _create_vaccination_plan(self, age: int, gender: str) -> Dict[str, Any]:
        """Create vaccination schedule."""
        vaccination_plan = {
            "recommended": [],
            "overdue": [],
            "upcoming": [],
            "completed": []
        }
        
        # Get vaccinations for age group
        if age < 18:
            vaccinations = self.vaccination_schedule["children"]
        else:
            vaccinations = self.vaccination_schedule["adults"]
        
        for vaccine, schedule in vaccinations.items():
            if age >= schedule["age_start"]:
                vaccination_plan["recommended"].append({
                    "name": vaccine,
                    "frequency": schedule["frequency"],
                    "age_start": schedule["age_start"],
                    "description": f"Recommended {vaccine} vaccination"
                })
        
        return vaccination_plan

    async def _develop_wellness_plan(
        self, age: int, gender: str, lifestyle_factors: List[str],
        current_conditions: List[str]
    ) -> Dict[str, Any]:
        """Develop personalized wellness recommendations."""
        wellness_plan = {
            "lifestyle_recommendations": [],
            "nutrition_guidance": [],
            "exercise_plan": [],
            "stress_management": [],
            "sleep_hygiene": []
        }
        
        # Age-based recommendations
        if age < 30:
            wellness_plan["lifestyle_recommendations"].extend([
                "Establish healthy habits early",
                "Focus on preventive care",
                "Build strong social connections"
            ])
        elif age < 50:
            wellness_plan["lifestyle_recommendations"].extend([
                "Maintain work-life balance",
                "Prioritize stress management",
                "Regular health check-ups"
            ])
        else:
            wellness_plan["lifestyle_recommendations"].extend([
                "Focus on mobility and strength",
                "Regular preventive screenings",
                "Social engagement and mental health"
            ])
        
        # Lifestyle factor recommendations
        if "smoking" in lifestyle_factors:
            wellness_plan["lifestyle_recommendations"].append("Smoking cessation program")
        
        if "sedentary" in lifestyle_factors:
            wellness_plan["exercise_plan"].extend([
                "Start with 30 minutes of moderate activity daily",
                "Gradually increase intensity",
                "Include strength training 2-3 times per week"
            ])
        
        if "poor_diet" in lifestyle_factors:
            wellness_plan["nutrition_guidance"].extend([
                "Increase fruit and vegetable intake",
                "Reduce processed foods",
                "Stay hydrated with water"
            ])
        
        # General wellness recommendations
        wellness_plan["stress_management"] = [
            "Practice mindfulness or meditation",
            "Regular exercise",
            "Adequate sleep",
            "Social support networks"
        ]
        
        wellness_plan["sleep_hygiene"] = [
            "7-9 hours of sleep per night",
            "Consistent sleep schedule",
            "Avoid screens before bedtime",
            "Create a relaxing bedtime routine"
        ]
        
        return wellness_plan

    async def _assess_risk_factors(
        self, age: int, gender: str, family_history: List[str],
        lifestyle_factors: List[str], current_conditions: List[str]
    ) -> Dict[str, Any]:
        """Assess individual risk factors."""
        risk_assessment = {
            "overall_risk": "low",
            "risk_factors": [],
            "modifiable_risks": [],
            "non_modifiable_risks": [],
            "recommendations": []
        }
        
        risk_score = 0
        
        # Age-based risks
        if age > 65:
            risk_score += 3
            risk_assessment["non_modifiable_risks"].append("Advanced age")
        
        # Family history risks
        for condition in family_history:
            if condition in ["heart_disease", "diabetes", "cancer"]:
                risk_score += 2
                risk_assessment["non_modifiable_risks"].append(f"Family history of {condition}")
        
        # Lifestyle risks
        for factor in lifestyle_factors:
            if factor == "smoking":
                risk_score += 4
                risk_assessment["modifiable_risks"].append("Smoking")
                risk_assessment["recommendations"].append("Smoking cessation program")
            elif factor == "obesity":
                risk_score += 3
                risk_assessment["modifiable_risks"].append("Obesity")
                risk_assessment["recommendations"].append("Weight management program")
            elif factor == "sedentary":
                risk_score += 2
                risk_assessment["modifiable_risks"].append("Sedentary lifestyle")
                risk_assessment["recommendations"].append("Regular exercise program")
        
        # Current conditions
        for condition in current_conditions:
            if condition in ["diabetes", "hypertension", "heart_disease"]:
                risk_score += 3
                risk_assessment["risk_factors"].append(f"Current condition: {condition}")
        
        # Determine overall risk level
        if risk_score >= 8:
            risk_assessment["overall_risk"] = "high"
        elif risk_score >= 4:
            risk_assessment["overall_risk"] = "moderate"
        else:
            risk_assessment["overall_risk"] = "low"
        
        return risk_assessment

    async def _create_care_calendar(
        self, screening_plan: Dict[str, Any], vaccination_plan: Dict[str, Any],
        wellness_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create preventive care calendar."""
        calendar = {
            "immediate_actions": [],
            "next_30_days": [],
            "next_90_days": [],
            "next_6_months": [],
            "annual_plan": []
        }
        
        # Immediate actions (overdue screenings)
        for screening in screening_plan.get("overdue", []):
            calendar["immediate_actions"].append({
                "type": "screening",
                "name": screening["name"],
                "priority": "high",
                "description": f"Schedule {screening['name']} screening"
            })
        
        # Next 30 days
        for screening in screening_plan.get("upcoming", []):
            calendar["next_30_days"].append({
                "type": "screening",
                "name": screening["name"],
                "priority": "medium",
                "description": f"Schedule {screening['name']} screening"
            })
        
        # Wellness activities
        calendar["next_30_days"].extend([
            {
                "type": "wellness",
                "name": "Exercise Program",
                "priority": "medium",
                "description": "Start regular exercise routine"
            },
            {
                "type": "wellness",
                "name": "Nutrition Plan",
                "priority": "medium",
                "description": "Implement healthy eating plan"
            }
        ])
        
        return calendar

    def _get_base_screenings(self, age: int, gender: str) -> List[Dict[str, Any]]:
        """Get base screening recommendations for age and gender."""
        screenings = []
        
        for screening, guidelines in self.screening_guidelines["general_population"].items():
            if age >= guidelines["age_start"]:
                screenings.append({
                    "name": screening,
                    "frequency": guidelines["frequency"],
                    "age_start": guidelines["age_start"],
                    "description": f"Standard {screening} screening"
                })
        
        return screenings

    def _get_high_risk_screenings(self, family_history: List[str], age: int) -> List[Dict[str, Any]]:
        """Get high-risk screenings based on family history."""
        screenings = []
        
        for condition in family_history:
            if condition in self.screening_guidelines["high_risk_factors"]["family_history"]:
                guidelines = self.screening_guidelines["high_risk_factors"]["family_history"][condition]
                if age >= guidelines["age_start"]:
                    screenings.append({
                        "name": f"{condition}_screening",
                        "frequency": guidelines["frequency"],
                        "age_start": guidelines["age_start"],
                        "description": f"High-risk {condition} screening due to family history"
                    })
        
        return screenings

    def _get_lifestyle_screenings(self, lifestyle_factors: List[str], age: int) -> List[Dict[str, Any]]:
        """Get lifestyle-based screening recommendations."""
        screenings = []
        
        for factor in lifestyle_factors:
            if factor in self.screening_guidelines["high_risk_factors"]["lifestyle"]:
                factor_guidelines = self.screening_guidelines["high_risk_factors"]["lifestyle"][factor]
                for screening, guidelines in factor_guidelines.items():
                    if age >= guidelines["age_start"]:
                        screenings.append({
                            "name": screening,
                            "frequency": guidelines["frequency"],
                            "age_start": guidelines["age_start"],
                            "description": f"{screening} screening due to {factor} lifestyle"
                        })
        
        return screenings

    def _calculate_next_due_date(self, last_date: datetime, frequency: str) -> datetime:
        """Calculate next due date based on frequency."""
        if frequency == "annual":
            return last_date + timedelta(days=365)
        elif frequency == "every_2_years":
            return last_date + timedelta(days=730)
        elif frequency == "every_3_years":
            return last_date + timedelta(days=1095)
        elif frequency == "every_5_years":
            return last_date + timedelta(days=1825)
        elif frequency == "every_10_years":
            return last_date + timedelta(days=3650)
        else:
            return last_date + timedelta(days=365)  # Default to annual

    def _get_age_group(self, age: int) -> str:
        """Get age group classification."""
        if age < 18:
            return "child"
        elif age < 30:
            return "young_adult"
        elif age < 50:
            return "adult"
        elif age < 65:
            return "middle_age"
        else:
            return "senior"

    def _generate_priority_recommendations(
        self, screening_plan: Dict[str, Any], risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate priority recommendations."""
        recommendations = []
        
        # Overdue screenings
        if screening_plan.get("overdue"):
            recommendations.append("URGENT: Schedule overdue screenings immediately")
        
        # High-risk individuals
        if risk_assessment.get("overall_risk") == "high":
            recommendations.append("High-risk individual - consider more frequent monitoring")
        
        # Modifiable risks
        modifiable_risks = risk_assessment.get("modifiable_risks", [])
        if modifiable_risks:
            recommendations.append(f"Focus on addressing modifiable risks: {', '.join(modifiable_risks)}")
        
        return recommendations

    def _estimate_costs(
        self, screening_plan: Dict[str, Any], vaccination_plan: Dict[str, Any],
        insurance_coverage: str
    ) -> Dict[str, Any]:
        """Estimate costs for preventive care."""
        cost_estimates = {
            "total_estimated_cost": 0,
            "insurance_coverage": insurance_coverage,
            "out_of_pocket_estimate": 0,
            "cost_breakdown": {}
        }
        
        # Rough cost estimates (these would be more accurate with real data)
        screening_costs = {
            "blood_pressure": 0,  # Usually free
            "cholesterol": 50,
            "diabetes": 50,
            "colorectal_cancer": 500,
            "breast_cancer": 200,
            "prostate_cancer": 100,
            "osteoporosis": 150
        }
        
        vaccination_costs = {
            "flu": 30,
            "tdap": 50,
            "covid_19": 0,  # Usually free
            "shingles": 200,
            "pneumonia": 100
        }
        
        total_cost = 0
        
        # Calculate screening costs
        for screening in screening_plan.get("recommended", []):
            screening_name = screening["name"]
            if screening_name in screening_costs:
                cost = screening_costs[screening_name]
                cost_estimates["cost_breakdown"][screening_name] = cost
                total_cost += cost
        
        # Calculate vaccination costs
        for vaccine in vaccination_plan.get("recommended", []):
            vaccine_name = vaccine["name"]
            if vaccine_name in vaccination_costs:
                cost = vaccination_costs[vaccine_name]
                cost_estimates["cost_breakdown"][vaccine_name] = cost
                total_cost += cost
        
        cost_estimates["total_estimated_cost"] = total_cost
        
        # Estimate out-of-pocket based on insurance
        if insurance_coverage == "comprehensive":
            cost_estimates["out_of_pocket_estimate"] = total_cost * 0.1
        elif insurance_coverage == "standard":
            cost_estimates["out_of_pocket_estimate"] = total_cost * 0.3
        else:
            cost_estimates["out_of_pocket_estimate"] = total_cost * 0.8
        
        return cost_estimates

    def can_handle(self, context: AgentContext, **kwargs) -> bool:
        """Check if this agent can handle the request."""
        return "age" in kwargs and "gender" in kwargs

    def get_provided_capabilities(self) -> List[str]:
        """Get capabilities provided by this agent."""
        return [
            "preventive_care_planning",
            "screening_recommendations",
            "vaccination_scheduling",
            "wellness_guidance",
            "risk_assessment",
            "cost_estimation"
        ]
