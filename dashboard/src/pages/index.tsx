import { useState, useEffect } from 'react'
import { Calendar, Filter, Search, Plus, Clock, Star } from 'lucide-react'

interface Opportunity {
  id: number
  title: string
  category: string
  deadline: string | null
  priority_score: number
  status: string
  created_at: string
}

export default function Dashboard() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [filter, setFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [newOpportunityContent, setNewOpportunityContent] = useState('')

  useEffect(() => {
    fetchOpportunities()
  }, [])

  const fetchOpportunities = async () => {
    try {
      const response = await fetch('https://ochatbot-9nd0.onrender.com/opportunities')
      const data = await response.json()
      setOpportunities(data)
    } catch (error) {
      console.error('Error fetching opportunities:', error)
    }
  }

  const createOpportunity = async () => {
    try {
      const response = await fetch('https://ochatbot-9nd0.onrender.com/opportunities', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: newOpportunityContent }),
      })
      if (response.ok) {
        setNewOpportunityContent('')
        setShowModal(false)
        fetchOpportunities() // Refresh the list
      } else {
        console.error('Error creating opportunity')
      }
    } catch (error) {
      console.error('Error creating opportunity:', error)
    }
  }

  const filteredOpportunities = opportunities.filter(opp => {
    const matchesFilter = filter === 'all' || opp.category === filter
    const matchesSearch = opp.title.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const getStatusColor = (status: string) => {
    const colors = {
      new: 'bg-blue-100 text-blue-800',
      applied: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-purple-100 text-purple-800',
      completed: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  const getPriorityColor = (score: number) => {
    if (score >= 8) return 'text-red-500'
    if (score >= 6) return 'text-yellow-500'
    return 'text-green-500'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">OpportunityBot Dashboard</h1>
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
              onClick={() => setShowModal(true)}
            >
              <Plus size={20} />
              Add Opportunity
            </button>
          </div>
        </div>
      </header>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Total Opportunities</h3>
            <p className="text-2xl font-bold text-gray-900">{opportunities.length}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Active Applications</h3>
            <p className="text-2xl font-bold text-blue-600">
              {opportunities.filter(o => o.status === 'applied').length}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Completed</h3>
            <p className="text-2xl font-bold text-green-600">
              {opportunities.filter(o => o.status === 'completed').length}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">High Priority</h3>
            <p className="text-2xl font-bold text-red-600">
              {opportunities.filter(o => o.priority_score >= 8).length}
            </p>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Search opportunities..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <select
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="all">All Categories</option>
              <option value="job">Jobs</option>
              <option value="freelance">Freelance</option>
              <option value="business">Business</option>
              <option value="grant">Grants</option>
              <option value="competition">Competitions</option>
            </select>
          </div>
        </div>

        {/* Opportunities List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Opportunities</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {filteredOpportunities.map((opportunity) => (
              <div key={opportunity.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      {opportunity.title}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(opportunity.status)}`}>
                        {opportunity.status.replace('_', ' ')}
                      </span>
                      <span className="capitalize">{opportunity.category}</span>
                      {opportunity.deadline && (
                        <span className="flex items-center gap-1">
                          <Clock size={14} />
                          {new Date(opportunity.deadline).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Star className={`${getPriorityColor(opportunity.priority_score)}`} size={16} />
                    <span className={`font-medium ${getPriorityColor(opportunity.priority_score)}`}>
                      {opportunity.priority_score}/10
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>

    {/* Modal for adding new opportunity */}
    {showModal && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
          <h2 className="text-xl font-semibold mb-4">Add New Opportunity</h2>
          <textarea
            className="w-full border border-gray-300 rounded-lg p-2 mb-4"
            rows={4}
            value={newOpportunityContent}
            onChange={(e) => setNewOpportunityContent(e.target.value)}
            placeholder="Enter opportunity details here..."
          />
          <div className="flex justify-end gap-4">
            <button
              className="px-4 py-2 bg-gray-300 rounded-lg hover:bg-gray-400"
              onClick={() => setShowModal(false)}
            >
              Cancel
            </button>
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              onClick={createOpportunity}
            >
              Add
            </button>
          </div>
        </div>
      </div>
    )}
  )
}
