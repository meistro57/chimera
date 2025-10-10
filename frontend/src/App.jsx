import React, { useState, useEffect } from 'react'
import ChatWindow from './components/Chat/ChatWindow'
import ConversationControls from './components/Controls/ConversationControls'
import PersonaCards from './components/Controls/PersonaCards'
import PersonaCreator from './components/Controls/PersonaCreator'
import Header from './components/Layout/Header'
import { useWebSocket } from './hooks/useWebSocket'
import { useConversation } from './hooks/useConversation'

function App() {
  const [currentConversationId, setCurrentConversationId] = useState('demo-conversation')
  const [isConnected, setIsConnected] = useState(false)
  const [showCardView, setShowCardView] = useState(true)
  const [participants, setParticipants] = useState([])
  const [showPersonaCreator, setShowPersonaCreator] = useState(false)

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
    <div className="h-full flex flex-col bg-gray-50">
      <Header
        isConnected={isConnected}
        connectionStatus={connectionStatus}
      />

      <div className="flex-1 flex items-center justify-center">
        {showCardView ? (
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-6">Select Your AI Personas</h2>
            <PersonaCards participants={participants} setParticipants={setParticipants} />
            <button
              onClick={() => setShowCardView(false)}
              className="mt-6 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              disabled={participants.length === 0}
            >
              Start Chatting
            </button>
          </div>
        ) : (
          <div className="flex overflow-hidden w-full h-full">
            <div className="flex-1 flex flex-col">
              <ChatWindow
                messages={messages}
                conversationId={currentConversationId}
              />
            </div>
            <div className="w-80 border-l border-gray-200 bg-white">
              <ConversationControls
                isConversationActive={isConversationActive}
                onStartConversation={handleStartConversation}
                onStopConversation={handleStopConversation}
                conversationId={currentConversationId}
              />
              <PersonaCards participants={participants} setParticipants={setParticipants} />
              <button
                onClick={() => setShowCardView(true)}
                className="m-4 px-4 py-2 bg-green-500 text-white rounded"
              >
                Change Personas
              </button>
            </div>
          </div>
        )}
      </div>

      {showPersonaCreator && (
        <PersonaCreator onClose={() => setShowPersonaCreator(false)} />
      )}
    </div>
  )
}

export default App