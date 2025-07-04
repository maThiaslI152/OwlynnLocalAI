import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { CopilotKit } from '@copilotkit/react-core';
import Chat from './pages/Chat';
import Documents from './pages/Documents';
import Settings from './pages/Settings';
import Navigation from './components/Navigation';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
  },
});

function App() {
  return (
    <CopilotKit
      runtimeUrl="http://localhost:8001/api/v1"
    >
      <CssBaseline />
      <Router>
        <ThemeProvider theme={theme}>
          <Navigation />
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </ThemeProvider>
      </Router>
    </CopilotKit>
  );
}

export default App; 