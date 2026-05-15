import { useState } from 'react'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { CheckCircle, AlertCircle, Download } from 'lucide-react'

export default function ScraperPage() {
  const [query, setQuery] = useState('')
  const [sources, setSources] = useState<string[]>(['twitter', 'press'])
  const [status, setStatus] = useState<'idle' | 'loading' | 'done' | 'error'>('idle')
  const [progress, setProgress] = useState(0)
  const [jobId, setJobId] = useState<string | null>(null)

  const handleStartScraper = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setStatus('loading')
    setProgress(10)

    try {
      const token = localStorage.getItem('token')
      const res = await fetch('/api/scraper/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query, sources }),
      })
      const data = await res.json()
      setJobId(data.job_id)

      // Simulate progress
      let currentProgress = 10
      const interval = setInterval(() => {
        currentProgress += Math.random() * 25
        if (currentProgress >= 90) currentProgress = 90
        setProgress(Math.round(currentProgress))
      }, 500)

      // Complete after 5 seconds
      setTimeout(() => {
        clearInterval(interval)
        setProgress(100)
        setStatus('done')
      }, 5000)
    } catch (err) {
      console.error(err)
      setStatus('error')
    }
  }

  const sourceOptions = [
    { id: 'twitter', label: '𝕏 Twitter', desc: 'Real-time social media mentions' },
    { id: 'press', label: '📰 Press', desc: 'News articles and media coverage' },
    { id: 'reddit', label: '🔗 Reddit', desc: 'Forum discussions and communities' },
  ]

  return (
    <div className="space-y-6">
      {/* Scraper Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🕷️ Web Scraper Configuration
          </CardTitle>
          <CardDescription>Configure and start a new scraping job</CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleStartScraper} className="space-y-6">
            {/* Query Input */}
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-900">Search Query</label>
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., product quality, food safety, customer experience"
                disabled={status === 'loading'}
                className="text-base"
              />
              <p className="text-xs text-slate-500">
                Enter keywords or phrases to search across all selected sources
              </p>
            </div>

            {/* Data Sources */}
            <div className="space-y-3">
              <label className="text-sm font-semibold text-slate-900">Data Sources</label>
              <div className="space-y-2">
                {sourceOptions.map((source) => (
                  <label
                    key={source.id}
                    className="flex items-start gap-3 p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={sources.includes(source.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSources([...sources, source.id])
                        } else {
                          setSources(sources.filter((s) => s !== source.id))
                        }
                      }}
                      disabled={status === 'loading'}
                      className="mt-1 w-4 h-4 cursor-pointer"
                    />
                    <div>
                      <p className="font-semibold text-slate-900">{source.label}</p>
                      <p className="text-xs text-slate-600">{source.desc}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={status === 'loading' || !query.trim()}
              className="w-full h-11 text-base"
            >
              {status === 'loading' ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Scraping in progress...
                </>
              ) : (
                '▶️ Start Scraper'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Progress Card */}
      {status === 'loading' && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6 space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-900">Scraping Progress</span>
                <span className="text-sm font-bold text-blue-600">{progress}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-600 to-purple-600 h-full transition-all duration-300 rounded-full"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            <div className="space-y-2 text-sm text-slate-700">
              <p>
                {progress < 25 && '🔍 Initializing scraper...'}
                {progress >= 25 && progress < 50 && '🌐 Connecting to data sources...'}
                {progress >= 50 && progress < 75 && '📥 Downloading data...'}
                {progress >= 75 && progress < 100 && '⚙️ Processing results...'}
                {progress === 100 && '✅ Processing complete!'}
              </p>
              {jobId && <p className="text-xs text-slate-600">Job ID: {jobId.substring(0, 12)}...</p>}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Success Card */}
      {status === 'done' && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-green-900 mb-1">Scraping Completed Successfully!</h3>
                <p className="text-sm text-green-700 mb-4">
                  {progress}% of data collected from {sources.join(', ')}
                </p>
                <Button className="bg-green-600 hover:bg-green-700">
                  <Download size={18} className="mr-2" />
                  Download Results
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Card */}
      {status === 'error' && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900 mb-1">Scraping Failed</h3>
                <p className="text-sm text-red-700">
                  An error occurred while scraping. Please check your query and try again.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Jobs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            📊 Recent Scraping Jobs
          </CardTitle>
          <CardDescription>History of scraping operations</CardDescription>
        </CardHeader>

        <CardContent>
          <div className="space-y-3">
            {[
              { query: 'food safety', status: 'completed', date: '2 hours ago', count: '1,250' },
              { query: 'product quality', status: 'completed', date: '1 day ago', count: '3,890' },
              { query: 'customer service', status: 'completed', date: '3 days ago', count: '2,150' },
            ].map((job, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
                <div>
                  <p className="font-semibold text-slate-900">"{job.query}"</p>
                  <div className="flex gap-4 text-xs text-slate-600 mt-1">
                    <span>📅 {job.date}</span>
                    <span>📦 {job.count} results</span>
                  </div>
                </div>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                  ✓ {job.status}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}