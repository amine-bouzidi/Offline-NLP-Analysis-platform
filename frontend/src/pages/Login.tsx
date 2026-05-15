import { useState } from 'react'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

interface LoginPageProps {
  setUser: (user: any) => void
}

export default function LoginPage({ setUser }: LoginPageProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      const data = await res.json()

      if (data.access_token) {
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        setUser(data.user)
      }
    } finally {
      setLoading(false)
    }
  }

  const quickDemo = (u: string, p: string) => {
    setUsername(u)
    setPassword(p)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-2 text-center">
          <CardTitle className="text-3xl">📊 InsightFlow</CardTitle>
          <CardDescription>Enterprise Text Analysis Platform</CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold">Username</label>
              <Input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold">Password</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                disabled={loading}
              />
            </div>

            <Button className="w-full" disabled={loading || !username || !password}>
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </form>

          <div className="border-t pt-4">
            <p className="text-sm font-semibold mb-3">📌 Demo Credentials</p>
            <button
              onClick={() => quickDemo('analyst', 'analyst123')}
              className="w-full mb-2 p-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-left text-sm border border-blue-200"
            >
              <strong className="block">👨‍💻 Analyst</strong>
              <span className="text-gray-600 text-xs">analyst / analyst123</span>
            </button>
            <button
              onClick={() => quickDemo('decision_maker', 'decision123')}
              className="w-full p-3 bg-purple-50 hover:bg-purple-100 rounded-lg text-left text-sm border border-purple-200"
            >
              <strong className="block">👔 Decision Maker</strong>
              <span className="text-gray-600 text-xs">decision_maker / decision123</span>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}