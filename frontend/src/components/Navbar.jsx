import React, { useState } from 'react';
import { 
  Activity, 
  UploadCloud, 
  FileText, 
  User, 
  ShieldCheck, 
  History, 
  Settings, 
  LogOut, 
  LogIn, 
  Menu, 
  X,
  HeartPulse,
  Radio,
  Sparkles,
  Users
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar = ({ activePage, setActivePage }) => {
  const { user, role, isPublic, isPatient, isCaregiver, logout, currentPatientId, switchDemoPersona } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNavClick = (page) => {
    setActivePage(page);
    setMobileMenuOpen(false);
  };

  const handlePersonaSelect = async (persona) => {
    const result = await switchDemoPersona(persona);
    if (result) {
      setActivePage(result.page);
    }
  };

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      boxShadow: 'var(--shadow-sm)'
    }}>
      {/* Quick Demo Workflow Persona Bar */}
      <div style={{
        backgroundColor: '#0c2235',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        padding: '0.4rem 1.5rem',
        fontSize: '0.78rem',
        color: 'rgba(255, 255, 255, 0.85)',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '0.5rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={13} color="var(--color-teal)" />
          <span style={{ fontWeight: 600, color: 'var(--color-teal)' }}>Interactive Workflow Personas:</span>
          <span style={{ color: 'rgba(255, 255, 255, 0.65)' }}>Click to switch role & test live flow:</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <button
            onClick={() => handlePersonaSelect('patient')}
            style={personaBtnStyle(isPatient)}
            title="Switch to Rajesh Patel (Patient PT-4082)"
          >
            👤 Patient: Rajesh Patel (PT-4082)
          </button>

          <button
            onClick={() => handlePersonaSelect('caregiver')}
            style={personaBtnStyle(isCaregiver)}
            title="Switch to Priya Patel (Caretaker)"
          >
            🛡️ Caretaker: Priya Patel
          </button>

          <button
            onClick={() => handlePersonaSelect('public')}
            style={personaBtnStyle(isPublic)}
            title="Switch to Public Guest User (Anonymous Upload)"
          >
            🌐 Public Guest
          </button>
        </div>
      </div>

      {/* Main Navbar */}
      <div style={{
        backgroundColor: 'var(--color-navy)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        padding: '0.75rem 1.5rem'
      }}>
        <div style={{
          maxWidth: '1280px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          {/* Brand / Logo */}
          <div 
            onClick={() => handleNavClick('home')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.65rem',
              cursor: 'pointer',
              userSelect: 'none'
            }}
          >
            <div style={{
              backgroundColor: 'var(--color-teal)',
              width: '38px',
              height: '38px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff'
            }}>
              <HeartPulse size={22} strokeWidth={2.4} />
            </div>
            <div>
              <div style={{
                fontSize: '1.25rem',
                fontWeight: 800,
                color: '#FFFFFF',
                letterSpacing: '0.04em',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem'
              }}>
                DRISTHI
                <span style={{
                  fontSize: '0.65rem',
                  backgroundColor: 'rgba(32, 163, 158, 0.25)',
                  color: '#20A39E',
                  padding: '0.1rem 0.4rem',
                  borderRadius: '4px',
                  fontWeight: 700,
                  border: '1px solid rgba(32, 163, 158, 0.5)'
                }}>
                  RESEARCH v1.0
                </span>
              </div>
              <div style={{
                fontSize: '0.72rem',
                color: 'rgba(255, 255, 255, 0.7)',
                letterSpacing: '0.02em'
              }}>
                From ECG Signals to Timely Action
              </div>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem'
          }} className="desktop-nav">
            <button
              onClick={() => handleNavClick('home')}
              style={navItemStyle(activePage === 'home')}
            >
              Home
            </button>

            <button
              onClick={() => handleNavClick('upload')}
              style={navItemStyle(activePage === 'upload')}
            >
              <UploadCloud size={16} />
              ECG Upload
            </button>

            <button
              onClick={() => handleNavClick('analysis')}
              style={navItemStyle(activePage === 'analysis')}
            >
              <Activity size={16} />
              ECG Analysis
            </button>

            {/* Role-specific Navigation */}
            {isPatient && (
              <>
                <button
                  onClick={() => handleNavClick('patient-dashboard')}
                  style={navItemStyle(activePage === 'patient-dashboard')}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => handleNavClick('history')}
                  style={navItemStyle(activePage === 'history')}
                >
                  <History size={16} />
                  Records
                </button>
                <button
                  onClick={() => handleNavClick('profile')}
                  style={navItemStyle(activePage === 'profile')}
                >
                  <User size={16} />
                  Profile
                </button>
              </>
            )}

            {isCaregiver && (
              <button
                onClick={() => handleNavClick('caregiver-dashboard')}
                style={navItemStyle(activePage === 'caregiver-dashboard')}
              >
                <ShieldCheck size={16} />
                Caregiver Dashboard
              </button>
            )}

            <button
              onClick={() => handleNavClick('settings')}
              style={navItemStyle(activePage === 'settings')}
            >
              <Settings size={16} />
              Settings
            </button>
          </nav>

          {/* Auth / Account Action Button */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {isPublic ? (
              <button
                onClick={() => handleNavClick('auth')}
                className="btn btn-secondary"
                style={{
                  padding: '0.5rem 1rem',
                  fontSize: '0.875rem'
                }}
              >
                <LogIn size={16} />
                Sign In / Register
              </button>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <div style={{
                  textAlign: 'right',
                  display: 'none',
                  color: '#fff'
                }} className="user-indicator">
                  <div style={{ fontSize: '0.82rem', fontWeight: 600 }}>{user?.full_name || user?.email}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--color-teal)' }}>
                    {role.toUpperCase()} • ID: {currentPatientId}
                  </div>
                </div>
                <button
                  onClick={logout}
                  className="btn btn-outline"
                  style={{
                    color: '#fff',
                    borderColor: 'rgba(255, 255, 255, 0.25)',
                    padding: '0.45rem 0.85rem',
                    fontSize: '0.825rem'
                  }}
                  title="Sign Out"
                >
                  <LogOut size={15} />
                  <span className="logout-text">Sign Out</span>
                </button>
              </div>
            )}

            {/* Mobile menu toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              style={{
                background: 'transparent',
                color: '#fff',
                display: 'none',
                padding: '0.4rem'
              }}
              className="mobile-toggle"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div style={{
          backgroundColor: '#0d2235',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          padding: '1rem 1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}>
          <button onClick={() => handleNavClick('home')} style={mobileNavItemStyle(activePage === 'home')}>Home</button>
          <button onClick={() => handleNavClick('upload')} style={mobileNavItemStyle(activePage === 'upload')}>ECG Upload</button>
          <button onClick={() => handleNavClick('analysis')} style={mobileNavItemStyle(activePage === 'analysis')}>ECG Analysis</button>
          {isPatient && (
            <>
              <button onClick={() => handleNavClick('patient-dashboard')} style={mobileNavItemStyle(activePage === 'patient-dashboard')}>Patient Dashboard</button>
              <button onClick={() => handleNavClick('history')} style={mobileNavItemStyle(activePage === 'history')}>ECG Records History</button>
              <button onClick={() => handleNavClick('profile')} style={mobileNavItemStyle(activePage === 'profile')}>Patient Profile</button>
            </>
          )}
          {isCaregiver && (
            <button onClick={() => handleNavClick('caregiver-dashboard')} style={mobileNavItemStyle(activePage === 'caregiver-dashboard')}>Caregiver Dashboard</button>
          )}
          <button onClick={() => handleNavClick('settings')} style={mobileNavItemStyle(activePage === 'settings')}>Settings</button>
          {isPublic && (
            <button onClick={() => handleNavClick('auth')} style={mobileNavItemStyle(activePage === 'auth')}>Sign In / Register</button>
          )}
        </div>
      )}

      <style>{`
        @media (max-width: 900px) {
          .desktop-nav { display: none !important; }
          .mobile-toggle { display: block !important; }
          .user-indicator { display: none !important; }
          .logout-text { display: none !important; }
        }
        @media (min-width: 901px) {
          .user-indicator { display: block !important; }
        }
      `}</style>
    </header>
  );
};

const navItemStyle = (isActive) => ({
  display: 'inline-flex',
  alignItems: 'center',
  gap: '0.4rem',
  padding: '0.5rem 0.85rem',
  borderRadius: '6px',
  fontSize: '0.875rem',
  fontWeight: isActive ? 600 : 500,
  color: isActive ? '#FFFFFF' : 'rgba(255, 255, 255, 0.78)',
  backgroundColor: isActive ? 'rgba(40, 120, 181, 0.35)' : 'transparent',
  border: isActive ? '1px solid rgba(40, 120, 181, 0.5)' : '1px solid transparent'
});

const personaBtnStyle = (isActive) => ({
  padding: '0.2rem 0.55rem',
  borderRadius: '4px',
  fontSize: '0.725rem',
  fontWeight: 600,
  border: isActive ? '1px solid var(--color-teal)' : '1px solid rgba(255, 255, 255, 0.15)',
  backgroundColor: isActive ? 'rgba(32, 163, 158, 0.25)' : 'rgba(255, 255, 255, 0.05)',
  color: isActive ? '#FFFFFF' : 'rgba(255, 255, 255, 0.75)',
  cursor: 'pointer'
});

const mobileNavItemStyle = (isActive) => ({
  textAlign: 'left',
  padding: '0.65rem 0.5rem',
  color: isActive ? 'var(--color-teal)' : '#FFFFFF',
  backgroundColor: 'transparent',
  fontSize: '0.95rem',
  fontWeight: 600,
  borderBottom: '1px solid rgba(255, 255, 255, 0.05)'
});
