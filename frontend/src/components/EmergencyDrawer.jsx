import React, { useState, useEffect } from 'react';
import { PhoneCall, ShieldAlert, Flame, Shield, X } from 'lucide-react';
import api from '../services/api';

const EmergencyDrawer = ({ isOpen, onClose }) => {
  const [contacts, setContacts] = useState([]);

  useEffect(() => {
    if (isOpen) {
      api.get('/api/emergency-contacts').then(res => {
        if (res.data) setContacts(res.data);
      }).catch(err => console.warn(err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-700 rounded-3xl p-6 shadow-2xl text-white">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-red-500/20 text-red-400 border border-red-500/30">
              <PhoneCall className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-base text-white">DANH BẠ CỨU NẠN KHẨN CẤP</h3>
              <p className="text-xs text-slate-400">Gọi miễn cước 24/7 trong mọi tình huống thiên tai</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-4 space-y-2.5 max-h-[60vh] overflow-y-auto">
          {contacts.map(c => (
            <div key={c.id} className="p-3 bg-slate-800/80 hover:bg-slate-800 rounded-2xl border border-slate-700/60 flex items-center justify-between transition">
              <div>
                <div className="font-bold text-sm text-white">{c.name}</div>
                <div className="text-xs text-slate-400 mt-0.5">{c.description}</div>
              </div>
              <a
                href={`tel:${c.phone}`}
                className="px-3.5 py-2 rounded-xl bg-red-600 hover:bg-red-500 font-black text-sm text-white flex items-center gap-1.5 shadow-lg shadow-red-600/30"
              >
                <PhoneCall className="w-3.5 h-3.5" />
                {c.phone}
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EmergencyDrawer;
