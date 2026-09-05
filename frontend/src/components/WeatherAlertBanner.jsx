import React, { useState, useEffect } from 'react';
import { CloudRain, Wind, AlertTriangle, RefreshCw, ShieldCheck } from 'lucide-react';
import api from '../services/api';

const WeatherAlertBanner = () => {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchWeather = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/alerts/weather-live?lat=21.0285&lng=105.8542');
      if (res.data) {
        setWeather(res.data);
      }
    } catch (err) {
      console.warn("Lỗi tải thông tin thời tiết Open-Meteo:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeather();
    const interval = setInterval(fetchWeather, 60000); // 1 minute
    return () => clearInterval(interval);
  }, []);

  if (!weather) return null;

  const isRed = weather.alert_level === 'RED';
  const isOrange = weather.alert_level === 'ORANGE';

  const bannerBg = isRed
    ? 'bg-gradient-to-r from-red-950/90 via-red-900/80 to-rose-950/90 border-red-500/50 text-red-200'
    : isOrange
    ? 'bg-gradient-to-r from-orange-950/90 via-amber-900/80 to-yellow-950/90 border-orange-500/50 text-orange-200'
    : 'bg-gradient-to-r from-slate-900/90 via-slate-800/80 to-slate-900/90 border-slate-700/60 text-slate-300';

  return (
    <div className={`w-full rounded-2xl border p-4 shadow-xl backdrop-blur-md transition-all ${bannerBg}`}>
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-xl border ${isRed ? 'bg-red-500/20 border-red-500/40 text-red-400 animate-pulse' : isOrange ? 'bg-orange-500/20 border-orange-500/40 text-orange-400' : 'bg-blue-500/20 border-blue-500/40 text-blue-400'}`}>
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-wider px-2 py-0.5 rounded bg-black/40 border border-white/10">
                {weather.source}
              </span>
              <span className="font-extrabold text-sm text-white">{weather.weather_description}</span>
            </div>
            <p className="text-xs mt-1 text-slate-200">{weather.safety_guideline}</p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-medium self-end md:self-center">
          <div className="flex items-center gap-1.5 bg-black/30 px-3 py-1.5 rounded-lg border border-white/10">
            <CloudRain className="w-4 h-4 text-blue-400" />
            <span>Mưa: <b>{weather.precipitation || 0} mm</b></span>
          </div>
          <div className="flex items-center gap-1.5 bg-black/30 px-3 py-1.5 rounded-lg border border-white/10">
            <Wind className="w-4 h-4 text-cyan-400" />
            <span>Gió: <b>{weather.wind_speed || 0} km/h</b></span>
          </div>
          <button
            onClick={fetchWeather}
            disabled={loading}
            className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 transition text-white"
            title="Làm mới thời tiết"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default WeatherAlertBanner;
