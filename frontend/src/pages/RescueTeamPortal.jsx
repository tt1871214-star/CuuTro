import React, { useState, useEffect } from 'react';
import { Flame, ShieldAlert, CheckCircle2, Clock, MapPin, Phone, RefreshCw, AlertCircle, ArrowRight, XCircle } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useRealtime } from '../context/RealtimeContext';
import MapComponent from '../components/MapComponent';

const RescueTeamPortal = () => {
  const { user } = useAuth();
  const { refreshTrigger } = useRealtime();

  const [requests, setRequests] = useState([]);
  const [zones, setZones] = useState([]);
  const [assemblyPoints, setAssemblyPoints] = useState([]);
  const [teams, setTeams] = useState([]);
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [loading, setLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState(null);
  const [notice, setNotice] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      // 1. Fetch Requests
      const reqRes = await api.get('/api/rescue-requests');
      if (reqRes.data) setRequests(reqRes.data);

      // 2. Fetch Zones
      const zonesRes = await api.get('/api/zones');
      if (zonesRes.data) setZones(zonesRes.data);

      // 3. Fetch Assembly Points
      const apRes = await api.get('/api/assembly-points');
      if (apRes.data) setAssemblyPoints(apRes.data);

      // 4. Fetch Rescue Teams
      const teamsRes = await api.get('/api/rescue-teams');
      if (teamsRes.data) setTeams(teamsRes.data);
    } catch (err) {
      console.warn("Lỗi tải dữ liệu điều phối:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const handleUpdateStatus = async (requestId, targetStatus, notes = '') => {
    setActionLoadingId(requestId);
    setNotice(null);
    try {
      const res = await api.put(`/api/rescue-requests/${requestId}/status`, {
        status: targetStatus,
        notes: notes || `Chuyển sang ${targetStatus} bởi ${user?.full_name}`
      });
      if (res.data) {
        setNotice({ type: 'success', text: `Cập nhật trạng thái thành công: ${targetStatus}` });
        loadData();
      }
    } catch (err) {
      setNotice({ type: 'error', text: err.response?.data?.detail || 'Lỗi cập nhật trạng thái theo State Machine.' });
    } finally {
      setActionLoadingId(null);
    }
  };

  // Status counts
  const pendingCount = requests.filter(r => r.status === 'PENDING').length;
  const acceptedCount = requests.filter(r => r.status === 'ACCEPTED').length;
  const inProgressCount = requests.filter(r => r.status === 'IN_PROGRESS').length;
  const completedCount = requests.filter(r => r.status === 'COMPLETED').length;

  const filteredRequests = requests.filter(r => {
    if (filterStatus === 'ALL') return true;
    return r.status === filterStatus;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
              <Flame className="w-5 h-5" />
            </span>
            <h1 className="text-xl font-black text-white tracking-wide">CỔNG ĐIỀU PHỐI & PHẢN ỨNG CỨU HỘ</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Trung tâm tác chiến tiếp nhận, điều phối và chuyển trạng thái nhiệm vụ cứu nạn thực địa
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Làm mới dữ liệu
        </button>
      </div>

      {notice && (
        <div className={`p-3.5 rounded-2xl border text-xs font-bold flex items-center justify-between ${
          notice.type === 'success' ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300' : 'bg-red-500/20 border-red-500/40 text-red-300'
        }`}>
          <span>{notice.text}</span>
          <button onClick={() => setNotice(null)} className="underline text-[11px]">Đóng</button>
        </div>
      )}

      {/* KPI METRIC CARDS */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-amber-950/40 border border-amber-500/40 text-amber-200">
          <div className="text-xs font-bold uppercase tracking-wider">Đang chờ xử lý</div>
          <div className="text-2xl font-black mt-1 text-amber-400">{pendingCount}</div>
          <div className="text-[11px] text-amber-300/70 mt-0.5">Yêu cầu mới chưa tiếp nhận</div>
        </div>

        <div className="p-4 rounded-2xl bg-blue-950/40 border border-blue-500/40 text-blue-200">
          <div className="text-xs font-bold uppercase tracking-wider">Đã tiếp nhận</div>
          <div className="text-2xl font-black mt-1 text-blue-400">{acceptedCount}</div>
          <div className="text-[11px] text-blue-300/70 mt-0.5">Đội cứu hộ chuẩn bị xuất kích</div>
        </div>

        <div className="p-4 rounded-2xl bg-cyan-950/40 border border-cyan-500/40 text-cyan-200">
          <div className="text-xs font-bold uppercase tracking-wider">Đang triển khai</div>
          <div className="text-2xl font-black mt-1 text-cyan-400">{inProgressCount}</div>
          <div className="text-[11px] text-cyan-300/70 mt-0.5">Đang tiếp cận hiện trường</div>
        </div>

        <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-200">
          <div className="text-xs font-bold uppercase tracking-wider">Đã hoàn thành</div>
          <div className="text-2xl font-black mt-1 text-emerald-400">{completedCount}</div>
          <div className="text-[11px] text-emerald-300/70 mt-0.5">Đưa nạn nhân về nơi an toàn</div>
        </div>
      </div>

      {/* MAP & DISPATCH QUEUE */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Map View (6 cols) */}
        <div className="lg:col-span-6 flex flex-col gap-3">
          <div className="h-[550px] rounded-3xl overflow-hidden border border-slate-800 shadow-2xl">
            <MapComponent
              zones={zones}
              requests={requests}
              assemblyPoints={assemblyPoints}
              rescueTeams={teams}
            />
          </div>
        </div>

        {/* Dispatch Tasks List (6 cols) */}
        <div className="lg:col-span-6 flex flex-col gap-3">
          
          {/* Status Filter Tabs */}
          <div className="flex items-center gap-1.5 p-1.5 bg-slate-900 rounded-2xl border border-slate-800 text-xs font-bold">
            {['ALL', 'PENDING', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED'].map(st => (
              <button
                key={st}
                onClick={() => setFilterStatus(st)}
                className={`flex-1 py-1.5 rounded-xl transition ${
                  filterStatus === st ? 'bg-cyan-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                }`}
              >
                {st === 'ALL' ? 'Tất cả' : st === 'PENDING' ? 'Chờ nhận' : st === 'ACCEPTED' ? 'Đã nhận' : st === 'IN_PROGRESS' ? 'Đang cứu' : 'Xong'}
              </button>
            ))}
          </div>

          {/* Request Cards Container */}
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
            {filteredRequests.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs bg-slate-900/60 rounded-2xl border border-slate-800">
                Không có yêu cầu cứu trợ nào trong danh mục này.
              </div>
            ) : (
              filteredRequests.map(req => (
                <div key={req.id} className="p-4 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition space-y-3">
                  
                  {/* Top Bar */}
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-black border ${
                          req.status === 'PENDING' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                          req.status === 'ACCEPTED' ? 'bg-blue-500/20 text-blue-300 border-blue-500/40' :
                          req.status === 'IN_PROGRESS' ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' :
                          'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                        }`}>
                          {req.status}
                        </span>
                        <span className="font-extrabold text-sm text-white">{req.relief_type}</span>
                      </div>
                      <div className="text-xs text-slate-400 mt-1 flex items-center gap-3">
                        <span>Người dân: <b className="text-slate-200">{req.sender_name}</b></span>
                        <a href={`tel:${req.sender_phone}`} className="text-cyan-400 hover:underline flex items-center gap-1">
                          <Phone className="w-3 h-3" /> {req.sender_phone}
                        </a>
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                        {req.zone_name}
                      </span>
                      <div className="text-[10px] text-rose-400 font-bold mt-1">Khẩn cấp: {req.personal_urgency}</div>
                    </div>
                  </div>

                  {/* Description */}
                  {req.description && (
                    <p className="text-xs text-slate-300 bg-slate-800/60 p-2.5 rounded-xl border border-slate-800">
                      "{req.description}"
                    </p>
                  )}

                  {/* Image proof */}
                  {req.image_url && (
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <span>Minh chứng:</span>
                      <a href={req.image_url} target="_blank" rel="noreferrer" className="text-cyan-400 underline font-semibold">
                        Xem hình ảnh hiện trường ↗
                      </a>
                    </div>
                  )}

                  {/* State Machine Action Buttons */}
                  <div className="pt-2 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2">
                    <div className="text-[11px] text-slate-400">
                      Tọa độ: [{req.latitude}, {req.longitude}]
                    </div>

                    <div className="flex items-center gap-2">
                      {req.status === 'PENDING' && (
                        <button
                          onClick={() => handleUpdateStatus(req.id, 'ACCEPTED', 'Đội cứu hộ tiếp nhận nhiệm vụ')}
                          disabled={actionLoadingId === req.id}
                          className="px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 font-black text-xs text-white shadow-md transition"
                        >
                          {actionLoadingId === req.id ? 'Đang lưu...' : 'Tiếp nhận ứng cứu'}
                        </button>
                      )}

                      {req.status === 'ACCEPTED' && (
                        <>
                          <button
                            onClick={() => handleUpdateStatus(req.id, 'IN_PROGRESS', 'Đội cứu hộ xuất kích ca nô')}
                            disabled={actionLoadingId === req.id}
                            className="px-3 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 font-black text-xs text-white shadow-md transition"
                          >
                            Xuất kích / Di chuyển
                          </button>
                          <button
                            onClick={() => handleUpdateStatus(req.id, 'CANCELLED', 'Hủy tiếp nhận - trả về hàng đợi')}
                            disabled={actionLoadingId === req.id}
                            className="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-rose-900/60 text-slate-400 hover:text-rose-300 text-xs font-bold transition"
                          >
                            Hủy nhận
                          </button>
                        </>
                      )}

                      {req.status === 'IN_PROGRESS' && (
                        <>
                          <button
                            onClick={() => handleUpdateStatus(req.id, 'COMPLETED', 'Đã giải cứu nạn nhân thành công')}
                            disabled={actionLoadingId === req.id}
                            className="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-black text-xs text-white shadow-md transition"
                          >
                            Hoàn thành cứu hộ
                          </button>
                          <button
                            onClick={() => handleUpdateStatus(req.id, 'CANCELLED', 'Gặp trở ngại bất khả kháng - trả về hàng đợi')}
                            disabled={actionLoadingId === req.id}
                            className="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-rose-900/60 text-slate-400 hover:text-rose-300 text-xs font-bold transition"
                          >
                            Hủy nhiệm vụ
                          </button>
                        </>
                      )}

                      {req.status === 'COMPLETED' && (
                        <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                          <CheckCircle2 className="w-4 h-4" /> Đã hoàn tất nhiệm vụ
                        </span>
                      )}
                    </div>
                  </div>

                </div>
              ))
            )}
          </div>
        </div>
      </div>

    </div>
  );
};

export default RescueTeamPortal;
