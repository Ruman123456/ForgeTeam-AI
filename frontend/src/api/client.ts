import {
  Project,
  ProjectCreate,
  ProjectListResponse,
  AgentRun,
  RunCreate,
  RunListResponse,
  AgentEvent,
  Artifact,
  ArtifactContent,
  HealthResponse,
  ConfigResponse,
  OllamaCheckResponse,
  DashboardStats,
} from '../types';

const API_BASE = '/api';

class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      let errorDetail = `HTTP ${response.status} ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson && errorJson.detail) {
          errorDetail = typeof errorJson.detail === 'string'
            ? errorJson.detail
            : JSON.stringify(errorJson.detail);
        }
      } catch {
        // Fallback to text or statusText
      }
      throw new ApiError(response.status, errorDetail);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return (await response.json()) as T;
  } catch (err: any) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(0, err.message || 'Network connection failed. Backend might be offline.');
  }
}

export const api = {
  // System
  getHealth: () => request<HealthResponse>('/health'),
  getConfig: () => request<ConfigResponse>('/config'),
  checkOllama: () => request<OllamaCheckResponse>('/ollama/check', { method: 'POST' }),
  checkGroq: () => request<{ configured: boolean; connected: boolean; model: string; message: string }>('/groq/check', { method: 'POST' }),
  saveGroqKey: (apiKey: string) => request<{ success: boolean; connected: boolean; message: string }>('/groq/key', { method: 'POST', body: JSON.stringify({ api_key: apiKey }) }),
  getDashboardStats: () => request<DashboardStats>('/dashboard/stats'),

  // Projects
  getProjects: (skip = 0, limit = 50) =>
    request<ProjectListResponse>(`/projects?skip=${skip}&limit=${limit}`),
  getProject: (id: string) => request<Project>(`/projects/${id}`),
  createProject: (data: ProjectCreate) =>
    request<Project>('/projects', { method: 'POST', body: JSON.stringify(data) }),
  updateProject: (id: string, data: Partial<ProjectCreate>) =>
    request<Project>(`/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteProject: (id: string) => request<void>(`/projects/${id}`, { method: 'DELETE' }),

  // Runs
  getRuns: (projectId?: string, status?: string, skip = 0, limit = 50) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (projectId) params.append('project_id', projectId);
    if (status) params.append('status', status);
    return request<RunListResponse>(`/runs?${params.toString()}`);
  },
  getRun: (id: string) => request<AgentRun>(`/runs/${id}`),
  createRun: (data: RunCreate) =>
    request<AgentRun>('/runs', { method: 'POST', body: JSON.stringify(data) }),
  cancelRun: (id: string) => request<{ message: string; run_id: string }>(`/runs/${id}/cancel`, { method: 'POST' }),
  getRunLogs: (id: string) => request<AgentEvent[]>(`/runs/${id}/logs`),
  getRunArtifacts: (id: string) => request<Artifact[]>(`/runs/${id}/artifacts`),
  getArtifactContent: (runId: string, artifactId: string) =>
    request<ArtifactContent>(`/runs/${runId}/artifacts/${artifactId}`),
  getDownloadZipUrl: (runId: string) => `${API_BASE}/runs/${runId}/download`,
};
