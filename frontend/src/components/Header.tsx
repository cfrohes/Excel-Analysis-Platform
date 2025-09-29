import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { Analytics as AnalyticsIcon } from '@mui/icons-material';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogoClick = () => {
    navigate('/');
  };

  return (
    <AppBar position="static" elevation={2}>
      <Toolbar>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            cursor: 'pointer',
            mr: 4,
          }}
          onClick={handleLogoClick}
        >
          <AnalyticsIcon sx={{ mr: 1 }} />
          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
            Excel Analysis Platform
          </Typography>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        <Button
          color="inherit"
          onClick={() => navigate('/')}
          sx={{
            backgroundColor: location.pathname === '/' ? 'rgba(255,255,255,0.1)' : 'transparent',
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.1)',
            },
          }}
        >
          Home
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
