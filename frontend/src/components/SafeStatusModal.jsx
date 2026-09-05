import React, { useState } from 'react';
import { CheckCircle2, MapPin, X, Loader2, Battery } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const SafeStatusModal = ({ isOpen, onClose, onSuccess }) => {
  const { user } = useAuth();
  const [message, setMessage] = useState('Tôi an toàn, hiện đang ở điểm trú ẩn cao ráo!');
  const [latitude, setLatitude] = useState(21.0285);
  const [longitude, setLongitude] = useState(105.8542);
  const [battery, setBattery] = useState(85);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setLatitude(Number(pos.coords.latitude.toFixed(6)));
        setLongitude(Number(pos.coords.longitude.toFixed(6)));
      });
    }
    if (navigator.getBattery) {
      navigator.getBattery().then(b => {
        setBattery(Math.round(b.level * 100));
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    try {
      const res = await api.post('/api/safe/check-in', {
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        status_message: message,
        battery_level: parseInt(battery)
      });
      if (res.data) {
        onSuccess(res.data);
        onClose();
      }
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Không thể lưu trạng thái an toàn.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
      <div className="relative w-full max-w-md bg-slate-900 border-2 border-emerald-500/80 rounded-3xl p-6 shadow-[0_0_50px_rgba(16,185,129,0.2)] text-white">
        
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-base text-emerald-400">XÁC NHẬN "TÔI AN TOÀN"</h3>
              <p className="text-xs text-slate-400">Thông báo trạng thái an toàn để gia đình yên tâm</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {errorMsg && (
          <div className="mt-3 p-2.5 rounded-xl bg-red-500/20 text-red-300 text-xs font-semibold">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 space-y-3.5 text-xs">
          <div>
            <label className="font-bold text-slate-300">TIN NHẮN TRẤN AN</label>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-white font-medium focus:outline-none focus:border-emerald-500"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="font-bold text-slate-300 flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-emerald-400" /> Tọa độ Lat/Lng
              </label>
              <button
                type="button"
                onClick={handleGetLocation}
                className="mt-1 text-[11px] text-cyan-400 hover:underline block font-semibold"
              >
                🎯 Cập nhật vị trí hiện tại
              </button>
            </div>
            <div>
              <label className="font-bold text-slate-300 flex items-center gap-1">
                <Battery className="w-3.5 h-3.5 text-emerald-400" /> Dung lượng pin (%):
              </label>
              <input
                type="number"
                value={battery}
                onChange={(e) => setBattery(e.target.value)}
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5 text-white text-center"
              />
            </div>
          </div>

          <div className="pt-2 flex gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="w-1/3 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 font-bold text-slate-300"
            >
              ĐÓNG
            </button>
            <button
              type="submit"
              disabled={loading}
              className="w-2/3 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-black text-white tracking-wide shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
              {loading ? 'ĐANG LƯU...' : 'GỬI BÁO CÁO AN TOÀN'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SafeStatusModal;
