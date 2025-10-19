import React, { useState, useRef, useEffect } from 'react';
import {
  Box, Paper, TextField, IconButton, Typography, Grid, Card,
  CardMedia, CardContent, CircularProgress, Alert
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { fetchRecommendations } from '../services/api';

const RecommendationChat = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      type: 'text',
      content: "Welcome to FurniFindr! What are you looking for today? (e.g., 'a modern white chair' or 'a rustic bookshelf')"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom effect
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (input.trim() === '' || isLoading) return;

    const userMessage = { sender: 'user', type: 'text', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetchRecommendations(input);
      const botMessage = {
        sender: 'bot',
        type: 'recommendation',
        recommendations: response.data.recommendations
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error("Error fetching recommendations:", err);
      const errorMsg = "Sorry, I had trouble finding that. Please try another search.";
      setError(errorMsg);
      setMessages(prev => [...prev, { sender: 'bot', type: 'text', content: errorMsg }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessageContent = (msg, index) => {
    if (msg.type === 'text') {
      return (
        <Paper
          elevation={1}
          sx={{
            p: 2,
            bgcolor: msg.sender === 'user' ? 'primary.main' : 'secondary.main',
            color: msg.sender === 'user' ? 'white' : 'black',
            ml: msg.sender === 'user' ? 'auto' : 0,
            mr: msg.sender === 'user' ? 0 : 'auto',
            maxWidth: '70%',
            wordWrap: 'break-word',
          }}
        >
          <Typography variant="body1">{msg.content}</Typography>
        </Paper>
      );
    }

    if (msg.type === 'recommendation') {
      return (
        <Box sx={{ width: '100%' }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Here's what I found for you:
          </Typography>
          <Grid container spacing={2}>
            {msg.recommendations.map(item => (
              <Grid item xs={12} md={4} key={item.uniq_id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardMedia
                    component="img"
                    height="190"
                    image={item.images?.[0] || 'https://via.placeholder.com/300x200?text=No+Image'}
                    alt={item.title}
                    sx={{ objectFit: 'contain' }}
                  />
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography gutterBottom variant="h6" component="div" sx={{ fontSize: '1rem' }}>
                      {item.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Brand:</strong> {item.brand || 'N/A'}
                    </Typography>
                    <Typography variant="body1" color="primary" sx={{ fontWeight: 'bold', my: 1 }}>
                      {item.price}
                    </Typography>
                    <Typography variant="body2" color="text.primary" sx={{ fontStyle: 'italic', mt: 1, borderLeft: '3px solid', borderColor: 'secondary.main', pl: 1 }}>
                      {item.generated_description || 'A great choice for your home!'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      );
    }
    return null;
  };

  return (
    <Paper elevation={3} sx={{ height: 'calc(100vh - 150px)', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h5" align="center" sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        Recommendation Chat
      </Typography>
      
      {/* Message List */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 3 }}>
        {messages.map((msg, index) => (
          <Box key={index} sx={{ mb: 2, display: 'flex' }}>
            {renderMessageContent(msg, index)}
          </Box>
        ))}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
            <CircularProgress size={24} />
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>
      
      {/* Input Area */}
      <Box
        component="form"
        sx={{ p: 2, borderTop: 1, borderColor: 'divider', display: 'flex', alignItems: 'center' }}
        onSubmit={(e) => { e.preventDefault(); handleSend(); }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your request..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <IconButton color="primary" type="submit" disabled={isLoading}>
          <SendIcon />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default RecommendationChat;