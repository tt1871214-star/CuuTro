import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldAlert, UserPlus, Phone, Lock, User, Flame, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Register = () => {
  const { registerCitizen, registerRescueTeam } = useAuth();
  const navigate = useNavigate();

  const [roleType, setRoleType] = useState('PEOPLE'); // PEOPLE or RESCUE_TEAM
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');

  // Rescue Team specific fields
  const [teamName, setTeamName] = useState('');
  const [leaderName, setLeaderName] = useState('');
  const [contactPhone, setContactPhone] = useState('');

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    let res;
    if (roleType === 'PEOPLE') {
      res = await registerCitizen(phone, password, fullName);
    } else {
      res = await registerRescueTeam({
        phone,
        password,
        full_name: fullName,
        team_name: teamName || fullName,
        leader_name: leaderName || fullName,
        contact_phone: contactPhone || phone,
        current_lat: 21.0285,
        current_lng: 105.8542
      });
    }

    setLoading(false);
    if (res.success) {
      if (roleType === 'RESCUE_TEAM') {
        navigate('/rescue');
      } else {
        navigate('/');
      }
    } else {
      setErrorMsg(res.message);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
        
        {/* Title */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-cyan-600 to-emerald-500 flex items-center justify-center shadow-xl shadow-cyan-600/30">
            <UserPlus className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-black tracking-wide text-white">ĐĂNG KÝ TÀI KHOẢN</h2>
          <p className="text-xs text-slate-400">Tham gia mạng lưới cảnh báo và ứng cứu thiên tai cộng đồng</p>
        </div>

        {/* Role Picker (Mục 7.1: Người dân & Đội cứu hộ - Không cho phép đăng ký Admin) */}
        <div className="grid grid-cols-2 gap-2 p-1.5 bg-slate-800/80 rounded-2xl border border-slate-700 text-xs font-bold">
          <button
            type="button"
            onClick={() => setRoleType('PEOPLE')}
            className={`py-2 rounded-xl transition ${
              roleType === 'PEOPLE' ? 'bg-emerald-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            👤 Người dân (Resident)
          </button>
          <button
            type="button"
            onClick={() => setRoleType('RESCUE_TEAM')}
            className={`py-2 rounded-xl transition ${
              roleType === 'RESCUE_TEAM' ? 'bg-cyan-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            🚤 Đội cứu hộ (Rescue Team)
          </button>
        </div>

        <div className="text-[11px] text-slate-400 bg-slate-800/50 p-2.5 rounded-xl border border-slate-800">
          ℹ️ <b>Quy định phân quyền:</b> Tài khoản Quản trị viên (Admin) không mở đăng ký tự do, chỉ được cấp phát theo chỉ đạo ban chỉ huy.
        </div>

        {errorMsg && (
          <div className="p-3.5 rounded-2xl bg-red-500/20 border border-red-500/40 text-red-300 text-xs font-bold text-center">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
          <div>
            <label className="font-bold text-slate-300 flex items-center gap-1.5 mb-1">
              <User className="w-3.5 h-3.5 text-cyan-400" /> HỌ VÀ TÊN
            </label>
            <input
              type="text"
              placeholder="VD: Nguyễn Văn An"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-white font-medium focus:outline-none focus:border-cyan-500"
              required
            />
          </div>

          <div>
            <label className="font-bold text-slate-300 flex items-center gap-1.5 mb-1">
              <Phone className="w-3.5 h-3.5 text-cyan-400" /> SỐ ĐIỆN THOẠI
            </label>
            <input
              type="text"
              placeholder="VD: 0987654321"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-white font-medium focus:outline-none focus:border-cyan-500"
              required
            />
          </div>

          <div>
            <label className="font-bold text-slate-300 flex items-center gap-1.5 mb-1">
              <Lock className="w-3.5 h-3.5 text-cyan-400" /> MẬT KHẨU
            </label>
            <input
              type="password"
              placeholder="Nhập mật khẩu an toàn..."
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-white font-medium focus:outline-none focus:border-cyan-500"
              required
            />
          </div>

          {/* If Rescue Team selected */}
          {roleType === 'RESCUE_TEAM' && (
            <div className="p-4 bg-slate-800/60 rounded-2xl border border-cyan-500/30 space-y-3">
              <div className="font-bold text-cyan-400 flex items-center gap-1.5">
                <Flame className="w-4 h-4" /> THÔNG TIN ĐỘI CỨU HỘ
              </div>
              <div>
                <label className="font-bold text-slate-300">Tên đơn vị / Đội cứu trợ:</label>
                <input
                  type="text"
                  placeholder="VD: Đội Xuồng Cứu Nạn Thanh Xuân"
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-bold text-slate-300">Đội trưởng phụ trách:</label>
                  <input
                    type="text"
                    placeholder="VD: Lê Văn Bình"
                    value={leaderName}
                    onChange={(e) => setLeaderName(e.target.value)}
                    className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                    required
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-300">Hotline đội trực chiến:</label>
                  <input
                    type="text"
                    placeholder="VD: 0912345678"
                    value={contactPhone}
                    onChange={(e) => setContactPhone(e.target.value)}
                    className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                    required
                  />
                </div>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 font-black text-sm text-white shadow-lg shadow-cyan-600/30 flex items-center justify-center gap-2 transition"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <UserPlus className="w-4 h-4" />}
            {loading ? 'ĐANG TẠO TÀI KHOẢN...' : 'HOÀN TẤT ĐĂNG KÝ'}
          </button>
        </form>

        <div className="text-center text-xs text-slate-400">
          Đã có tài khoản?{' '}
          <Link to="/login" className="font-extrabold text-cyan-400 hover:underline">
            Đăng nhập ngay ↗
          </Link>
        </div>

      </div>
    </div>
  );
};

export default Register;
