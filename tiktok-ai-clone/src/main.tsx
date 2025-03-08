import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './styles/global.css';

// Add error handling for HMR WebSocket connection failures
if (import.meta.hot) {
  import.meta.hot.on('vite:beforeUpdate', () => {
    console.log('HMR update detected');
  });

  // Handle potential WebSocket connection errors
  const originalWebSocket = window.WebSocket;
  window.WebSocket = function(url, protocols) {
    const ws = new originalWebSocket(url, protocols);
    
    ws.addEventListener('error', (error) => {
      console.warn('WebSocket connection error:', error);
      // The app will continue to work, just without HMR
      console.log('HMR WebSocket connection failed. App will continue to work, but you may need to manually refresh to see changes.');
    });
    
    return ws;
  } as any;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
); 