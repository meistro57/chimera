// src/components/Chat/ChatStoreProvider.test.jsx
import React from 'react'
import { beforeEach, describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChatStoreProvider, { useChatStore } from '../../store/ChatStore'
import ConnectionStatus from '../ConnectionStatus'
import ChatWindow from './ChatWindow'

const conversationId = 'conversation-test'

const StoreHarness = () => {
  const { dispatch, state } = useChatStore()

  return (
    <div>
      <ConnectionStatus />
      <ChatWindow />
      <div data-testid="last-error">{state.lastError || ''}</div>
      <button
        data-testid="connect"
        onClick={() => dispatch({ type: 'CONNECTION_STATUS_CHANGED', payload: { status: 'Connected' } })}
      >
        Connect
      </button>
      <button
        data-testid="disconnect"
        onClick={() => dispatch({ type: 'CONNECTION_STATUS_CHANGED', payload: { status: 'Disconnected' } })}
      >
        Disconnect
      </button>
      <button
        data-testid="add-message"
        onClick={() => {
          dispatch({ type: 'SET_ACTIVE_CONVERSATION', payload: { conversationId } })
          dispatch({
            type: 'MESSAGE_RECEIVED',
            payload: {
              conversationId,
              message: {
                id: 'm-1',
                type: 'message',
                sender_type: 'system',
                content: 'Hello from the reducer',
                timestamp: Date.now() / 1000
              }
            }
          })
        }}
      >
        Add message
      </button>
      <button
        data-testid="trigger-error"
        onClick={() => dispatch({ type: 'SET_ERROR', payload: { conversationId, error: 'WebSocket down' } })}
      >
        Trigger error
      </button>
    </div>
  )
}

const renderHarness = () => render(
  <ChatStoreProvider>
    <StoreHarness />
  </ChatStoreProvider>
)

describe('Chat store provider integration', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  it('updates connection status in the UI when dispatched', async () => {
    const user = userEvent.setup()
    renderHarness()

    expect(screen.getByText('Disconnected')).toBeInTheDocument()

    await user.click(screen.getByTestId('connect'))
    expect(screen.getByText('Connected')).toBeInTheDocument()

    await user.click(screen.getByTestId('disconnect'))
    expect(screen.getByText('Disconnected')).toBeInTheDocument()
  })

  it('renders newly received messages for the active conversation', async () => {
    const user = userEvent.setup()
    renderHarness()

    await user.click(screen.getByTestId('add-message'))
    expect(screen.getByText('Hello from the reducer')).toBeInTheDocument()
  })

  it('captures error states from the reducer', async () => {
    const user = userEvent.setup()
    renderHarness()

    await user.click(screen.getByTestId('trigger-error'))
    expect(screen.getByTestId('last-error')).toHaveTextContent('WebSocket down')
  })
})
