import React, { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'

const ChatWindow = ({ messages, conversationId }) => {
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto scrollbar-thin p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No messages yet
              </h3>
              <p className="text-gray-500">
                Start the conversation to see AI personalities interact!
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <MessageBubble
                key={message.id || index}
                message={message}
              />
            ))}

            {/* Typing indicators for active AIs */}
            {messages.some(m => m.type === 'typing') && (
              <TypingIndicator
                message={messages.find(m => m.type === 'typing')}
              />
            )}
          </>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Welcome Message */}
      {messages.length === 0 && (
        <div className="border-t border-gray-200 p-6 bg-blue-50">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">!</span>
            </div>
            <div>
              <h4 className="font-medium text-blue-900">Welcome to Chimera</h4>
              <p className="text-sm text-blue-700 mt-1">
                Click "Start Conversation" to watch three AI personalities engage in
                dynamic discussions. Each AI has a unique perspective: the thoughtful
                Philosopher, the witty Comedian, and the analytical Scientist.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ChatWindow