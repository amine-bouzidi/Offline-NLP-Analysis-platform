import { useState, useEffect } from 'react'
import { Button } from './components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { Input } from './components/ui/input'
import { LogOut, Menu, X } from 'lucide-react'
import LoginPage from './pages/Login'
import ScraperPage from './pages/Scraper'
import DashboardPage from './pages/Dashboard'

export default function App() {
  const [user, setUser] = useState(null)
  const [currentPage, setCurrentPage] = useState('login')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      setUser(JSON.parse(storedUser))
      setCurrentPage('dashboard')
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    setUser(null)
    setCurrentPage('login')
  }

  if (!user) {
    return <LoginPage setUser={setUser} />
  }

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-slate-900 text-white transition-all duration-300 flex flex-col`}
      >
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          {sidebarOpen && <h1 className="text-xl font-bold">📊 InsightFlow</h1>}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 hover:bg-slate-800 rounded-lg"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <button
            onClick={() => setCurrentPage('dashboard')}
            className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
              currentPage === 'dashboard'
                ? 'bg-blue-600'
                : 'hover:bg-slate-800'
            }`}
          >
            {sidebarOpen && '📊 Dashboard'}
          </button>
          <button
            onClick={() => setCurrentPage('scraper')}
            className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
              currentPage === 'scraper'
                ? 'bg-blue-600'
                : 'hover:bg-slate-800'
            }`}
          >
            {sidebarOpen && '🕷️ Scraper'}
          </button>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
          >
            <LogOut size={18} />
            {sidebarOpen && 'Logout'}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <header className="bg-white border-b border-slate-200 px-8 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-slate-900">
            {currentPage === 'dashboard' && '📊 Dashboard'}
            {currentPage === 'scraper' && '🕷️ Web Scraper'}
          </h2>
          <div className="flex items-center gap-4">
            <span className="text-sm font-semibold text-slate-700">{user.username}</span>
            <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
              {user.username[0].toUpperCase()}
            </div>
          </div>
        </header>

        <div className="p-8">
          {currentPage === 'dashboard' && <DashboardPage userRole={user.role} />}
          {currentPage === 'scraper' && <ScraperPage />}
        </div>
      </main>
    </div>
  )
}