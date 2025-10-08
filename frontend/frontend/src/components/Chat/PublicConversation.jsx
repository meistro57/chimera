// components/Chat/PublicConversation.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const PublicConversation = () => {
  const { shareToken } = useParams();
  const [conversation, setConversation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPublicConversation = async () => {
      try {
        const response = await fetch(`/api/public/conversations/${shareToken}`);
        if (!response.ok) {
          throw new Error('Conversation not found');
        }
        const data = await response.json();
        setConversation(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPublicConversation();
  }, [shareToken]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading conversation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Conversation Not Found</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.href = '/'}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <Header title={`Public Conversation: ${conversation.title}`} />

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col">
          <div className="flex-1 p-4 overflow-y-auto">
            <div className="max-w-4xl mx-auto space-y-4">
              <div className="bg-white p-4 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-2">{conversation.title}</h2>
                <p className="text-sm text-gray-500 mb-4">
                  Shared conversation • Participants: {conversation.participants.join(', ')}
                </p>
              </div>

              {conversation.messages.map((message) => (
                <div key={message.id} className="flex space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-sm font-medium">
                      {message.sender_id[0].toUpperCase()}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-gray-900">{message.sender_id}</span>
                      {message.persona && (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          {message.persona}
                        </span>
                      )}
                      <span className="text-xs text-gray-500">
                        {new Date(message.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-gray-800 whitespace-pre-wrap">
                      {message.content}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="w-80 border-l border-gray-200 bg-white p-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-medium text-blue-900 mb-2">About This Conversation</h3>
            <p className="text-sm text-blue-800 mb-3">
              This is a public conversation shared from Chimera. AI personalities having a live discussion.
            </p>
            <p className="text-xs text-blue-700">
              Started: {new Date(conversation.created_at).toLocaleString()}
            </p>
          </div>

          <div className="mt-4 flex justify-center">
            <button
              onClick={() => window.location.href = '/'}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Try Chimera Yourself
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicConversation;