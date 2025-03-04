import React from 'react';
import {BrowserRouter, Routes, Route} from 'react-router-dom';
import LaptopList from './LaptopList';
import LapAdvisor from './LapAdvisor';
import HomePage from './HomePage';
import Navbar from './Navbar';
import Chatbot from './Chatbot';

function App() {
  return (
    // Arka plan rengini buradaki style ile veya CSS dosyasıyla verebilirsiniz
    <div style={styles.appContainer}>
       <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/LapAdvisor" element={<LapAdvisor />} />
        <Route path="/LaptopList" element={<LaptopList />} />
        <Route path="/" element={<HomePage />} />
        <Route path="/Chatbot" element={<Chatbot />} />
      </Routes>
    </BrowserRouter>
      
    </div>
  );
}

const styles = {
  appContainer: {
    backgroundColor: '#f0f0f0', // Arka plan rengi
    minHeight: '100vh',         // Ekranın tamamını kapsasın
    margin: 0,
    padding: 0
  }
 
};

export default App;