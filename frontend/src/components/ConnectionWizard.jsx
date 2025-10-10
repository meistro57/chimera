import React, { useState, useEffect } from 'react'

const ConnectionWizard = ({ onClose }) => {
  const [apiKeys, setApiKeys] = useState({
    openrouter: '',
    openai: '',
    anthropic: '',
    deepseek: '',
    google: '',
  })

  const [loading, setLoading] = useState(false)
  const [configured, setConfigured] = useState({})

  useEffect(() => {
    fetchProviderStatuses()
  }, [])

  const providers = [
    { key: 'openrouter', displayName: 'OpenRouter', description: 'Access to OpenAI, Claude, and many other models' },
    { key: 'openai', displayName: 'OpenAI', description: 'Direct OpenAI API access' },
    { key: 'anthropic', displayName: 'Anthropic', description: 'Claude models' },
    { key: 'deepseek', displayName: 'DeepSeek', description: 'Fast and affordable models' },
    { key: 'google', displayName: 'Google AI', description: 'Gemini models' },
  ]

  const fetchProviderStatuses = async () => {
    try {
      const response = await fetch('/api/providers')
      if (response.ok) {
        const data = await response.json()
        const statusMap = {}
        data.forEach(provider => {
          statusMap[provider.type] = provider.configured
        })
        setConfigured(statusMap)
      }
    } catch (error) {
      console.error('Failed to fetch provider statuses:', error)
    }
  }

  const saveApiKey = async (provider, apiKey) => {
    setLoading(true)
    try {
      const response = await fetch('/api/providers/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, api_key: apiKey })
      })
      
      if (response.ok) {
        await fetchProviderStatuses()
        alert(`${provider} API key saved successfully!`)
      } else {
        alert('Failed to save API key')
      }
    } catch (err) {
      alert('Error saving API key: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const testProvider = async (provider) => {
    setLoading(true)
    try {
      const response = await fetch('/api/providers/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider })
      })
      const result = await response.json()
      
      if (result.status === 'success') {
        await fetchProviderStatuses()
        alert(`✅ ${result.provider}: ${result.message}\n\nTest response: "${result.response_sample}"`)
      } else {
        alert(`❌ ${result.provider}: ${result.message}`)
      }
    } catch (err) {
      alert(`❌ Test failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg max-w-lg w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Configure AI Providers</h2>
          <button
            onClick={fetchProviderStatuses}
            disabled={loading}
            className={`px-3 py-1 ${loading ? 'bg-gray-300' : 'bg-gray-500 hover:bg-gray-600'} text-white text-xs rounded`}
          >
            ↻ Refresh
          </button>
        </div>
        <p className="mb-4 text-sm text-gray-600">
          Configure API keys for AI providers. You only need one to start (OpenRouter recommended), but you can add more later.
        </p>
        
        <div className="space-y-4">
          {providers.map(provider => {
            const isConfigured = configured[provider.key]
            return (
              <div key={provider.key} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <h3 className="font-medium">{provider.displayName}</h3>
                    {isConfigured && (
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                        ✓ Configured
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-gray-500">{provider.description}</span>
                </div>
                
                <div className="space-y-2">
                  <input
                    type="password"
                    className="w-full p-2 border border-gray-300 rounded text-sm"
                    placeholder={`Enter ${provider.displayName} API key`}
                    value={apiKeys[provider.key]}
                    onChange={(e) => setApiKeys(prev => ({
                      ...prev,
                      [provider.key]: e.target.value
                    }))}
                  />
                  
                  <div className="flex gap-2">
                    <button
                      disabled={loading}
                      onClick={() => {
                        const apiKey = apiKeys[provider.key].trim()
                        if (apiKey) {
                          saveApiKey(provider.key, apiKey)
                        } else {
                          alert('Please enter an API key first')
                        }
                      }}
                      className={`px-3 py-1 ${loading ? 'bg-blue-300' : 'bg-blue-500 hover:bg-blue-600'} text-white text-xs rounded`}
                    >
                      {loading ? 'Saving...' : 'Save'}
                    </button>
                    
                    <button
                      disabled={loading || !isConfigured}
                      onClick={() => testProvider(provider.key)}
                      className={`px-3 py-1 ${
                        loading || !isConfigured 
                          ? 'bg-green-200 text-gray-500 cursor-not-allowed' 
                          : 'bg-green-500 hover:bg-green-600'
                      } text-white text-xs rounded`}
                      title={!isConfigured ? 'Save API key first to enable testing' : 'Test API key functionality'}
                    >
                      {loading ? 'Testing...' : 'Test'}
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConnectionWizard