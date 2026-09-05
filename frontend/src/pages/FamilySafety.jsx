import React, { useState, useEffect } from 'react';
import { CheckCircle2, MapPin, Battery, Plus, RefreshCw, Phone, ShieldCheck } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import SafeStatusModal from '../components/SafeStatusModal';

const FamilySafety = () => {
  const { user } = useAuth();
  const [safeList, setSafeList] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchSafeRecords = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/safe/recent');
      if (res.data) setSafeList(res.data);
    } catch (err) {
      console.warn('Lỗi tải danh sách an toàn:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSafeRecords();
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
              <CheckCircle2 className="w-5 h-5" />
            </span>
            <h1 className="text-xl font-black text-white tracking-wide">THEO DÕI AN TOÀN & NGƯỜI THÂN</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Chức năng "Tôi an toàn" giúp xác nhận vị trí, tình trạng sức khỏe và mức pin điện thoại
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 font-extrabold text-xs text-white shadow-lg shadow-emerald-600/30 flex items-center gap-2"
        >
          <ShieldCheck className="w-4 h-4" /> BÁO "TÔI AN TOÀN" NGAY
        </button>
      </div>

      {/* List */}
      <div className="space-y-3">
        {safeList.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs bg-slate-900 rounded-2xl border border-slate-800">
            Chưa có ghi nhận an toàn nào gần đây.
          </div>
        ) : (
          safeList.map(item => (
            <div key={item.id} className="p-4 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition flex items-start justify-between gap-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                  <span className="font-extrabold text-sm text-white">{item.user_name}</span>
                  <span className="text-xs text-slate-400 font-mono">({item.user_phone})</span>
                </div>
                <p className="text-xs text-emerald-300 font-medium">"{item.status_message}"</p>
                <div className="flex items-center gap-4 text-[11px] text-slate-400 pt-1">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-rose-400" /> [{item.latitude}, {item.longitude}]
                  </span>
                  {item.battery_level && (
                    <span className="flex items-center gap-1 text-slate-300">
                      <Battery className="w-3.5 h-3.5 text-emerald-400" /> Pin: {item.battery_level}%
                    </span>
                  )}
                </div>
              </div>

              <div className="text-right text-[11px] text-slate-400">
                {new Date(item.created_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' })}
              </div>
            </div>
          ))
        )}
      </div>

      <SafeStatusModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSuccess={() => fetchSafeRecords()}
      />

    </div>
  );
};

export default FamilySafety;
