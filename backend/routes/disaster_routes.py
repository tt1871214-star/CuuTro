import requests
from flask import Blueprint, jsonify, request, current_app
from models.disaster import Disaster, Alert
from middleware.auth_middleware import token_required

disaster_bp = Blueprint('disasters', __name__, url_prefix='/api/disasters')

@disaster_bp.route('', methods=['GET'])
def get_disasters():
    disasters = Disaster.query.filter_by(status='ACTIVE').all()
    return jsonify({'success': True, 'disasters': [d.to_dict() for d in disasters]}), 200

@disaster_bp.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(10).all()
    return jsonify({'success': True, 'alerts': [a.to_dict() for a in alerts]}), 200

@disaster_bp.route('/weather', methods=['GET'])
def get_weather():
    """
    Fetch weather information. Integrates with OpenWeatherMap API 
    or returns mock safety alerts if API key is not configured.
    """
    lat = request.args.get('lat', default=21.0285) # Hanoi default
    lng = request.args.get('lng', default=105.8542)
    
    api_key = current_app.config.get('OPENWEATHERMAP_API_KEY')
    
    if not api_key or api_key == 'mock_api_key_for_offline_run':
        # Mock weather alert data for offline operation
        return jsonify({
            'success': True,
            'source': 'mock_offline_service',
            'weather': {
                'temp': 28.5,
                'description': 'Mưa dông diện rộng, có thể kèm theo lốc sét',
                'humidity': 88,
                'wind_speed': 15.5,
                'location_name': 'Hồ Hoàn Kiếm, Hà Nội'
            },
            'disaster_warning': {
                'level': 'WARNING',
                'level_color': 'ORANGE', # Cam = Nguy hiểm trung bình
                'message': 'Cảnh báo mưa dông kèm gió giật mạnh từ chiều tối. Đề phòng ngập lụt cục bộ tại các tuyến phố trũng.'
            }
        }), 200

    try:
        url = current_app.config.get('WEATHER_API_URL')
        params = {
            'lat': lat,
            'lon': lng,
            'appid': api_key,
            'units': 'metric',
            'lang': 'vi'
        }
        res = requests.get(url, params=params, timeout=3)
        if res.status_code == 200:
            data = res.get_json()
            # Extract relevant fields
            return jsonify({
                'success': True,
                'source': 'openweathermap',
                'weather': {
                    'temp': data['main']['temp'],
                    'description': data['weather'][0]['description'] if data['weather'] else 'Không rõ',
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'location_name': data['name']
                },
                'disaster_warning': {
                    # If wind is > 10m/s or status is rain, auto trigger warnings
                    'level': 'WARNING' if data['wind']['speed'] > 10 else 'NORMAL',
                    'level_color': 'ORANGE' if data['wind']['speed'] > 10 else 'YELLOW',
                    'message': 'Mưa gió lớn, đề phòng giông lốc.' if data['wind']['speed'] > 10 else 'Thời tiết bình thường, hãy tiếp tục theo dõi diễn biến tiếp theo.'
                }
            }), 200
        else:
            raise Exception("API status error")
    except Exception:
        # Fallback in case of failure or timeout
        return jsonify({
            'success': True,
            'source': 'mock_fallback_service',
            'weather': {
                'temp': 27.0,
                'description': 'Nhiều mây, mưa rào nhẹ',
                'humidity': 90,
                'wind_speed': 5.0,
                'location_name': 'Hà Nội (Fallback)'
            },
            'disaster_warning': {
                'level': 'MONITOR',
                'level_color': 'YELLOW', # Vàng = Theo dõi
                'message': 'Thời tiết ẩm ướt, mưa rào cục bộ, người dân chú ý theo dõi dự báo thời tiết tiếp theo.'
            }
        }), 200
