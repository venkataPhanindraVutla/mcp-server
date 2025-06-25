
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Alert,
  Paper,
  CircularProgress
} from '@mui/material';
import { Assessment, Refresh } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const DoctorReports = () => {
  const { user } = useAuth();
  const [reportType, setReportType] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const reportTypes = [
    { value: 'daily_summary', label: 'Daily Summary' },
    { value: 'yesterday_visits', label: 'Yesterday\'s Visits' },
    { value: 'today_tomorrow_appointments', label: 'Today & Tomorrow Appointments' },
    { value: 'symptom_analysis', label: 'Symptom Analysis' }
  ];

  const generateReport = async () => {
    if (!reportType) {
      setError('Please select a report type');
      return;
    }

    setLoading(true);
    setError('');
    setReportData(null);

    try {
      const response = await axios.post(`/doctors/${user.id}/reports`, {
        report_type: reportType,
        date_filter: dateFilter || undefined
      });

      setReportData(response.data.report);
    } catch (error) {
      console.error('Failed to generate report:', error);
      setError(error.response?.data?.detail || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickReport = async (type, filter = '') => {
    setReportType(type);
    setDateFilter(filter);
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`/doctors/${user.id}/reports`, {
        report_type: type,
        date_filter: filter || undefined
      });

      setReportData(response.data.report);
    } catch (error) {
      console.error('Failed to generate report:', error);
      setError(error.response?.data?.detail || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        📊 Doctor Reports
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Generate Custom Report
              </Typography>

              <FormControl fullWidth margin="normal">
                <InputLabel>Report Type</InputLabel>
                <Select
                  value={reportType}
                  label="Report Type"
                  onChange={(e) => setReportType(e.target.value)}
                >
                  {reportTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                fullWidth
                margin="normal"
                label={reportType === 'symptom_analysis' ? 'Symptom to analyze' : 'Date filter (optional)'}
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                placeholder={
                  reportType === 'symptom_analysis' 
                    ? 'e.g., fever, headache, cough'
                    : 'YYYY-MM-DD'
                }
                type={reportType === 'symptom_analysis' ? 'text' : 'date'}
              />

              <Button
                fullWidth
                variant="contained"
                startIcon={<Assessment />}
                onClick={generateReport}
                disabled={loading || !reportType}
                sx={{ mt: 2 }}
              >
                {loading ? 'Generating...' : 'Generate Report'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Reports
              </Typography>
              
              <Button
                fullWidth
                variant="outlined"
                onClick={() => handleQuickReport('today_tomorrow_appointments')}
                disabled={loading}
                sx={{ mb: 2 }}
              >
                Today & Tomorrow Schedule
              </Button>
              
              <Button
                fullWidth
                variant="outlined"
                onClick={() => handleQuickReport('yesterday_visits')}
                disabled={loading}
                sx={{ mb: 2 }}
              >
                Yesterday's Patients
              </Button>
              
              <Button
                fullWidth
                variant="outlined"
                onClick={() => handleQuickReport('daily_summary', new Date().toISOString().split('T')[0])}
                disabled={loading}
                sx={{ mb: 2 }}
              >
                Today's Summary
              </Button>

              <Button
                fullWidth
                variant="outlined"
                onClick={() => handleQuickReport('symptom_analysis', 'fever')}
                disabled={loading}
              >
                Fever Cases Analysis
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {loading && (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
              <CircularProgress />
              <Typography variant="body1" sx={{ ml: 2 }}>
                Generating report...
              </Typography>
            </Box>
          )}

          {reportData && !loading && (
            <Paper elevation={3} sx={{ p: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Report Results
                </Typography>
                <Button
                  startIcon={<Refresh />}
                  onClick={generateReport}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Box>

              {typeof reportData === 'string' ? (
                <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                  {reportData}
                </Typography>
              ) : (
                <Box>
                  {reportData.summary && (
                    <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-line' }}>
                      {reportData.summary}
                    </Typography>
                  )}
                  
                  {reportData.details && Array.isArray(reportData.details) && (
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Details:
                      </Typography>
                      {reportData.details.map((detail, index) => (
                        <Card key={index} sx={{ mb: 1 }}>
                          <CardContent sx={{ py: 1 }}>
                            <Typography variant="body2">
                              {typeof detail === 'string' ? detail : JSON.stringify(detail)}
                            </Typography>
                          </CardContent>
                        </Card>
                      ))}
                    </Box>
                  )}

                  {reportData.statistics && (
                    <Box mt={2}>
                      <Typography variant="h6" gutterBottom>
                        Statistics:
                      </Typography>
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                        {JSON.stringify(reportData.statistics, null, 2)}
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default DoctorReports;
