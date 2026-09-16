import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import './i18n';
import { VerificationProvider } from './context/VerificationContext';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <VerificationProvider>
      <App />
    </VerificationProvider>
  </React.StrictMode>,
);
