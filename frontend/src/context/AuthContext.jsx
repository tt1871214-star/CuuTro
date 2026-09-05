import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  const checkUser = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const res = await api.get('/api/auth/me');
      if (res.data) {
        setUser(res.data);
        localStorage.setItem('user', JSON.stringify(res.data));
      }
    } catch (err) {
      console.warn("Phiên đăng nhập hết hạn hoặc lỗi xác thực:", err);
      logout();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkUser();
  }, []);

  const login = async (phone, password) => {
    try {
      const res = await api.post('/api/auth/login', { phone, password });
      if (res.data && res.data.access_token) {
        const { access_token, user: userData } = res.data;
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        return { success: true, user: userData };
      }
      return { success: false, message: 'Đăng nhập không thành công.' };
    } catch (err) {
      return {
        success: false,
        message: err.response?.data?.detail || 'Số điện thoại hoặc mật khẩu không chính xác.'
      };
    }
  };

  const registerCitizen = async (phone, password, fullName) => {
    try {
      const res = await api.post('/api/auth/register/citizen', {
        phone,
        password,
        full_name: fullName
      });
      if (res.data && res.data.access_token) {
        const { access_token, user: userData } = res.data;
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        return { success: true, user: userData };
      }
      return { success: false, message: 'Đăng ký không thành công.' };
    } catch (err) {
      return {
        success: false,
        message: err.response?.data?.detail || 'Có lỗi xảy ra khi đăng ký.'
      };
    }
  };

  const registerRescueTeam = async (formData) => {
    try {
      const res = await api.post('/api/auth/register/rescue-team', formData);
      if (res.data && res.data.access_token) {
        const { access_token, user: userData } = res.data;
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        return { success: true, user: userData };
      }
      return { success: false, message: 'Đăng ký không thành công.' };
    } catch (err) {
      return {
        success: false,
        message: err.response?.data?.detail || 'Có lỗi xảy ra khi đăng ký đội cứu hộ.'
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const isCitizen = user?.role === 'PEOPLE';
  const isRescueTeam = user?.role === 'RESCUE_TEAM';
  const isAdmin = user?.role === 'ADMIN';

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      registerCitizen,
      registerRescueTeam,
      logout,
      checkUser,
      isCitizen,
      isRescueTeam,
      isAdmin
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
