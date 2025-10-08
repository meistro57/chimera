import React, { useState, useEffect } from 'react'
import { Play, Square, Users, Settings, Share2, Check, Copy } from 'lucide-react'
import PersonaSelector from './PersonaSelector'
import PersonaCreator from './PersonaCreator'

const ConversationControls = ({
  isConversationActive,
  onStartConversation,
  onStopConversation,
  conversationId
}) => {
  const [personaRefreshTrigger, setPersonaRefreshTrigger] = useState(0);
  const [isShared, setIsShared] = useState(false);
  const [shareToken, setShareToken] = useState('');
  const [showShareLink, setShowShareLink] = useState(false);

  const handlePersonaCreated = (newPersona) => {
    // Trigger refresh of persona list
    setPersonaRefreshTrigger(prev => prev + 1);
    console.log('New persona created:', newPersona);
  }

  useEffect(() => {
    if (conversationId) {
      fetchConversationDetails();
    }
  }, [conversationId])

  const fetchConversationDetails = async () => {
    try {
      // Note: This assumes we have auth token in localStorage or similar
      const response = await fetch(`/api/conversations/${conversationId}`);
      if (response.ok) {
        const data = await response.json();
        setIsShared(data.is_shared || data.is_public);
        setShareToken(data.share_token || '');
      }
    } catch (error) {
      console.error('Failed to fetch conversation details:', error);
    }
  }

  const toggleShare = async () => {
    try {
      const response = await fetch(`/api/conversations/${conversationId}/share`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        setIsShared(data.is_public);
        setShareToken(data.share_token || '');
        setShowShareLink(data.is_public);
      } else {
        console.error('Failed to toggle share:', await response.text());
      }
    } catch (error) {
      console.error('Error toggling share:', error);
    }
  }

  const copyShareLink = () => {
    const link = `${window.location.origin}/public/conversation/${shareToken}`;
    navigator.clipboard.writeText(link);
    setShowShareLink(false);
  }
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          Conversation Controls
        </h2>
      </div>

      <div className="flex-1 p-4 space-y-6 overflow-y-auto">
        {/* Conversation Status */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-2">Status</h3>
          <div className="flex items-center space-x-2">
            <div
              className={`w-2 h-2 rounded-full ${
                isConversationActive ? 'bg-green-500' : 'bg-gray-400'
              }`}
            ></div>
            <span className="text-sm text-gray-600">
              {isConversationActive ? 'Active' : 'Inactive'}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Conversation ID: {conversationId}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={onStartConversation}
            disabled={isConversationActive}
            className={`w-full flex items-center justify-center px-4 py-3 rounded-lg font-medium transition-colors ${
              isConversationActive
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            <Play className="w-4 h-4 mr-2" />
            Start Conversation
          </button>

          <button
            onClick={onStopConversation}
            disabled={!isConversationActive}
            className={`w-full flex items-center justify-center px-4 py-3 rounded-lg font-medium transition-colors ${
              !isConversationActive
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-red-600 hover:bg-red-700 text-white'
            }`}
          >
            <Square className="w-4 h-4 mr-2" />
            Stop Conversation
          </button>

          <button
            onClick={toggleShare}
            className="w-full flex items-center justify-center px-4 py-3 rounded-lg font-medium transition-colors bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Share2 className="w-4 h-4 mr-2" />
            {isShared ? 'Make Private' : 'Share Conversation'}
          </button>
        </div>

        {/* Participants Section */}
        <div>
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <Users className="w-4 h-4 mr-2" />
            AI Participants
          </h3>
          <div className="mb-4">
            <PersonaCreator onPersonaCreated={handlePersonaCreated} />
          </div>
          <PersonaSelector refreshTrigger={personaRefreshTrigger} />
        </div>

        {/* Share Link */}
        {showShareLink && shareToken && (
          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-medium text-green-900 mb-2">Conversation Shared!</h4>
            <p className="text-sm text-green-800 mb-3">
              Anyone with this link can view the conversation:
            </p>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={`${window.location.origin}/public/conversation/${shareToken}`}
                readOnly
                className="flex-1 text-sm p-2 border border-gray-300 rounded"
              />
              <button
                onClick={copyShareLink}
                className="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center"
              >
                <Copy className="w-4 h-4 mr-1" />
                Copy
              </button>
            </div>
            <button
              onClick={() => setShowShareLink(false)}
              className="mt-2 text-sm text-green-700 hover:text-green-900"
            >
              × Close
            </button>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">How it works</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Click "Start" to begin the AI conversation</li>
            <li>• Watch as different AI personalities interact</li>
            <li>• Each AI has unique traits and speaking styles</li>
            <li>• Conversations are generated in real-time</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default ConversationControls