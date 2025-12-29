// src/components/ConnectionStatus.jsx
import React from 'react'
import { Wifi, WifiOff, Loader2 } from 'lucide-react'
import { useChatStore } from '../store/ChatStore'

const statusConfig = {
  Connected: {
    icon: Wifi,
    color: 'text-green-600',
    label: 'Connected'
  },
  'Connecting...': {
    icon: Loader2,
    color: 'text-blue-600 animate-spin',
    label: 'Connecting'
  },
  Disconnected: {
    icon: WifiOff,
    color: 'text-gray-500',
    label: 'Disconnected'
  },
  Error: {
    icon: WifiOff,
    color: 'text-red-600',
    label: 'Error'
  }
}

const ConnectionStatus = () => {
  const { state } = useChatStore()
  const config = statusConfig[state.connectionStatus] || statusConfig.Disconnected
  const Icon = config.icon

  return (
    <div className="flex items-center space-x-2" role="status" aria-label="Connection status">
      <Icon className={`w-4 h-4 ${config.color}`} />
      <span className="text-sm text-gray-700">{config.label}</span>
    </div>
  )
}

export default ConnectionStatus
