import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldAlert, LogIn, Phone, Lock, Loader2, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    const res = await login(phone, password);
    setLoading(false);

    if (res.success) {
      const role = res.user.role;
      if (role === 'ADMIN') {
        navigate('/admin');
      } else if (role === 'RESCUE_TEAM') {
        navigate('/rescue');
      } else {
        navigate('/');
      }
    } else {
      setErrorMsg(res.message);
    }
  };

  const handleQuickFill = (p, pwd) => {
    setPhone(p);
    setPassword(pwd);
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
        
        {/* Logo */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-red-600 to-amber-500 flex items-center justify-center shadow-xl shadow-red-600/30">
            <ShieldAlert className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-black tracking-wide text-white">ĐĂNG NHẬP CỨU TRỢ</h2>
          <p className="text-xs text-slate-400">Nền tảng Cảnh báo & Ứng cứu Thiên tai Cộng đồng</p>
        </div>

        {errorMsg && (
          <div className="p-3.5 rounded-2xl bg-red-500/20 border border-red-500/40 text-red-300 text-xs font-bold text-center">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="font-bold text-slate-300 flex items-center gap-1.5 mb-1">
              <Phone className="w-3.5 h-3.5 text-cyan-400" /> SỐ ĐIỆN THOẠI
            </label>
            <input
              type="text"
              placeholder="VD: 0987654321"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-3 text-sm text-white font-medium focus:outline-none focus:border-red-500"
              required
            />
          </div>

          <div>
            <label className="font-bold text-slate-300 flex items-center gap-1.5 mb-1">
              <Lock className="w-3.5 h-3.5 text-cyan-400" /> MẬT KHẨU
            </label>
            <input
              type="password"
              placeholder="Nhập mật khẩu..."
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-3 text-sm text-white font-medium focus:outline-none focus:border-red-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 font-black text-sm text-white shadow-lg shadow-red-600/30 flex items-center justify-center gap-2 transition"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <LogIn className="w-4 h-4" />}
            {loading ? 'ĐANG XÁC THỰC...' : 'ĐĂNG NHẬP VÀO HỆ THỐNG'}
          </button>
        </form>

        {/* Quick Testing Accounts */}
        <div className="pt-3 border-t border-slate-800 space-y-2 text-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block text-center">
            TÀI KHOẢN MẪU KHẢO SÁT (TESTING)
          </span>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => handleQuickFill('0987654321', 'citizen123')}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-center font-bold text-[11px] text-emerald-400 transition"
            >
              Người dân
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('0912345678', 'rescue123')}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-center font-bold text-[11px] text-cyan-400 transition"
            >
              Đội cứu hộ
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('0901234567', 'admin123')}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-center font-bold text-[11px] text-purple-400 transition"
            >
              Admin
            </button>
          </div>
        </div>

        <div className="text-center text-xs text-slate-400">
          Chưa có tài khoản?{' '}
          <Link to="/register" className="font-extrabold text-red-400 hover:underline">
            Đăng ký tài khoản mới ↗
          </Link>
        </div>

      </div>
    </div>
  );
};

export default Login;
