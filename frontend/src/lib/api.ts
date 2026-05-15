import axios from 'axios';
import AuthService from './auth';
import type { ScraperConfig, ScraperJob, AnalysisResult } from '@/types/scraper';

const API = AuthService.getAxiosInstance();

export const ScraperAPI = {
  start: async (config: ScraperConfig): Promise<{ job_id: string }> => {
    const response = await API.post('/scraper/start', config);
    return response.data;
  },

  getStatus: async (jobId: string): Promise<ScraperJob> => {
    const response = await API.get(`/scraper/status/${jobId}`);
    return response.data;
  },

  listJobs: async (): Promise<ScraperJob[]> => {
    const response = await API.get('/scraper/list');
    return response.data.jobs;
  },
};

export const DashboardAPI = {
  getAnalyses: async (): Promise<AnalysisResult[]> => {
    const response = await API.get('/dashboard/analyses');
    return response.data.analyses;
  },

  getAnalysisData: async (analysisId: string): Promise<AnalysisResult> => {
    const response = await API.get(`/dashboard/data/${analysisId}`);
    return response.data;
  },

  uploadFile: async (file: File, name: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);
    const response = await API.post('/dashboard/upload', formData);
    return response.data;
  },

  getStatsByRole: async (role: string) => {
    const response = await API.get(`/dashboard/stats/${role}`);
    return response.data;
  },
};