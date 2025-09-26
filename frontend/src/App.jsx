/**
 * Main App component for OMR Checker
 */

import React, { useState, useEffect } from 'react';
import FileUploader from './components/FileUploader';
import ResultDisplay from './components/ResultDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import { getAnswerKeys, checkServerHealth } from './api';
import { FileText, CheckCircle, AlertCircle } from 'lucide-react';

function App() {
  const [currentView, setCurrentView] = useState('upload'); // 'upload' or 'result'
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableKeys, setAvailableKeys] = useState(['exam1']);
  const [serverStatus, setServerStatus] = useState('checking');

  useEffect(() => {
    // Check server health and load answer keys on component mount
    const initializeApp = async () => {
      try {
        await checkServerHealth();
        setServerStatus('connected');
        
        const keys = await getAnswerKeys();
        setAvailableKeys(keys);
      } catch (error) {
        setServerStatus('disconnected');
        console.error('Failed to connect to server:', error);
      }
    };

    initializeApp();
  }, []);

  const handleUploadSuccess = (resultData) => {
    setResult(resultData);
    setCurrentView('result');
    setLoading(false);
    setError(null);
  };

  const handleUploadError = (errorMessage) => {
    setError(errorMessage);
    setLoading(false);
  };

  const handleStartOver = () => {
    setCurrentView('upload');
    setResult(null);
    setError(null);
  };

  const renderServerStatus = () => {
    if (serverStatus === 'checking') {
      return (
        <div className="flex items-center text-yellow-600 text-sm">
          <AlertCircle className="w-4 h-4 mr-1" />
          Checking server connection...
        </div>
      );
    } else if (serverStatus === 'connected') {
      return (
        <div className="flex items-center text-green-600 text-sm">
          <CheckCircle className="w-4 h-4 mr-1" />
          Server connected
        </div>
      );
    } else {
      return (
        <div className="flex items-center text-red-600 text-sm">
          <AlertCircle className="w-4 h-4 mr-1" />
          Server disconnected - Please start the backend
        </div>
      );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-primary-600 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">OMR Checker</h1>
                <p className="text-sm text-gray-600">Automated OMR sheet evaluation system</p>
              </div>
            </div>
            {renderServerStatus()}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading && <LoadingSpinner />}
        
        {error && (
          <ErrorMessage 
            message={error} 
            onDismiss={() => setError(null)} 
          />
        )}

        {currentView === 'upload' && !loading && (
          <FileUploader
            onUploadStart={() => setLoading(true)}
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
            availableKeys={availableKeys}
            serverConnected={serverStatus === 'connected'}
          />
        )}

        {currentView === 'result' && result && !loading && (
          <ResultDisplay
            result={result}
            onStartOver={handleStartOver}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-600 text-sm">
            <p>OMR Checker - Automated bubble sheet evaluation using OpenCV</p>
            <p className="mt-1">Upload your scanned OMR sheets for instant evaluation</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
