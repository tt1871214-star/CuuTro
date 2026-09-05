import React, { useState } from 'react';
import { AlertOctagon, MapPin, Upload, X, Loader2, ShieldAlert } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const SOSModal = ({ isOpen, onClose, onSuccess, initialCoords = null }) => {
  const { user } = useAuth();
  const [reliefType, setReliefType] = useState('CỨU NGƯỜI MẮC KẸT');
  const [urgency, setUrgency] = useState('NGUY KỊCH');
  const [description, setDescription] = useState('');
  const [latitude, setLatitude] = useState(initialCoords?.latitude || 21.0285);
  const [longitude, setLongitude] = useState(initialCoords?.longitude || 105.8542);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const handleGetCurrentGPS = () => {
    if (!navigator.geolocation) {
      setErrorMsg('Trình duyệt của bạn không hỗ trợ Geolocation API.');
      return;
    }
    setGpsLoading(true);
    setErrorMsg('');
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLatitude(Number(pos.coords.latitude.toFixed(6)));
        setLongitude(Number(pos.coords.longitude.toFixed(6)));
        setGpsLoading(false);
      },
      (err) => {
        setErrorMsg('Không thể tự động lấy tọa độ GPS. Vui lòng cho phép quyền truy cập vị trí hoặc chọn điểm trên bản đồ.');
        setGpsLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg('');

    try {
      let uploadedUrl = null;
      if (imageFile) {
        const formData = new FormData();
        formData.append('file', imageFile);
        const uploadRes = await api.post('/api/rescue-requests/upload-proof', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        if (uploadRes.data && uploadRes.data.url) {
          uploadedUrl = uploadRes.data.url;
        }
      }

      const res = await api.post('/api/rescue-requests', {
        relief_type: reliefType,
        personal_urgency: urgency,
        description: description || 'Yêu cầu cứu trợ khẩn cấp',
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        image_url: uploadedUrl
      });

      if (res.data) {
        onSuccess(res.data);
        onClose();
      }
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Không thể gửi yêu cầu cứu trợ. Vui lòng thử lại.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-slate-900 border-2 border-red-500/80 rounded-3xl p-6 shadow-[0_0_50px_rgba(239,68,68,0.3)] text-white max-h-[90vh] overflow-y-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-red-600 text-white shadow-lg animate-pulse">
              <AlertOctagon className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-black tracking-wide text-red-400">GỬI YÊU CẦU CỨU TRỢ (SOS)</h2>
              <p className="text-xs text-slate-400">Hệ thống sẽ tự động gán Zone và điều phối đội cứu hộ gần nhất</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {errorMsg && (
          <div className="mt-4 p-3 rounded-xl bg-red-500/20 border border-red-500/40 text-red-300 text-xs font-semibold">
            {errorMsg}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-5 space-y-4 text-sm">
          
          {/* Sender Info Preview */}
          <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/60 flex justify-between items-center text-xs">
            <div>
              <span className="text-slate-400">Người gửi: </span>
              <span className="font-bold text-white">{user?.full_name || 'Khách vãng lai'}</span>
            </div>
            <div>
              <span className="text-slate-400">SĐT: </span>
              <span className="font-bold text-amber-300">{user?.phone || 'Chưa cập nhật'}</span>
            </div>
          </div>

          {/* GPS Coordinates */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-red-400" /> TỌA ĐỘ GPS KHẨN CẤP
              </label>
              <button
                type="button"
                onClick={handleGetCurrentGPS}
                disabled={gpsLoading}
                className="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
              >
                {gpsLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : '🎯 Lấy vị trí thiết bị'}
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                step="any"
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                placeholder="Vĩ độ (Lat)"
                required
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-red-500"
              />
              <input
                type="number"
                step="any"
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                placeholder="Kinh độ (Lng)"
                required
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-red-500"
              />
            </div>
          </div>

          {/* Relief Type */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300">LOẠI HỖ TRỢ CẦN THIẾT</label>
            <select
              value={reliefType}
              onChange={(e) => setReliefType(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-xs text-white font-semibold focus:outline-none focus:border-red-500"
            >
              <option value="CỨU NGƯỜI MẮC KẸT">🚨 Cứu người mắc kẹt (nước dâng cao / cô lập)</option>
              <option value="Y TẾ KHẨN CẤP">🚑 Y tế khẩn cấp (chấn thương / bệnh lý nguy kịch)</option>
              <option value="LƯƠNG THỰC - NƯỚC UỐNG">🍞 Lương thực - Nước uống - Sữa trẻ em</option>
              <option value="DI TẢN KHẨN CẤP">🏃 Di tản khẩn cấp (nguy cơ sạt lở đồi núi / vỡ đê)</option>
              <option value="KHÁC">⚠️ Nhu cầu cứu trợ khác</option>
            </select>
          </div>

          {/* Personal Urgency Level */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300">MỨC ĐỘ KHẨN CẤP CỦA BẠN</label>
            <div className="grid grid-cols-4 gap-2">
              {[
                { label: 'Bình thường', val: 'BÌNH THƯỜNG', color: 'border-yellow-500 text-yellow-400' },
                { label: 'Cao', val: 'CAO', color: 'border-orange-500 text-orange-400' },
                { label: 'Khẩn cấp', val: 'KHẨN CẤP', color: 'border-rose-500 text-rose-400' },
                { label: 'Nguy kịch', val: 'NGUY KỊCH', color: 'border-red-600 text-red-500' },
              ].map(u => (
                <button
                  type="button"
                  key={u.val}
                  onClick={() => setUrgency(u.val)}
                  className={`py-2 text-[11px] font-black rounded-xl border transition ${
                    urgency === u.val ? `bg-white/10 ${u.color} ring-2 ring-red-500/50` : 'border-slate-800 text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  {u.label}
                </button>
              ))}
            </div>
          </div>

          {/* Description */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300">MÔ TẢ CHI TIẾT TÌNH TRẠNG</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ví dụ: Có 3 người (1 người già, 2 trẻ em) đang ở trên gác lửng, nước dâng tới 1.5m, sắp mất sóng điện thoại..."
              className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-red-500 placeholder:text-slate-500"
            />
          </div>

          {/* Image Upload */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300 flex items-center gap-1">
              <Upload className="w-3.5 h-3.5" /> ẢNH MINH CHỨNG HIỆN TRƯỜNG (NẾU CÓ)
            </label>
            <div className="flex items-center gap-3">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 cursor-pointer"
              />
              {imagePreview && (
                <img src={imagePreview} alt="Preview" className="w-12 h-12 object-cover rounded-lg border border-slate-700" />
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="pt-3 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="w-1/3 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 font-bold text-xs text-slate-300 transition"
            >
              HỦY BỎ
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="w-2/3 py-3 rounded-2xl bg-gradient-to-r from-red-600 via-red-500 to-rose-600 hover:from-red-500 hover:to-rose-500 font-black text-xs text-white tracking-wider shadow-lg shadow-red-600/40 flex items-center justify-center gap-2 transition"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldAlert className="w-4 h-4" />}
              {submitting ? 'ĐANG GỬI SOS...' : 'PHÁT TÍN HIỆU CỨU TRỢ NGAY'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SOSModal;
