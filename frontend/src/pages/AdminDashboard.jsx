import React, { useState, useEffect } from 'react';
import { 
  Users, Sliders, ShieldAlert, BarChart3, Radio, Plus, Trash2, 
  CheckCircle2, RefreshCw, AlertTriangle, CloudRain, ShieldCheck, MapPin
} from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useRealtime } from '../context/RealtimeContext';
import MapComponent from '../components/MapComponent';

const AdminDashboard = () => {
  const { user } = useAuth();
  const { refreshTrigger, triggerManualRefresh } = useRealtime();

  const [activeTab, setActiveTab] = useState('overview'); // overview, zones, users, teams, system
  const [overview, setOverview] = useState(null);
  const [zones, setZones] = useState([]);
  const [thresholds, setThresholds] = useState({ yellow_max: 20, orange_max: 50, red_min: 50 });
  const [requests, setRequests] = useState([]);
  const [assemblyPoints, setAssemblyPoints] = useState([]);
  const [usersList, setUsersList] = useState([]);
  const [teamsList, setTeamsList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState(null);

  // New Zone Form
  const [newZoneCode, setNewZoneCode] = useState('');
  const [newZoneName, setNewZoneName] = useState('');
  const [newZoneLat, setNewZoneLat] = useState('21.0285');
  const [newZoneLng, setNewZoneLng] = useState('105.8542');
  const [newZoneRadius, setNewZoneRadius] = useState('5.0');
  const [newZoneDesc, setNewZoneDesc] = useState('');

  // Alert Form
  const [alertTitle, setAlertTitle] = useState('');
  const [alertType, setAlertType] = useState('MƯA LŨ / NGẬP ÚNG');
  const [alertArea, setAlertArea] = useState('Toàn TP. Hà Nội');
  const [alertLevel, setAlertLevel] = useState('ORANGE');
  const [alertMsg, setAlertMsg] = useState('');

  const loadAllAdminData = async () => {
    setLoading(true);
    try {
      const ovRes = await api.get('/api/dashboard/overview');
      if (ovRes.data) setOverview(ovRes.data);

      const zRes = await api.get('/api/zones');
      if (zRes.data) setZones(zRes.data);

      const thRes = await api.get('/api/zones/config/thresholds');
      if (thRes.data) setThresholds(thRes.data);

      const reqRes = await api.get('/api/rescue-requests');
      if (reqRes.data) setRequests(reqRes.data);

      const apRes = await api.get('/api/assembly-points');
      if (apRes.data) setAssemblyPoints(apRes.data);

      const uRes = await api.get('/api/users');
      if (uRes.data) setUsersList(uRes.data);

      const tRes = await api.get('/api/rescue-teams');
      if (tRes.data) setTeamsList(tRes.data);
    } catch (err) {
      console.warn('Lỗi tải dữ liệu quản trị:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllAdminData();
  }, [refreshTrigger]);

  const handleSaveThresholds = async (e) => {
    e.preventDefault();
    setMsg(null);
    try {
      const res = await api.put('/api/zones/config/thresholds', {
        yellow_max: parseInt(thresholds.yellow_max),
        orange_max: parseInt(thresholds.orange_max),
        red_min: parseInt(thresholds.red_min)
      });
      if (res.data) {
        setMsg({ type: 'success', text: 'Cập nhật cấu hình ngưỡng thành công! Zone Engine đã tính toán lại toàn bộ phân vùng.' });
        loadAllAdminData();
        triggerManualRefresh();
      }
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.detail || 'Lỗi lưu cấu hình ngưỡng.' });
    }
  };

  const handleCreateZone = async (e) => {
    e.preventDefault();
    setMsg(null);
    try {
      const res = await api.post('/api/zones', {
        code: newZoneCode,
        name: newZoneName,
        description: newZoneDesc,
        center_lat: parseFloat(newZoneLat),
        center_lng: parseFloat(newZoneLng),
        radius_km: parseFloat(newZoneRadius)
      });
      if (res.data) {
        setMsg({ type: 'success', text: `Đã tạo thành công phân vùng Zone: ${newZoneName}` });
        setNewZoneCode('');
        setNewZoneName('');
        setNewZoneDesc('');
        loadAllAdminData();
        triggerManualRefresh();
      }
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.detail || 'Lỗi tạo Zone.' });
    }
  };

  const handleDeleteZone = async (id, name) => {
    if (!window.confirm(`Bạn có chắc chắn muốn xóa phân vùng "${name}"?`)) return;
    try {
      await api.delete(`/api/zones/${id}`);
      setMsg({ type: 'success', text: `Đã xóa phân vùng ${name}.` });
      loadAllAdminData();
      triggerManualRefresh();
    } catch (err) {
      alert(err.response?.data?.detail || 'Lỗi khi xóa Zone.');
    }
  };

  const handleToggleUser = async (id) => {
    try {
      await api.put(`/api/users/${id}/status`);
      loadAllAdminData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể đổi trạng thái tài khoản.');
    }
  };

  const handlePublishAlert = async (e) => {
    e.preventDefault();
    setMsg(null);
    try {
      const res = await api.post('/api/alerts', {
        title: alertTitle,
        disaster_type: alertType,
        target_area: alertArea,
        alert_level: alertLevel,
        message: alertMsg,
        guidelines: 'Khuyến cáo người dân kê cao tài sản, ngắt nguồn điện và chuẩn bị sẵn đồ dùng thiết yếu.'
      });
      if (res.data) {
        setMsg({ type: 'success', text: 'Đã phát cảnh báo thiên tai khẩn cấp tới toàn bộ hệ thống!' });
        setAlertTitle('');
        setAlertMsg('');
        loadAllAdminData();
        triggerManualRefresh();
      }
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.detail || 'Lỗi phát cảnh báo.' });
    }
  };

  const handleSyncWeather = async () => {
    setMsg(null);
    try {
      await api.post('/api/alerts/weather-sync?area=Hà Nội & Miền Bắc&lat=21.0285&lng=105.8542');
      setMsg({ type: 'success', text: 'Đã đồng bộ cảnh báo khí tượng tự động từ Open-Meteo API thành công!' });
      loadAllAdminData();
      triggerManualRefresh();
    } catch (err) {
      alert('Có lỗi khi đồng bộ Open-Meteo.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/40">
              <BarChart3 className="w-5 h-5" />
            </span>
            <h1 className="text-xl font-black text-white tracking-wide">TRUNG TÂM CHỈ HUY QUẢN TRỊ (ADMIN)</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Quản trị Zone & cấu hình ngưỡng động, quản lý người dùng, điều phối hệ thống cứu trợ
          </p>
        </div>

        <button
          onClick={loadAllAdminData}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Làm mới
        </button>
      </div>

      {msg && (
        <div className={`p-3.5 rounded-2xl border text-xs font-bold flex items-center justify-between ${
          msg.type === 'success' ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300' : 'bg-red-500/20 border-red-500/40 text-red-300'
        }`}>
          <span>{msg.text}</span>
          <button onClick={() => setMsg(null)} className="underline text-[11px]">Đóng</button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 p-1.5 bg-slate-900 rounded-2xl border border-slate-800 text-xs font-bold">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 rounded-xl transition flex items-center gap-2 ${
            activeTab === 'overview' ? 'bg-purple-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
          }`}
        >
          <BarChart3 className="w-4 h-4" /> Tổng quan & KPI
        </button>
        <button
          onClick={() => setActiveTab('zones')}
          className={`px-4 py-2 rounded-xl transition flex items-center gap-2 ${
            activeTab === 'zones' ? 'bg-purple-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Sliders className="w-4 h-4 text-amber-400" /> Quản lý Zone & Cấu hình Ngưỡng
        </button>
        <button
          onClick={() => setActiveTab('users')}
          className={`px-4 py-2 rounded-xl transition flex items-center gap-2 ${
            activeTab === 'users' ? 'bg-purple-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Users className="w-4 h-4 text-cyan-400" /> Người dùng
        </button>
        <button
          onClick={() => setActiveTab('teams')}
          className={`px-4 py-2 rounded-xl transition flex items-center gap-2 ${
            activeTab === 'teams' ? 'bg-purple-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
          }`}
        >
          <ShieldCheck className="w-4 h-4 text-emerald-400" /> Đội cứu hộ
        </button>
        <button
          onClick={() => setActiveTab('system')}
          className={`px-4 py-2 rounded-xl transition flex items-center gap-2 ${
            activeTab === 'system' ? 'bg-purple-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Radio className="w-4 h-4 text-red-400" /> Cảnh báo & Open-Meteo
        </button>
      </div>

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && overview && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3.5">
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
              <div className="text-[11px] font-bold text-slate-400 uppercase">Tổng yêu cầu</div>
              <div className="text-2xl font-black text-white mt-1">{overview.total_requests}</div>
            </div>
            <div className="p-4 rounded-2xl bg-amber-950/40 border border-amber-500/40">
              <div className="text-[11px] font-bold text-amber-300 uppercase">Đang chờ (Pending)</div>
              <div className="text-2xl font-black text-amber-400 mt-1">{overview.pending_requests}</div>
            </div>
            <div className="p-4 rounded-2xl bg-cyan-950/40 border border-cyan-500/40">
              <div className="text-[11px] font-bold text-cyan-300 uppercase">Đang cứu (In Progress)</div>
              <div className="text-2xl font-black text-cyan-400 mt-1">{overview.in_progress_requests}</div>
            </div>
            <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/40">
              <div className="text-[11px] font-bold text-emerald-300 uppercase">Hoàn thành</div>
              <div className="text-2xl font-black text-emerald-400 mt-1">{overview.completed_requests}</div>
            </div>
            <div className="p-4 rounded-2xl bg-red-950/40 border border-red-500/40">
              <div className="text-[11px] font-bold text-red-300 uppercase">Zone Đỏ (Nguy kịch)</div>
              <div className="text-2xl font-black text-red-400 mt-1">{overview.red_zones_count}</div>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
              <div className="text-[11px] font-bold text-cyan-400 uppercase">Đội cứu hộ trực</div>
              <div className="text-2xl font-black text-white mt-1">{overview.active_teams_count}</div>
            </div>
          </div>

          <div className="h-[520px] rounded-3xl overflow-hidden border border-slate-800 shadow-2xl">
            <MapComponent
              zones={zones}
              requests={requests}
              assemblyPoints={assemblyPoints}
              rescueTeams={teamsList}
            />
          </div>
        </div>
      )}

      {/* Tab 2: Zones & Threshold Config */}
      {activeTab === 'zones' && (
        <div className="space-y-6">
          <div className="p-5 rounded-3xl bg-gradient-to-r from-amber-950/80 via-slate-900 to-slate-900 border-2 border-amber-500/60 text-xs text-slate-200 space-y-2">
            <div className="flex items-center gap-2 text-amber-400 font-extrabold text-sm">
              <Sliders className="w-5 h-5" /> QUY TẮC NGHIỆP VỤ — XÁC ĐỊNH MỨC ZONE (MỤC 7.4)
            </div>
            <p>
              • <b>KHÔNG</b> xác định mức độ khẩn cấp theo thời gian chờ của từng cá nhân.<br/>
              • Xác định theo <b>số lượng yêu cầu cứu trợ tích lũy trong cùng một Zone</b>.<br/>
              • Ngưỡng số lượng chuyển mức Zone là <b>cấu hình động</b> do Admin điều chỉnh linh hoạt:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs">
              <div className="p-3 rounded-xl bg-yellow-500/10 border border-yellow-500/40 text-yellow-300">
                <b>Zone Vàng (Gold):</b> Từ 0 đến {'<'} {thresholds.yellow_max} yêu cầu.
              </div>
              <div className="p-3 rounded-xl bg-orange-500/10 border border-orange-500/40 text-orange-300">
                <b>Zone Cam (Orange):</b> Từ {thresholds.yellow_max} đến {'<'} {thresholds.orange_max} yêu cầu.
              </div>
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/40 text-red-300">
                <b>Zone Đỏ (Red):</b> Từ ≥ {thresholds.red_min} yêu cầu.
              </div>
            </div>
          </div>

          {/* Threshold Config Form */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="font-extrabold text-sm text-white flex items-center gap-2">
              <Sliders className="w-4 h-4 text-purple-400" /> MÀN HÌNH CẤU HÌNH NGƯỠNG ZONE ENGINE
            </h3>
            
            <form onSubmit={handleSaveThresholds} className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs">
              <div>
                <label className="font-bold text-yellow-400">Ngưỡng Zone Vàng (yellow_max):</label>
                <input
                  type="number"
                  min="1"
                  value={thresholds.yellow_max}
                  onChange={(e) => setThresholds({ ...thresholds, yellow_max: e.target.value })}
                  className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white font-bold text-center"
                  required
                />
                <span className="text-[10px] text-slate-400">Dưới mức này là Zone Vàng</span>
              </div>

              <div>
                <label className="font-bold text-orange-400">Ngưỡng Zone Cam (orange_max):</label>
                <input
                  type="number"
                  min="2"
                  value={thresholds.orange_max}
                  onChange={(e) => setThresholds({ ...thresholds, orange_max: e.target.value })}
                  className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white font-bold text-center"
                  required
                />
                <span className="text-[10px] text-slate-400">Dưới mức này là Zone Cam</span>
              </div>

              <div>
                <label className="font-bold text-red-400">Ngưỡng Zone Đỏ (red_min):</label>
                <input
                  type="number"
                  min="2"
                  value={thresholds.red_min}
                  onChange={(e) => setThresholds({ ...thresholds, red_min: e.target.value })}
                  className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white font-bold text-center"
                  required
                />
                <span className="text-[10px] text-slate-400">Từ mức này trở lên là Zone Đỏ</span>
              </div>

              <div className="flex items-end">
                <button
                  type="submit"
                  className="w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-black tracking-wide shadow-lg shadow-purple-600/30 transition"
                >
                  LƯU CẤU HÌNH NGƯỠNG
                </button>
              </div>
            </form>
          </div>

          {/* Zones Table & Form */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-4 p-5 rounded-3xl bg-slate-900 border border-slate-800 space-y-3 text-xs">
              <h4 className="font-extrabold text-sm text-white flex items-center gap-1.5">
                <Plus className="w-4 h-4 text-emerald-400" /> THÊM PHÂN VÙNG ZONE MỚI
              </h4>
              <form onSubmit={handleCreateZone} className="space-y-3">
                <div>
                  <label className="font-bold text-slate-300">Mã Zone:</label>
                  <input
                    type="text"
                    placeholder="VD: ZONE-CG-01"
                    value={newZoneCode}
                    onChange={(e) => setNewZoneCode(e.target.value)}
                    className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                    required
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-300">Tên phân vùng:</label>
                  <input
                    type="text"
                    placeholder="VD: Khu vực Cầu Giấy"
                    value={newZoneName}
                    onChange={(e) => setNewZoneName(e.target.value)}
                    className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="font-bold text-slate-300">Tâm Lat:</label>
                    <input
                      type="number"
                      step="any"
                      value={newZoneLat}
                      onChange={(e) => setNewZoneLat(e.target.value)}
                      className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="font-bold text-slate-300">Tâm Lng:</label>
                    <input
                      type="number"
                      step="any"
                      value={newZoneLng}
                      onChange={(e) => setNewZoneLng(e.target.value)}
                      className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label className="font-bold text-slate-300">Bán kính (km):</label>
                  <input
                    type="number"
                    step="0.5"
                    value={newZoneRadius}
                    onChange={(e) => setNewZoneRadius(e.target.value)}
                    className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                    required
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-300">Mô tả:</label>
                  <textarea
                    rows={2}
                    value={newZoneDesc}
                    onChange={(e) => setNewZoneDesc(e.target.value)}
                    className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl p-2.5 text-white"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-bold text-white shadow-md transition"
                >
                  TẠO PHÂN VÙNG ZONE
                </button>
              </form>
            </div>

            <div className="lg:col-span-8 p-5 rounded-3xl bg-slate-900 border border-slate-800 space-y-3">
              <h4 className="font-extrabold text-sm text-white">DANH SÁCH CÁC ZONE VÀ TRẠNG THÁI</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-800/80 uppercase text-[11px] text-slate-400">
                    <tr>
                      <th className="p-3">Mã</th>
                      <th className="p-3">Tên</th>
                      <th className="p-3 text-center">Bán kính</th>
                      <th className="p-3 text-center">Số Request</th>
                      <th className="p-3 text-center">Trạng thái</th>
                      <th className="p-3 text-right">Thao tác</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {zones.map(z => (
                      <tr key={z.id} className="hover:bg-slate-800/40 transition">
                        <td className="p-3 font-mono font-bold text-cyan-300">{z.code}</td>
                        <td className="p-3 font-bold text-white">{z.name}</td>
                        <td className="p-3 text-center">{z.radius_km} km</td>
                        <td className="p-3 text-center font-bold text-white">{z.request_count}</td>
                        <td className="p-3 text-center">
                          <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-black border ${
                            z.status === 'RED' ? 'bg-red-500/20 text-red-400 border-red-500/40 animate-pulse' :
                            z.status === 'ORANGE' ? 'bg-orange-500/20 text-orange-400 border-orange-500/40' :
                            'bg-yellow-500/20 text-yellow-400 border-yellow-500/40'
                          }`}>
                            {z.status === 'RED' ? 'ZONE ĐỎ' : z.status === 'ORANGE' ? 'ZONE CAM' : 'ZONE VÀNG'}
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <button
                            onClick={() => handleDeleteZone(z.id, z.name)}
                            className="p-1.5 text-slate-500 hover:text-red-400 transition"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Users */}
      {activeTab === 'users' && (
        <div className="p-5 rounded-3xl bg-slate-900 border border-slate-800 space-y-3">
          <h4 className="font-extrabold text-sm text-white flex items-center gap-2">
            <Users className="w-4 h-4 text-cyan-400" /> QUẢN LÝ TÀI KHOẢN NGƯỜI DÙNG
          </h4>
          <div className="overflow-x-auto max-h-[500px]">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-800/80 uppercase text-[11px] text-slate-400">
                <tr>
                  <th className="p-2.5">Họ tên</th>
                  <th className="p-2.5">Số điện thoại</th>
                  <th className="p-2.5">Vai trò</th>
                  <th className="p-2.5 text-center">Trạng thái</th>
                  <th className="p-2.5 text-right">Khóa/Mở</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {usersList.map(u => (
                  <tr key={u.id}>
                    <td className="p-2.5 font-bold text-white">{u.full_name}</td>
                    <td className="p-2.5 font-mono">{u.phone}</td>
                    <td className="p-2.5 font-bold text-slate-300">{u.role}</td>
                    <td className="p-2.5 text-center">
                      <span className={`text-[10px] font-bold ${u.is_active ? 'text-emerald-400' : 'text-red-400'}`}>
                        {u.is_active ? 'Hoạt động' : 'Đã khóa'}
                      </span>
                    </td>
                    <td className="p-2.5 text-right">
                      <button
                        onClick={() => handleToggleUser(u.id)}
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[11px] text-slate-300"
                      >
                        {u.is_active ? 'Khóa' : 'Mở'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 4: Rescue Teams */}
      {activeTab === 'teams' && (
        <div className="p-5 rounded-3xl bg-slate-900 border border-slate-800 space-y-3">
          <h4 className="font-extrabold text-sm text-white flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" /> DANH SÁCH ĐỘI CỨU HỘ TRỰC CHIẾN
          </h4>
          <div className="overflow-x-auto max-h-[500px]">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-800/80 uppercase text-[11px] text-slate-400">
                <tr>
                  <th className="p-2.5">Tên đội</th>
                  <th className="p-2.5">Đội trưởng</th>
                  <th className="p-2.5">Hotline</th>
                  <th className="p-2.5 text-center">Trạng thái</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {teamsList.map(t => (
                  <tr key={t.id}>
                    <td className="p-2.5 font-bold text-white">{t.team_name}</td>
                    <td className="p-2.5">{t.leader_name}</td>
                    <td className="p-2.5 font-mono text-cyan-300">{t.contact_phone}</td>
                    <td className="p-2.5 text-center">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold">
                        {t.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 5: System & Alerts */}
      {activeTab === 'system' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
            <h4 className="font-extrabold text-sm text-white flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" /> PHÁT CẢNH BÁO THIÊN TAI KHẨN CẤP
            </h4>
            <form onSubmit={handlePublishAlert} className="space-y-3">
              <div>
                <label className="font-bold text-slate-300">Tiêu đề:</label>
                <input
                  type="text"
                  value={alertTitle}
                  onChange={(e) => setAlertTitle(e.target.value)}
                  className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-bold text-slate-300">Loại hình:</label>
                  <input
                    type="text"
                    value={alertType}
                    onChange={(e) => setAlertType(e.target.value)}
                    className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-300">Mức cảnh báo:</label>
                  <select
                    value={alertLevel}
                    onChange={(e) => setAlertLevel(e.target.value)}
                    className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white font-bold"
                  >
                    <option value="YELLOW">VÀNG</option>
                    <option value="ORANGE">CAM</option>
                    <option value="RED">ĐỎ</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="font-bold text-slate-300">Khu vực:</label>
                <input
                  type="text"
                  value={alertArea}
                  onChange={(e) => setAlertArea(e.target.value)}
                  className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                  required
                />
              </div>
              <div>
                <label className="font-bold text-slate-300">Nội dung chi tiết:</label>
                <textarea
                  rows={3}
                  value={alertMsg}
                  onChange={(e) => setAlertMsg(e.target.value)}
                  className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl p-2.5 text-white"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-red-600 hover:bg-red-500 font-bold text-white shadow-lg transition"
              >
                PHÁT CẢNH BÁO
              </button>
            </form>
          </div>

          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
            <h4 className="font-extrabold text-sm text-white flex items-center gap-2">
              <CloudRain className="w-4 h-4 text-blue-400" /> ĐỒNG BỘ OPEN-METEO API
            </h4>
            <p className="text-slate-300 leading-relaxed">
              Tự động thu thập dữ liệu khí tượng trực tiếp từ Open-Meteo và phát cảnh báo rủi ro thiên tai.
            </p>
            <button
              onClick={handleSyncWeather}
              className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 font-black text-white shadow-lg flex items-center justify-center gap-2 transition"
            >
              <RefreshCw className="w-4 h-4" /> ĐỒNG BỘ CẢNH BÁO TỪ OPEN-METEO NGAY
            </button>
          </div>
        </div>
      )}

    </div>
  );
};

export default AdminDashboard;
