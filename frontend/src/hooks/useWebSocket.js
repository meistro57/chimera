// src/hooks/useWebSocket.js
import { useCallback, useEffect, useRef } from 'react'
import { useChatStore } from '../store/ChatStore'

export const useWebSocket = ({ conversationId }) => {
  const { state, dispatch, stateRef } = useChatStore()
  const ws = useRef(null)
  const pendingRef = useRef(state.pendingUserMessages)

  useEffect(() => {
    pendingRef.current = state.pendingUserMessages
  }, [state.pendingUserMessages])

  const updateStatus = useCallback((status, error) => {
    dispatch({ type: 'CONNECTION_STATUS_CHANGED', payload: { status, error } })
  }, [dispatch])

  const connect = useCallback(() => {
    if (!conversationId) return
    if (ws.current?.readyState === WebSocket.OPEN) {
      return
    }

    const backendUrl = process.env.NODE_ENV === 'development'
      ? 'ws://backend:8000'
      : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`

    const wsUrl = `${backendUrl}/ws/conversation/${conversationId}`
    updateStatus('Connecting...')

    try {
      ws.current = new WebSocket(wsUrl)

      ws.current.onopen = () => {
        updateStatus('Connected')
        pendingRef.current.forEach(entry => {
          ws.current?.send(JSON.stringify(entry.message))
          dispatch({ type: 'RESOLVE_PENDING_USER_MESSAGE', payload: { id: entry.id } })
        })
        dispatch({ type: 'FLUSH_PENDING_USER_MESSAGES' })
      }

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          const payloadConversationId = message.conversation_id || conversationId || stateRef.current.activeConversationId
          dispatch({ type: 'MESSAGE_RECEIVED', payload: { conversationId: payloadConversationId, message } })
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
          updateStatus('Error', error?.message)
        }
      }

      ws.current.onclose = (event) => {
        updateStatus('Disconnected')
        if (!event.wasClean) {
          setTimeout(() => {
            if (ws.current?.readyState !== WebSocket.OPEN) {
              connect()
            }
          }, 3000)
        }
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        updateStatus('Error', error?.message)
      }
    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
      updateStatus('Error', error?.message)
    }
  }, [conversationId, dispatch, stateRef, updateStatus])

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close()
      ws.current = null
    }
    updateStatus('Disconnected')
  }, [updateStatus])

  const sendMessage = useCallback((message) => {
    const messageId = message.id || `pending_${Date.now()}`
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
      dispatch({ type: 'RESOLVE_PENDING_USER_MESSAGE', payload: { id: messageId } })
      return
    }

    dispatch({ type: 'QUEUE_PENDING_USER_MESSAGE', payload: { id: messageId, message } })
  }, [dispatch])

  const ping = useCallback(() => {
    sendMessage({ type: 'ping' })
  }, [sendMessage])

  return {
    connect,
    disconnect,
    sendMessage,
    ping,
    connectionStatus: state.connectionStatus,
    isConnected: state.connectionStatus === 'Connected'
  }
}
