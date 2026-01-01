// src/components/Chat/TypingIndicator.jsx
import React, { useMemo } from 'react'
import { selectMessages, useChatStore } from '../../store/ChatStore'
import PersonaAvatar from './PersonaAvatar'

const TypingIndicator = ({ message: typingMessageOverride }) => {
  const { state } = useChatStore()
  const { activeConversationId, conversations } = state

  const message = useMemo(() => {
    if (typingMessageOverride) return typingMessageOverride
    if (!activeConversationId) return null
    const messages = selectMessages({ conversations }, activeConversationId)
    return messages.find(entry => entry.type === 'typing')
  }, [activeConversationId, conversations, typingMessageOverride])

  if (!message || message.type !== 'typing') {
    return null
  }

  return (
    <div className="flex items-start space-x-3">
      <PersonaAvatar
        persona={message.persona}
        avatarColor={message.avatar_color}
        size="md"
      />

      <div className="flex-1">
        <div className="flex items-center space-x-2 mb-1">
          <span className="font-medium text-gray-900">
            {message.persona_name}
          </span>
        </div>

        <div className="message-bubble bg-gray-100 border-l-4 border-gray-300">
          <div className="typing-indicator">
            <div className="typing-dot" style={{ animationDelay: '0ms' }}></div>
            <div className="typing-dot" style={{ animationDelay: '150ms' }}></div>
            <div className="typing-dot" style={{ animationDelay: '300ms' }}></div>
            <span className="text-gray-600 ml-2 text-sm">
              {message.persona_name} is typing...
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TypingIndicator
