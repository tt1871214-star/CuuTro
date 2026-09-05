import React, { useState, useEffect } from 'react';
import { Radio, Plus, CheckCircle2, XCircle, MapPin, AlertTriangle, MessageSquare, ThumbsUp, ThumbsDown, Loader2 } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useRealtime } from '../context/RealtimeContext';

const CommunityBoard = () => {
  const { user } = useAuth();
  const { refreshTrigger } = useRealtime();

  const [posts, setPosts] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [postType, setPostType] = useState('FLOOD');
  const [lat, setLat] = useState(21.0285);
  const [lng, setLng] = useState(105.8542);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [verifyingId, setVerifyingId] = useState(null);

  const fetchPosts = async () => {
    try {
      const res = await api.get('/api/community/posts');
      if (res.data) setPosts(res.data);
    } catch (err) {
      console.warn('Lỗi tải bảng tin:', err);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, [refreshTrigger]);

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(pos => {
        setLat(Number(pos.coords.latitude.toFixed(6)));
        setLng(Number(pos.coords.longitude.toFixed(6)));
      });
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    if (!user) {
      setFeedback({ type: 'error', text: 'Vui lòng đăng nhập để đăng tin thực địa.' });
      return;
    }
    setLoading(true);
    setFeedback(null);
    try {
      const res = await api.post('/api/community/posts', {
        title,
        content,
        post_type: postType,
        latitude: parseFloat(lat),
        longitude: parseFloat(lng)
      });
      if (res.data) {
        setFeedback({ type: 'success', text: 'Đăng tin thực tế thành công! Tin sẽ được cộng đồng lân cận xác minh chéo.' });
        setTitle('');
        setContent('');
        setShowCreateModal(false);
        fetchPosts();
      }
    } catch (err) {
      setFeedback({ type: 'error', text: err.response?.data?.detail || 'Lỗi khi đăng tin.' });
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = (postId, isConfirm) => {
    if (!user) {
      alert('Vui lòng đăng nhập để xác minh thông tin.');
      return;
    }

    if (!navigator.geolocation) {
      alert('Trình duyệt cần hỗ trợ GPS để kiểm tra bạn có ở trong bán kính 5km hay không.');
      return;
    }

    setVerifyingId(postId);
    setFeedback(null);

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const res = await api.post(`/api/community/posts/${postId}/verify`, {
            is_confirm: isConfirm,
            current_lat: pos.coords.latitude,
            current_lng: pos.coords.longitude
          });
          if (res.data) {
            setFeedback({ type: 'success', text: 'Xác minh thông tin thành công!' });
            fetchPosts();
          }
        } catch (err) {
          setFeedback({
            type: 'error',
            text: err.response?.data?.detail || 'Lỗi khi xác minh thông tin (chỉ người dùng cách hiện trường < 5km mới được xác minh).'
          });
        } finally {
          setVerifyingId(null);
        }
      },
      (err) => {
        setFeedback({ type: 'error', text: 'Không lấy được GPS để kiểm tra bán kính 5km.' });
        setVerifyingId(null);
      },
      { timeout: 8000 }
    );
  };

  const getPostTypeBadge = (t) => {
    const map = {
      'FLOOD': { label: 'Ngập lụt', color: 'bg-blue-500/20 text-blue-300 border-blue-500/40' },
      'LANDSLIDE': { label: 'Sạt lở', color: 'bg-rose-500/20 text-rose-300 border-rose-500/40' },
      'ROAD_DAMAGE': { label: 'Đường hỏng', color: 'bg-amber-500/20 text-amber-300 border-amber-500/40' },
      'BRIDGE_DAMAGE': { label: 'Cầu sập/hỏng', color: 'bg-red-500/20 text-red-300 border-red-500/40' },
      'POWER_OUTAGE': { label: 'Mất điện', color: 'bg-purple-500/20 text-purple-300 border-purple-500/40' },
      'REFUGE': { label: 'Điểm trú ẩn', color: 'bg-teal-500/20 text-teal-300 border-teal-500/40' },
      'TRAFFIC': { label: 'Giao thông', color: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' },
      'NEED_HELP': { label: 'Cần trợ giúp', color: 'bg-red-500/20 text-red-400 border-red-500/40' }
    };
    const b = map[t] || { label: t, color: 'bg-slate-700 text-slate-300 border-slate-600' };
    return <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-black border ${b.color}`}>{b.label}</span>;
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
              <Radio className="w-5 h-5" />
            </span>
            <h1 className="text-xl font-black text-white tracking-wide">BẢNG TIN THỰC ĐỊA CỘNG ĐỒNG</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Người dân chia sẻ thông tin thực tế: đường ngập, cầu sập, mất điện, điểm trú ẩn — cơ chế xác minh chéo trong bán kính 5km
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2.5 rounded-2xl bg-cyan-600 hover:bg-cyan-500 font-extrabold text-xs text-white shadow-lg shadow-cyan-600/30 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> ĐĂNG TIN THỰC TẾ
        </button>
      </div>

      {feedback && (
        <div className={`p-3.5 rounded-2xl border text-xs font-bold flex items-center justify-between ${
          feedback.type === 'success' ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300' : 'bg-red-500/20 border-red-500/40 text-red-300'
        }`}>
          <span>{feedback.text}</span>
          <button onClick={() => setFeedback(null)} className="underline text-[11px]">Đóng</button>
        </div>
      )}

      {/* Verification Rule Notice */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex items-center gap-3 text-xs text-slate-300">
        <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0" />
        <div>
          <b>Quy định xác minh thực địa (Mục 6.3.2):</b> Các tin chưa đủ 3 lượt xác nhận sẽ hiển thị là <i>"Chưa xác thực"</i>. Chỉ người dân có vị trí GPS trong bán kính <b>dưới 5km</b> so với địa điểm xảy ra sự cố mới có quyền biểu quyết xác thực.
        </div>
      </div>

      {/* Posts List */}
      <div className="space-y-4">
        {posts.map(post => {
          const isVerified = post.verification_status === 'VERIFIED';
          const isRejected = post.verification_status === 'REJECTED';

          return (
            <div key={post.id} className="p-5 rounded-3xl bg-slate-900 border border-slate-800 space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {getPostTypeBadge(post.post_type)}
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-black border ${
                      isVerified ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                      isRejected ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' :
                      'bg-amber-500/20 text-amber-300 border-amber-500/40'
                    }`}>
                      {isVerified ? '✓ ĐÃ XÁC THỰC' : isRejected ? '✗ TIN BÁO SAI' : '⚠️ CHƯA XÁC THỰC'}
                    </span>
                  </div>
                  <h3 className="font-extrabold text-base text-white">{post.title}</h3>
                </div>

                <div className="text-right text-[11px] text-slate-400">
                  <div>Đăng bởi: <b className="text-slate-200">{post.author_name}</b></div>
                  <div>{new Date(post.created_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}</div>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line bg-slate-800/40 p-3 rounded-2xl border border-slate-800">
                {post.content}
              </p>

              <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-800 text-xs text-slate-400">
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-rose-400" />
                  <span>Tọa độ: [{post.latitude}, {post.longitude}]</span>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-[11px] text-emerald-400 font-bold">✓ {post.confirm_count} xác nhận</span>
                  <span className="text-[11px] text-rose-400 font-bold">✗ {post.deny_count} báo sai</span>

                  <div className="flex items-center gap-1.5 pl-2 border-l border-slate-800">
                    <button
                      onClick={() => handleVerify(post.id, true)}
                      disabled={verifyingId === post.id}
                      className="px-2.5 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 text-xs font-bold flex items-center gap-1 transition"
                    >
                      {verifyingId === post.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ThumbsUp className="w-3.5 h-3.5" />}
                      Xác nhận đúng
                    </button>
                    <button
                      onClick={() => handleVerify(post.id, false)}
                      disabled={verifyingId === post.id}
                      className="px-2.5 py-1.5 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/40 text-rose-300 text-xs font-bold flex items-center gap-1 transition"
                    >
                      <ThumbsDown className="w-3.5 h-3.5" /> Báo tin sai
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* CREATE POST MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-700 rounded-3xl p-6 shadow-2xl text-white space-y-4">
            <h3 className="font-black text-base text-cyan-400">ĐĂNG TIN THỰC ĐỊA CỘNG ĐỒNG</h3>
            <form onSubmit={handleCreatePost} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-300">Tiêu đề ngắn gọn:</label>
                <input
                  type="text"
                  placeholder="VD: Cầu Trắng bị ngập sâu, phương tiện không qua được..."
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                  required
                />
              </div>

              <div>
                <label className="font-bold text-slate-300">Phân loại sự cố:</label>
                <select
                  value={postType}
                  onChange={(e) => setPostType(e.target.value)}
                  className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white font-bold"
                >
                  <option value="FLOOD">🌊 Đường ngập nước sâu</option>
                  <option value="LANDSLIDE">⛰️ Sạt lở đất đá</option>
                  <option value="ROAD_DAMAGE">🚧 Đường hỏng / sụt lún</option>
                  <option value="BRIDGE_DAMAGE">🌉 Cầu sập / ngập mố cầu</option>
                  <option value="POWER_OUTAGE">⚡ Mất điện diện rộng</option>
                  <option value="REFUGE">🛡️ Điểm trú ẩn / tiếp tế mới</option>
                  <option value="TRAFFIC">🚗 Tắc nghẽn giao thông khẩn cấp</option>
                  <option value="NEED_HELP">🆘 Cần trợ giúp khẩn</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-bold text-slate-300">Vĩ độ (Lat):</label>
                  <input
                    type="number"
                    step="any"
                    value={lat}
                    onChange={(e) => setLat(e.target.value)}
                    className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5 text-white"
                    required
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-300">Kinh độ (Lng):</label>
                  <input
                    type="number"
                    step="any"
                    value={lng}
                    onChange={(e) => setLng(e.target.value)}
                    className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5 text-white"
                    required
                  />
                </div>
              </div>

              <button
                type="button"
                onClick={handleGetLocation}
                className="text-[11px] text-cyan-400 font-bold hover:underline"
              >
                🎯 Lấy tọa độ GPS thiết bị hiện tại
              </button>

              <div>
                <label className="font-bold text-slate-300">Nội dung mô tả hiện trường:</label>
                <textarea
                  rows={3}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Mô tả cụ thể để người dân tránh khu vực này hoặc đội cứu hộ biết tình hình..."
                  className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-xl p-2.5 text-white"
                  required
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="w-1/3 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 font-bold"
                >
                  HỦY
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-2/3 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 font-bold text-white shadow-lg shadow-cyan-600/30"
                >
                  {loading ? 'ĐANG ĐĂNG...' : 'ĐĂNG TIN THỰC TẾ'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default CommunityBoard;
