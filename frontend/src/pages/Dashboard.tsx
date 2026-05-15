import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, 
         XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
         AreaChart, Area } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { TrendingUp, Users, AlertCircle, Target } from 'lucide-react'

interface DashboardPageProps {
  userRole: string
}

export default function DashboardPage({ userRole }: DashboardPageProps) {
  // Sample data
  const topicsData = [
    { name: 'Quality', value: 35, docs: 250 },
    { name: 'Safety', value: 25, docs: 180 },
    { name: 'Service', value: 20, docs: 145 },
    { name: 'Price', value: 12, docs: 85 },
    { name: 'Other', value: 8, docs: 55 },
  ]

  const temporalData = [
    { month: 'Jan', tweets: 450, articles: 120 },
    { month: 'Feb', tweets: 520, articles: 135 },
    { month: 'Mar', tweets: 480, articles: 125 },
    { month: 'Apr', tweets: 610, articles: 145 },
    { month: 'May', tweets: 750, articles: 165 },
    { month: 'Jun', tweets: 680, articles: 155 },
  ]

  const metricsData = [
    { metric: 'TTR', value: 0.92, benchmark: 0.80 },
    { metric: 'Coherence', value: 0.45, benchmark: 0.40 },
    { metric: 'Info Density', value: 0.71, benchmark: 0.65 },
    { metric: 'Complexity', value: 8.2, benchmark: 10 },
  ]

  const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

  // Decision Maker View
  if (userRole === 'decision_maker') {
    return (
      <div className="space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Overall Sentiment', value: '+68%', icon: TrendingUp, color: 'bg-green-500' },
            { label: 'Engagement Rate', value: '12.5%', icon: Users, color: 'bg-blue-500' },
            { label: 'Risk Score', value: 'MEDIUM', icon: AlertCircle, color: 'bg-yellow-500' },
            { label: 'Coverage', value: '1.2M', icon: Target, color: 'bg-purple-500' },
          ].map((kpi) => {
            const Icon = kpi.icon
            return (
              <Card key={kpi.label} className="hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-slate-600 mb-1">{kpi.label}</p>
                      <p className="text-3xl font-bold text-slate-900">{kpi.value}</p>
                    </div>
                    <div className={`${kpi.color} p-3 rounded-lg text-white`}>
                      <Icon size={20} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Executive Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              📋 Executive Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-slate-700 leading-relaxed">
              Based on comprehensive analysis of 1.2M mentions across press and social media,
              your organization demonstrates strong market positioning with particular strength
              in product quality perception. However, emerging safety concerns require strategic
              attention.
            </p>
            <p className="text-slate-700 leading-relaxed">
              Current engagement levels (12.5% interaction rate) indicate effective communication,
              with 68% positive sentiment overall. The organization maintains strong brand favorability
              compared to competitors.
            </p>
          </CardContent>
        </Card>

        {/* Key Insights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              icon: '✅',
              title: 'Strong Product Quality',
              description: 'Quality-related mentions increased 45% with 92% positive sentiment',
              color: 'border-l-green-500',
            },
            {
              icon: '⚠️',
              title: 'Safety Concerns Emerging',
              description: 'Food safety mentions peaked in April, requires immediate attention',
              color: 'border-l-yellow-500',
            },
            {
              icon: '📈',
              title: 'Customer Engagement',
              description: 'Social media engagement up 35%, driven by customer service initiative',
              color: 'border-l-blue-500',
            },
            {
              icon: '🎯',
              title: 'Competitive Positioning',
              description: 'Brand favorability vs competitors improved to 78%',
              color: 'border-l-purple-500',
            },
          ].map((insight) => (
            <Card key={insight.title} className={`border-l-4 ${insight.color}`}>
              <CardContent className="pt-6">
                <span className="text-3xl block mb-2">{insight.icon}</span>
                <h3 className="font-bold mb-2">{insight.title}</h3>
                <p className="text-sm text-slate-600">{insight.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recommendations */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              💡 Strategic Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="space-y-3">
              {[
                'Continue leveraging positive quality feedback in marketing campaigns',
                'Establish rapid response team for emerging safety concerns',
                'Invest further in customer service enhancement programs',
                'Monitor competitive landscape weekly during peak engagement periods',
                'Develop targeted messaging for risk mitigation during sensitive periods',
              ].map((rec, idx) => (
                <li key={idx} className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    {idx + 1}
                  </span>
                  <span className="text-slate-700 pt-0.5">{rec}</span>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Analyst View
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Topics Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              📈 Topics Distribution
            </CardTitle>
            <CardDescription>Top topics by document count</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={topicsData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {topicsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value} docs`} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Activity Timeline */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              📅 Activity Timeline
            </CardTitle>
            <CardDescription>Mentions over time by source</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={temporalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Legend />
                <Line type="monotone" dataKey="tweets" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6' }} />
                <Line type="monotone" dataKey="articles" stroke="#ef4444" strokeWidth={2} dot={{ fill: '#ef4444' }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Linguistic Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              📊 Linguistic Metrics
            </CardTitle>
            <CardDescription>Text analysis indicators</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={metricsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="metric" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Legend />
                <Bar dataKey="value" fill="#3b82f6" name="Actual" radius={[8, 8, 0, 0]} />
                <Bar dataKey="benchmark" fill="#cbd5e1" name="Benchmark" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top Keywords */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              🏷️ Top Keywords
            </CardTitle>
            <CardDescription>Most frequent terms in corpus</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {[
                { word: 'quality', size: 28 },
                { word: 'customer', size: 24 },
                { word: 'service', size: 20 },
                { word: 'good', size: 18 },
                { word: 'product', size: 22 },
                { word: 'satisfied', size: 16 },
                { word: 'issue', size: 19 },
                { word: 'recommend', size: 21 },
                { word: 'excellent', size: 17 },
                { word: 'improvement', size: 15 },
              ].map((item) => (
                <span
                  key={item.word}
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full"
                  style={{ fontSize: `${item.size}px` }}
                >
                  {item.word}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Convergence Heatmap */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🔄 Lexical Convergence
          </CardTitle>
          <CardDescription>Vocabulary overlap between periods</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={temporalData}>
              <defs>
                <linearGradient id="colorTweets" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorArticles" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="month" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#fff' }}
              />
              <Area 
                type="monotone" 
                dataKey="tweets" 
                stroke="#3b82f6" 
                fillOpacity={1} 
                fill="url(#colorTweets)"
              />
              <Area 
                type="monotone" 
                dataKey="articles" 
                stroke="#ef4444" 
                fillOpacity={1} 
                fill="url(#colorArticles)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Generated Reports */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            📄 Generated Reports
          </CardTitle>
          <CardDescription>LLM-generated syntheses</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { type: 'Semantic Summary', desc: 'Topics and key themes analysis' },
              { type: 'Temporal Summary', desc: 'Activity patterns and trends' },
              { type: 'Cognitive Summary', desc: 'Linguistic and discourse analysis' },
              { type: 'Executive Summary', desc: 'One-page overview for decision makers' },
            ].map((report) => (
              <div key={report.type} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
                <div>
                  <h4 className="font-semibold text-slate-900">{report.type}</h4>
                  <p className="text-sm text-slate-600">{report.desc}</p>
                </div>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-semibold">
                  Download
                </button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}