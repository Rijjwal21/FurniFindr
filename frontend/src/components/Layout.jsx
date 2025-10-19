import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import ChatIcon from '@mui/icons-material/Chat';
import AnalyticsIcon from '@mui/icons-material/Analytics';

const Layout = ({ children }) => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            FurniFindr
          </Typography>
          <Button
            component={RouterLink}
            to="/"
            color="inherit"
            startIcon={<ChatIcon />}
          >
            Chat
          </Button>
          <Button
            component={RouterLink}
            to="/analytics"
            color="inherit"
            startIcon={<AnalyticsIcon />}
          >
            Analytics
          </Button>
        </Toolbar>
      </AppBar>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        {children}
      </Box>
    </Box>
  );
};

export default Layout;