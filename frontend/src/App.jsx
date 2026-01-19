// src/App.jsx
import React, { useEffect, useState } from 'react'
import ChatWindow from './components/Chat/ChatWindow'
import ConversationControls from './components/Controls/ConversationControls'
import ConversationList from './components/Controls/ConversationList'
import PersonaCards from './components/Controls/PersonaCards'
import PersonaCreator from './components/Controls/PersonaCreator'
import Header from './components/Layout/Header'
import { useWebSocket } from './hooks/useWebSocket'
import { useConversation } from './hooks/useConversation'
import { api } from './services/api'

const DEFAULT_PERSONAS = ['philosopher', 'comedian', 'scientist']

function App() {
  const [showCardView, setShowCardView] = useState(true)
  const [participants, setParticipants] = useState(DEFAULT_PERSONAS)
  const [showPersonaCreator, setShowPersonaCreator] = useState(false)

  const {
    isConversationActive,
    startConversation,
    stopConversation,
    clearMessages,
    setActiveConversation,
    loadConversationHistory,
    activeConversationId,
    loading,
    error
  } = useConversation()

  const handleSelectConversation = async (conversation) => {
    if (!conversation?.id) return
    setParticipants(conversation.ai_participants || DEFAULT_PERSONAS)
    setActiveConversation(conversation.id)
    await loadConversationHistory(conversation.id)
    setShowCardView(false)
  }

  const { connect, disconnect } = useWebSocket({ conversationId: activeConversationId })

  useEffect(() => {
    if (activeConversationId) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [activeConversationId, connect, disconnect])

  const handleStartConversation = async () => {
    const success = await startConversation(activeConversationId)
    if (success) {
      setShowCardView(false)
    }
  }

  const handleStartFromCards = async () => {
    const personaSelection = participants.length ? participants : DEFAULT_PERSONAS

    try {
      const conversationData = {
        title: `Conversation with ${personaSelection.join(', ')}`,
        ai_participants: personaSelection,
        conversation_mode: 'sequential',
        is_public: false
      }
      const newConversation = await api.createConversation(conversationData)
      const conversationId = newConversation.id || newConversation.conversation_id

      setParticipants(personaSelection)
      setActiveConversation(conversationId)

      const success = await startConversation(conversationId)
      if (success) {
        setShowCardView(false)
      }
    } catch (error) {
      console.error('Error creating conversation:', error)
      alert('Failed to start conversation: ' + error.message)
    }
  }

  const handleStopConversation = async () => {
    await stopConversation(activeConversationId)
  }

  const handleClearConversation = () => {
    if (!activeConversationId) return
    const shouldClear = window.confirm('Clear all messages in this conversation?')
    if (!shouldClear) return
    clearMessages(activeConversationId)
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <Header />

      <div className="flex-1 flex items-center justify-center">
        {showCardView ? (
          <div className="text-center w-full max-w-xl">
            <h2 className="text-2xl font-bold mb-6">Select Your AI Personas</h2>
            <PersonaCards participants={participants} setParticipants={setParticipants} />
            <button
              onClick={handleStartFromCards}
              className="mt-6 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Start Chatting
            </button>
            <div className="mt-8 text-left">
              <ConversationList
                activeConversationId={activeConversationId}
                onSelectConversation={handleSelectConversation}
              />
            </div>
          </div>
        ) : (
          <div className="flex overflow-hidden w-full h-full">
            <div className="flex-1 flex flex-col">
              <ChatWindow />
            </div>
            <div className="w-80 border-l border-gray-200 bg-white">
              <ConversationControls
                isConversationActive={isConversationActive}
                onStartConversation={handleStartConversation}
                onStopConversation={handleStopConversation}
                onClearConversation={handleClearConversation}
                conversationId={activeConversationId}
                loading={loading}
                error={error}
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
