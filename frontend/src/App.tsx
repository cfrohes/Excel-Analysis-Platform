import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Container, createTheme, Box } from '@mui/material';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import FileList from './components/FileList';
import FilePage from './components/FilePage';

const theme = createTheme({});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Header />
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Routes>
            <Route
              path="/"
              element={
                <Box>
                  <FileUpload />
                  <FileList />
                </Box>
              }
            />
            <Route path="/file/:id" element={<FilePage />} />
          </Routes>
        </Container>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;


