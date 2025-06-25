import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Container } from '@mui/material';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Appointments from './pages/Appointments';
import BookAppointment from './pages/BookAppointment';
import DoctorReports from './pages/DoctorReports';
import ChatInterface from './pages/ChatInterface';
import { useAuth } from './contexts/AuthContext';

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return null; // Or a loading spinner component
  }

  if (!user) {
    return (
      <div className="App">
        <Navbar />
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<Navigate to="/login" />} />
          </Routes>
        </Container>
      </div>
    );
  }

  return (
    <div className="App">
      <Navbar />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" />} />
          <Route path="/register" element={!user ? <Register /> : <Navigate to="/dashboard" />} />
          <Route
            path="/dashboard"
            element={user ? <Dashboard /> : <Navigate to="/login" />}
          />
          <Route
            path="/appointments"
            element={user ? <Appointments /> : <Navigate to="/login" />}
          />
          <Route
            path="/book-appointment"
            element={user?.role === 'patient' ? <BookAppointment /> : <Navigate to="/dashboard" />}
          />
          <Route
            path="/reports"
            element={user?.role === 'doctor' ? <DoctorReports /> : <Navigate to="/dashboard" />}
          />
          <Route
            path="/chat"
            element={user ? <ChatInterface /> : <Navigate to="/login" />}
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Container>
    </div>
  );
}

export default App;
