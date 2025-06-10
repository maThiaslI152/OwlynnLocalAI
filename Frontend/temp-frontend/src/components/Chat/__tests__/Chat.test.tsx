import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Chat from '../../../pages/Chat';

// Mock the API calls
jest.mock('../../../services/api', () => ({
  sendMessage: jest.fn().mockResolvedValue({
    response: 'Test response',
    session_id: 'test-session',
    metadata: {}
  })
}));

jest.mock('react-markdown', () => () => <div data-testid="react-markdown" />);

describe('Chat Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  it('renders chat interface', () => {
    render(<Chat />);
    expect(screen.getByPlaceholderText(/Type your message/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send message/i })).toBeInTheDocument();
  });

  it('sends message when form is submitted', async () => {
    render(<Chat />);
    const input = screen.getByPlaceholderText(/Type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });
  });

  it('displays loading state while waiting for response', async () => {
    render(<Chat />);
    const input = screen.getByPlaceholderText(/Type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
}); 