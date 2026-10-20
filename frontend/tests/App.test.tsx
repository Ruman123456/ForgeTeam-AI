import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import App from '../src/App';
import { StatusBadge } from '../src/components/StatusBadge';
import { AgentCard } from '../src/components/AgentCard';

// Mock the API client
vi.mock('../src/api/client', () => ({
  api: {
    getConfig: vi.fn().mockResolvedValue({
      ollama_base_url: 'http://127.0.0.1:11434',
      ollama_model: 'qwen2.5-coder:3b',
      demo_mode: true,
      docker_enabled: false,
      max_revision_attempts: 2,
      ollama_connected: false,
      ollama_model_available: false,
    }),
    getDashboardStats: vi.fn().mockResolvedValue({
      total_projects: 3,
      total_runs: 5,
      completed_runs: 4,
      failed_runs: 1,
      running_runs: 0,
    }),
    getProjects: vi.fn().mockResolvedValue({
      projects: [
        {
          id: 'proj-1',
          name: 'Task Manager Pro',
          description: 'A complete task management system with priorities',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          run_count: 2,
        },
      ],
      total: 1,
    }),
  },
}));

describe('Frontend Component & Page Verification', () => {
  it('renders navigation bar brand correctly', async () => {
    render(<App />);
    expect(screen.getByText('ForgeTeam')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Create Project')).toBeInTheDocument();
  });

  it('renders dashboard metrics after data fetching', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('Total Projects')).toBeInTheDocument();
      expect(screen.getByText('Task Manager Pro')).toBeInTheDocument();
    });
  });

  it('renders StatusBadge component correctly for various statuses', () => {
    const { rerender } = render(<StatusBadge status="completed" />);
    expect(screen.getByText('Completed')).toBeInTheDocument();

    rerender(<StatusBadge status="failed" />);
    expect(screen.getByText('Failed')).toBeInTheDocument();

    rerender(<StatusBadge status="running" />);
    expect(screen.getByText('Running')).toBeInTheDocument();
  });

  it('renders AgentCard with appropriate roles and statuses', () => {
    render(
      <AgentCard
        role="developer"
        status="running"
        message="Generating 20 files based on architecture"
        isCurrent={true}
      />
    );
    expect(screen.getByText('Developer Agent')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(
      screen.getByText('Generating 20 files based on architecture')
    ).toBeInTheDocument();
  });
});
