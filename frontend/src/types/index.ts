export interface Project {
  id: string;
  name: string;
  description: string;
  language_preference?: string | null;
  framework_preference?: string | null;
  created_at: string;
  updated_at: string;
  run_count: number;
}

export interface ProjectCreate {
  name: string;
  description: string;
  language_preference?: string;
  framework_preference?: string;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}

export interface AgentRun {
  id: string;
  project_id: string;
  project_name: string;
  original_request: string;
  selected_model?: string | null;
  demo_mode: boolean;
  status: 'queued' | 'running' | 'completed' | 'completed_with_issues' | 'failed' | 'cancelled';
  current_stage?: string | null;
  retry_count: number;
  final_summary?: string | null;
  error_summary?: string | null;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  artifact_count: number;
  event_count: number;
}

export interface RunCreate {
  project_id: string;
  demo_mode?: boolean;
  engine?: 'local' | 'groq' | 'demo';
}

export interface RunListResponse {
  runs: AgentRun[];
  total: number;
}

export interface AgentEvent {
  id: string;
  run_id: string;
  agent_name: string;
  event_type: string;
  status: string;
  message?: string | null;
  metadata_json?: string | null;
  created_at: string;
}

export interface Artifact {
  id: string;
  run_id: string;
  relative_path: string;
  artifact_type: string;
  description?: string | null;
  checksum?: string | null;
  created_at: string;
}

export interface ArtifactContent {
  id: string;
  relative_path: string;
  artifact_type: string;
  content: string;
  description?: string | null;
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  ollama_configured: boolean;
  demo_mode: boolean;
}

export interface ConfigResponse {
  ollama_base_url: string;
  ollama_model: string;
  demo_mode: boolean;
  docker_enabled: boolean;
  max_revision_attempts: number;
  ollama_connected: boolean;
  ollama_model_available: boolean;
  groq_configured?: boolean;
  groq_model?: string;
  default_engine?: string;
}

export interface OllamaCheckResponse {
  connected: boolean;
  model_available: boolean;
  models: string[];
  error?: string | null;
}

export interface DashboardStats {
  total_projects: number;
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  running_runs: number;
}

export interface ReviewFinding {
  severity: 'error' | 'warning' | 'info';
  category: string;
  file_path?: string | null;
  line_number?: number | null;
  description: string;
  suggestion: string;
}

export interface ReviewOutput {
  findings: ReviewFinding[];
  approval: boolean;
  summary: string;
  recommendation: string;
}

export interface TestResultItem {
  test_name: string;
  status: 'passed' | 'failed' | 'skipped' | 'blocked';
  message: string;
  file_path?: string | null;
}

export interface TesterOutput {
  test_files_created: Array<{ path: string; description: string; content: string }>;
  test_results: TestResultItem[];
  passed: number;
  failed: number;
  skipped: number;
  blocked: number;
  summary: string;
  execution_method: string;
}

export interface TaskItem {
  id: string;
  title: string;
  priority: 'high' | 'medium' | 'low';
  depends_on: string[];
}

export interface PlannerOutput {
  project_summary: string;
  requirements: string[];
  task_list: TaskItem[];
  dependencies: string[];
  acceptance_criteria: string[];
  technical_constraints: string[];
  assumptions: string[];
}

export interface ArchitectOutput {
  architecture_summary: string;
  file_tree: string[];
  component_responsibilities: Array<{ component: string; responsibility: string }>;
  api_outline: Array<{ method: string; path: string; description: string }>;
  data_model: Array<{ entity: string; fields: string[] }>;
  implementation_plan: string[];
}
