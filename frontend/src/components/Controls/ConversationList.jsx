// src/components/Controls/ConversationList.jsx
import React, { useEffect, useState, useCallback } from 'react'
import { Globe, Lock, RefreshCw, Share2 } from 'lucide-react'
import { api } from '../../services/api'

const ConversationList = ({ activeConversationId, onSelectConversation }) => {
  const [conversations, setConversations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchConversations = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getConversations()
      setConversations(data || [])
    } catch (err) {
      console.error('Unable to load conversations', err)
      setError(err.message || 'Unable to load conversations')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchConversations()
  }, [fetchConversations])

  const handleSelect = async (conversation) => {
    if (!conversation?.id) return
    await onSelectConversation(conversation)
  }

  return (
    <div className="mt-6 bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
          <Share2 className="w-4 h-4 text-gray-500" />
          Existing Conversations
        </h3>
        <button
          className="text-xs font-semibold text-blue-500 flex items-center gap-1"
          onClick={fetchConversations}
          disabled={loading}
        >
          <RefreshCw className="w-4 h-4" />
          {loading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="px-4 py-3 text-xs text-red-600">
          {error}
        </div>
      )}

      <div className="space-y-2 p-4">
        {conversations.length === 0 && !loading && (
          <p className="text-xs text-gray-500">No saved conversations yet.</p>
        )}

        {conversations.map((conversation) => {
          const isActive = conversation.id === activeConversationId
          const title = conversation.title || 'Untitled conversation'
          const subtitle = conversation.ai_participants?.join(', ') || 'No personas'

          return (
            <button
              key={conversation.id}
              onClick={() => handleSelect(conversation)}
              className={`w-full text-left p-3 rounded-lg border transition-colors flex flex-col space-y-1 ${
                isActive
                  ? 'border-blue-500 bg-blue-50 shadow-sm'
                  : 'border-transparent hover:border-gray-200 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between text-sm font-semibold text-gray-900">
                <span>{title}</span>
                <span className="flex items-center gap-1 text-xs text-gray-600">
                  {conversation.is_public ? (
                    <>
                      <Globe className="w-3 h-3 text-green-600" />
                      Shared
                    </>
                  ) : (
                    <>
                      <Lock className="w-3 h-3 text-gray-500" />
                      Private
                    </>
                  )}
                </span>
              </div>
              <p className="text-xs text-gray-500">{subtitle}</p>
              <div className="text-xs text-gray-400 flex items-center justify-between">
                <span>{conversation.created_at ? new Date(conversation.created_at).toLocaleString() : '—'}</span>
                {conversation.share_token && (
                  <span className="text-xs text-green-600">link available</span>
                )}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default ConversationList
