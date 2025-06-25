
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Button
} from '@mui/material';
import { Calendar, Person, LocalHospital, AccessTime } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Appointments = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAppointments();
  }, [user]);

  const fetchAppointments = async () => {
    try {
      setLoading(true);
      const params = user.role === 'doctor' 
        ? `doctor_id=${user.id}` 
        : `user_id=${user.id}`;
      
      const response = await axios.get(`/appointments?${params}`);
      setAppointments(response.data);
    } catch (error) {
      console.error('Failed to fetch appointments:', error);
      setError('Failed to load appointments');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'confirmed':
      case 'scheduled':
        return 'success';
      case 'pending':
        return 'warning';
      case 'cancelled':
        return 'error';
      case 'completed':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          📅 My Appointments
        </Typography>
        {user?.role === 'patient' && (
          <Button
            variant="contained"
            onClick={() => navigate('/book-appointment')}
          >
            Book New Appointment
          </Button>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {appointments.length === 0 ? (
        <Alert severity="info">
          {user?.role === 'doctor' 
            ? 'No appointments scheduled with patients yet.'
            : 'No appointments booked yet. Book your first appointment!'
          }
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {appointments.map((appointment) => (
            <Grid item xs={12} md={6} lg={4} key={appointment.id}>
              <Card elevation={3}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Typography variant="h6" component="div">
                      {user.role === 'doctor' 
                        ? appointment.patient_name 
                        : appointment.doctor_name
                      }
                    </Typography>
                    <Chip
                      label={appointment.status || 'scheduled'}
                      color={getStatusColor(appointment.status)}
                      size="small"
                    />
                  </Box>

                  <Box display="flex" alignItems="center" mb={1}>
                    <Calendar fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">
                      {formatDate(appointment.date)}
                    </Typography>
                  </Box>

                  <Box display="flex" alignItems="center" mb={1}>
                    <AccessTime fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">
                      {appointment.time_slot}
                    </Typography>
                  </Box>

                  <Box display="flex" alignItems="center" mb={2}>
                    {user.role === 'doctor' ? (
                      <Person fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                    ) : (
                      <LocalHospital fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                    )}
                    <Typography variant="body2" color="text.secondary">
                      {user.role === 'doctor' 
                        ? `Patient: ${appointment.patient_name}`
                        : `Doctor: ${appointment.doctor_name}`
                      }
                    </Typography>
                  </Box>

                  {appointment.symptoms && (
                    <Box>
                      <Typography variant="body2" color="text.primary" fontWeight="medium">
                        Symptoms:
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {appointment.symptoms}
                      </Typography>
                    </Box>
                  )}

                  {appointment.notes && (
                    <Box mt={1}>
                      <Typography variant="body2" color="text.primary" fontWeight="medium">
                        Notes:
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {appointment.notes}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default Appointments;
