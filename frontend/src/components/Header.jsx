import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Bell, CloudSun, LogOut, ShieldAlert, User as UserIcon, Menu, X } from 'lucide-react';
import api from '../services/api';

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [showNotifDropdown, setShowNotifDropdown] = useState(false);
  const [weatherAlert, setWeatherAlert] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const isAdmin = user?.role === 'ADMIN' || user?.role_name === 'Admin';
  const isRescueTeam = user?.role === 'RESCUE_TEAM' || user?.role_name === 'RescueTeam';

  useEffect(() => {
    if (!user) return;
    
    const fetchNotifications = async () => {
      try {
        const res = await api.get('/api/notifications?unread_only=true');
        if (res.data && res.data.success) {
          setNotifications(res.data.notifications);
        }
      } catch (err) {
        console.error("Lỗi tải thông báo:", err);
      }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 15000); // refresh every 15s
    return () => clearInterval(interval);
  }, [user]);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const res = await api.get('/api/disasters/weather');
        if (res.data && res.data.success) {
          setWeatherAlert(res.data);
        }
      } catch (err) {
        console.error("Lỗi tải thời tiết:", err);
      }
    };
    fetchWeather();
    const interval = setInterval(fetchWeather, 300000); // 5 mins
    return () => clearInterval(interval);
  }, []);

  const handleMarkAllRead = async () => {
    try {
      await api.post('/api/notifications/read-all');
      setNotifications([]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = () => {
    const wasAdmin = isAdmin || window.location.pathname.startsWith('/admin');
    logout();
    navigate(wasAdmin ? '/admin/login' : '/login');
  };

  return (
    <header className="sticky top-0 z-[999] w-full bg-[#0B0F19]/85 backdrop-blur-md border-b border-white/10 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* LOGO */}
        <Link to={isAdmin ? "/admin" : "/"} className="flex items-center gap-2">
          <span className="text-2xl">🚨</span>
          <span className="text-xl font-extrabold tracking-wider text-gradient font-outfit">CỨU TRỢ</span>
        </Link>

        {/* WEATHER SUMMARY */}
        {weatherAlert && (
          <div className="hidden md:flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-white/5 border border-white/5">
            <CloudSun className="w-4 h-4 text-amber-400" />
            <span className="text-xs text-gray-300">
              {weatherAlert.weather.location_name}: <strong className="text-white">{weatherAlert.weather.temp}°C</strong>, {weatherAlert.weather.description}
            </span>
            {weatherAlert.disaster_warning?.level_color === 'ORANGE' && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30 animate-pulse">
                Theo dõi
              </span>
            )}
            {weatherAlert.disaster_warning?.level_color === 'RED' && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/30 animate-pulse">
                Cảnh báo ĐỎ
              </span>
            )}
          </div>
        )}

        {/* NAVIGATION & USER ACTIONS */}
        <div className="hidden md:flex items-center gap-6">
          <nav className="flex items-center gap-5">
            {!isAdmin && (
              <>
                <Link to="/" className="text-sm font-semibold text-gray-300 hover:text-white transition-colors">Bản đồ cứu trợ</Link>
                <Link to="/community" className="text-sm font-semibold text-gray-300 hover:text-white transition-colors">Bảng tin</Link>
                {user && (
                  <Link to="/safe" className="text-sm font-semibold text-gray-300 hover:text-white transition-colors">Người thân & An toàn</Link>
                )}
              </>
            )}
            {(isRescueTeam || isAdmin) && (
              <Link to="/rescue" className="text-sm font-semibold text-cyan-400 hover:text-cyan-300 transition-colors">Điều phối Cứu hộ</Link>
            )}
            {isAdmin && (
              <Link to="/admin" className="text-sm font-semibold text-red-400 hover:text-red-300 transition-colors">Trung tâm Quản trị</Link>
            )}
          </nav>

          {user ? (
            <div className="flex items-center gap-4 border-l border-white/10 pl-4">
              
              {/* NOTIFICATION FEED */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifDropdown(!showNotifDropdown)}
                  className="relative p-2 rounded-full hover:bg-white/5 transition-colors"
                >
                  <Bell className="w-5 h-5 text-gray-300 hover:text-white" />
                  {notifications.length > 0 && (
                    <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-black text-white">
                      {notifications.length}
                    </span>
                  )}
                </button>

                {showNotifDropdown && (
                  <div className="absolute right-0 mt-3 w-80 glass-card rounded-xl p-4 shadow-2xl z-50 animate-fade-in">
                    <div className="flex justify-between items-center mb-3">
                      <span className="font-bold text-sm text-white">Thông báo mới nhất</span>
                      {notifications.length > 0 && (
                        <button
                          onClick={handleMarkAllRead}
                          className="text-xs text-blue-400 hover:underline"
                        >
                          Đọc tất cả
                        </button>
                      )}
                    </div>
                    <div className="max-h-64 overflow-y-auto flex flex-col gap-2">
                      {notifications.length === 0 ? (
                        <p className="text-xs text-gray-400 text-center py-4">Không có thông báo mới.</p>
                      ) : (
                        notifications.map((n) => (
                          <div key={n.id} className="p-2.5 rounded bg-white/5 border border-white/5 text-xs">
                            <h4 className="font-bold text-white mb-0.5">{n.title}</h4>
                            <p className="text-gray-300 leading-relaxed">{n.content}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* USER PROFILE INFO */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
                  <UserIcon className="w-4 h-4 text-blue-400" />
                </div>
                <div className="flex flex-col text-left">
                  <span className="text-xs font-bold text-white leading-tight">{user.full_name}</span>
                  <span className="text-[10px] text-gray-400 leading-none">{user.role_name}</span>
                </div>
              </div>

              {/* LOGOUT */}
              <button
                onClick={handleLogout}
                className="p-2 rounded-full hover:bg-red-500/10 text-gray-400 hover:text-red-400 transition-colors"
                title="Đăng xuất"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="text-sm font-semibold text-gray-300 hover:text-white px-4 py-2"
              >
                Đăng nhập
              </Link>
              <Link
                to="/register"
                className="text-sm font-bold bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg hover:shadow-blue-500/20 transition-all"
              >
                Đăng ký
              </Link>
            </div>
          )}
        </div>

        {/* MOBILE MENU TOGGLE */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded hover:bg-white/5"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>

      </div>

      {/* MOBILE NAV MENU */}
      {mobileMenuOpen && (
        <div className="md:hidden mt-4 pt-4 border-t border-white/10 flex flex-col gap-3">
          {!isAdmin && (
            <>
              <Link to="/" onClick={() => setMobileMenuOpen(false)} className="text-sm text-gray-300 hover:text-white py-2 block">Bản đồ cứu trợ</Link>
              <Link to="/community" onClick={() => setMobileMenuOpen(false)} className="text-sm text-gray-300 hover:text-white py-2 block">Bảng tin</Link>
            </>
          )}
          {user ? (
            <>
              {!isAdmin && (
                <Link to="/safe" onClick={() => setMobileMenuOpen(false)} className="text-sm text-gray-300 hover:text-white py-2 block">Người thân & An toàn</Link>
              )}
              {(isRescueTeam || isAdmin) && (
                <Link to="/rescue" onClick={() => setMobileMenuOpen(false)} className="text-sm text-cyan-400 py-2 block">Điều phối Cứu hộ</Link>
              )}
              {isAdmin && (
                <Link to="/admin" onClick={() => setMobileMenuOpen(false)} className="text-sm text-red-400 py-2 block">Trung tâm Quản trị</Link>
              )}
              <div className="pt-2 border-t border-white/5 flex items-center justify-between">
                <span className="text-xs font-bold text-white">{user.full_name}</span>
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleLogout();
                  }}
                  className="flex items-center gap-1.5 text-xs text-red-400 font-bold"
                >
                  <LogOut className="w-4 h-4" /> Đăng xuất
                </button>
              </div>
            </>
          ) : (
            <div className="flex flex-col gap-2 pt-2 border-t border-white/5">
              <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="text-sm text-gray-300 py-2 block text-center">Đăng nhập</Link>
              <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="text-sm bg-blue-600 text-white text-center font-bold py-2 rounded">Đăng ký</Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
};

export default Header;
