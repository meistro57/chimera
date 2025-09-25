import React from 'react'
import { Brain, Smile, Microscope, User } from 'lucide-react'

const PersonaAvatar = ({ persona, avatarColor, size = 'md' }) => {
  const getIcon = (persona) => {
    switch (persona) {
      case 'philosopher':
        return Brain
      case 'comedian':
        return Smile
      case 'scientist':
        return Microscope
      default:
        return User
    }
  }

  const getSizeClass = (size) => {
    switch (size) {
      case 'sm':
        return 'w-6 h-6'
      case 'lg':
        return 'w-12 h-12'
      default:
        return 'w-8 h-8'
    }
  }

  const getIconSize = (size) => {
    switch (size) {
      case 'sm':
        return 'w-3 h-3'
      case 'lg':
        return 'w-6 h-6'
      default:
        return 'w-4 h-4'
    }
  }

  const Icon = getIcon(persona)
  const bgColor = avatarColor || '#6366f1'

  return (
    <div
      className={`${getSizeClass(size)} rounded-full flex items-center justify-center text-white font-medium`}
      style={{ backgroundColor: bgColor }}
    >
      <Icon className={getIconSize(size)} />
    </div>
  )
}

export default PersonaAvatar