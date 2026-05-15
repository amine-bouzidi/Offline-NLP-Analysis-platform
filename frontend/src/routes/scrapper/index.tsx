import ScraperInterface from '@/components/scraper/ScraperForm';

export default function ScraperPage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">🕷️ Web Scraper</h1>
      <ScraperInterface />
    </div>
  );
}