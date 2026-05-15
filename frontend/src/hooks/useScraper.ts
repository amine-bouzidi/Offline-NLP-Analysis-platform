import { useState, useCallback } from 'react';
import { ScraperAPI } from '@/lib/api';
import type { ScraperConfig, ScraperJob } from '@/types/scraper';

export const useScraper = () => {
  const [job, setJob] = useState<ScraperJob | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startScraping = useCallback(async (config: ScraperConfig) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await ScraperAPI.start(config);
      setJob({ id: result.job_id } as ScraperJob);
      
      // Poll status
      const pollInterval = setInterval(async () => {
        try {
          const status = await ScraperAPI.getStatus(result.job_id);
          setJob(status);
          
          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(pollInterval);
          }
        } catch (err) {
          console.error('Status poll error:', err);
        }
      }, 2000);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    job,
    isLoading,
    error,
    startScraping,
  };
};