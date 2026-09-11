import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  Lock, 
  Phone, 
  KeyRound, 
  Loader2, 
  ArrowLeft, 
  AlertCircle, 
  ShieldAlert, 
  Terminal, 
  Server
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const AdminLogin = () => {
  const { adminLogin } = useAuth();
  const navigate = useNavigate();

  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    const res = await adminLogin(phone, password);
    setLoading(false);

    if (res.success) {
      navigate('/admin');
    } else {
      setErrorMsg(res.message);
    }
  };

  const handleQuickFillAdmin = () => {
    setPhone('0901234567');
    setPassword('admin123');
  };

  return (
    <div className="min-h-[88vh] flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[550px] h-[550px] bg-purple-600/10 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute bottom-10 right-10 w-72 h-72 bg-indigo-600/10 rounded-full blur-2xl pointer-events-none -z-10" />

      <div className="w-full max-w-md bg-slate-900/95 backdrop-blur-xl border border-purple-500/30 rounded-3xl p-8 shadow-2xl shadow-purple-950/50 space-y-6 relative">
        
        {/* Top security tag */}
        <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-purple-400 border-b border-slate-800 pb-3">
          <span className="flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5 text-purple-400" />
            SECURE ACCESS GATEWAY
          </span>
          <span className="px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20 font-mono text-[10px]">
            PORTAL: /admin/login
          </span>
        </div>

        {/* Header / Logo */}
        <div className="text-center space-y-2">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-tr from-purple-700 via-indigo-600 to-violet-500 flex items-center justify-center shadow-xl shadow-purple-600/30 ring-4 ring-purple-500/20">
            <ShieldCheck className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-2xl font-black tracking-wide text-white">
            BAN CHỈ HUY QUẢN TRỊ
          </h1>
          <p className="text-xs text-slate-400">
            Trung tâm Điều hành Ứng phó & Điều phối Thiên tai Khẩn cấp
          </p>
        </div>

        {/* Security Alert Note */}
        <div className="p-3 rounded-2xl bg-slate-950/70 border border-purple-500/20 text-slate-400 text-xs flex items-start gap-2.5">
          <Terminal className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
          <p className="leading-relaxed text-[11px]">
            Cổng này chỉ cấp quyền cho <strong className="text-purple-300">Quản trị viên (Admin)</strong>. Người dân và đội cứu hộ vui lòng dùng cổng thông thường.
          </p>
        </div>

        {errorMsg && (
          <div className="p-3.5 rounded-2xl bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs font-bold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="font-bold text-slate-300 flex items-center gap-1.5 mb-1.5">
              <Phone className="w-3.5 h-3.5 text-purple-400" /> SỐ ĐIỆN THOẠI QUẢN TRỊ
            </label>
            <input
              type="text"
              placeholder="VD: 0901234567"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-700/80 focus:border-purple-500 rounded-xl px-3.5 py-3 text-sm text-white font-medium focus:outline-none transition shadow-inner placeholder:text-slate-600"
              required
            />
          </div>

          <div>
            <label className="font-bold text-slate-300 flex items-center gap-1.5 mb-1.5">
              <Lock className="w-3.5 h-3.5 text-purple-400" /> MẬT KHẨU BẢO MẬT
            </label>
            <input
              type="password"
              placeholder="Nhập mật khẩu quản trị..."
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-700/80 focus:border-purple-500 rounded-xl px-3.5 py-3 text-sm text-white font-medium focus:outline-none transition shadow-inner placeholder:text-slate-600"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 font-black text-sm text-white shadow-lg shadow-purple-600/30 flex items-center justify-center gap-2 transition disabled:opacity-60"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <KeyRound className="w-4 h-4" />}
            {loading ? 'ĐANG XÁC THỰC QUYỀN...' : 'ĐĂNG NHẬP BAN CHỈ HUY'}
          </button>
        </form>

        {/* Quick Testing Accounts for Admin */}
        <div className="pt-3 border-t border-slate-800 space-y-2 text-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block text-center">
            TÀI KHOẢN MẪU KHẢO SÁT BAN CHỈ HUY
          </span>
          <button
            type="button"
            onClick={handleQuickFillAdmin}
            className="w-full p-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-purple-500/30 text-center font-bold text-xs text-purple-300 transition flex items-center justify-center gap-2"
          >
            <Server className="w-3.5 h-3.5 text-purple-400" />
            Ban Chỉ Huy (0901234567 / admin123)
          </button>
        </div>

        {/* Navigation back to Citizen & Rescue Login */}
        <div className="pt-2 text-center text-xs">
          <Link 
            to="/login" 
            className="inline-flex items-center gap-1.5 text-slate-400 hover:text-white transition font-medium text-[11px]"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Cổng đăng nhập Người dân & Đội cứu hộ
          </Link>
        </div>

      </div>
    </div>
  );
};

export default AdminLogin;
