import React, { useState } from 'react'
import { Wifi, WifiOff, MessageSquare, Settings } from 'lucide-react'
import ConnectionWizard from '../ConnectionWizard'
import ProviderStatus from '../ProviderStatus'

const Header = ({ isConnected, connectionStatus }) => {
  const [showSettings, setShowSettings] = useState(false)

  return (
    <>
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <MessageSquare className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Chimera Multi-AI Chat
              </h1>
              <p className="text-sm text-gray-500">
                Watch AI personalities interact in real-time
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Settings Button */}
            <button
              onClick={() => setShowSettings(true)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors"
              title="Configure AI Providers"
            >
              <Settings className="w-5 h-5" />
            </button>

            {/* Provider Status */}
            <ProviderStatus />
          </div>
        </div>
      </header>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">AI Provider Configuration</h2>
                <button
                  onClick={() => setShowSettings(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
              <ConnectionWizard onClose={() => setShowSettings(false)} />
              <div className="flex justify-end mt-6">
                <button
                  onClick={() => setShowSettings(false)}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default Header