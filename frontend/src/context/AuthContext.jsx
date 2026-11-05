import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [role, setRole] = useState('public'); // 'public', 'patient', 'caregiver'
  const [currentPatientId, setCurrentPatientId] = useState(localStorage.getItem('dristhi_active_pid') || 'PT-4082');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('dristhi_token');
      if (token) {
        api.setToken(token);
        try {
          const profile = await api.getMe();
          setUser(profile);
          setRole(profile.role);
          if (profile.patient_id) {
            setCurrentPatientId(profile.patient_id);
            localStorage.setItem('dristhi_active_pid', profile.patient_id);
          }
        } catch (err) {
          console.warn('Session expired or invalid token:', err.message);
          api.setToken(null);
          setUser(null);
          setRole('public');
        }
      } else {
        setRole('public');
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials) => {
    const resp = await api.login(credentials);
    api.setToken(resp.access_token);
    setUser(resp.user);
    setRole(resp.user.role);
    if (resp.user.patient_id) {
      setCurrentPatientId(resp.user.patient_id);
      localStorage.setItem('dristhi_active_pid', resp.user.patient_id);
    }
    return resp.user;
  };

  const register = async (userData) => {
    const resp = await api.register(userData);
    api.setToken(resp.access_token);
    setUser(resp.user);
    setRole(resp.user.role);
    if (resp.user.patient_id) {
      setCurrentPatientId(resp.user.patient_id);
      localStorage.setItem('dristhi_active_pid', resp.user.patient_id);
    }
    return resp.user;
  };

  const logout = () => {
    api.setToken(null);
    setUser(null);
    setRole('public');
    setCurrentPatientId('PT-4082');
  };

  const updateActivePatientId = (newPid) => {
    if (newPid && newPid.trim()) {
      const cleaned = newPid.trim().toUpperCase();
      setCurrentPatientId(cleaned);
      localStorage.setItem('dristhi_active_pid', cleaned);
    }
  };

  // Quick Workflow Demo Helpers for instant persona switching
  const switchDemoPersona = async (persona) => {
    try {
      if (persona === 'patient') {
        const u = await login({ email: 'rajesh.patel@example.com', password: 'patient123' });
        return { role: 'patient', page: 'patient-dashboard' };
      } else if (persona === 'caregiver') {
        const u = await login({ email: 'priya.patel@example.com', password: 'caregiver123' });
        return { role: 'caregiver', page: 'caregiver-dashboard' };
      } else {
        logout();
        return { role: 'public', page: 'home' };
      }
    } catch (err) {
      console.error('Failed to switch demo persona:', err);
      return null;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        isPublic: role === 'public',
        isPatient: role === 'patient',
        isCaregiver: role === 'caregiver',
        currentPatientId,
        updateActivePatientId,
        login,
        register,
        logout,
        switchDemoPersona,
        loading
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
