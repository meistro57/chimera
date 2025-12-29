// src/store/ChatStore.test.jsx
import { describe, expect, it } from 'vitest'
import { chatReducer, initialState } from './ChatStore'

const conversationId = 'test-convo'

describe('chatReducer', () => {
  it('handles connect and disconnect transitions', () => {
    const connected = chatReducer(initialState, {
      type: 'CONNECTION_STATUS_CHANGED',
      payload: { status: 'Connected' }
    })
    expect(connected.connectionStatus).toBe('Connected')

    const disconnected = chatReducer(connected, {
      type: 'CONNECTION_STATUS_CHANGED',
      payload: { status: 'Disconnected' }
    })
    expect(disconnected.connectionStatus).toBe('Disconnected')
  })

  it('records new messages per conversation', () => {
    const withActive = chatReducer(initialState, {
      type: 'SET_ACTIVE_CONVERSATION',
      payload: { conversationId }
    })

    const nextState = chatReducer(withActive, {
      type: 'MESSAGE_RECEIVED',
      payload: { conversationId, message: { id: '1', type: 'message', content: 'Hello' } }
    })

    expect(nextState.conversations[conversationId].messages).toHaveLength(1)
    expect(nextState.conversations[conversationId].messages[0].content).toBe('Hello')
  })

  it('replaces typing indicators when new typing events arrive', () => {
    const withTyping = chatReducer(initialState, {
      type: 'MESSAGE_RECEIVED',
      payload: { conversationId, message: { id: 'typing', type: 'typing' } }
    })

    const updated = chatReducer(withTyping, {
      type: 'MESSAGE_RECEIVED',
      payload: { conversationId, message: { id: 'typing2', type: 'typing' } }
    })

    expect(updated.conversations[conversationId].messages).toHaveLength(1)
    expect(updated.conversations[conversationId].messages[0].id).toBe('typing2')
  })

  it('persists error states per conversation', () => {
    const errored = chatReducer(initialState, {
      type: 'SET_ERROR',
      payload: { conversationId, error: 'Connection lost' }
    })

    expect(errored.conversations[conversationId].error).toBe('Connection lost')
    expect(errored.lastError).toBe('Connection lost')
  })
})
