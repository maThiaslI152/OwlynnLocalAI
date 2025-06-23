import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Send as SendIcon, Delete as DeleteIcon } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { uploadDocument, sendMessage } from '../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  metadata?: Record<string, any>;
}

interface ChatState {
  current_state: string;
  context: Record<string, any>;
}

const STORAGE_KEY = 'chat_messages';

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>(() => {
    // Load messages from localStorage on initial render
    const savedMessages = localStorage.getItem(STORAGE_KEY);
    return savedMessages ? JSON.parse(savedMessages) : [];
  });
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [chatState, setChatState] = useState<ChatState>({
    current_state: 'idle',
    context: {}
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleFileDrop,
    accept: {
      'text/*': ['.txt', '.md'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/rtf': ['.rtf'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'text/x-python': ['.py'],
      'application/javascript': ['.js'],
      'application/json': ['.json'],
      'text/yaml': ['.yml', '.yaml'],
      'text/html': ['.html'],
      'application/xml': ['.xml'],
      'text/css': ['.css'],
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    },
    noClick: false,
    noKeyboard: false,
    multiple: true,
    preventDropOnDocument: true,
  });

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  async function handleFileDrop(acceptedFiles: File[]) {
    setUploadError(null);
    setIsLoading(true);

    try {
      for (const file of acceptedFiles) {
        const result = await uploadDocument(file);
        
        // Add a system message about the uploaded file
        setMessages(prev => {
          const newMessage: Message = {
            role: 'assistant',
            content: `File "${file.name}" has been uploaded and processed successfully.`,
            metadata: result
          };
          return [...prev, newMessage];
        });
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadError('Error uploading file. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendMessage(userMessage.content);
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        metadata: response.metadata,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, there was an error processing your message.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Add a function to clear chat history
  const clearChatHistory = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  return (
    <Box sx={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      <Paper
        elevation={3}
        sx={{
          flex: 1,
          mb: 2,
          p: 2,
          overflow: 'auto',
          backgroundColor: 'background.paper',
          position: 'relative',
          transition: 'all 0.2s ease-in-out',
          ...(isDragActive && {
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              zIndex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease-in-out',
            },
            '&::after': {
              content: '"Drop files here"',
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              color: 'white',
              fontSize: '1.5rem',
              fontWeight: 'bold',
              zIndex: 2,
              textShadow: '0 2px 4px rgba(0,0,0,0.3)',
              transition: 'all 0.2s ease-in-out',
            }
          })
        }}
        {...getRootProps()}
      >
        <input {...getInputProps()} />
        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            <Paper
              elevation={1}
              sx={{
                p: 2,
                maxWidth: '70%',
                backgroundColor: message.role === 'user' ? 'primary.light' : 'background.paper',
                color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
              }}
            >
              <ReactMarkdown>{message.content}</ReactMarkdown>
              {message.metadata && (
                <Typography variant="caption" color="text.secondary">
                  {JSON.stringify(message.metadata)}
                </Typography>
              )}
            </Paper>
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Paper>

      {uploadError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {uploadError}
        </Alert>
      )}

      {chatState.current_state !== 'idle' && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Current state: {chatState.current_state}
        </Alert>
      )}

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <IconButton
          color="primary"
          onClick={handleSubmit}
          disabled={isLoading || !input.trim()}
          aria-label="Send message"
        >
          {isLoading ? <CircularProgress size={24} /> : <SendIcon />}
        </IconButton>
        <IconButton
          color="secondary"
          onClick={clearChatHistory}
          title="Clear chat history"
        >
          <DeleteIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default Chat; 