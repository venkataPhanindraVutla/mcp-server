
import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem
} from '@mui/material';
import {
  LocalHospital,
  AccountCircle,
  Dashboard,
  Chat,
  Assessment
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
    handleClose();
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <LocalHospital sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Smart Doctor Appointment System
        </Typography>

        {user ? (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Button
              color="inherit"
              startIcon={<Dashboard />}
              onClick={() => navigate('/dashboard')}
            >
              Dashboard
            </Button>
            
            <Button
              color="inherit"
              startIcon={<Calendar />}
              onClick={() => navigate('/appointments')}
            >
              Appointments
            </Button>

            {user.role === 'patient' && (
              <Button
                color="inherit"
                onClick={() => navigate('/book-appointment')}
              >
                Book
              </Button>
            )}

            {user.role === 'doctor' && (
              <Button
                color="inherit"
                startIcon={<Assessment />}
                onClick={() => navigate('/reports')}
              >
                Reports
              </Button>
            )}

            <Button
              color="inherit"
              startIcon={<Chat />}
              onClick={() => navigate('/chat')}
            >
              AI Chat
            </Button>

            <IconButton
              size="large"
              color="inherit"
              onClick={handleMenu}
            >
              <AccountCircle />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem disabled>
                {user.name} ({user.role})
              </MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </Box>
        ) : (
          <Box>
            <Button color="inherit" onClick={() => navigate('/login')}>
              Login
            </Button>
            <Button color="inherit" onClick={() => navigate('/register')}>
              Register
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
