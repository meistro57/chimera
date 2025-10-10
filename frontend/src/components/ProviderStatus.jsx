import React, { useState, useEffect } from 'react'

const providerIcons = {
  'openai': '🤖',
  'anthropic': '🧠',
  'deepseek': '🔬',
  'google': '🌐',
  'openrouter': '🎯',
  'lmstudio': '🖥️',
  'ollama': '🐪'
}

const ProviderStatus = () => {
  const [personas, setPersonas] = useState({})
  const [providers, setProviders] = useState([])
  const [loading, setLoading] = useState(true)
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    fetchProviderStatuses()
    fetchPersonas()
    // Refresh provider status every 30 seconds
    const interval = setInterval(() => {
      fetchProviderStatuses()
      fetchPersonas()
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchPersonas = async () => {
    try {
      const response = await fetch('/api/personas')
      if (response.ok) {
        const data = await response.json()
        setPersonas(data)
      }
    } catch (error) {
      console.error('Failed to fetch personas:', error)
    }
  }

  const fetchProviderStatuses = async () => {
    try {
      const response = await fetch('/api/providers')
      if (response.ok) {
        const data = await response.json()
        setProviders(data)
      }
    } catch (error) {
      console.error('Failed to fetch providers:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <span className="text-xs font-medium text-gray-600">
        Loading...
      </span>
    )
  }

  const configuredProviders = providers.filter(p => p.configured)
  const hasConfiguredProviders = configuredProviders.length > 0

  return (
    <div className="flex items-center space-x-2 relative">
      {/* Status text */}
      <span className={`text-xs font-medium ${
        hasConfiguredProviders ? 'text-green-600' : 'text-amber-600'
      }`}>
        {hasConfiguredProviders ? 'Live AIs' : 'Setup Required'}
      </span>

      {/* Provider icons */}
      <div className="flex space-x-1">
        {providers.filter(p => p.configured).map((provider) => (
          <div
            key={provider.type}
            className={`w-5 h-5 rounded-full flex items-center justify-center text-xs cursor-pointer hover:scale-110 transition border ${
              provider.healthy 
                ? 'bg-green-100 border-green-300 hover:bg-green-200' 
                : 'bg-yellow-100 border-yellow-300 hover:bg-yellow-200'
            }`}
            title={`${provider.name} - ${provider.models?.length || 0} models`}
            onClick={() => setShowDetails(!showDetails)}
          >
            {providerIcons[provider.type] || '🤖'}
          </div>
        ))}
      </div>

      {/* Detailed configuration tooltip */}
      {showDetails && (
        <div className="absolute top-full mt-2 right-0 z-50 bg-white border border-gray-200 rounded-lg p-3 shadow-lg min-w-48">
          <div className="text-sm font-medium mb-2">AI Configurations</div>
          <div className="space-y-2">
            {Object.entries(personas).map(([personaName, persona]) => {
              const providerDisplay = persona.provider === 'auto' ? 'Auto' : persona.provider || 'Auto'
              return (
                <div key={personaName} className="text-xs">
                  <span className="font-medium capitalize">{personaName}</span>: 
                  <span className="ml-1 text-gray-600">{providerDisplay}</span>
                  {persona.model && <span className="text-gray-500"> ({persona.model})</span>}
                </div>
              )
            })}
          </div>
          <button
            onClick={() => setShowDetails(false)}
            className="mt-2 text-xs text-gray-500 hover:text-gray-700"
          >
            Close
          </button>
        </div>
      )}
    </div>
  )
}

export default ProviderStatus