import React from 'react'
import { Wifi, WifiOff, MessageSquare } from 'lucide-react'

const Header = ({ isConnected, connectionStatus, title }) => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <MessageSquare className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-xl font-semibold text-gray-900">
              {title || 'Chimera Multi-AI Chat'}
            </h1>
            <p className="text-sm text-gray-500">
              {title ? 'Public Conversation View' : 'Watch AI personalities interact in real-time'}
            </p>
          </div>
        </div>

        {(isConnected !== undefined) && (
          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <>
                  <Wifi className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-green-600 font-medium">
                    Connected
                  </span>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 text-red-500" />
                  <span className="text-sm text-red-600 font-medium">
                    {connectionStatus || 'Disconnected'}
                  </span>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header