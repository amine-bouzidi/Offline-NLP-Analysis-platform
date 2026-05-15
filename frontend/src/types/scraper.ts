export type DataSource = 'twitter' | 'press' | 'reddit';

export interface ScraperJob {
  id: string;
  query: string;
  sources: DataSource[];
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  startedAt: string;
  completedAt?: string;
  resultPath?: string;
}

export interface ScraperConfig {
  query: string;
  sources: DataSource[];
  maxTweets?: number;
  maxArticles?: number;
}

export interface AnalysisResult {
  id: string;
  name: string;
  corpus: any[];
  metrics: any;
  syntheses: any;
  createdAt: string;
}