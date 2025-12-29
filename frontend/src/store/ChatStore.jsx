// src/store/ChatStore.jsx
import React, { createContext, useContext, useEffect, useMemo, useReducer, useRef } from 'react'

const STORAGE_KEY = 'chimera.chatStore'
const STORAGE_VERSION = 1
const MAX_MESSAGES_PER_CONVERSATION = 200

export const initialState = {
  version: STORAGE_VERSION,
  activeConversationId: null,
  connectionStatus: 'Disconnected',
  conversations: {},
  pendingUserMessages: [],
  lastError: null
}

const hydrateState = () => {
  if (typeof window === 'undefined') {
    return initialState
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return initialState

    const parsed = JSON.parse(raw)
    if (parsed.version !== STORAGE_VERSION) {
      window.localStorage.removeItem(STORAGE_KEY)
      return initialState
    }

    return {
      ...initialState,
      ...parsed,
      conversations: parsed.conversations || {},
      pendingUserMessages: parsed.pendingUserMessages || []
    }
  } catch (error) {
    console.error('Failed to hydrate chat store:', error)
    return initialState
  }
}

const persistState = (state) => {
  if (typeof window === 'undefined') return
  try {
    const snapshot = JSON.stringify({
      ...state,
      version: STORAGE_VERSION
    })
    window.localStorage.setItem(STORAGE_KEY, snapshot)
  } catch (error) {
    console.error('Failed to persist chat store:', error)
  }
}

const ensureConversation = (state, conversationId) => {
  if (!conversationId) return state
  if (state.conversations[conversationId]) return state

  return {
    ...state,
    conversations: {
      ...state.conversations,
      [conversationId]: {
        messages: [],
        isActive: false,
        error: null
      }
    }
  }
}

const upsertMessage = (messages, incoming) => {
  if (!incoming) return messages

  const withoutTyping = incoming.type === 'message'
    ? messages.filter(message => message.type !== 'typing')
    : messages

  const withoutExistingTyping = incoming.type === 'typing'
    ? messages.filter(message => message.type !== 'typing')
    : withoutTyping

  const updated = [...withoutExistingTyping, incoming]
  if (updated.length > MAX_MESSAGES_PER_CONVERSATION) {
    return updated.slice(updated.length - MAX_MESSAGES_PER_CONVERSATION)
  }
  return updated
}

export const chatReducer = (state, action) => {
  switch (action.type) {
    case 'SET_ACTIVE_CONVERSATION': {
      const { conversationId } = action.payload
      const nextState = ensureConversation(state, conversationId)
      return {
        ...nextState,
        activeConversationId: conversationId
      }
    }

    case 'CONNECTION_STATUS_CHANGED': {
      const { status, error } = action.payload
      return {
        ...state,
        connectionStatus: status,
        lastError: error ?? state.lastError
      }
    }

    case 'START_CONVERSATION': {
      const { conversationId } = action.payload
      const nextState = ensureConversation(state, conversationId)
      return {
        ...nextState,
        activeConversationId: conversationId,
        conversations: {
          ...nextState.conversations,
          [conversationId]: {
            ...nextState.conversations[conversationId],
            isActive: true,
            error: null
          }
        }
      }
    }

    case 'STOP_CONVERSATION': {
      const { conversationId } = action.payload
      const conversation = state.conversations[conversationId]
      if (!conversation) return state
      return {
        ...state,
        conversations: {
          ...state.conversations,
          [conversationId]: {
            ...conversation,
            isActive: false
          }
        }
      }
    }

    case 'LOAD_MESSAGES': {
      const { conversationId, messages } = action.payload
      const nextState = ensureConversation(state, conversationId)
      return {
        ...nextState,
        conversations: {
          ...nextState.conversations,
          [conversationId]: {
            ...nextState.conversations[conversationId],
            messages: messages.slice(-MAX_MESSAGES_PER_CONVERSATION)
          }
        }
      }
    }

    case 'MESSAGE_RECEIVED': {
      const { conversationId, message } = action.payload
      const nextState = ensureConversation(state, conversationId)
      const conversation = nextState.conversations[conversationId]
      const updatedMessages = upsertMessage(conversation.messages, message)

      return {
        ...nextState,
        conversations: {
          ...nextState.conversations,
          [conversationId]: {
            ...conversation,
            messages: updatedMessages
          }
        }
      }
    }

    case 'SET_ERROR': {
      const { conversationId, error } = action.payload
      const nextState = ensureConversation(state, conversationId)
      const conversation = nextState.conversations[conversationId]
      return {
        ...nextState,
        conversations: {
          ...nextState.conversations,
          [conversationId]: {
            ...conversation,
            error
          }
        },
        lastError: error
      }
    }

    case 'QUEUE_PENDING_USER_MESSAGE': {
      const { id, message } = action.payload
      const existing = state.pendingUserMessages.find(entry => entry.id === id)
      if (existing) return state
      return {
        ...state,
        pendingUserMessages: [...state.pendingUserMessages, { id, message }]
      }
    }

    case 'RESOLVE_PENDING_USER_MESSAGE': {
      const { id } = action.payload
      return {
        ...state,
        pendingUserMessages: state.pendingUserMessages.filter(entry => entry.id !== id)
      }
    }

    case 'FLUSH_PENDING_USER_MESSAGES':
      return {
        ...state,
        pendingUserMessages: []
      }

    default:
      return state
  }
}

const ChatStoreContext = createContext(null)

export const ChatStoreProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState, hydrateState)
  const stateRef = useRef(state)

  useEffect(() => {
    stateRef.current = state
    persistState(state)
  }, [state])

  const value = useMemo(() => ({ state, dispatch, stateRef }), [state])
  return (
    <ChatStoreContext.Provider value={value}>
      {children}
    </ChatStoreContext.Provider>
  )
}

export const useChatStore = () => {
  const context = useContext(ChatStoreContext)
  if (!context) {
    throw new Error('useChatStore must be used within a ChatStoreProvider')
  }
  return context
}

export const selectMessages = (state, conversationId) => (
  state.conversations[conversationId]?.messages || []
)

export default ChatStoreProvider
