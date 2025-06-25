
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  Avatar,
  CircularProgress
} from '@mui/material';
import { Send, SmartToy, Person } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const ChatInterface = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      content: `Hello ${user?.name}! I'm your AI assistant. I can help you with:
      
      ${user?.role === 'patient' 
        ? '• Booking appointments\n• Checking doctor availability\n• Managing your appointments'
        : '• Generating reports\n• Checking patient statistics\n• Managing your schedule'
      }
      
      Try saying something like: "${user?.role === 'patient' 
        ? 'I want to book an appointment with Dr. Smith tomorrow at 2 PM'
        : 'How many patients do I have today?'
      }"`
    }
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || loading) return;

    const userMessage = currentMessage.trim();
    setCurrentMessage('');
    
    // Add user message to chat
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(`/chat?user_id=${user.id}&message=${encodeURIComponent(userMessage)}`);
      
      // Add bot response to chat
      setMessages(prev => [...prev, { 
        type: 'bot', 
        content: response.data.response || response.data.fallback_response || 'I received your message but couldn\'t process it properly.' 
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        type: 'bot', 
        content: 'Sorry, I\'m having trouble connecting to the AI service. Please try again later.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const suggestedMessages = user?.role === 'patient' 
    ? [
        'Check Dr. Smith\'s availability for tomorrow',
        'Book an appointment with Dr. Johnson',
        'Show my upcoming appointments',
        'Cancel my appointment with Dr. Brown'
      ]
    : [
        'How many patients do I have today?',
        'Show me yesterday\'s patient count',
        'Generate my weekly report',
        'How many patients had fever symptoms?'
      ];

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        🤖 AI Assistant
      </Typography>
      
      <Paper elevation={3} sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
        {/* Messages Area */}
        <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto' }}>
          {messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                mb: 2
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  maxWidth: '70%',
                  flexDirection: message.type === 'user' ? 'row-reverse' : 'row'
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: message.type === 'user' ? 'primary.main' : 'secondary.main',
                    mx: 1
                  }}
                >
                  {message.type === 'user' ? <Person /> : <SmartToy />}
                </Avatar>
                <Card
                  sx={{
                    bgcolor: message.type === 'user' ? 'primary.light' : 'grey.100',
                    color: message.type === 'user' ? 'white' : 'text.primary'
                  }}
                >
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                      {message.content}
                    </Typography>
                  </CardContent>
                </Card>
              </Box>
            </Box>
          ))}
          
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'secondary.main', mx: 1 }}>
                  <SmartToy />
                </Avatar>
                <Card sx={{ bgcolor: 'grey.100' }}>
                  <CardContent sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    <Typography variant="body1">Thinking...</Typography>
                  </CardContent>
                </Card>
              </Box>
            </Box>
          )}
          
          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        <Box sx={{ p: 2, borderTop: '1px solid #e0e0e0' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              placeholder="Type your message here..."
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
            />
            <Button
              variant="contained"
              endIcon={<Send />}
              onClick={handleSendMessage}
              disabled={loading || !currentMessage.trim()}
              sx={{ minWidth: 'auto' }}
            >
              Send
            </Button>
          </Box>
          
          {/* Suggested Messages */}
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="textSecondary" gutterBottom>
              Try these suggestions:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
              {suggestedMessages.map((suggestion, index) => (
                <Button
                  key={index}
                  size="small"
                  variant="outlined"
                  onClick={() => setCurrentMessage(suggestion)}
                  disabled={loading}
                  sx={{ fontSize: '0.75rem' }}
                >
                  {suggestion}
                </Button>
              ))}
            </Box>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatInterface;
