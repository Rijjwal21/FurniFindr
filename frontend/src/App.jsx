import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Container } from '@mui/material';
import Layout from './components/Layout';
import RecommendationChat from './components/RecommendationChat';
import Analytics from './components/Analytics';

// A simple theme for our app
const theme = createTheme({
  palette: {
    primary: {
      main: '#386641', // A nice green
    },
    secondary: {
      main: '#A7C957', // A lighter green
    },
    background: {
      default: '#F5F5F5', // Light grey background
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Layout>
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Routes>
              <Route path="/" element={<RecommendationChat />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </Container>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;