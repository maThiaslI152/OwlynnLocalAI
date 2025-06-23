import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Description as DocumentIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

interface Document {
  id: number;
  filename: string;
  file_type: string;
  content: string;
  metadata: Record<string, any>;
  created_at: string;
}

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  async function handleFileDrop(acceptedFiles: File[]) {
    setIsLoading(true);
    setError(null);

    try {
      for (const file of acceptedFiles) {
        const formData = new FormData();
        formData.append('file', file);

        await axios.post('http://localhost:8001/api/v1/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      }

      // Refresh document list
      fetchDocuments();
    } catch (error) {
      console.error('Error uploading file:', error);
      setError('Error uploading file. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  async function fetchDocuments() {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.get('http://localhost:8001/api/v1/search', {
        params: {
          query: '',
          limit: 100,
        },
      });
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError('Error fetching documents. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <Box sx={{ height: 'calc(100vh - 100px)' }}>
      <Paper
        {...getRootProps()}
        sx={{
          p: 3,
          mb: 2,
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'divider',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          },
          position: 'relative',
          minHeight: '150px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <input {...getInputProps()} />
        <Typography variant="h6" gutterBottom>
          {isDragActive
            ? 'Drop the files here...'
            : 'Drag and drop files here, or click to select files'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Supported formats: TXT, MD, PDF, DOCX, RTF, CSV, XLSX, PPTX, PY, JS, JSON, YAML, HTML, XML, CSS, Images
        </Typography>
        {isDragActive && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1,
            }}
          />
        )}
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 2, height: 'calc(100% - 200px)', overflow: 'auto' }}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <List>
            {documents.map((doc) => (
              <ListItem
                key={doc.id}
                secondaryAction={
                  <IconButton edge="end" aria-label="delete">
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  <DocumentIcon />
                </ListItemIcon>
                <ListItemText
                  primary={doc.filename}
                  secondary={`Type: ${doc.file_type} | Created: ${new Date(
                    doc.created_at
                  ).toLocaleString()}`}
                />
              </ListItem>
            ))}
          </List>
        )}
      </Paper>
    </Box>
  );
};

export default Documents; 