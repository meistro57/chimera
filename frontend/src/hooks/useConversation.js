import { useState, useCallback } from 'react'
import { api } from '../services/api'

export const useConversation = () => {
  const [messages, setMessages] = useState([])
  const [isConversationActive, setIsConversationActive] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const addMessage = useCallback((message) => {
    setMessages(prev => {
      // Remove typing indicators when a real message comes in
      if (message.type === 'message') {
        const filtered = prev.filter(m => m.type !== 'typing')
        return [...filtered, message]
      }

      // For typing indicators, replace existing typing indicator
      if (message.type === 'typing') {
        const filtered = prev.filter(m => m.type !== 'typing')
        return [...filtered, message]
      }

      // For other message types
      return [...prev, message]
    })
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  const startConversation = useCallback(async (conversationId) => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.post(`/conversations/${conversationId}/start`)

      if (response.status === 'started') {
        setIsConversationActive(true)
        addMessage({
          id: `system_${Date.now()}`,
          type: 'message',
          sender_type: 'system',
          content: 'AI conversation started! The participants will begin discussing shortly...',
          timestamp: Date.now() / 1000
        })
        return true
      }

      return false
    } catch (err) {
      setError(err.message)
      console.error('Error starting conversation:', err)
      return false
    } finally {
      setLoading(false)
    }
  }, [addMessage])

  const stopConversation = useCallback(async (conversationId) => {
    try {
      setLoading(true)
      setError(null)

      await api.post(`/conversations/${conversationId}/stop`)

      setIsConversationActive(false)
      addMessage({
        id: `system_${Date.now()}`,
        type: 'message',
        sender_type: 'system',
        content: 'Conversation stopped.',
        timestamp: Date.now() / 1000
      })
    } catch (err) {
      setError(err.message)
      console.error('Error stopping conversation:', err)
    } finally {
      setLoading(false)
    }
  }, [addMessage])

  const loadConversationHistory = useCallback(async (conversationId) => {
    try {
      setLoading(true)
      setError(null)

      const messages = await api.get(`/conversations/${conversationId}/messages`)
      setMessages(messages)
    } catch (err) {
      setError(err.message)
      console.error('Error loading conversation history:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    messages,
    isConversationActive,
    loading,
    error,
    addMessage,
    clearMessages,
    startConversation,
    stopConversation,
    loadConversationHistory
  }
}