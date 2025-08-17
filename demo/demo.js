// CSV Parser and Data Manager for AI Health Navigator Demo
class CSVDataManager {
    constructor() {
        this.data = {
            patients: [],
            symptoms: [],
            healthcare_providers: [],
            agent_conclusions: [],
            ai_analysis_results: []
        };
        this.loadedFiles = 0;
        this.totalFiles = 5;
    }

    // Parse CSV string to array of objects
    parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        const data = [];
        
        for (let i = 1; i < lines.length; i++) {
            const values = this.parseCSVLine(lines[i]);
            const row = {};
            headers.forEach((header, index) => {
                row[header] = values[index] || '';
            });
            data.push(row);
        }
        
        return data;
    }

    // Handle CSV parsing with quoted values
    parseCSVLine(line) {
        const result = [];
        let current = '';
        let inQuotes = false;
        
        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                result.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }
        
        result.push(current.trim());
        return result;
    }

    // Load CSV file
    async loadCSVFile(filename) {
        try {
            const response = await fetch(`mock-data/${filename}`);
            const csvText = await response.text();
            const data = this.parseCSV(csvText);
            
            // Store data based on filename
            const key = filename.replace('.csv', '');
            this.data[key] = data;
            
            this.loadedFiles++;
            console.log(`Loaded ${filename}: ${data.length} records`);
            
            if (this.loadedFiles === this.totalFiles) {
                this.onAllDataLoaded();
            }
        } catch (error) {
            console.error(`Error loading ${filename}:`, error);
        }
    }

    // Load all CSV files
    async loadAllData() {
        const files = [
            'patients.csv',
            'symptoms.csv',
            'healthcare_providers.csv',
            'agent_conclusions.csv',
            'ai_analysis_results.csv'
        ];
        
        for (const file of files) {
            await this.loadCSVFile(file);
        }
    }

    // Called when all data is loaded
    onAllDataLoaded() {
        console.log('All CSV data loaded successfully!');
        this.updateDashboard();
    }

    // Update dashboard with real data
    updateDashboard() {
        this.updateStats();
        this.updateEmergencyCases();
        this.updateAIAnalyses();
        this.updateProviders();
        this.updateCharts();
    }

    // Update statistics
    updateStats() {
        const stats = {
            patients: this.data.patients.length,
            symptoms: this.data.symptoms.length,
            aiAnalyses: this.data.ai_analysis_results.length,
            providers: this.data.healthcare_providers.length
        };

        // Update stats cards
        document.querySelector('[data-stat="patients"]').textContent = stats.patients;
        document.querySelector('[data-stat="symptoms"]').textContent = stats.symptoms;
        document.querySelector('[data-stat="aiAnalyses"]').textContent = stats.aiAnalyses;
        document.querySelector('[data-stat="providers"]').textContent = stats.providers;
    }

    // Update emergency cases
    updateEmergencyCases() {
        const container = document.getElementById('emergencyCases');
        container.innerHTML = '';

        // Get critical cases from agent conclusions
        const criticalCases = this.data.agent_conclusions.filter(
            conclusion => conclusion.emergency_flags === 'True'
        ).slice(0, 6);

        criticalCases.forEach(case_ => {
            const patient = this.data.patients.find(p => p.patient_id === case_.patient_id);
            const symptom = this.data.symptoms.find(s => s.symptom_id === case_.symptom_id);
            
            const card = document.createElement('div');
            card.className = 'emergency text-white rounded-lg p-4 card-hover';
            card.innerHTML = `
                <div class="flex items-start justify-between">
                    <div>
                        <h3 class="font-semibold mb-1">${patient ? patient.first_name + ' ' + patient.last_name : 'Unknown Patient'}</h3>
                        <p class="text-sm opacity-90 mb-2">${symptom ? symptom.symptom_name : 'Unknown Symptom'}</p>
                        <p class="text-xs opacity-75">${case_.agent_type}</p>
                    </div>
                    <span class="bg-white bg-opacity-20 px-2 py-1 rounded text-xs font-semibold">
                        ${case_.risk_level}
                    </span>
                </div>
                <div class="mt-3">
                    <p class="text-sm font-semibold">${case_.recommendations}</p>
                </div>
            `;
            container.appendChild(card);
        });
    }

    // Update AI analyses table
    updateAIAnalyses() {
        const tbody = document.getElementById('aiAnalyses');
        tbody.innerHTML = '';

        // Get recent analyses (last 10)
        const recentAnalyses = this.data.agent_conclusions.slice(-10);

        recentAnalyses.forEach(analysis => {
            const patient = this.data.patients.find(p => p.patient_id === analysis.patient_id);
            const riskClass = analysis.risk_level === 'Critical' ? 'emergency' : 
                            analysis.risk_level === 'High' ? 'high-risk' : 
                            analysis.risk_level === 'Medium' ? 'medium-risk' : 'low-risk';
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">${patient ? patient.first_name + ' ' + patient.last_name : 'Unknown'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${analysis.agent_type}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${riskClass} text-white">
                        ${analysis.risk_level}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${Math.round(analysis.confidence_score * 100)}%
                </td>
                <td class="px-6 py-4">
                    <div class="text-sm text-gray-900">${analysis.conclusion_text.substring(0, 100)}...</div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // Update healthcare providers
    updateProviders() {
        const container = document.getElementById('providers');
        container.innerHTML = '';

        // Get first 6 providers
        const providers = this.data.healthcare_providers.slice(0, 6);

        providers.forEach(provider => {
            const card = document.createElement('div');
            card.className = 'bg-gray-50 rounded-lg p-4 card-hover';
            card.innerHTML = `
                <div class="flex items-start justify-between mb-2">
                    <h3 class="font-semibold text-gray-900">${provider.name}</h3>
                    <span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-semibold">
                        ${provider.accepting_patients === 'True' ? 'Accepting' : 'Full'}
                    </span>
                </div>
                <p class="text-sm text-gray-600 mb-2">${provider.specialty}</p>
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <span class="text-yellow-500 mr-1">★</span>
                        <span class="text-sm text-gray-600">${provider.rating}</span>
                    </div>
                    <span class="text-xs text-gray-500">${provider.city}, ${provider.state}</span>
                </div>
            `;
            container.appendChild(card);
        });
    }

    // Update charts with real data
    updateCharts() {
        this.updateRiskChart();
        this.updateConfidenceChart();
        this.updateDemographicsChart();
        this.updateSymptomsChart();
    }

    // Update risk level distribution chart
    updateRiskChart() {
        const riskCounts = {};
        this.data.agent_conclusions.forEach(conclusion => {
            const risk = conclusion.risk_level;
            riskCounts[risk] = (riskCounts[risk] || 0) + 1;
        });

        const labels = Object.keys(riskCounts);
        const data = Object.values(riskCounts);
        const colors = ['#4caf50', '#ffc107', '#ff9800', '#f44336'];

        const ctx = document.getElementById('riskChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.slice(0, labels.length),
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Update confidence scores chart
    updateConfidenceChart() {
        const confidenceRanges = {
            '0-20%': 0, '21-40%': 0, '41-60%': 0, '61-80%': 0, '81-100%': 0
        };

        this.data.agent_conclusions.forEach(conclusion => {
            const confidence = parseFloat(conclusion.confidence_score) * 100;
            if (confidence <= 20) confidenceRanges['0-20%']++;
            else if (confidence <= 40) confidenceRanges['21-40%']++;
            else if (confidence <= 60) confidenceRanges['41-60%']++;
            else if (confidence <= 80) confidenceRanges['61-80%']++;
            else confidenceRanges['81-100%']++;
        });

        const ctx = document.getElementById('confidenceChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: Object.keys(confidenceRanges),
                datasets: [{
                    label: 'Number of Analyses',
                    data: Object.values(confidenceRanges),
                    borderColor: '#2196f3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Update demographics chart
    updateDemographicsChart() {
        const ageRanges = {
            '18-30': 0, '31-40': 0, '41-50': 0, '51-60': 0, '60+': 0
        };

        this.data.patients.forEach(patient => {
            const age = 2024 - new Date(patient.date_of_birth).getFullYear();
            if (age <= 30) ageRanges['18-30']++;
            else if (age <= 40) ageRanges['31-40']++;
            else if (age <= 50) ageRanges['41-50']++;
            else if (age <= 60) ageRanges['51-60']++;
            else ageRanges['60+']++;
        });

        const ctx = document.getElementById('demographicsChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(ageRanges),
                datasets: [{
                    label: 'Patients',
                    data: Object.values(ageRanges),
                    backgroundColor: '#4caf50'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Update symptoms chart
    updateSymptomsChart() {
        const symptomCategories = {};
        
        this.data.symptoms.forEach(symptom => {
            const category = this.categorizeSymptom(symptom.symptom_name);
            symptomCategories[category] = (symptomCategories[category] || 0) + 1;
        });

        const ctx = document.getElementById('symptomsChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(symptomCategories),
                datasets: [{
                    label: 'Symptoms',
                    data: Object.values(symptomCategories),
                    backgroundColor: '#ff9800'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Categorize symptoms
    categorizeSymptom(symptomName) {
        const name = symptomName.toLowerCase();
        
        if (name.includes('chest') || name.includes('heart') || name.includes('palpitation')) return 'Cardiac';
        if (name.includes('cough') || name.includes('breath') || name.includes('wheezing')) return 'Respiratory';
        if (name.includes('anxiety') || name.includes('depression') || name.includes('panic') || name.includes('suicidal')) return 'Mental Health';
        if (name.includes('stomach') || name.includes('nausea') || name.includes('constipation') || name.includes('heartburn')) return 'Gastrointestinal';
        if (name.includes('headache') || name.includes('dizziness') || name.includes('numbness') || name.includes('tremor')) return 'Neurological';
        return 'Other';
    }

    // Get patient by ID
    getPatientById(patientId) {
        return this.data.patients.find(p => p.patient_id === patientId);
    }

    // Get symptom by ID
    getSymptomById(symptomId) {
        return this.data.symptoms.find(s => s.symptom_id === symptomId);
    }

    // Get provider by ID
    getProviderById(providerId) {
        return this.data.healthcare_providers.find(p => p.provider_id === providerId);
    }

    // Search patients
    searchPatients(query) {
        const searchTerm = query.toLowerCase();
        return this.data.patients.filter(patient => 
            patient.first_name.toLowerCase().includes(searchTerm) ||
            patient.last_name.toLowerCase().includes(searchTerm) ||
            patient.patient_id.toLowerCase().includes(searchTerm)
        );
    }

    // Get statistics
    getStatistics() {
        return {
            totalPatients: this.data.patients.length,
            totalSymptoms: this.data.symptoms.length,
            totalAnalyses: this.data.agent_conclusions.length,
            totalProviders: this.data.healthcare_providers.length,
            criticalCases: this.data.agent_conclusions.filter(c => c.emergency_flags === 'True').length,
            averageConfidence: this.data.agent_conclusions.reduce((sum, c) => sum + parseFloat(c.confidence_score), 0) / this.data.agent_conclusions.length
        };
    }
}

// Initialize the demo when the page loads
document.addEventListener('DOMContentLoaded', function() {
    const dataManager = new CSVDataManager();
    
    // Add data attributes to stats cards for easy updating
    document.querySelectorAll('[data-stat]').forEach(element => {
        // This will be updated when data loads
    });
    
    // Load all CSV data
    dataManager.loadAllData();
    
    // Make dataManager available globally for debugging
    window.dataManager = dataManager;
});
