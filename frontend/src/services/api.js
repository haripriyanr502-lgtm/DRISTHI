// DRISTHI Frontend API Service Layer
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '3000') 
    ? '/api/v1' 
    : 'http://127.0.0.1:8000/api/v1');

class ApiService {
  constructor() {
    this.token = localStorage.getItem('dristhi_token') || null;
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('dristhi_token', token);
    } else {
      localStorage.removeItem('dristhi_token');
    }
  }

  getHeaders(isFormData = false) {
    const headers = {};
    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async handleResponse(response) {
    const contentType = response.headers.get('content-type');
    let data;
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const errorMsg = data?.detail || data?.message || (typeof data === 'string' ? data : 'API Request Failed');
      throw new Error(errorMsg);
    }
    return data;
  }

  // Health & Diagnostics
  async getHealth() {
    const res = await fetch(`${API_BASE_URL}/health`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }

  // Authentication
  async register(userData) {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(userData)
    });
    return this.handleResponse(res);
  }

  async login(credentials) {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(credentials)
    });
    return this.handleResponse(res);
  }

  async getMe() {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }

  // Patient Profile
  async getPatientProfile(patientId) {
    const res = await fetch(`${API_BASE_URL}/patients/${patientId}`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }

  async savePatientProfile(patientData) {
    const res = await fetch(`${API_BASE_URL}/patients`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(patientData)
    });
    return this.handleResponse(res);
  }

  async getPatientRecords(patientId) {
    const res = await fetch(`${API_BASE_URL}/patients/${patientId}/records`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }

  // ECG Upload & Processing
  // ECG Upload & Processing (digital signals)
  async uploadECG({ file, patientId, consentForResearch, samplingRate = 250.0 }) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('patient_id', patientId);
    formData.append('consent_for_research', consentForResearch ? 'true' : 'false');
    formData.append('sampling_rate', samplingRate);

    const res = await fetch(`${API_BASE_URL}/ecg/upload`, {
      method: 'POST',
      headers: this.getHeaders(true),
      body: formData,
    });
    return this.handleResponse(res);
  }

  // ECG Image to Waveform conversion
  async uploadECGImage({ file, patientId, consentForResearch, speed_mm_s, amp_mm_mv }) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('patient_id', patientId);
    formData.append('consent_for_research', consentForResearch ? 'true' : 'false');
    if (speed_mm_s !== undefined && speed_mm_s !== null) formData.append('speed_mm_s', speed_mm_s);
    if (amp_mm_mv !== undefined && amp_mm_mv !== null) formData.append('amp_mm_mv', amp_mm_mv);

    const res = await fetch(`${API_BASE_URL}/ecg_image/upload_image`, {
      method: 'POST',
      headers: this.getHeaders(true),
      body: formData,
    });
    return this.handleResponse(res);
  }


  async loadSampleECG({ patientId = 'PT-DEMO-01', rhythmType = 'normal', consentForResearch = false }) {
    const formData = new FormData();
    formData.append('patient_id', patientId);
    formData.append('rhythm_type', rhythmType);
    formData.append('consent_for_research', consentForResearch ? 'true' : 'false');

    const res = await fetch(`${API_BASE_URL}/ecg/sample`, {
      method: 'POST',
      headers: this.getHeaders(true),
      body: formData
    });
    return this.handleResponse(res);
  }

  // Analysis Results
  async getAnalysisResults(analysisId) {
    const res = await fetch(`${API_BASE_URL}/analysis/${analysisId}`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }

  async getAIStatus() {
    const res = await fetch(`${API_BASE_URL}/analysis/status`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }

  // Caregiver Portal
  async getCaregiverDashboard() {
    const res = await fetch(`${API_BASE_URL}/caregivers/dashboard`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }

  async acknowledgeAlert(alertId, caregiverName) {
    const res = await fetch(`${API_BASE_URL}/caregivers/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ caregiver_name: caregiverName })
    });
    return this.handleResponse(res);
  }

  // Future Hardware Monitoring
  async getHardwareStatus() {
    const res = await fetch(`${API_BASE_URL}/monitoring/status`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }

  // Temporary Demo Data Mode
  async getDemoCases() {
    const res = await fetch(`${API_BASE_URL}/demo/cases`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }

  async getDemoCaseDetail(caseId) {
    const res = await fetch(`${API_BASE_URL}/demo/cases/${caseId}`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }

  async loadDemoCase(caseId) {
    const res = await fetch(`${API_BASE_URL}/demo/load/${caseId}`, {
      method: 'POST',
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }
}

export const api = new ApiService();
