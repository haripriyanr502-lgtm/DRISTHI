import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';

// Pages
import { HomePage } from './pages/HomePage';
import { AuthPage } from './pages/AuthPage';
import { PatientProfilePage } from './pages/PatientProfilePage';
import { ECGUploadPage } from './pages/ECGUploadPage';
import { ECGAnalysisPage } from './pages/ECGAnalysisPage';
import { AnalysisResultsPage } from './pages/AnalysisResultsPage';
import { PatientDashboardPage } from './pages/PatientDashboardPage';
import { CaregiverDashboardPage } from './pages/CaregiverDashboardPage';
import { PatientHistoryPage } from './pages/PatientHistoryPage';
import { SettingsPage } from './pages/SettingsPage';

function AppContent() {
  const [activePage, setActivePage] = useState('home');
  const [activeAnalysisId, setActiveAnalysisId] = useState(null);
  const { isPublic, isPatient, isCaregiver } = useAuth();

  const handleAnalysisComplete = (analysisId) => {
    setActiveAnalysisId(analysisId);
    setActivePage('results');
  };

  const renderPage = () => {
    switch (activePage) {
      case 'home':
        return (
          <HomePage
            setActivePage={setActivePage}
            onStartSampleDemo={() => setActivePage('upload')}
          />
        );
      case 'auth':
        return <AuthPage setActivePage={setActivePage} />;
      case 'profile':
        return <PatientProfilePage />;
      case 'upload':
        return (
          <ECGUploadPage
            setActivePage={setActivePage}
            onAnalysisComplete={handleAnalysisComplete}
          />
        );
      case 'analysis':
        return (
          <ECGAnalysisPage
            setActivePage={setActivePage}
            latestAnalysisId={activeAnalysisId}
          />
        );
      case 'results':
        return (
          <AnalysisResultsPage
            setActivePage={setActivePage}
            analysisId={activeAnalysisId}
            onBackToUpload={() => setActivePage('upload')}
          />
        );
      case 'patient-dashboard':
        return (
          <PatientDashboardPage
            setActivePage={setActivePage}
            onSelectAnalysis={(id) => setActiveAnalysisId(id)}
          />
        );
      case 'caregiver-dashboard':
        return <CaregiverDashboardPage setActivePage={setActivePage} />;
      case 'history':
        return (
          <PatientHistoryPage
            setActivePage={setActivePage}
            onSelectAnalysis={(id) => setActiveAnalysisId(id)}
          />
        );
      case 'settings':
        return <SettingsPage setActivePage={setActivePage} />;
      default:
        return <HomePage setActivePage={setActivePage} />;
    }
  };

  return (
    <div className="app-container">
      <Navbar activePage={activePage} setActivePage={setActivePage} />
      <main className="main-content">
        {renderPage()}
      </main>
      <Footer />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
