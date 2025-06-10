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
import { Send as SendIcon, AttachFile as AttachFileIcon } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { uploadDocument } from '../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  metadata?: Record<string, any>;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
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
  });

  async function handleFileDrop(acceptedFiles: File[]) {
    setUploadError(null);
    setIsLoading(true);

    try {
      for (const file of acceptedFiles) {
        const result = await uploadDocument(file);
        
        // Add a system message about the uploaded file
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `File "${file.name}" has been uploaded and processed successfully.`,
          metadata: result
        }]);
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
      const response = await axios.post('http://localhost:8001/api/v1/chat', {
        message: userMessage.content,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        metadata: response.data.metadata,
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
            },
            '&::after': {
              content: '"Drop files here"',
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              color: 'white',
              fontSize: '1.5rem',
              zIndex: 2,
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
                backgroundColor: message.role === 'user' ? 'primary.dark' : 'background.paper',
              }}
            >
              <Typography
                variant="body1"
                component="div"
                sx={{
                  '& pre': {
                    backgroundColor: 'background.default',
                    p: 1,
                    borderRadius: 1,
                    overflow: 'auto',
                  },
                  '& code': {
                    backgroundColor: 'background.default',
                    p: 0.5,
                    borderRadius: 0.5,
                  },
                }}
              >
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </Typography>
            </Paper>
          </Box>
        ))}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Paper>

      {uploadError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {uploadError}
        </Alert>
      )}

      <Paper
        component="form"
        onSubmit={handleSubmit}
        sx={{
          p: 2,
          display: 'flex',
          gap: 2,
          alignItems: 'center',
        }}
      >
        <TextField
          fullWidth
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
        />
        <IconButton type="submit" disabled={isLoading || !input.trim()}>
          <SendIcon />
        </IconButton>
      </Paper>
    </Box>
  );
};

export default Chat; 