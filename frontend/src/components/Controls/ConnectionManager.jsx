import React, { useState, useEffect } from 'react'
import { Key, Zap, Server, ChevronDown, ChevronUp, Eye, EyeOff } from 'lucide-react'

const ConnectionManager = () => {
  const [providers, setProviders] = useState([])
  const [apiKeys, setApiKeys] = useState({})
  const [showPasswords, setShowPasswords] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState({})

  const availableProviders = [
    { name: 'openai', displayName: 'OpenAI', color: 'bg-blue-500' },
    { name: 'anthropic', displayName: 'Anthropic Claude', color: 'bg-orange-500' },
    { name: 'deepseek', displayName: 'DeepSeek', color: 'bg-teal-500' },
    { name: 'google', displayName: 'Google Gemini', color: 'bg-green-500' },
    { name: 'openrouter', displayName: 'OpenRouter', color: 'bg-purple-500' },
    { name: 'lmstudio', displayName: 'LM Studio', color: 'bg-red-500' },
    { name: 'ollama', displayName: 'Ollama', color: 'bg-cyan-500' }
  ]

  const fetchProviders = async () => {
    try {
      const response = await fetch('/api/providers')
      const data = await response.json()
      setProviders(data)
    } catch (err) {
      console.error('Failed to fetch providers:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProviders()
  }, [])

  const handleApiKeyChange = (provider, value) => {
    setApiKeys(prev => ({
      ...prev,
      [provider]: value
    }))
  }

  const togglePasswordVisibility = (provider) => {
    setShowPasswords(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }))
  }

  const saveApiKey = async (provider) => {
    if (!apiKeys[provider]) return

    setSaving(prev => ({ ...prev, [provider]: true }))

    try {
      const response = await fetch('/api/providers/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          provider: provider,
          api_key: apiKeys[provider]
        })
      })

      if (response.ok) {
        alert(`API key saved for ${provider}`)
        // Reload providers to check connectivity
        fetchProviders()
      } else {
        const error = await response.json()
        alert(`Error saving API key: ${error.detail || 'Unknown error'}`)
      }
    } catch (err) {
      console.error('Failed to save API key:', err)
      alert('Failed to save API key')
    } finally {
      setSaving(prev => ({ ...prev, [provider]: false }))
    }
  }

  if (loading) {
    return (
      <div className="p-4 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-2 text-sm text-gray-600">Loading providers...</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        {availableProviders.map((provider) => {
          const providerData = providers.find(p => p.type === provider.name)
          const isConfigured = providerData?.healthy || false

          return (
            <div key={provider.name} className="border border-gray-200 rounded-lg overflow-hidden">
              <div className="p-4 bg-gray-50 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full ${provider.color}`}></div>
                  <div>
                    <h4 className="font-medium text-gray-900">{provider.displayName}</h4>
                    <p className="text-sm text-gray-500">
                      {isConfigured ? (
                        <span className="text-green-600">✓ Configured and healthy</span>
                      ) : (
                        <span>Needs API key</span>
                      )}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {providerData && (
                    <div className="text-sm text-gray-500">
                      {providerData.models?.length || 0} models available
                    </div>
                  )}
                </div>
              </div>

              <div className="p-4 space-y-3">
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showPasswords[provider.name] ? "text" : "password"}
                      value={apiKeys[provider.name] || ''}
                      onChange={(e) => handleApiKeyChange(provider.name, e.target.value)}
                      placeholder={`Enter ${provider.displayName} API key`}
                      className="w-full pr-10 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button
                      type="button"
                      onClick={() => togglePasswordVisibility(provider.name)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showPasswords[provider.name] ? (
                        <EyeOff className="h-4 w-4 text-gray-400" />
                      ) : (
                        <Eye className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>

                <button
                  onClick={() => saveApiKey(provider.name)}
                  disabled={!apiKeys[provider.name] || saving[provider.name]}
                  className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-md font-medium transition-colors"
                >
                  {saving[provider.name] ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Saving...
                    </>
                  ) : (
                    <>
                      <Key className="w-4 h-4 mr-2" />
                      Save API Key
                    </>
                  )}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      <div className="bg-blue-50 p-4 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">API Key Security</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• API keys are stored securely on the server</li>
          <li>• Configure keys only for providers you plan to use</li>
          <li>• You can test connectivity when selecting models for personas</li>
        </ul>
      </div>
    </div>
  )
}

export default ConnectionManager