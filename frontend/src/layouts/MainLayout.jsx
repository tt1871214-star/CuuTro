import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from '../components/Header';
import EmergencyContacts from '../components/EmergencyContacts';

const MainLayout = () => {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Top Navbar */}
      <Header />
      
      {/* Page Content Body */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-6 py-6 pb-24">
        <Outlet />
      </main>

      {/* SOS Direct Dial Floating Widget (Giao diện offline - luôn cố định hiển thị) */}
      <EmergencyContacts />
    </div>
  );
};

export default MainLayout;
