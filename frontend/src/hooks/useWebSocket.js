import { useState, useRef, useCallback } from 'react'

export const useWebSocket = ({ onMessage, onConnect, onDisconnect }) => {
  const [connectionStatus, setConnectionStatus] = useState('Disconnected')
  const ws = useRef(null)

  const connect = useCallback((conversationId) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      return
    }

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/conversation/${conversationId}`

    setConnectionStatus('Connecting...')

    try {
      ws.current = new WebSocket(wsUrl)

      ws.current.onopen = () => {
        setConnectionStatus('Connected')
        onConnect?.()
      }

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          onMessage?.(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.current.onclose = (event) => {
        setConnectionStatus('Disconnected')
        onDisconnect?.()

        // Attempt to reconnect after 3 seconds if not intentionally closed
        if (!event.wasClean) {
          setTimeout(() => {
            if (ws.current?.readyState !== WebSocket.OPEN) {
              connect(conversationId)
            }
          }, 3000)
        }
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionStatus('Error')
      }

    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
      setConnectionStatus('Error')
    }
  }, [onMessage, onConnect, onDisconnect])

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close()
      ws.current = null
    }
    setConnectionStatus('Disconnected')
  }, [])

  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
    }
  }, [])

  const ping = useCallback(() => {
    sendMessage({ type: 'ping' })
  }, [sendMessage])

  return {
    connect,
    disconnect,
    sendMessage,
    ping,
    connectionStatus,
    isConnected: connectionStatus === 'Connected'
  }
}