import {
  IncidentRankingResponse,
  Incident,
  IncidentComparisonResponse,
  SimulationRequest,
  SimulationResponse,
  AnalyticsSummary,
  ModelPerformance,
  ReportItem,
  User
} from '../types';

const API_BASE = '/api';

function getHeaders(): HeadersInit {
  const token = localStorage.getItem('soc_jwt_token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'An unknown server error occurred' }));
    throw new Error(errorData.detail || `HTTP Error ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Auth
  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return handleResponse(res);
  },

  async register(email: string, password: string, fullName: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name: fullName })
    });
    return handleResponse(res);
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  // Incidents
  async getRankedIncidents(status?: string, search?: string, limit = 50, offset = 0): Promise<IncidentRankingResponse> {
    const params = new URLSearchParams();
    if (status && status !== 'all') params.append('status', status);
    if (search) params.append('search', search);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const res = await fetch(`${API_BASE}/incidents/ranking?${params.toString()}`, {
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  async getIncident(id: number): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents/${id}`, {
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  async updateIncidentStatus(id: number, status: string): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents/${id}/status`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify({ status })
    });
    return handleResponse(res);
  },

  async prioritizeIncident(id: number): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents/${id}/prioritize`, {
      method: 'POST',
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  async compareIncidents(id: number, otherId: number): Promise<IncidentComparisonResponse> {
    const res = await fetch(`${API_BASE}/incidents/${id}/compare/${otherId}`, {
      method: 'POST',
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  // Simulator
  async simulateScenario(data: SimulationRequest): Promise<SimulationResponse> {
    const res = await fetch(`${API_BASE}/simulator`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse(res);
  },

  // Analytics
  async getAnalytics(): Promise<AnalyticsSummary> {
    const res = await fetch(`${API_BASE}/analytics`, {
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  // Reports
  async generateReport(incidentId: number, reportType = 'executive'): Promise<ReportItem> {
    const res = await fetch(`${API_BASE}/reports`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ incident_id: incidentId, report_type: reportType })
    });
    return handleResponse(res);
  },

  async getReports(): Promise<ReportItem[]> {
    const res = await fetch(`${API_BASE}/reports`, {
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  // Model
  async getModelPerformance(): Promise<ModelPerformance> {
    const res = await fetch(`${API_BASE}/model/performance`, {
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  // Demo
  async loadDemoData(): Promise<{ message: string; total_incidents: number; top_incident: any }> {
    const res = await fetch(`${API_BASE}/demo/load`, {
      method: 'POST',
      headers: getHeaders()
    });
    return handleResponse(res);
  }
};
