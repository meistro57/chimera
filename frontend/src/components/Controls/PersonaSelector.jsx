import React from 'react'
import PersonaAvatar from '../Chat/PersonaAvatar'

const PersonaSelector = () => {
  const personas = [
    {
      name: 'philosopher',
      display_name: 'The Philosopher',
      avatar_color: '#6366f1',
      personality_traits: ['thoughtful', 'abstract', 'wise', 'questioning'],
      description: 'Contemplates deep questions about existence and ethics'
    },
    {
      name: 'comedian',
      display_name: 'The Comedian',
      avatar_color: '#f59e0b',
      personality_traits: ['witty', 'playful', 'spontaneous', 'entertaining'],
      description: 'Finds humor in everyday situations with quick wit'
    },
    {
      name: 'scientist',
      display_name: 'The Scientist',
      avatar_color: '#10b981',
      personality_traits: ['logical', 'factual', 'methodical', 'precise'],
      description: 'Approaches problems with evidence and logic'
    }
  ]

  return (
    <div className="space-y-3">
      {personas.map((persona) => (
        <div
          key={persona.name}
          className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
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
              {persona.description}
            </p>
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
          </div>
        </div>
      ))}
    </div>
  )
}

export default PersonaSelector