import React, { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import ChatWindow from './components/Chat/ChatWindow'
import ConversationControls from './components/Controls/ConversationControls'
import Header from './components/Layout/Header'
import PublicConversation from './components/Chat/PublicConversation'
import { useWebSocket } from './hooks/useWebSocket'
import { useConversation } from './hooks/useConversation'

function App() {
  const [currentConversationId, setCurrentConversationId] = useState('demo-conversation')
  const [isConnected, setIsConnected] = useState(false)

  const {
    messages,
    isConversationActive,
    startConversation,
    stopConversation,
    addMessage
  } = useConversation()

  const { connect, disconnect, sendMessage, connectionStatus } = useWebSocket({
    onMessage: (message) => {
      // Handle incoming WebSocket messages
      console.log('Received message:', message)
      addMessage(message)
    },
    onConnect: () => setIsConnected(true),
    onDisconnect: () => setIsConnected(false)
  })

  useEffect(() => {
    // Connect to WebSocket when component mounts
    if (currentConversationId) {
      connect(currentConversationId)
    }

    return () => {
      disconnect()
    }
  }, [currentConversationId])

  const handleStartConversation = async () => {
    const success = await startConversation(currentConversationId)
    if (success) {
      console.log('Conversation started successfully')
    }
  }

  const handleStopConversation = async () => {
    await stopConversation(currentConversationId)
    console.log('Conversation stopped')
  }

  return (
    <Routes>
      <Route path="/public/conversation/:shareToken" element={<PublicConversation />} />
      <Route path="/" element={
        <div className="h-full flex flex-col bg-gray-50">
          <Header
            isConnected={isConnected}
            connectionStatus={connectionStatus}
          />

          <div className="flex-1 flex overflow-hidden">
            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
              <ChatWindow
                messages={messages}
                conversationId={currentConversationId}
              />
            </div>

            {/* Sidebar Controls */}
            <div className="w-80 border-l border-gray-200 bg-white">
              <ConversationControls
                isConversationActive={isConversationActive}
                onStartConversation={handleStartConversation}
                onStopConversation={handleStopConversation}
                conversationId={currentConversationId}
              />
            </div>
          </div>
        </div>
      } />
    </Routes>
  )
}

export default App