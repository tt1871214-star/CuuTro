import { useState, useEffect } from 'react';

export const useLocation = (autoFetch = false) => {
  const [coords, setCoords] = useState({ latitude: null, longitude: null });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const getLocation = () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        const errStr = 'Định vị GPS không được hỗ trợ bởi trình duyệt của bạn.';
        setError(errStr);
        reject(errStr);
        return;
      }

      setLoading(true);
      setError(null);

      // High accuracy options for emergency coordination
      const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      };

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const newCoords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          setCoords(newCoords);
          setLoading(false);
          resolve(newCoords);
        },
        (err) => {
          let errMsg = 'Không thể lấy được vị trí GPS.';
          if (err.code === err.PERMISSION_DENIED) {
            errMsg = 'Người dùng từ chối cấp quyền truy cập GPS.';
          } else if (err.code === err.POSITION_UNAVAILABLE) {
            errMsg = 'Vị trí GPS không khả dụng.';
          } else if (err.code === err.TIMEOUT) {
            errMsg = 'Hết thời gian lấy tọa độ GPS.';
          }
          setError(errMsg);
          setLoading(false);
          reject(errMsg);
        },
        options
      );
    });
  };

  useEffect(() => {
    if (autoFetch) {
      getLocation().catch(console.error);
    }
  }, [autoFetch]);

  return { coords, error, loading, getLocation };
};
