import React, { useState, useEffect } from 'react'
import ChatWindow from './components/Chat/ChatWindow'
import ConversationControls from './components/Controls/ConversationControls'
import PersonaCards from './components/Controls/PersonaCards'
import PersonaCreator from './components/Controls/PersonaCreator'
import Header from './components/Layout/Header'
import { useWebSocket } from './hooks/useWebSocket'
import { useConversation } from './hooks/useConversation'
import { api } from './services/api'

function App() {
  const [currentConversationId, setCurrentConversationId] = useState(null)
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
    // Only connect to WebSocket when component mounts if there's an actual conversation
    if (currentConversationId && currentConversationId !== 'demo-conversation') {
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
      setShowCardView(false)  // Move to chat view after starting conversation
    }
  }

  const handleStartFromCards = async () => {
    try {
      // Create a new conversation first
      const conversationData = {}
      const newConversation = await api.createConversation(conversationData)
      const conversationId = newConversation.id || newConversation.conversation_id
      
      // Set the current conversation ID
      setCurrentConversationId(conversationId)
      
      // Start the conversation
      const success = await startConversation(conversationId)
      if (success) {
        console.log('Conversation started successfully from card view')
        setShowCardView(false)
      }
    } catch (error) {
      console.error('Error creating conversation:', error)
      alert('Failed to start conversation: ' + error.message)
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
              onClick={handleStartFromCards}
              className="mt-6 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
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