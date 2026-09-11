import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldAlert, Radio, Users, Phone, LogOut, LogIn, UserPlus, Flame, Map, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import EmergencyDrawer from './EmergencyDrawer';

const Navbar = () => {
  const { user, logout, isCitizen, isRescueTeam, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [showHotline, setShowHotline] = useState(false);

  const handleLogout = () => {
    const wasAdmin = user?.role === 'ADMIN' || window.location.pathname.startsWith('/admin');
    logout();
    if (wasAdmin) {
      navigate('/admin/login');
    } else {
      navigate('/login');
    }
  };

  const getRoleBadge = () => {
    if (!user) return null;
    if (user.role === 'ADMIN') {
      return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-purple-500/20 text-purple-300 border border-purple-500/40">QUẢN TRỊ VIÊN</span>;
    }
    if (user.role === 'RESCUE_TEAM') {
      return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">ĐỘI CỨU HỘ</span>;
    }
    return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">NGƯỜI DÂN</span>;
  };

  return (
    <>
      <nav className="sticky top-0 z-40 w-full bg-slate-950/90 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-red-600 via-rose-500 to-amber-500 flex items-center justify-center shadow-lg shadow-red-600/30 group-hover:scale-105 transition-transform">
              <ShieldAlert className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="font-black text-lg tracking-wider text-white flex items-center gap-1.5">
                CỨU TRỢ
                <span className="inline-block w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
              </div>
              <p className="text-[10px] text-slate-400 font-medium hidden sm:block">Community Disaster Alert & Relief Platform</p>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-1 text-xs font-bold text-slate-300">
            <Link to="/" className="px-3 py-2 rounded-xl hover:bg-slate-800 hover:text-white transition flex items-center gap-1.5">
              <Map className="w-4 h-4 text-amber-400" /> Bản đồ cứu trợ
            </Link>
            <Link to="/community" className="px-3 py-2 rounded-xl hover:bg-slate-800 hover:text-white transition flex items-center gap-1.5">
              <Radio className="w-4 h-4 text-cyan-400" /> Bảng tin thực địa
            </Link>
            <Link to="/safety" className="px-3 py-2 rounded-xl hover:bg-slate-800 hover:text-white transition flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Báo an toàn
            </Link>
            
            {/* Rescue Team Portal Link */}
            {(isRescueTeam || isAdmin) && (
              <Link to="/rescue" className="px-3 py-2 rounded-xl bg-cyan-950/60 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-900/60 transition flex items-center gap-1.5 font-extrabold">
                <Flame className="w-4 h-4 text-cyan-400 animate-pulse" /> Điều phối Cứu hộ
              </Link>
            )}

            {/* Admin Dashboard Link */}
            {isAdmin && (
              <Link to="/admin" className="px-3 py-2 rounded-xl bg-purple-950/60 text-purple-300 border border-purple-500/40 hover:bg-purple-900/60 transition flex items-center gap-1.5 font-extrabold">
                <Users className="w-4 h-4 text-purple-400" /> Trung tâm Quản trị
              </Link>
            )}
          </div>

          {/* Right Action Bar */}
          <div className="flex items-center gap-3">
            {/* Hotline button */}
            <button
              onClick={() => setShowHotline(true)}
              className="px-3 py-1.5 rounded-xl bg-red-600/20 border border-red-500/40 hover:bg-red-600/30 text-red-400 font-extrabold text-xs flex items-center gap-1.5 transition"
            >
              <Phone className="w-3.5 h-3.5 animate-bounce" />
              <span className="hidden sm:inline">Đường dây nóng</span> 112
            </button>

            {/* User status */}
            {user ? (
              <div className="flex items-center gap-2.5 pl-2 border-l border-slate-800">
                <div className="hidden sm:flex flex-col items-end">
                  <span className="text-xs font-bold text-white leading-tight">{user.full_name}</span>
                  {getRoleBadge()}
                </div>
                <button
                  onClick={handleLogout}
                  title="Đăng xuất"
                  className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-rose-400 transition"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-white transition flex items-center gap-1"
                >
                  <LogIn className="w-3.5 h-3.5" /> Đăng nhập
                </Link>
                <Link
                  to="/register"
                  className="hidden sm:flex px-3 py-1.5 rounded-xl bg-red-600 hover:bg-red-500 text-xs font-extrabold text-white transition items-center gap-1 shadow-md shadow-red-600/30"
                >
                  <UserPlus className="w-3.5 h-3.5" /> Đăng ký
                </Link>
              </div>
            )}
          </div>
        </div>
      </nav>

      <EmergencyDrawer isOpen={showHotline} onClose={() => setShowHotline(false)} />
    </>
  );
};

export default Navbar;
