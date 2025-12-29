// src/hooks/useConversation.js
import { useCallback, useMemo, useState } from 'react'
import { api } from '../services/api'
import { selectMessages, useChatStore } from '../store/ChatStore'

export const useConversation = () => {
  const { state, dispatch } = useChatStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const messages = useMemo(() => {
    if (!state.activeConversationId) return []
    return selectMessages(state, state.activeConversationId)
  }, [state])

  const addMessage = useCallback((message, conversationId = state.activeConversationId) => {
    if (!conversationId) return
    dispatch({ type: 'MESSAGE_RECEIVED', payload: { conversationId, message } })
  }, [dispatch, state.activeConversationId])

  const clearMessages = useCallback((conversationId = state.activeConversationId) => {
    if (!conversationId) return
    dispatch({ type: 'LOAD_MESSAGES', payload: { conversationId, messages: [] } })
  }, [dispatch, state.activeConversationId])

  const setActiveConversation = useCallback((conversationId) => {
    if (!conversationId) return
    dispatch({ type: 'SET_ACTIVE_CONVERSATION', payload: { conversationId } })
  }, [dispatch])

  const startConversation = useCallback(async (conversationId) => {
    if (!conversationId) return false

    try {
      setLoading(true)
      setError(null)
      dispatch({ type: 'START_CONVERSATION', payload: { conversationId } })

      const response = await api.post(`/conversations/${conversationId}/start`)
      if (response.status === 'started') {
        addMessage({
          id: `system_${Date.now()}`,
          type: 'message',
          sender_type: 'system',
          content: 'AI conversation started! The participants will begin discussing shortly...',
          timestamp: Date.now() / 1000
        }, conversationId)
        return true
      }

      return false
    } catch (err) {
      setError(err.message)
      dispatch({ type: 'SET_ERROR', payload: { conversationId, error: err.message } })
      return false
    } finally {
      setLoading(false)
    }
  }, [addMessage, dispatch])

  const stopConversation = useCallback(async (conversationId = state.activeConversationId) => {
    if (!conversationId) return
    try {
      setLoading(true)
      setError(null)

      await api.post(`/conversations/${conversationId}/stop`)
      dispatch({ type: 'STOP_CONVERSATION', payload: { conversationId } })
      addMessage({
        id: `system_${Date.now()}`,
        type: 'message',
        sender_type: 'system',
        content: 'Conversation stopped.',
        timestamp: Date.now() / 1000
      }, conversationId)
    } catch (err) {
      setError(err.message)
      dispatch({ type: 'SET_ERROR', payload: { conversationId, error: err.message } })
    } finally {
      setLoading(false)
    }
  }, [addMessage, dispatch, state.activeConversationId])

  const loadConversationHistory = useCallback(async (conversationId) => {
    if (!conversationId) return

    try {
      setLoading(true)
      setError(null)

      const existingMessages = await api.get(`/conversations/${conversationId}/messages`)
      dispatch({ type: 'LOAD_MESSAGES', payload: { conversationId, messages: existingMessages } })
    } catch (err) {
      setError(err.message)
      dispatch({ type: 'SET_ERROR', payload: { conversationId, error: err.message } })
    } finally {
      setLoading(false)
    }
  }, [dispatch])

  return {
    messages,
    isConversationActive: state.conversations[state.activeConversationId]?.isActive || false,
    loading,
    error,
    addMessage,
    clearMessages,
    startConversation,
    stopConversation,
    loadConversationHistory,
    setActiveConversation,
    activeConversationId: state.activeConversationId
  }
}
