
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Grid,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const BookAppointment = () => {
  const { user } = useAuth();
  const [doctors, setDoctors] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [selectedDate, setSelectedDate] = useState(null);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [checkingAvailability, setCheckingAvailability] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    fetchDoctors();
  }, []);

  useEffect(() => {
    if (selectedDoctor && selectedDate) {
      checkAvailability();
    } else {
      setAvailableSlots([]);
      setSelectedSlot('');
    }
  }, [selectedDoctor, selectedDate]);

  const fetchDoctors = async () => {
    try {
      const response = await axios.get('/doctors');
      setDoctors(response.data);
    } catch (error) {
      console.error('Failed to fetch doctors:', error);
      setMessage({ type: 'error', text: 'Failed to load doctors' });
    }
  };

  const checkAvailability = async () => {
    if (!selectedDoctor || !selectedDate) return;

    setCheckingAvailability(true);
    try {
      const dateStr = selectedDate.toISOString().split('T')[0];
      const response = await axios.get(`/availability/${encodeURIComponent(selectedDoctor)}/${dateStr}`);
      setAvailableSlots(response.data.available_slots || []);
      setSelectedSlot('');
    } catch (error) {
      console.error('Failed to check availability:', error);
      setMessage({ type: 'error', text: 'Failed to check availability' });
      setAvailableSlots([]);
    } finally {
      setCheckingAvailability(false);
    }
  };

  const handleBookAppointment = async () => {
    if (!selectedDoctor || !selectedDate || !selectedSlot) {
      setMessage({ type: 'error', text: 'Please fill in all required fields' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const dateStr = selectedDate.toISOString().split('T')[0];
      const response = await axios.post(`/appointments/book?user_id=${user.id}`, {
        doctor_name: selectedDoctor,
        date: dateStr,
        time_slot: selectedSlot,
        symptoms: symptoms
      });

      setMessage({ type: 'success', text: response.data.message });
      
      // Reset form
      setSelectedDoctor('');
      setSelectedDate(null);
      setSelectedSlot('');
      setSymptoms('');
      setAvailableSlots([]);
      
    } catch (error) {
      console.error('Failed to book appointment:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to book appointment' 
      });
    } finally {
      setLoading(false);
    }
  };

  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        📅 Book Appointment
      </Typography>

      {message.text && (
        <Alert severity={message.type} sx={{ mb: 3 }}>
          {message.text}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Appointment Details
            </Typography>

            <FormControl fullWidth margin="normal">
              <InputLabel>Select Doctor</InputLabel>
              <Select
                value={selectedDoctor}
                label="Select Doctor"
                onChange={(e) => setSelectedDoctor(e.target.value)}
              >
                {doctors.map((doctor) => (
                  <MenuItem key={doctor.id} value={doctor.name}>
                    {doctor.name} - {doctor.specialization}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Select Date"
                value={selectedDate}
                onChange={setSelectedDate}
                minDate={tomorrow}
                maxDate={new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)}
                renderInput={(params) => 
                  <TextField {...params} fullWidth margin="normal" />
                }
              />
            </LocalizationProvider>

            <TextField
              fullWidth
              margin="normal"
              label="Symptoms (Optional)"
              multiline
              rows={3}
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="Describe your symptoms or reason for visit..."
            />

            <Button
              fullWidth
              variant="contained"
              size="large"
              sx={{ mt: 3 }}
              onClick={handleBookAppointment}
              disabled={loading || !selectedDoctor || !selectedDate || !selectedSlot}
            >
              {loading ? 'Booking...' : 'Book Appointment'}
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Available Time Slots
              </Typography>
              
              {!selectedDoctor || !selectedDate ? (
                <Typography variant="body2" color="text.secondary">
                  Please select a doctor and date to see available slots
                </Typography>
              ) : checkingAvailability ? (
                <Typography variant="body2" color="text.secondary">
                  Checking availability...
                </Typography>
              ) : availableSlots.length === 0 ? (
                <Alert severity="warning">
                  No available slots for this date. Please try another date.
                </Alert>
              ) : (
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Click to select a time slot:
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {availableSlots.map((slot) => (
                      <Chip
                        key={slot}
                        label={slot}
                        onClick={() => setSelectedSlot(slot)}
                        color={selectedSlot === slot ? 'primary' : 'default'}
                        variant={selectedSlot === slot ? 'filled' : 'outlined'}
                        clickable
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>

          {selectedDoctor && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Selected Doctor
                </Typography>
                <Typography variant="body1">
                  {selectedDoctor}
                </Typography>
                {doctors.find(d => d.name === selectedDoctor) && (
                  <Typography variant="body2" color="text.secondary">
                    {doctors.find(d => d.name === selectedDoctor).specialization}
                  </Typography>
                )}
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default BookAppointment;
