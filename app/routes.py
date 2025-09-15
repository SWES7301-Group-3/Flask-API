from flask import request, current_app
from flask_restx import Resource, fields, Namespace
from app.extensions import db, api
from app.models import User, Telemetry, UserRole
from app.subscription_auth import (
    basic_subscription_required, 
    researcher_subscription_required, 
    premium_subscription_required,
    any_valid_subscription,
    verify_subscription_token
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create namespaces with better organization
public_ns = api.namespace('public', description='Public endpoints (no subscription required)')
basic_ns = api.namespace('basic', description='Basic subscription endpoints')
research_ns = api.namespace('research', description='Research subscription endpoints')
premium_ns = api.namespace('premium', description='Premium subscription endpoints')
subscription_ns = api.namespace('subscription', description='Subscription management')

# API Models
telemetry_basic_model = api.model('TelemetryBasic', {
    'id': fields.Integer(description='Record ID'),
    'date': fields.String(description='Date'),
    'time': fields.String(description='Time'),
    'coordinates': fields.String(description='Coordinates'),
    'temperatures': fields.Raw(description='Temperature data'),
    'humidity': fields.Float(description='Humidity %')
})

telemetry_research_model = api.model('TelemetryResearch', {
    'id': fields.Integer(description='Record ID'),
    'date': fields.String(description='Date'),
    'time': fields.String(description='Time'),
    'timezone': fields.String(description='Timezone'),
    'coordinates': fields.String(description='Coordinates'),
    'temperatures': fields.Raw(description='Temperature data'),
    'humidity': fields.Float(description='Humidity %'),
    'wind': fields.Raw(description='Wind data'),
    'precipitation': fields.Float(description='Precipitation mm'),
    'haze': fields.Boolean(description='Haze condition'),
    'salinity': fields.Float(description='Salinity level'),
    'ph_level': fields.Float(description='pH level'),
    'pollutants': fields.Raw(description='Pollutant levels')
})

telemetry_premium_model = api.model('TelemetryPremium', {
    'id': fields.Integer(description='Record ID'),
    'date': fields.String(description='Date'),
    'time': fields.String(description='Time'),
    'timezone': fields.String(description='Timezone'),
    'coordinates': fields.String(description='Coordinates'),
    'temperatures': fields.Raw(description='Temperature data'),
    'humidity': fields.Float(description='Humidity %'),
    'wind': fields.Raw(description='Wind data'),
    'precipitation': fields.Float(description='Precipitation mm'),
    'haze': fields.Boolean(description='Haze condition'),
    'notes': fields.String(description='Internal notes'),
    'salinity': fields.Float(description='Salinity level'),
    'ph_level': fields.Float(description='pH level'),
    'pollutants': fields.Raw(description='Pollutant levels')
})

subscription_info_model = api.model('SubscriptionInfo', {
    'user_id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'plan_type': fields.String(description='Subscription plan type'),
    'rate_limit': fields.Integer(description='API rate limit per hour'),
    'subscription_active': fields.Boolean(description='Subscription status'),
    'days_remaining': fields.Integer(description='Days until expiration')
})

# ================= PUBLIC ENDPOINTS =================
@public_ns.route('/info')
class PublicInfo(Resource):
    def get(self):
        """Get public API information"""
        return {
            'api_name': 'Environmental Data API',
            'version': '1.0',
            'description': 'Subscription-based environmental telemetry data',
            'subscription_required': True,
            'subscription_url': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/plans/",
            'documentation': '/swagger/',
            'subscription_tiers': {
                'basic_user': {
                    'price': '$9.99/month',
                    'features': ['Basic telemetry data', '1000 API calls/hour', 'JSON responses'],
                    'data_access': ['Temperature', 'Humidity', 'Coordinates']
                },
                'researcher': {
                    'price': '$49.99/3 months', 
                    'features': ['Detailed environmental data', '5000 API calls/hour', 'Research tools'],
                    'data_access': ['All basic data', 'Salinity', 'pH levels', 'Pollutants', 'Wind data']
                },
                'premium': {
                    'price': '$199.99/year',
                    'features': ['Full data access', '10000 API calls/hour', 'Admin features'],
                    'data_access': ['All data', 'Internal notes', 'Advanced analytics', 'Admin endpoints']
                }
            }
        }

@public_ns.route('/telemetry/summary')
class PublicTelemetrySummary(Resource):
    def get(self):
        """Get public telemetry summary (limited data)"""
        from sqlalchemy import func
        stats = db.session.query(
            func.count(Telemetry.id).label('total_records'),
            func.avg(Telemetry.humidity).label('avg_humidity')
        ).first()
        
        return {
            'public_summary': {
                'total_records': stats.total_records or 0,
                'average_humidity': round(float(stats.avg_humidity), 2) if stats.avg_humidity else 0,
                'last_updated': datetime.utcnow().isoformat(),
            },
            'message': 'Subscribe for detailed data access',
            'subscription_url': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/plans/",
            'api_documentation': '/swagger/'
        }

# ================= BASIC SUBSCRIPTION ENDPOINTS =================
@basic_ns.route('/telemetry')
class BasicTelemetry(Resource):
    @basic_ns.doc(security='SubscriptionToken')
    @basic_ns.marshal_list_with(telemetry_basic_model)
    @basic_subscription_required
    def get(self):
        """Get basic telemetry data (Basic subscription required)"""
        user_info = request.current_user
        
        # Get basic telemetry data
        records = Telemetry.query.with_entities(
            Telemetry.id, Telemetry.date, Telemetry.time,
            Telemetry.coordinates, Telemetry.temperatures, Telemetry.humidity
        ).all()
        
        data = [{
            'id': r.id,
            'date': r.date.isoformat() if r.date else None,
            'time': r.time.isoformat() if r.time else None,
            'coordinates': r.coordinates,
            'temperatures': r.temperatures,
            'humidity': r.humidity
        } for r in records]
        
        return {
            'data': data,
            'subscription_info': {
                'plan_type': user_info.get('plan_type'),
                'access_level': 'basic',
                'rate_limit': user_info.get('rate_limit'),
                'records_returned': len(data)
            }
        }

@basic_ns.route('/telemetry/<int:record_id>')
class BasicTelemetryRecord(Resource):
    @basic_ns.doc(security='SubscriptionToken')
    @basic_ns.marshal_with(telemetry_basic_model)
    @basic_subscription_required
    def get(self, record_id):
        """Get single basic telemetry record"""
        record = Telemetry.query.get_or_404(record_id)
        
        return {
            'id': record.id,
            'date': record.date.isoformat() if record.date else None,
            'time': record.time.isoformat() if record.time else None,
            'coordinates': record.coordinates,
            'temperatures': record.temperatures,
            'humidity': record.humidity
        }

# ================= RESEARCH SUBSCRIPTION ENDPOINTS =================
@research_ns.route('/telemetry')
class ResearchTelemetry(Resource):
    @research_ns.doc(security='SubscriptionToken')
    @research_ns.marshal_list_with(telemetry_research_model)
    @researcher_subscription_required
    def get(self):
        """Get detailed telemetry data (Research subscription required)"""
        user_info = request.current_user
        
        records = Telemetry.query.all()
        data = [{
            'id': r.id,
            'date': r.date.isoformat() if r.date else None,
            'time': r.time.isoformat() if r.time else None,
            'timezone': r.timezone,
            'coordinates': r.coordinates,
            'temperatures': r.temperatures,
            'humidity': r.humidity,
            'wind': r.wind,
            'precipitation': r.precipitation,
            'haze': r.haze,
            'salinity': r.salinity,
            'ph_level': r.ph_level,
            'pollutants': r.pollutants
        } for r in records]
        
        return {
            'data': data,
            'subscription_info': {
                'plan_type': user_info.get('plan_type'),
                'access_level': 'research',
                'rate_limit': user_info.get('rate_limit'),
                'records_returned': len(data)
            }
        }

@research_ns.route('/analytics/salinity')
class SalinityAnalytics(Resource):
    @research_ns.doc(security='SubscriptionToken')
    @researcher_subscription_required
    def get(self):
        """Get salinity analytics (Research subscription required) - SQLite Compatible"""
        from sqlalchemy import func
        
        # SQLite-compatible query (no stddev function)
        stats = db.session.query(
            func.count(Telemetry.salinity).label('sample_count'),
            func.avg(Telemetry.salinity).label('avg_salinity'),
            func.min(Telemetry.salinity).label('min_salinity'),
            func.max(Telemetry.salinity).label('max_salinity')
        ).filter(Telemetry.salinity.isnot(None)).first()
        
        return {
            'salinity_analytics': {
                'sample_count': stats.sample_count or 0,
                'average': round(float(stats.avg_salinity), 3) if stats.avg_salinity else 0,
                'minimum': float(stats.min_salinity) if stats.min_salinity else 0,
                'maximum': float(stats.max_salinity) if stats.max_salinity else 0,
                'standard_deviation': 'Not available in SQLite',  # Temporary
                'note': 'Using SQLite-compatible functions'
            },
            'subscription_info': {
                'access_level': 'research_analytics',
                'plan_type': request.current_user.get('plan_type')
            }
        }

# ================= PREMIUM SUBSCRIPTION ENDPOINTS =================
@premium_ns.route('/telemetry/full')
class PremiumTelemetry(Resource):
    @premium_ns.doc(security='SubscriptionToken')
    @premium_ns.marshal_list_with(telemetry_premium_model)
    @premium_subscription_required
    def get(self):
        """Get full telemetry data including notes (Premium subscription required)"""
        user_info = request.current_user
        
        records = Telemetry.query.all()
        data = [{
            'id': r.id,
            'date': r.date.isoformat() if r.date else None,
            'time': r.time.isoformat() if r.time else None,
            'timezone': r.timezone,
            'coordinates': r.coordinates,
            'temperatures': r.temperatures,
            'humidity': r.humidity,
            'wind': r.wind,
            'precipitation': r.precipitation,
            'haze': r.haze,
            'notes': r.notes,  # Only available in premium
            'salinity': r.salinity,
            'ph_level': r.ph_level,
            'pollutants': r.pollutants
        } for r in records]
        
        return {
            'data': data,
            'subscription_info': {
                'plan_type': user_info.get('plan_type'),
                'access_level': 'premium',
                'rate_limit': user_info.get('rate_limit'),
                'records_returned': len(data),
                'includes_notes': True
            }
        }

@premium_ns.route('/analytics/advanced')
class AdvancedAnalytics(Resource):
    @premium_ns.doc(security='SubscriptionToken')
    @premium_subscription_required
    def get(self):
        """Get advanced analytics (Premium subscription ONLY)"""
        
        # This should never be reached by non-premium users due to the decorator
        # But let's add a safety check with proper JSON response
        user_info = getattr(request, 'current_user', {})
        
        if user_info.get('plan_type') != 'premium':
            # Safety net - should never execute due to decorator
            logger.error(f"SECURITY BYPASS DETECTED: {user_info.get('username')} reached premium endpoint")
            
            return {
                'error': 'Security Bypass Detected',
                'error_code': 'DECORATOR_BYPASS_VIOLATION',
                'message': 'Premium subscription required - security violation detected',
                'timestamp': '2025-09-10 21:20:21',
                'github_user': 'NeduStack',
                'security_alert': {
                    'user': user_info.get('username', 'Unknown'),
                    'plan': user_info.get('plan_type', 'Unknown'),
                    'role': user_info.get('role', 'Unknown'),
                    'endpoint': '/premium/analytics/advanced',
                    'expected_plan': 'premium',
                    'violation_type': 'decorator_bypass'
                },
                'immediate_action_required': {
                    'contact_support': 'support@swes7301-group3.com',
                    'report_issue': 'https://github.com/SWES7301-Group-3/Flask-API/issues'
                }
            }, 403
        
        # Premium analytics logic here
        try:
            from sqlalchemy import func
            
            total_records = int(db.session.query(func.count(Telemetry.id)).scalar() or 0)
            
            return {
                'premium_analytics': {
                    'success': True,
                    'total_records': total_records,
                    'analysis_level': 'premium',
                    'user_verification': {
                        'username': user_info.get('username'),
                        'plan': user_info.get('plan_name'),
                        'plan_type': user_info.get('plan_type'),
                        'access_confirmed': True
                    }
                },
                'timestamp': '2025-09-10 21:20:21',
                'github_user': 'NeduStack'
            }
            
        except Exception as e:
            return {
                'error': 'Premium Analytics Processing Error',
                'message': str(e),
                'timestamp': '2025-09-10 21:20:21',
                'github_user': 'NeduStack'
            }, 500


# ================= SUBSCRIPTION MANAGEMENT =================
@subscription_ns.route('/info')
class SubscriptionInfo(Resource):
    @subscription_ns.doc(security='SubscriptionToken')
    @subscription_ns.marshal_with(subscription_info_model)
    @any_valid_subscription
    def get(self):
        """Get your subscription information"""
        user_info = request.current_user
        
        return {
            'subscription_details': {
                'user_id': user_info.get('user_id'),
                'username': user_info.get('username'),
                'email': user_info.get('email'),
                'plan_type': user_info.get('plan_type'),
                'plan_name': user_info.get('plan_name'),
                'role': user_info.get('role'),
                'rate_limit': user_info.get('rate_limit'),
                'subscription_active': user_info.get('subscription_active'),
                'days_remaining': user_info.get('days_remaining'),
                'features': user_info.get('features', [])
            },
            'api_access': {
                'basic_endpoints': ['/basic/telemetry'],
                'research_endpoints': ['/research/telemetry', '/research/analytics/*'] if user_info.get('role') in ['researcher', 'admin'] else [],
                'premium_endpoints': ['/premium/telemetry/full', '/premium/analytics/advanced'] if user_info.get('role') == 'admin' else []
            },
            'subscription_management': {
                'dashboard_url': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/my-subscriptions/",
                'upgrade_url': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/plans/",
                'support_url': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/dashboard/"
            }
        }

@subscription_ns.route('/test-token')
class TestToken(Resource):
    @subscription_ns.doc(security='SubscriptionToken')
    @any_valid_subscription
    def get(self):
        """Test your subscription token"""
        user_info = request.current_user
        
        return {
            'token_status': 'valid',
            'verified_at': datetime.utcnow().isoformat(),
            'user_details': {
                'username': user_info.get('username'),
                'plan_type': user_info.get('plan_type'),
                'role': user_info.get('role'),
                'subscription_active': user_info.get('subscription_active')
            },
            'access_permissions': {
                'can_access_basic': True,
                'can_access_research': user_info.get('role') in ['researcher', 'admin'],
                'can_access_premium': user_info.get('role') == 'admin'
            },
            'rate_limit_info': {
                'hourly_limit': user_info.get('rate_limit'),
                'current_usage': 0  # You can implement usage tracking
            }
        }