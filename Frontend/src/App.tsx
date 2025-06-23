import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import Chat from './pages/Chat';
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
    <>
      <CssBaseline />
      <Router>
        <ThemeProvider theme={theme}>
          <Navigation />
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </ThemeProvider>
      </Router>
    </>
  );
}

export default App; 