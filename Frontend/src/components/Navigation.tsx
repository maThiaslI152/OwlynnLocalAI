import React from 'react';
import { Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Box, Container } from '@mui/material';

const Navigation = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Owlynn Local AI
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Chat</Link>
            <Link to="/documents" style={{ color: 'white', textDecoration: 'none' }}>Documents</Link>
            <Link to="/settings" style={{ color: 'white', textDecoration: 'none' }}>Settings</Link>
          </Box>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {/* Content will be rendered here */}
      </Container>
    </Box>
  );
};

export default Navigation; 