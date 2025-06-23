import React, { ReactNode } from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Chat from '../Chat';
import axios from 'axios';
import '@testing-library/jest-dom';
import { act } from 'react';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock localStorage
const localStorageMock = (() => {
  let store: { [key: string]: string } = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

jest.mock('react-markdown', () => ({ children }: { children: ReactNode }) => <div>{children}</div>);

describe('Chat Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    localStorageMock.clear();
  });

  it('renders chat interface', () => {
    render(<Chat />);
    expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('sends message to backend and displays response', async () => {
    // Mock successful API response
    const mockResponse = {
      data: {
        session_id: 'test-session-123',
        response: 'Hello! I am the AI assistant.',
        metadata: {},
        state: 'idle',
        context: {}
      }
    };
    mockedAxios.post.mockResolvedValueOnce(mockResponse);

    render(<Chat />);
    
    // Get the input field and send button
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    // Type and send a message
    await act(async () => {
      await userEvent.type(input, 'Hello AI');
      fireEvent.click(sendButton);
    });

    // Verify API call
    expect(mockedAxios.post).toHaveBeenCalledWith(
      'http://localhost:8001/api/v1/chat',
      expect.objectContaining({
        message: 'Hello AI',
        session_id: undefined
      })
    );

    // Wait for and verify the response is displayed
    await waitFor(() => {
      expect(screen.getByText('Hello! I am the AI assistant.')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    // Mock API error
    mockedAxios.post.mockRejectedValueOnce(new Error('API Error'));

    render(<Chat />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    // Type and send a message
    await act(async () => {
      await userEvent.type(input, 'Hello AI');
      fireEvent.click(sendButton);
    });

    // Wait for and verify error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/sorry, there was an error processing your message/i)).toBeInTheDocument();
    });
  });

  it('maintains chat history in localStorage', async () => {
    const mockResponse = {
      data: {
        session_id: 'test-session-123',
        response: 'Hello! I am the AI assistant.',
        metadata: {},
        state: 'idle',
        context: {}
      }
    };
    mockedAxios.post.mockResolvedValueOnce(mockResponse);

    render(<Chat />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    // Send a message
    await act(async () => {
      await userEvent.type(input, 'Hello AI');
      fireEvent.click(sendButton);
    });

    // Find the last call to setItem for chat_messages
    const setItemCalls = localStorageMock.setItem.mock.calls.filter(call => call[0] === 'chat_messages');
    expect(setItemCalls.length).toBeGreaterThan(0);
    const storedMessages = JSON.parse(setItemCalls[setItemCalls.length - 1][1]);
    expect(storedMessages).toHaveLength(2);
    expect(storedMessages[0].role).toBe('user');
    expect(storedMessages[0].content).toBe('Hello AI');
    expect(storedMessages[1].role).toBe('assistant');
    expect(storedMessages[1].content).toBe('Hello! I am the AI assistant.');
  });

  it('clears chat history when clear button is clicked', async () => {
    render(<Chat />);
    
    const clearButton = screen.getByRole('button', { name: /clear chat history/i });
    
    await act(async () => {
      fireEvent.click(clearButton);
    });

    expect(localStorageMock.removeItem).toHaveBeenCalledWith('chat_messages');
  });
}); 