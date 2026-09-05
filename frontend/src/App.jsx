import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import CommunityBoard from './pages/CommunityBoard';
import FamilySafety from './pages/FamilySafety';
import RescueTeamPortal from './pages/RescueTeamPortal';
import AdminDashboard from './pages/AdminDashboard';
import Login from './pages/Login';
import Register from './pages/Register';

// Protected Route for Rescue Teams & Admin
const RescueRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== 'RESCUE_TEAM' && user.role !== 'ADMIN') {
    return <Navigate to="/" replace />;
  }
  return children;
};

// Protected Route for Admin only
const AdminRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== 'ADMIN') {
    return <Navigate to="/" replace />;
  }
  return children;
};

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-red-500 selection:text-white">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/community" element={<CommunityBoard />} />
          <Route path="/safety" element={<FamilySafety />} />
          <Route 
            path="/rescue" 
            element={
              <RescueRoute>
                <RescueTeamPortal />
              </RescueRoute>
            } 
          />
          <Route 
            path="/admin" 
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            } 
          />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      
      {/* Emergency Status Footer */}
      <footer className="w-full bg-slate-900 border-t border-slate-800 py-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>© 2026 CỨU TRỢ — Community Disaster Alert and Relief Platform</span>
          <span className="text-amber-400 font-bold">Hệ thống Trực ban & Cứu nạn 24/7 | Tổng đài khẩn cấp 112 / 114 / 115</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
