import React, { useState, useEffect } from 'react';
import { Shield, Flame, HeartPulse, PhoneCall, ChevronUp, ChevronDown } from 'lucide-react';
import api from '../services/api';

const EmergencyContacts = () => {
  const [contacts, setContacts] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  // Default hardcoded contacts for offline/first-run safety
  const defaultContacts = [
    { id: 1, name: '113 Công an', phone: '113', icon_type: 'shield' },
    { id: 2, name: '114 Cứu hỏa & Cứu nạn', phone: '114', icon_type: 'flame' },
    { id: 3, name: '115 Cấp cứu y tế', phone: '115', icon_type: 'heart-pulse' },
    { id: 4, name: 'Đường dây nóng Thiên tai', phone: '18001022', icon_type: 'phone-call' }
  ];

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const res = await api.get('/api/emergency/contacts');
        if (res.data && res.data.success) {
          setContacts(res.data.contacts);
        } else {
          setContacts(defaultContacts);
        }
      } catch (err) {
        console.warn("Lỗi tải danh bạ từ backend, chuyển sang ngoại tuyến:", err);
        setContacts(defaultContacts);
      }
    };
    fetchContacts();
  }, []);

  const getIcon = (type) => {
    switch (type) {
      case 'shield':
        return <Shield className="w-5 h-5 text-blue-400" />;
      case 'flame':
        return <Flame className="w-5 h-5 text-red-400" />;
      case 'heart-pulse':
        return <HeartPulse className="w-5 h-5 text-emerald-400" />;
      default:
        return <PhoneCall className="w-5 h-5 text-amber-400" />;
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[1000] flex flex-col items-end">
      {/* Expanded Contact List */}
      {isOpen && (
        <div className="mb-3 w-72 glass-card rounded-xl p-4 shadow-2xl animate-fade-in border border-white/10 overflow-hidden">
          <h3 className="font-bold text-base mb-3 text-red-400 flex items-center gap-2">
            <span className="animate-ping w-2.5 h-2.5 rounded-full bg-red-500 inline-block"></span>
            ĐƯỜNG DÂY NÓNG KHẨN CẤP
          </h3>
          <div className="flex flex-col gap-2.5">
            {contacts.map((c) => (
              <a
                key={c.id}
                href={`tel:${c.phone}`}
                className="flex items-center justify-between p-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-black/30 group-hover:scale-110 transition-transform">
                    {getIcon(c.icon_type)}
                  </div>
                  <div>
                    <p className="font-semibold text-sm text-white">{c.name}</p>
                    <p className="text-[11px] text-gray-400">Bấm để gọi điện trực tiếp</p>
                  </div>
                </div>
                <span className="px-2.5 py-1 text-xs font-black rounded-full bg-red-500/20 text-red-400 group-hover:bg-red-500 group-hover:text-white transition-colors">
                  {c.phone}
                </span>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Trigger SOS Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-5 py-3 rounded-full font-bold shadow-2xl transition-all duration-300 transform hover:scale-105 active:scale-95 ${
          isOpen 
            ? 'bg-gray-800 text-white border border-white/10' 
            : 'bg-red-600 text-white animate-pulse-sos hover:bg-red-500'
        }`}
      >
        <PhoneCall className="w-5 h-5" />
        <span>{isOpen ? 'Đóng cuộc gọi' : 'GỌI KHẨN CẤP (SOS)'}</span>
        {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
      </button>
    </div>
  );
};

export default EmergencyContacts;
