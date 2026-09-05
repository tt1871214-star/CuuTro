from flask import Blueprint, jsonify
from database.db import db
from models.user import User
from models.rescue import RescueRequest, RescueTeam
from models.community import CommunityPost
from models.disaster import Disaster
from middleware.auth_middleware import token_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_dashboard_stats():
    """
    Compute system-wide dashboard statistics and heatmap coordinates.
    """
    # 1. Rescue requests stats
    total_requests = RescueRequest.query.count()
    waiting_requests = RescueRequest.query.filter_by(status='WAITING').count()
    received_requests = RescueRequest.query.filter_by(status='RECEIVED').count()
    moving_requests = RescueRequest.query.filter_by(status='MOVING').count()
    completed_requests = RescueRequest.query.filter_by(status='COMPLETED').count()
    cancelled_requests = RescueRequest.query.filter_by(status='CANCELLED').count()
    
    # 2. General user counts
    total_users = User.query.count()
    total_teams = RescueTeam.query.count()
    
    # 3. Community posts stats
    total_posts = CommunityPost.query.count()
    total_verified_posts = CommunityPost.query.filter_by(verification_status='VERIFIED').count()

    # 4. Generate Heatmap data for danger spots
    # Mix of active disasters and verified danger posts (FLOOD, LANDSLIDE, DANGER_ZONE)
    heatmap_data = []
    
    # Active disasters (High weight = 1.0)
    active_disasters = Disaster.query.filter_by(status='ACTIVE').all()
    for d in active_disasters:
        weight = 1.0 if d.alert_level == 'RED' else (0.7 if d.alert_level == 'ORANGE' else 0.4)
        heatmap_data.append({
            'lat': d.latitude,
            'lng': d.longitude,
            'weight': weight,
            'label': f"Thiên tai: {d.title}"
        })
        
    # Danger community posts that are VERIFIED (Medium weight = 0.5 - 0.8)
    verified_danger_posts = CommunityPost.query.filter_by(
        verification_status='VERIFIED'
    ).filter(
        CommunityPost.post_type.in_(['FLOOD', 'LANDSLIDE', 'DANGER_ZONE', 'BRIDGE_DAMAGE'])
    ).all()
    
    for p in verified_danger_posts:
        weight = 0.8 if p.post_type == 'LANDSLIDE' else 0.6
        heatmap_data.append({
            'lat': p.latitude,
            'lng': p.longitude,
            'weight': weight,
            'label': f"Nguy hiểm ({p.post_type}): {p.title}"
        })

    return jsonify({
        'success': True,
        'stats': {
            'rescue': {
                'total': total_requests,
                'waiting': waiting_requests,
                'processing': received_requests + moving_requests, # received/moving combined for active handling
                'completed': completed_requests,
                'cancelled': cancelled_requests,
                'received': received_requests,
                'moving': moving_requests
            },
            'users': {
                'total_users': total_users,
                'total_rescue_teams': total_teams
            },
            'community': {
                'total_posts': total_posts,
                'verified_posts': total_verified_posts
            }
        },
        'heatmap': heatmap_data
    }), 200
