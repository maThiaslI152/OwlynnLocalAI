import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

export const sendMessage = async (message: string, sessionId?: string) => {
  const response = await axios.post(`${API_BASE_URL}/chat`, {
    message,
    session_id: sessionId
  });
  return response.data;
};

export const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_BASE_URL}/documents/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return response.data;
};

export const getDocuments = async () => {
  const response = await axios.get(`${API_BASE_URL}/documents`);
  return response.data;
};

export const searchDocuments = async (query: string) => {
  const response = await axios.get(`${API_BASE_URL}/documents/search`, {
    params: { query }
  });
  return response.data;
}; 