/**
 * Demo Service for AI Health Navigator
 * Loads and serves mock data for demonstration purposes
 */

class DemoService {
  constructor() {
    this.config = null;
    this.data = {
      patients: [],
      symptoms: [],
      healthcare_providers: [],
      ai_analysis_results: []
    };
    this.isInitialized = false;
  }

  async initialize() {
    try {
      // Load demo configuration
      const configResponse = await fetch('./demo/demo-config.json');
      this.config = await configResponse.json();
      
      // Load all mock data files
      await this.loadMockData();
      
      this.isInitialized = true;
      console.log('Demo service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize demo service:', error);
      throw error;
    }
  }

  async loadMockData() {
    const dataFiles = this.config.data_files;
    
    for (const [key, filename] of Object.entries(dataFiles)) {
      try {
        const response = await fetch(`./demo/mock-data/${filename}`);
        const csvText = await response.text();
        this.data[key] = this.parseCSV(csvText);
        console.log(`Loaded ${this.data[key].length} records from ${filename}`);
      } catch (error) {
        console.error(`Failed to load ${filename}:`, error);
        this.data[key] = [];
      }
    }
  }

  parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',');
    const data = [];

    for (let i = 1; i < lines.length; i++) {
      const values = this.parseCSVLine(lines[i]);
      const row = {};
      
      headers.forEach((header, index) => {
        row[header.trim()] = values[index] ? values[index].trim() : '';
      });
      
      data.push(row);
    }

    return data;
  }

  parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        result.push(current);
        current = '';
      } else {
        current += char;
      }
    }
    
    result.push(current);
    return result;
  }

  // Mock API methods that simulate real API calls
  async getPatients(filters = {}) {
    await this.ensureInitialized();
    let patients = [...this.data.patients];
    
    // Apply filters
    if (filters.search) {
      const search = filters.search.toLowerCase();
      patients = patients.filter(p => 
        p.first_name.toLowerCase().includes(search) ||
        p.last_name.toLowerCase().includes(search) ||
        p.email.toLowerCase().includes(search)
      );
    }
    
    if (filters.limit) {
      patients = patients.slice(0, filters.limit);
    }
    
    return this.simulateAPIResponse(patients);
  }

  async getPatientById(patientId) {
    await this.ensureInitialized();
    const patient = this.data.patients.find(p => p.patient_id === patientId);
    return this.simulateAPIResponse(patient);
  }

  async getSymptoms(patientId = null) {
    await this.ensureInitialized();
    let symptoms = [...this.data.symptoms];
    
    if (patientId) {
      symptoms = symptoms.filter(s => s.patient_id === patientId);
    }
    
    return this.simulateAPIResponse(symptoms);
  }

  async getSymptomById(symptomId) {
    await this.ensureInitialized();
    const symptom = this.data.symptoms.find(s => s.symptom_id === symptomId);
    return this.simulateAPIResponse(symptom);
  }

  async getHealthcareProviders(filters = {}) {
    await this.ensureInitialized();
    let providers = [...this.data.healthcare_providers];
    
    // Apply filters
    if (filters.specialty) {
      providers = providers.filter(p => 
        p.specialty.toLowerCase().includes(filters.specialty.toLowerCase())
      );
    }
    
    if (filters.location) {
      const location = filters.location.toLowerCase();
      providers = providers.filter(p => 
        p.city.toLowerCase().includes(location) ||
        p.state.toLowerCase().includes(location)
      );
    }
    
    if (filters.insurance) {
      providers = providers.filter(p => 
        p.insurance_accepted.toLowerCase().includes(filters.insurance.toLowerCase())
      );
    }
    
    if (filters.limit) {
      providers = providers.slice(0, filters.limit);
    }
    
    return this.simulateAPIResponse(providers);
  }

  async getProviderById(providerId) {
    await this.ensureInitialized();
    const provider = this.data.healthcare_providers.find(p => p.provider_id === providerId);
    return this.simulateAPIResponse(provider);
  }

  async getAIAnalysisResults(patientId = null) {
    await this.ensureInitialized();
    let results = [...this.data.ai_analysis_results];
    
    if (patientId) {
      results = results.filter(r => r.patient_id === patientId);
    }
    
    return this.simulateAPIResponse(results);
  }

  async getAnalysisById(analysisId) {
    await this.ensureInitialized();
    const analysis = this.data.ai_analysis_results.find(a => a.analysis_id === analysisId);
    return this.simulateAPIResponse(analysis);
  }

  // Mock AI analysis endpoint
  async analyzeSymptoms(symptomData) {
    await this.ensureInitialized();
    
    // Find a relevant analysis result or create a mock one
    const mockAnalysis = {
      analysis_id: `AR${Date.now()}`,
      patient_id: symptomData.patient_id || 'P001',
      symptom_id: symptomData.symptom_id || 'S001',
      analysis_timestamp: new Date().toISOString(),
      ai_model_used: 'EnhancedSymptomAnalysisAgent',
      analysis_type: 'Memory-Based Analysis',
      confidence_score: 0.85,
      risk_level: 'Low',
      primary_diagnosis: 'Tension Headache',
      secondary_diagnoses: ['Migraine', 'Sinusitis', 'Eye strain'],
      differential_diagnoses: ['Cluster headache', 'Temporal arteritis', 'Intracranial pressure'],
      recommended_tests: ['None required'],
      recommended_treatments: ['Rest', 'hydration', 'stress management', 'OTC pain relievers'],
      emergency_indicators: false,
      urgency_score: 0.15,
      ai_reasoning: 'Patient has history of stress-related headaches. Current symptoms consistent with tension headache pattern. No red flags present.',
      medical_context_considered: 'Hypertension well-controlled with Lisinopril',
      medication_interactions: 'No relevant allergies',
      allergy_considerations: 'No relevant allergies',
      chronic_condition_impact: 'Hypertension may contribute to headache frequency',
      preventive_recommendations: ['Stress reduction techniques', 'regular exercise', 'sleep hygiene'],
      follow_up_timing: 'Monitor for 48 hours, return if worsening',
      specialist_referral: null,
      insurance_coverage_impact: 'Standard coverage',
      cost_estimates: 25.00,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    return this.simulateAPIResponse(mockAnalysis);
  }

  // Mock health summary endpoint
  async getHealthSummary(patientId) {
    await this.ensureInitialized();
    
    const patient = this.data.patients.find(p => p.patient_id === patientId);
    const symptoms = this.data.symptoms.filter(s => s.patient_id === patientId);
    const analyses = this.data.ai_analysis_results.filter(a => a.patient_id === patientId);
    
    const mockSummary = {
      patient_id: patientId,
      patient_name: patient ? `${patient.first_name} ${patient.last_name}` : 'Unknown Patient',
      health_status: patient ? patient.health_status : 'Unknown',
      risk_score: patient ? parseFloat(patient.risk_score) : 0.1,
      recent_symptoms: symptoms.slice(-5),
      recent_analyses: analyses.slice(-3),
      upcoming_appointments: patient ? [{
        date: patient.next_appointment,
        type: 'Follow-up',
        provider: patient.primary_care_physician
      }] : [],
      medications: patient ? JSON.parse(patient.medications || '[]') : [],
      chronic_conditions: patient ? patient.chronic_conditions : 'None',
      last_visit: patient ? patient.last_visit : null,
      next_appointment: patient ? patient.next_appointment : null
    };
    
    return this.simulateAPIResponse(mockSummary);
  }

  // Mock AI insights endpoint
  async getAIInsights(patientId) {
    await this.ensureInitialized();
    
    const analyses = this.data.ai_analysis_results.filter(a => a.patient_id === patientId);
    
    const mockInsights = {
      patient_id: patientId,
      insights: [
        {
          type: 'health_trend',
          title: 'Improving Health Patterns',
          description: 'Your recent symptoms show a positive trend with fewer severe episodes.',
          confidence: 0.85,
          recommendation: 'Continue current treatment plan and lifestyle modifications.'
        },
        {
          type: 'medication_optimization',
          title: 'Medication Effectiveness',
          description: 'Your current medications appear to be working well with minimal side effects.',
          confidence: 0.78,
          recommendation: 'Continue medication as prescribed and monitor for any changes.'
        },
        {
          type: 'preventive_care',
          title: 'Preventive Care Opportunities',
          description: 'Consider scheduling your annual physical and recommended screenings.',
          confidence: 0.92,
          recommendation: 'Contact your primary care provider to schedule preventive care appointments.'
        }
      ],
      risk_factors: [
        {
          factor: 'Stress Management',
          level: 'moderate',
          description: 'Stress levels may be contributing to some symptoms.',
          recommendation: 'Consider stress reduction techniques and regular exercise.'
        }
      ],
      generated_at: new Date().toISOString()
    };
    
    return this.simulateAPIResponse(mockInsights);
  }

  // Utility methods
  async ensureInitialized() {
    if (!this.isInitialized) {
      await this.initialize();
    }
  }

  async simulateAPIResponse(data) {
    // Simulate API delay
    const delay = this.config?.demo_settings?.mock_api_delay || 500;
    await new Promise(resolve => setTimeout(resolve, delay));
    
    return {
      success: true,
      data: data,
      timestamp: new Date().toISOString(),
      demo_mode: true
    };
  }

  // Get demo configuration
  getConfig() {
    return this.config;
  }

  // Check if demo mode is enabled
  isDemoMode() {
    return this.config?.demo_mode || false;
  }

  // Get demo user info
  getDemoUser() {
    return this.config?.demo_settings?.demo_user;
  }
}

// Create singleton instance
const demoService = new DemoService();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = demoService;
} else if (typeof window !== 'undefined') {
  window.demoService = demoService;
}
