import React from 'react'
import PersonaAvatar from './PersonaAvatar'

const MessageBubble = ({ message }) => {
  const getMessageStyle = (senderType, persona) => {
    if (senderType === 'system') return 'message-system'
    if (senderType === 'user') return 'message-user'
    if (persona === 'philosopher') return 'message-philosopher'
    if (persona === 'comedian') return 'message-comedian'
    if (persona === 'scientist') return 'message-scientist'
    return 'message-user'
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const isSystemMessage = message.sender_type === 'system'

  if (isSystemMessage) {
    return (
      <div className="flex justify-center">
        <div className={`message-bubble ${getMessageStyle(message.sender_type, message.persona)}`}>
          <p className="text-sm text-gray-600">{message.content}</p>
          <span className="text-xs text-gray-400 mt-2 block">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>
      </div>
    )
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
            {message.persona_name || message.sender_id || 'User'}
          </span>
          <span className="text-xs text-gray-500">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>

        <div className={`message-bubble ${getMessageStyle(message.sender_type, message.persona)}`}>
          <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
      </div>
    </div>
  )
}

export default MessageBubble