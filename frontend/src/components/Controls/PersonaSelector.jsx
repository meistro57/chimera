import React, { useState, useEffect } from 'react'
import PersonaAvatar from '../Chat/PersonaAvatar'

const PersonaSelector = ({ refreshTrigger }) => {
  const [personas, setPersonas] = useState({ default: [], custom: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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

  useEffect(() => {
    fetchPersonas();
  }, [refreshTrigger]);

  const renderPersonaGroup = (group, title) => (
    <div className="mb-6">
      <h4 className="text-sm font-medium text-gray-900 mb-3 uppercase tracking-wide">
        {title}
      </h4>
      <div className="space-y-3">
        {group.map((persona) => (
          <div
            key={persona.name}
            className={`flex items-start space-x-3 p-3 rounded-lg ${
              persona.custom ? 'bg-indigo-50' : 'bg-gray-50'
            }`}
          >
            <PersonaAvatar
              persona={persona.name}
              avatarColor={persona.avatar_color}
              size="md"
            />

            <div className="flex-1 min-w-0">
              <h4 className="font-medium text-gray-900 text-sm">
                {persona.display_name}
              </h4>
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
        ))}
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