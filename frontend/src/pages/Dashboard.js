
import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Alert
} from '@mui/material';
import {
  Person,
  LocalHospital,
  Assessment,
  Chat
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    appointments: 0,
    doctors: 0,
    patients: 0
  });
  const [recentAppointments, setRecentAppointments] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      // Fetch appointments
      const appointmentsResponse = await axios.get(
        user.role === 'doctor' 
          ? `/appointments?doctor_id=${user.id}`
          : `/appointments?user_id=${user.id}`
      );
      setRecentAppointments(appointmentsResponse.data.slice(0, 5));
      setStats(prev => ({ ...prev, appointments: appointmentsResponse.data.length }));

      // Fetch doctors count
      const doctorsResponse = await axios.get('/doctors');
      setStats(prev => ({ ...prev, doctors: doctorsResponse.data.length }));

      // Fetch users count (patients)
      const usersResponse = await axios.get('/users');
      const patients = usersResponse.data.filter(u => u.role === 'patient');
      setStats(prev => ({ ...prev, patients: patients.length }));
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  const DashboardCard = ({ title, value, icon, color, onClick }) => (
    <Card sx={{ cursor: onClick ? 'pointer' : 'default' }} onClick={onClick}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color: color }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome, {user?.name}! 👋
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Role: {user?.role === 'doctor' ? '👨‍⚕️ Doctor' : '🏥 Patient'}
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4}>
          <DashboardCard
            title="My Appointments"
            value={stats.appointments}
            icon={<Calendar fontSize="large" />}
            color="primary.main"
            onClick={() => navigate('/appointments')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <DashboardCard
            title="Available Doctors"
            value={stats.doctors}
            icon={<LocalHospital fontSize="large" />}
            color="secondary.main"
          />
        </Grid>
        
        {user?.role === 'doctor' && (
          <Grid item xs={12} sm={6} md={4}>
            <DashboardCard
              title="Total Patients"
              value={stats.patients}
              icon={<Person fontSize="large" />}
              color="success.main"
            />
          </Grid>
        )}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Appointments
              </Typography>
              {recentAppointments.length > 0 ? (
                recentAppointments.map((apt, index) => (
                  <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Typography variant="subtitle1">
                      {user.role === 'doctor' ? `Patient: ${apt.patient_name}` : `Doctor: ${apt.doctor_name}`}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {apt.date} at {apt.time_slot} - Status: {apt.status}
                    </Typography>
                    {apt.symptoms && (
                      <Typography variant="body2">
                        Symptoms: {apt.symptoms}
                      </Typography>
                    )}
                  </Box>
                ))
              ) : (
                <Alert severity="info">No appointments found</Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              
              {user?.role === 'patient' ? (
                <>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<Calendar />}
                    sx={{ mb: 2 }}
                    onClick={() => navigate('/book-appointment')}
                  >
                    Book Appointment
                  </Button>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Chat />}
                    onClick={() => navigate('/chat')}
                  >
                    AI Assistant
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<Assessment />}
                    sx={{ mb: 2 }}
                    onClick={() => navigate('/reports')}
                  >
                    View Reports
                  </Button>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Chat />}
                    onClick={() => navigate('/chat')}
                  >
                    AI Assistant
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
