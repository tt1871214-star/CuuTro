import React, { useState, useEffect } from 'react';
import { AlertOctagon, CheckCircle2, Bot, ShieldAlert, Phone, Navigation, Clock, RefreshCw, Send, AlertTriangle } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useRealtime } from '../context/RealtimeContext';
import MapComponent from '../components/MapComponent';
import WeatherAlertBanner from '../components/WeatherAlertBanner';
import SOSModal from '../components/SOSModal';
import SafeStatusModal from '../components/SafeStatusModal';

const Home = () => {
  const { user } = useAuth();
  const { refreshTrigger } = useRealtime();

  // Data states
  const [zones, setZones] = useState([]);
  const [assemblyPoints, setAssemblyPoints] = useState([]);
  const [rescueTeams, setRescueTeams] = useState([]);
  const [activeRequests, setActiveRequests] = useState([]);
  const [myActiveRequest, setMyActiveRequest] = useState(null);
  const [selectedPin, setSelectedPin] = useState(null);

  // Modals & Drawers
  const [showSOSModal, setShowSOSModal] = useState(false);
  const [showSafeModal, setShowSafeModal] = useState(false);
  const [showAIChat, setShowAIChat] = useState(false);

  // AI Chat
  const [chatMessages, setChatMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      text: 'Xin chào! Tôi là Trợ lý Cứu Nạn & Sơ Cứu CỨU TRỢ. Trong tình huống khẩn cấp, bạn có thể hỏi tôi về cách sơ cứu đuối nước, garo cầm máu, gãy xương hoặc cách ứng phó ngập lụt, sạt lở.'
    }
  ]);
  const [aiQuery, setAiQuery] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState('');

  const loadData = async () => {
    try {
      // 1. Fetch Zones
      const zonesRes = await api.get('/api/zones');
      if (zonesRes.data) setZones(zonesRes.data);

      // 2. Fetch Assembly Points & Shelters
      const pointsRes = await api.get('/api/assembly-points');
      if (pointsRes.data) setAssemblyPoints(pointsRes.data);

      // 3. Fetch My Active Request if logged in
      if (user) {
        const myRes = await api.get('/api/rescue-requests/my-active-status');
        if (myRes.data) setMyActiveRequest(myRes.data);
        else setMyActiveRequest(null);
      }
    } catch (err) {
      console.warn("Lỗi tải dữ liệu cứu trợ:", err);
    }
  };

  useEffect(() => {
    loadData();
  }, [user, refreshTrigger]);

  // Handle map click to pick SOS location
  const handleMapClick = (coords) => {
    setSelectedPin(coords);
  };

  const handleCancelMyRequest = async () => {
    if (!myActiveRequest) return;
    if (!window.confirm("Bạn xác nhận đã an toàn và muốn hủy yêu cầu cứu hộ này?")) return;

    try {
      await api.put(`/api/rescue-requests/${myActiveRequest.id}/citizen-cancel`);
      setMyActiveRequest(null);
      setFeedbackMsg('Đã hủy yêu cầu cứu trợ thành công. Rất mừng vì bạn đã an toàn!');
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Có lỗi xảy ra khi hủy yêu cầu.');
    }
  };

  const handleSendAIChat = async (e) => {
    e.preventDefault();
    if (!aiQuery.trim() || aiLoading) return;

    const q = aiQuery.trim();
    setAiQuery('');
    setChatMessages(prev => [...prev, { id: Date.now(), sender: 'user', text: q }]);
    setAiLoading(true);

    try {
      const res = await api.post('/api/community/ai-assistant', { query: q });
      if (res.data && res.data.response) {
        setChatMessages(prev => [...prev, {
          id: Date.now() + 1,
          sender: 'ai',
          text: res.data.response
        }]);
      }
    } catch (err) {
      setChatMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'ai',
        text: 'Không thể kết nối với máy chủ AI. Vui lòng kiểm tra lại mạng.'
      }]);
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* 1. Real-time Open-Meteo Weather Hazard Banner */}
      <WeatherAlertBanner />

      {feedbackMsg && (
        <div className="p-3.5 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-bold flex items-center justify-between">
          <span>{feedbackMsg}</span>
          <button onClick={() => setFeedbackMsg('')} className="underline text-[11px]">Đóng</button>
        </div>
      )}

      {/* 2. Main Grid: Map & Action Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left/Main Column: Map View (8 Cols) */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <div className="h-[65vh] min-h-[500px] relative rounded-3xl overflow-hidden shadow-2xl border border-slate-800">
            <MapComponent
              zones={zones}
              assemblyPoints={assemblyPoints}
              rescueTeams={rescueTeams}
              requests={myActiveRequest ? [myActiveRequest] : []}
              selectedLocation={selectedPin}
              onMapClick={handleMapClick}
              center={myActiveRequest ? [myActiveRequest.latitude, myActiveRequest.longitude] : [21.0285, 105.8542]}
            />
          </div>

          <div className="p-3.5 bg-slate-900/80 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-3">
            <div className="flex items-center gap-2">
              <Navigation className="w-4 h-4 text-cyan-400" />
              <span>Mẹo: Nhấp chuột trực tiếp lên bản đồ để chọn tọa độ GPS cần gửi yêu cầu cứu trợ.</span>
            </div>
            {selectedPin && (
              <span className="font-bold text-amber-300">
                Đã chọn: [{selectedPin.latitude}, {selectedPin.longitude}]
              </span>
            )}
          </div>
        </div>

        {/* Right Column: Citizen Actions & Emergency Control (4 Cols) */}
        <div className="lg:col-span-4 flex flex-col gap-5">
          
          {/* PRIMARY SOS BUTTON */}
          <div className="p-6 rounded-3xl bg-gradient-to-b from-red-950/80 via-slate-900 to-slate-900 border-2 border-red-500/60 shadow-[0_0_40px_rgba(239,68,68,0.2)] text-center space-y-4">
            <div className="w-16 h-16 mx-auto rounded-3xl bg-red-600 flex items-center justify-center shadow-xl shadow-red-600/50 animate-bounce">
              <AlertOctagon className="w-9 h-9 text-white" />
            </div>
            <div>
              <h3 className="font-black text-xl text-white tracking-wide">YÊU CẦU CỨU TRỢ KHẨN CẤP</h3>
              <p className="text-xs text-slate-300 mt-1">
                Tự động lấy tọa độ GPS, xác định phân vùng Zone và thông báo trực tiếp tới Đội phản ứng nhanh
              </p>
            </div>
            <button
              onClick={() => setShowSOSModal(true)}
              className="w-full py-4 rounded-2xl bg-gradient-to-r from-red-600 via-rose-600 to-red-600 hover:from-red-500 hover:to-rose-500 text-white font-black text-sm tracking-wider shadow-xl shadow-red-600/40 transform hover:-translate-y-0.5 transition active:translate-y-0"
            >
              🚨 PHÁT TÍN HIỆU SOS NGAY
            </button>
          </div>

          {/* ACTIVE REQUEST TRACKER CARD */}
          {myActiveRequest && (
            <div className="p-5 rounded-3xl bg-slate-900 border-2 border-amber-500/50 shadow-xl space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping"></span>
                  <h4 className="font-extrabold text-sm text-white">THEO DÕI YÊU CẦU CỨU HỘ</h4>
                </div>
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-black border ${
                  myActiveRequest.status === 'PENDING' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                  myActiveRequest.status === 'ACCEPTED' ? 'bg-blue-500/20 text-blue-300 border-blue-500/40' :
                  'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                }`}>
                  {myActiveRequest.status === 'PENDING' ? 'CHỜ ĐIỀU PHỐI' :
                   myActiveRequest.status === 'ACCEPTED' ? 'ĐÃ TIẾP NHẬN' : 'ĐANG TIẾP CẬN'}
                </span>
              </div>

              <div className="space-y-1.5 text-xs text-slate-300">
                <div>Phân vùng: <b className="text-white">{myActiveRequest.zone_name}</b></div>
                <div>Loại hỗ trợ: <b className="text-red-400">{myActiveRequest.relief_type}</b></div>
                <div>Mức khẩn cấp: <b className="text-amber-300">{myActiveRequest.personal_urgency}</b></div>
                {myActiveRequest.assigned_team_name && (
                  <div className="p-2.5 rounded-xl bg-cyan-950/60 border border-cyan-500/30 text-cyan-200 mt-2">
                    🚤 Đội ứng cứu: <b>{myActiveRequest.assigned_team_name}</b>
                  </div>
                )}
              </div>

              <button
                onClick={handleCancelMyRequest}
                className="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-300 hover:text-white transition"
              >
                Tôi đã an toàn, muốn hủy yêu cầu
              </button>
            </div>
          )}

          {/* QUICK "I AM SAFE" BUTTON & FIRST AID AI */}
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setShowSafeModal(true)}
              className="p-4 rounded-2xl bg-slate-900 hover:bg-slate-800 border border-emerald-500/40 text-left transition space-y-1.5 group"
            >
              <CheckCircle2 className="w-6 h-6 text-emerald-400 group-hover:scale-110 transition-transform" />
              <div className="font-extrabold text-xs text-white">Báo "Tôi an toàn"</div>
              <p className="text-[10px] text-slate-400">Gửi vị trí trấn an người thân</p>
            </button>

            <button
              onClick={() => setShowAIChat(true)}
              className="p-4 rounded-2xl bg-slate-900 hover:bg-slate-800 border border-cyan-500/40 text-left transition space-y-1.5 group"
            >
              <Bot className="w-6 h-6 text-cyan-400 group-hover:scale-110 transition-transform" />
              <div className="font-extrabold text-xs text-white">Trợ lý Sơ cứu AI</div>
              <p className="text-[10px] text-slate-400">Hướng dẫn kỹ năng cấp cứu</p>
            </button>
          </div>

          {/* ACTIVE ZONES HEALTH CARD */}
          <div className="p-5 rounded-3xl bg-slate-900 border border-slate-800 space-y-3">
            <h4 className="font-extrabold text-xs tracking-wider text-slate-300 uppercase">TÌNH HÌNH CÁC PHÂN VÙNG ZONE</h4>
            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
              {zones.map(z => (
                <div key={z.id} className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/50 flex items-center justify-between text-xs">
                  <div>
                    <div className="font-bold text-white">{z.name}</div>
                    <div className="text-[10px] text-slate-400">Mã: {z.code}</div>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-black ${
                      z.status === 'RED' ? 'bg-red-500/20 text-red-400 border border-red-500/40' :
                      z.status === 'ORANGE' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/40' :
                      'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40'
                    }`}>
                      {z.status === 'RED' ? 'ZONE ĐỎ' : z.status === 'ORANGE' ? 'ZONE CAM' : 'ZONE VÀNG'}
                    </span>
                    <div className="text-[10px] text-slate-400 mt-0.5">{z.request_count} yêu cầu</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* SOS MODAL */}
      <SOSModal
        isOpen={showSOSModal}
        onClose={() => setShowSOSModal(false)}
        initialCoords={selectedPin}
        onSuccess={(req) => {
          setMyActiveRequest(req);
          setFeedbackMsg('Đã phát tín hiệu SOS thành công! Đội cứu hộ đang tiếp nhận điều phối.');
          loadData();
        }}
      />

      {/* SAFE STATUS MODAL */}
      <SafeStatusModal
        isOpen={showSafeModal}
        onClose={() => setShowSafeModal(false)}
        onSuccess={() => {
          setFeedbackMsg('Đã ghi nhận trạng thái an toàn thành công!');
        }}
      />

      {/* FIRST AID AI DRAWER */}
      {showAIChat && (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-slate-900 border-l border-slate-800 shadow-2xl p-6 flex flex-col justify-between animate-in slide-in-from-right">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
                  <Bot className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-sm text-white">TRỢ LÝ SƠ CỨU & CỨU NẠN</h3>
                  <p className="text-[11px] text-slate-400">Hỗ trợ kỹ năng cấp cứu khẩn cấp 24/7</p>
                </div>
              </div>
              <button onClick={() => setShowAIChat(false)} className="p-1.5 text-slate-400 hover:text-white rounded-lg">✕</button>
            </div>

            <div className="mt-4 space-y-3 max-h-[60vh] overflow-y-auto pr-1">
              {chatMessages.map(m => (
                <div key={m.id} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`p-3 rounded-2xl text-xs max-w-[85%] whitespace-pre-line leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-red-600 text-white font-medium rounded-tr-none'
                      : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-none font-sans'
                  }`}>
                    {m.text}
                  </div>
                </div>
              ))}
              {aiLoading && (
                <div className="text-xs text-slate-400 italic">Trợ lý AI đang tra cứu hướng dẫn...</div>
              )}
            </div>
          </div>

          <form onSubmit={handleSendAIChat} className="pt-4 border-t border-slate-800 flex gap-2">
            <input
              type="text"
              value={aiQuery}
              onChange={(e) => setAiQuery(e.target.value)}
              placeholder="Hỏi cách sơ cứu (đuối nước, gãy xương...)"
              className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500 placeholder:text-slate-500"
            />
            <button
              type="submit"
              disabled={aiLoading}
              className="p-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}

    </div>
  );
};

export default Home;
