import { render, screen } from '@testing-library/react';
import MessageBubble from './MessageBubble';

describe('MessageBubble', () => {
  test('renders normal message', () => {
    render(
      <MessageBubble
        message={{
          sender_type: 'persona',
          sender: 'philosopher',
          content: 'Hello world',
          timestamp: 1234567890
        }}
      />
    );
    
    expect(screen.getByText('Hello world')).toBeInTheDocument();
    expect(screen.getByText('philosopher')).toBeInTheDocument();
  });

  test('renders error message', () => {
    render(
      <MessageBubble
        message={{
          type: 'error',
          content: 'Something went wrong',
          timestamp: 1234567890
        }}
      />
    );
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    // Check for error styling
  });
});

// Add tests for typing indicators, etc.