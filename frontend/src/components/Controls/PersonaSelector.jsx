import React, { useState, useEffect } from 'react'
import { ChevronDown, ChevronUp, Zap, Server, Check } from 'lucide-react'
import PersonaAvatar from '../Chat/PersonaAvatar'

const PersonaSelector = ({ refreshTrigger }) => {
  const [personas, setPersonas] = useState({ default: [], custom: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedPersona, setExpandedPersona] = useState(null);
  const [availableModels, setAvailableModels] = useState({});
  const [updatingProvider, setUpdatingProvider] = useState(null);

  const availableProviders = [
    { name: 'auto', displayName: 'Auto-select', color: 'bg-gray-500' },
    { name: 'openai', displayName: 'OpenAI', color: 'bg-blue-500' },
    { name: 'anthropic', displayName: 'Claude', color: 'bg-orange-500' },
    { name: 'deepseek', displayName: 'DeepSeek', color: 'bg-teal-500' },
    { name: 'google', displayName: 'Gemini', color: 'bg-green-500' },
    { name: 'openrouter', displayName: 'OpenRouter', color: 'bg-purple-500' },
    { name: 'lmstudio', displayName: 'LM Studio', color: 'bg-red-500' },
    { name: 'ollama', displayName: 'Ollama', color: 'bg-cyan-500' }
  ];

  const fetchPersonas = async () => {
    try {
      const response = await fetch('/api/personas/');
      const data = await response.json();
      setPersonas(data);
    } catch (err) {
      setError('Failed to load personas');
    } finally {
      setLoading(false);
    }
  };

  const fetchModelsForProvider = async (provider) => {
    if (provider === 'auto' || availableModels[provider]) return;

    try {
      const response = await fetch(`/api/providers/models/${provider}`);
      const data = await response.json();
      setAvailableModels(prev => ({
        ...prev,
        [provider]: data.models || []
      }));
    } catch (err) {
      console.error(`Failed to fetch models for ${provider}:`, err);
      setAvailableModels(prev => ({
        ...prev,
        [provider]: []
      }));
    }
  };

  const updatePersonaProvider = async (personaName, provider, model = null) => {
    setUpdatingProvider(personaName);

    try {
      const response = await fetch(`/api/personas/${personaName}/provider`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ provider, model })
      });

      if (response.ok) {
        // Refresh personas to get updated data
        await fetchPersonas();
      } else {
        const error = await response.json();
        alert(`Failed to update provider: ${error.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Failed to update persona provider:', err);
      alert('Failed to update provider configuration');
    } finally {
      setUpdatingProvider(null);
    }
  };

  useEffect(() => {
    fetchPersonas();
  }, [refreshTrigger]);

  const togglePersonaExpansion = (personaName) => {
    if (expandedPersona === personaName) {
      setExpandedPersona(null);
    } else {
      setExpandedPersona(personaName);
    }
  };

  const renderPersonaGroup = (group, title) => (
    <div className="mb-6">
      <h4 className="text-sm font-medium text-gray-900 mb-3 uppercase tracking-wide">
        {title}
      </h4>
      <div className="space-y-3">
        {group.map((persona) => {
          const isExpanded = expandedPersona === persona.name;
          const currentProvider = availableProviders.find(p => p.name === (persona.provider || 'auto'));
          const currentModel = persona.model;

          return (
            <div
              key={persona.name}
              className={`border border-gray-200 rounded-lg overflow-hidden ${
                persona.custom ? 'bg-indigo-50' : 'bg-gray-50'
              }`}
            >
              {/* Header */}
              <div
                className="flex items-start space-x-3 p-3 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => togglePersonaExpansion(persona.name)}
              >
                <PersonaAvatar
                  persona={persona.name}
                  avatarColor={persona.avatar_color}
                  size="md"
                />

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900 text-sm">
                      {persona.display_name}
                    </h4>
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${currentProvider?.color || 'bg-gray-500'}`}></div>
                      <span className="text-xs text-gray-600">
                        {currentProvider?.displayName || 'Auto-select'}
                      </span>
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  </div>

                  <p className="text-xs text-gray-600 mt-1 leading-relaxed">
                    {persona.system_prompt?.substring(0, 80) || persona.description}...
                  </p>

                  {persona.personality_traits && persona.personality_traits.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {persona.personality_traits.map((trait) => (
                        <span
                          key={trait}
                          className="inline-block px-2 py-0.5 bg-white text-xs text-gray-600 rounded border"
                        >
                          {trait}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Expanded Provider/Model Selection */}
              {isExpanded && (
                <div className="border-t border-gray-200 p-3 bg-white">
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-2">
                        AI Provider
                      </label>
                      <select
                        value={persona.provider || 'auto'}
                        onChange={(e) => {
                          const provider = e.target.value;
                          updatePersonaProvider(persona.name, provider);
                          fetchModelsForProvider(provider);
                        }}
                        disabled={updatingProvider === persona.name}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        {availableProviders.map(provider => (
                          <option key={provider.name} value={provider.name}>
                            <div className="flex items-center">
                              <div className={`w-2 h-2 rounded-full ${provider.color} mr-2`}></div>
                              {provider.displayName}
                            </div>
                          </option>
                        ))}
                      </select>
                    </div>

                    {(persona.provider || 'auto') !== 'auto' && (
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-2">
                          Model (Optional)
                        </label>
                        <select
                          value={currentModel || ''}
                          onChange={(e) => {
                            const model = e.target.value;
                            updatePersonaProvider(persona.name, persona.provider, model || null);
                          }}
                          disabled={updatingProvider === persona.name}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Auto-select best model</option>
                          {availableModels[persona.provider]?.map(model => (
                            <option key={model} value={model}>
                              {model}
                            </option>
                          ))}
                        </select>
                        {availableModels[persona.provider] && availableModels[persona.provider].length === 0 && (
                          <p className="text-xs text-amber-600 mt-1">Models loading...</p>
                        )}
                      </div>
                    )}

                    {updatingProvider === persona.name && (
                      <div className="flex items-center space-x-2 text-xs text-gray-600">
                        <div className="animate-spin rounded-full h-3 w-3 border-b border-blue-600"></div>
                        Updating provider configuration...
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );

  if (loading) {
    return <div className="text-sm text-gray-500">Loading personas...</div>;
  }

  if (error) {
    return <div className="text-sm text-red-500">{error}</div>;
  }

  return (
    <div className="space-y-6">
      {renderPersonaGroup(personas.default, "Default Personas")}
      {renderPersonaGroup(personas.custom, "Custom Personas")}
    </div>
  )
}

export default PersonaSelector