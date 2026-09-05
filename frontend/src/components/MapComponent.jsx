import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

const MapComponent = ({
  center = [21.0285, 105.8542],
  zoom = 12,
  zones = [],
  requests = [],
  assemblyPoints = [],
  rescueTeams = [],
  userLocation = null,
  onMapClick = null,
  selectedLocation = null
}) => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const zonesLayerRef = useRef(null);
  const requestsLayerRef = useRef(null);
  const assemblyLayerRef = useRef(null);
  const teamsLayerRef = useRef(null);
  const userMarkerRef = useRef(null);
  const selectedMarkerRef = useRef(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapRef.current) {
      mapRef.current = L.map(mapContainerRef.current, {
        zoomControl: true,
        attributionControl: false
      }).setView(center, zoom);

      // High-contrast dark tile layer (ideal for emergency red/orange/yellow visibility)
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19
      }).addTo(mapRef.current);

      zonesLayerRef.current = L.layerGroup().addTo(mapRef.current);
      requestsLayerRef.current = L.layerGroup().addTo(mapRef.current);
      assemblyLayerRef.current = L.layerGroup().addTo(mapRef.current);
      teamsLayerRef.current = L.layerGroup().addTo(mapRef.current);

      if (onMapClick) {
        mapRef.current.on('click', (e) => {
          onMapClick({
            latitude: Number(e.latlng.lat.toFixed(6)),
            longitude: Number(e.latlng.lng.toFixed(6))
          });
        });
      }
    } else {
      mapRef.current.setView(center, mapRef.current.getZoom());
    }
  }, [center]);

  // Render Zones (Vàng / Cam / Đỏ theo số lượng yêu cầu cứu trợ)
  useEffect(() => {
    if (!mapRef.current || !zonesLayerRef.current) return;
    zonesLayerRef.current.clearLayers();

    zones.forEach(z => {
      if (!z.center_lat || !z.center_lng) return;

      let strokeColor = '#EAB308'; // YELLOW
      let fillColor = '#FACC15';
      let fillOpacity = 0.22;
      let badgeBg = 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40';
      let statusText = 'Zone Vàng (Cần hỗ trợ)';

      if (z.status === 'RED') {
        strokeColor = '#EF4444';
        fillColor = '#DC2626';
        fillOpacity = 0.40;
        badgeBg = 'bg-red-500/20 text-red-300 border-red-500/40';
        statusText = 'Zone Đỏ (Nhu cầu hỗ trợ rất cao)';
      } else if (z.status === 'ORANGE') {
        strokeColor = '#F97316';
        fillColor = '#EA580C';
        fillOpacity = 0.32;
        badgeBg = 'bg-orange-500/20 text-orange-300 border-orange-500/40';
        statusText = 'Zone Cam (Nhu cầu hỗ trợ cao)';
      }

      // Draw Zone Circle
      const circle = L.circle([z.center_lat, z.center_lng], {
        color: strokeColor,
        weight: z.status === 'RED' ? 3 : 2,
        fillColor: fillColor,
        fillOpacity: fillOpacity,
        radius: (z.radius_km || 5.0) * 1000
      });

      const popupHtml = `
        <div class="p-3 text-slate-100 font-sans min-w-[220px]">
          <div class="flex items-center justify-between gap-2 mb-1.5">
            <span class="font-black text-xs tracking-wider px-2 py-0.5 rounded border ${badgeBg}">${z.code}</span>
            <span class="text-[11px] font-bold text-slate-300">${z.request_count || 0} yêu cầu</span>
          </div>
          <h4 class="font-extrabold text-sm text-white mb-1">${z.name}</h4>
          <p class="text-xs text-slate-300 mb-2">${z.description || 'Khu vực quản lý và điều phối thiên tai'}</p>
          <div class="text-[11px] font-semibold text-slate-400 border-t border-slate-700/60 pt-1.5 flex justify-between">
            <span>Bán kính: ${z.radius_km} km</span>
            <span class="font-bold">${statusText}</span>
          </div>
        </div>
      `;

      circle.bindPopup(popupHtml);
      circle.addTo(zonesLayerRef.current);
    });
  }, [zones]);

  // Render Assembly Points & Refuges (Điểm tập kết & Nơi trú ẩn)
  useEffect(() => {
    if (!mapRef.current || !assemblyLayerRef.current) return;
    assemblyLayerRef.current.clearLayers();

    assemblyPoints.forEach(p => {
      if (!p.latitude || !p.longitude) return;

      const isRefuge = p.point_type === 'REFUGE';
      const iconHtml = `
        <div class="w-8 h-8 rounded-xl ${isRefuge ? 'bg-teal-500' : 'bg-emerald-500'} border-2 border-white flex items-center justify-center shadow-lg shadow-emerald-950/60 transform hover:scale-110 transition-transform">
          <span class="text-sm">${isRefuge ? '🛡️' : '⛺'}</span>
        </div>
      `;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'custom-map-icon',
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      const marker = L.marker([p.latitude, p.longitude], { icon: customIcon });
      marker.bindPopup(`
        <div class="p-2.5 text-slate-100 min-w-[200px]">
          <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-400 mb-1">
            <span>${isRefuge ? '🛡️ NƠI TRÚ ẨN KIÊN CỐ' : '⛺ ĐIỂM TẬP KẾT ỨNG CỨU'}</span>
          </div>
          <h4 class="font-bold text-sm text-white mb-1">${p.name}</h4>
          <p class="text-xs text-slate-300 mb-1.5">📍 ${p.address}</p>
          <div class="text-xs text-slate-400 border-t border-slate-700 pt-1.5 space-y-0.5">
            <div>Sức chứa: <b>${p.capacity} người</b></div>
            ${p.contact_person ? `<div>Phụ trách: ${p.contact_person} - ${p.contact_phone || ''}</div>` : ''}
          </div>
        </div>
      `);
      marker.addTo(assemblyLayerRef.current);
    });
  }, [assemblyPoints]);

  // Render Rescue Requests
  useEffect(() => {
    if (!mapRef.current || !requestsLayerRef.current) return;
    requestsLayerRef.current.clearLayers();

    requests.forEach(r => {
      if (!r.latitude || !r.longitude) return;

      let bgColor = 'bg-red-600';
      let pingEffect = '<span class="absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75 animate-ping"></span>';
      
      if (r.status === 'COMPLETED') {
        bgColor = 'bg-emerald-500';
        pingEffect = '';
      } else if (r.status === 'IN_PROGRESS') {
        bgColor = 'bg-blue-500';
      } else if (r.status === 'ACCEPTED') {
        bgColor = 'bg-amber-500';
      }

      const iconHtml = `
        <div class="relative flex items-center justify-center w-7 h-7 rounded-full border-2 border-white ${bgColor} shadow-lg">
          ${r.status === 'PENDING' ? pingEffect : ''}
          <span class="text-[10px] font-black text-white">SOS</span>
        </div>
      `;

      const marker = L.marker([r.latitude, r.longitude], {
        icon: L.divIcon({
          html: iconHtml,
          className: 'custom-map-icon',
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        })
      });

      marker.bindPopup(`
        <div class="p-2.5 text-slate-100 min-w-[210px]">
          <div class="flex items-center justify-between text-xs font-bold mb-1">
            <span class="text-red-400">🚨 ${r.relief_type || 'CỨU TRỢ'}</span>
            <span class="px-1.5 py-0.5 rounded text-[10px] bg-white/10">${r.status}</span>
          </div>
          <div class="text-xs font-bold text-white mb-1">Người gửi: ${r.sender_name || 'Người dân'} (${r.sender_phone || ''})</div>
          <p class="text-xs text-slate-300 mb-2">${r.description || 'Cần hỗ trợ khẩn cấp'}</p>
          <div class="text-[10px] text-slate-400 border-t border-slate-700 pt-1">
            Mức khẩn cấp: <span class="font-bold text-amber-300">${r.personal_urgency}</span>
            ${r.assigned_team_name ? `<br/>Đội cứu hộ: <span class="text-cyan-300 font-bold">${r.assigned_team_name}</span>` : ''}
          </div>
        </div>
      `);
      marker.addTo(requestsLayerRef.current);
    });
  }, [requests]);

  // Render Rescue Teams
  useEffect(() => {
    if (!mapRef.current || !teamsLayerRef.current) return;
    teamsLayerRef.current.clearLayers();

    rescueTeams.forEach(t => {
      if (!t.current_lat || !t.current_lng) return;

      const iconHtml = `
        <div class="w-8 h-8 rounded-full bg-cyan-600 border-2 border-white flex items-center justify-center shadow-lg shadow-cyan-900/50">
          <span class="text-xs">🚤</span>
        </div>
      `;

      const marker = L.marker([t.current_lat, t.current_lng], {
        icon: L.divIcon({
          html: iconHtml,
          className: 'custom-map-icon',
          iconSize: [32, 32],
          iconAnchor: [16, 16]
        })
      });

      marker.bindPopup(`
        <div class="p-2.5 text-slate-100 min-w-[190px]">
          <div class="text-xs font-bold text-cyan-400 mb-0.5">🚤 ĐỘI CỨU HỘ</div>
          <h4 class="font-extrabold text-sm text-white mb-1">${t.team_name}</h4>
          <div class="text-xs text-slate-300">Đội trưởng: ${t.leader_name}</div>
          <div class="text-xs text-slate-300">Liên hệ: <a href="tel:${t.contact_phone}" class="text-cyan-300 underline font-bold">${t.contact_phone}</a></div>
          <div class="text-[10px] text-slate-400 mt-1">Trạng thái: <span class="text-emerald-400 font-bold">${t.status}</span></div>
        </div>
      `);
      marker.addTo(teamsLayerRef.current);
    });
  }, [rescueTeams]);

  // Selected Pin for SOS location selection
  useEffect(() => {
    if (!mapRef.current) return;
    if (selectedMarkerRef.current) {
      mapRef.current.removeLayer(selectedMarkerRef.current);
      selectedMarkerRef.current = null;
    }

    if (selectedLocation && selectedLocation.latitude && selectedLocation.longitude) {
      const pinHtml = `
        <div class="relative flex items-center justify-center w-8 h-8 rounded-full bg-red-600 border-2 border-white shadow-xl animate-bounce">
          <span class="text-sm">📍</span>
        </div>
      `;
      selectedMarkerRef.current = L.marker([selectedLocation.latitude, selectedLocation.longitude], {
        icon: L.divIcon({
          html: pinHtml,
          className: 'custom-pin',
          iconSize: [32, 32],
          iconAnchor: [16, 32]
        })
      }).addTo(mapRef.current);
    }
  }, [selectedLocation]);

  return (
    <div className="relative w-full h-full min-h-[450px] rounded-2xl overflow-hidden border border-slate-700/60 shadow-2xl">
      <div ref={mapContainerRef} className="w-full h-full absolute inset-0 z-0" />
      
      {/* Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 z-10 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-xl p-2.5 text-xs text-slate-300 shadow-xl space-y-1">
        <div class="font-bold text-white text-[11px] mb-1">CHÚ GIẢI BẢN ĐỒ CỨU HỘ</div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-yellow-500 inline-block"></span>
          <span>Zone Vàng (Cần hỗ trợ)</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-orange-500 inline-block"></span>
          <span>Zone Cam (Hỗ trợ cao)</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-red-500 inline-block"></span>
          <span>Zone Đỏ (Rất khẩn cấp)</span>
        </div>
        <div class="flex items-center gap-2 pt-0.5">
          <span class="text-xs">🛡️</span>
          <span>Nơi trú ẩn / Điểm tập kết</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs">🚤</span>
          <span>Đội cứu hộ đang trực</span>
        </div>
      </div>
    </div>
  );
};

export default MapComponent;
