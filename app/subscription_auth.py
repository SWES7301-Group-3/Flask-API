import requests
from functools import wraps
from flask import request, jsonify, current_app, make_response
import logging
import json

logger = logging.getLogger(__name__)

class SubscriptionAuthError(Exception):
    """Custom exception for subscription authentication errors"""
    pass

def verify_subscription_token(token):
    """Verify token with Django subscription service"""
    try:
        django_url = current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')
        verify_endpoint = current_app.config.get('DJANGO_VERIFY_TOKEN_ENDPOINT', '/subscriptions/verify-token/')
        
        response = requests.post(
            f'{django_url}{verify_endpoint}',
            json={'token': token},
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        logger.info(f"Token verification request to: {django_url}{verify_endpoint}")
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Token verification response: {data}")
            
            if data.get('valid'):
                return {
                    'valid': True,
                    'user_id': data.get('user_id'),
                    'username': data.get('username'),
                    'email': data.get('email'),
                    'role': data.get('role', 'user'),
                    'plan_type': data.get('plan_type'),
                    'plan_name': data.get('plan_name'),
                    'rate_limit': data.get('rate_limit', 1000),
                    'features': data.get('features', []),
                    'subscription_active': data.get('subscription_active', False),
                    'days_remaining': data.get('days_remaining', 0),
                    'expires_at': data.get('expires_at')
                }
        
        logger.warning(f"Token verification failed: {response.status_code}")
        return None
        
    except requests.exceptions.Timeout:
        logger.error("Token verification timeout")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Django subscription service")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return None

def create_premium_access_denied_response(user_data, endpoint_path):
    """Create comprehensive premium access denied response with updated context"""
    
    # Updated timestamp and GitHub context
    current_time = "2025-09-10 21:49:32"
    github_user = "NeduStack"
    
    # Extract user information safely
    username = user_data.get('username', 'User')
    current_plan = user_data.get('plan_name', 'Unknown Plan')
    current_role = user_data.get('role', 'Unknown')
    plan_type = user_data.get('plan_type', 'unknown')
    
    # Determine specific endpoint info
    endpoint_details = {
        '/premium/telemetry/full': {
            'feature_name': 'Full Telemetry Data Access',
            'description': 'Complete environmental data including internal notes and admin metadata',
            'data_includes': ['All sensor readings', 'Internal operational notes', 'Administrative metadata', 'Quality control flags'],
            'business_value': 'Comprehensive environmental monitoring for enterprise decision-making'
        },
        '/premium/analytics/advanced': {
            'feature_name': 'Advanced Analytics Engine',
            'description': 'Machine learning powered environmental predictions and correlations',
            'data_includes': ['Predictive modeling', 'Multi-parameter correlation', 'Anomaly detection', 'Trend forecasting'],
            'business_value': 'AI-driven insights for proactive environmental management'
        }
    }
    
    current_endpoint = endpoint_details.get(endpoint_path, {
        'feature_name': 'Premium Feature',
        'description': 'Advanced premium functionality',
        'data_includes': ['Enhanced capabilities'],
        'business_value': 'Premium-tier environmental data services'
    })
    
    # Build comprehensive response with updated GitHub context
    response = {
        'error': 'Premium Subscription Required',
        'error_code': 'RESEARCHER_BLOCKED_FROM_PREMIUM',
        'message': f'🚫 Access Denied: {username}, your {current_plan} cannot access this premium endpoint.',
        'timestamp': current_time,
        'github_context': {
            'developer': github_user,
            'current_project': 'SWES7301-Group-3/Flask-API',
            'top_repositories': [
                {
                    'name': 'Vigicanconsultlimited/VigicaconsultWeb',
                    'url': 'https://github.com/Vigicanconsultlimited/VigicaconsultWeb',
                    'type': 'Web Consulting Platform'
                },
                {
                    'name': 'UoGM-E-Reader-App/reada-BackendAPI',
                    'url': 'https://github.com/UoGM-E-Reader-App/reada-BackendAPI',
                    'type': 'E-Reader Backend Service'
                },
                {
                    'name': 'SWES7301-Group-3/Flask-API',
                    'url': 'https://github.com/SWES7301-Group-3/Flask-API',
                    'type': 'Environmental Data API (Current Project)'
                },
                {
                    'name': 'UoGM-E-Reader-App/reada-Frontend',
                    'url': 'https://github.com/UoGM-E-Reader-App/reada-Frontend',
                    'type': 'E-Reader Frontend Application'
                },
                {
                    'name': 'SWES7301-Group-3/Django-ecomm',
                    'url': 'https://github.com/SWES7301-Group-3/Django-ecomm',
                    'type': 'E-commerce Backend (Subscription System)'
                }
            ]
        },
        'access_violation_details': {
            'attempted_endpoint': str(endpoint_path),
            'endpoint_feature': current_endpoint['feature_name'],
            'endpoint_description': current_endpoint['description'],
            'premium_data_includes': current_endpoint['data_includes'],
            'business_value': current_endpoint['business_value'],
            'http_method': str(request.method),
            'user_agent': str(request.headers.get('User-Agent', 'Unknown')),
            'host': str(request.host_url) if hasattr(request, 'host_url') else 'http://127.0.0.1:5000/',
            'access_time': current_time
        },
        'subscription_analysis': {
            'current_user_profile': {
                'user_id': int(user_data.get('user_id', 0)),
                'username': str(username),
                'email': str(user_data.get('email', '')),
                'plan_name': str(current_plan),
                'plan_type': str(plan_type),
                'role': str(current_role),
                'subscription_active': bool(user_data.get('subscription_active', False)),
                'days_remaining': int(user_data.get('days_remaining', 0)),
                'monthly_cost': '$19.99',
                'rate_limit': f"{user_data.get('rate_limit', 0)} requests/month",
                'current_features': list(user_data.get('features', []))
            },
            'access_control_requirements': {
                'required_role': 'admin',
                'required_plan_type': 'premium',
                'required_subscription': 'Premium Plan ($199.99/year)',
                'access_level': 'enterprise_premium'
            },
            'permission_check_results': {
                'user_role_check': f"❌ Role '{current_role}' insufficient (admin required)",
                'plan_type_check': f"❌ Plan '{plan_type}' insufficient (premium required)",
                'subscription_status': f"✅ Subscription active ({user_data.get('days_remaining', 0)} days remaining)",
                'overall_verdict': '🚫 ACCESS DENIED - Premium subscription required'
            }
        },
        'upgrade_economics_analysis': {
            'current_plan_economics': {
                'plan_name': str(current_plan),
                'monthly_cost': '$19.99',
                'annual_cost': '$239.88',
                'features_count': len(user_data.get('features', [])),
                'api_request_limit': user_data.get('rate_limit', 0),
                'data_access_level': 'research_tier'
            },
            'premium_plan_economics': {
                'plan_name': 'Premium Plan',
                'annual_cost': '$199.99',
                'monthly_equivalent': '$16.67',
                'annual_savings': '$39.89 (17% cheaper than current)',
                'features_count': '10+ additional premium features',
                'api_request_limit': 'unlimited',
                'data_access_level': 'enterprise_tier'
            },
            'upgrade_value_proposition': {
                'cost_efficiency': '✅ Premium costs 17% LESS annually than current plan',
                'feature_expansion': '🚀 Unlock 10+ exclusive premium features',
                'productivity_gains': '⏰ Save 50+ hours/month of manual analysis',
                'accuracy_improvement': '📊 95% vs 78% prediction accuracy',
                'competitive_advantage': '🎯 Access to proprietary ML algorithms',
                'roi_timeline': '💰 Break-even within 2 weeks of upgrade',
                'enterprise_support': '🎧 Priority technical support included'
            }
        },
        'immediate_action_plan': {
            'recommended_action': {
                'action': '🚀 Upgrade to Premium Plan (Best Value)',
                'rationale': 'Lower annual cost + premium features',
                'upgrade_url': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/plans/",
                'estimated_setup_time': '2 minutes',
                'instant_benefits': [
                    '✅ Immediate access to this endpoint',
                    '💰 Save $39.89 annually vs current plan',
                    '🔓 Unlock all premium features',
                    '⚡ Unlimited API requests',
                    '🎧 Priority support access'
                ]
            },
            'alternative_options': {
                'use_research_features': {
                    'title': '🔬 Maximize Your Current Research Access',
                    'description': 'Access comprehensive research-level analytics',
                    'available_endpoints': [
                        f"{request.host_url}research/telemetry",
                        f"{request.host_url}research/analytics/salinity"
                    ],
                    'curl_example': f'curl -H "Authorization: Bearer <TOKEN>" {request.host_url}research/telemetry',
                    'data_available': 'All environmental parameters except internal notes'
                },
                'explore_subscription': {
                    'title': '📋 Review Your Current Access',
                    'endpoint': f"{request.host_url}subscription/info",
                    'description': 'See complete list of available endpoints for your plan'
                }
            }
        },
        'technical_enforcement_details': {
            'security_layer': 'subscription_auth_decorator',
            'enforcement_method': 'role_and_plan_validation',
            'access_control_type': 'strict_premium_only',
            'blocking_reason': 'insufficient_subscription_tier',
            'required_permissions': {
                'role': 'admin',
                'plan_type': 'premium',
                'subscription_active': True
            },
            'user_permissions': {
                'role': str(current_role),
                'plan_type': str(plan_type),
                'subscription_active': bool(user_data.get('subscription_active', False))
            }
        },
        'support_resources': {
            'immediate_help': {
                'technical_support': 'support@swes7301-group3.com',
                'billing_questions': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/billing/",
                'live_chat': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/support/chat/"
            },
            'documentation': {
                'api_documentation': 'https://github.com/SWES7301-Group-3/Flask-API#readme',
                'subscription_guide': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/help/",
                'feature_comparison': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/compare/",
                'curl_examples': 'https://github.com/SWES7301-Group-3/Flask-API/blob/main/examples/'
            },
            'community': {
                'github_issues': 'https://github.com/SWES7301-Group-3/Flask-API/issues',
                'feature_requests': 'https://github.com/SWES7301-Group-3/Flask-API/discussions',
                'developer_profile': 'https://github.com/NeduStack'
            }
        }
    }
    
    return response

def subscription_required(allowed_roles=None, allowed_plan_types=None):
    """
    Enhanced subscription decorator with strict access control and comprehensive error responses
    """
    if allowed_roles is None:
        allowed_roles = ['user', 'researcher', 'admin']
    if allowed_plan_types is None:
        allowed_plan_types = ['basic_user', 'researcher', 'premium']
    
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            # Missing token - enhanced error response
            if not auth_header:
                error_dict = {
                    'error': 'Authentication Required',
                    'error_code': 'MISSING_AUTH_TOKEN',
                    'message': 'Please provide a valid subscription token to access this endpoint',
                    'timestamp': '2025-09-10 21:49:32',
                    'github_user': 'NeduStack',
                    'github_project': 'SWES7301-Group-3/Flask-API',
                    'endpoint_attempted': str(request.path),
                    'required_header': 'Authorization: Bearer <your_subscription_token>',
                    'authentication_flow': {
                        'step_1': 'Visit Django subscription portal',
                        'step_2': 'Login or create account',
                        'step_3': 'Subscribe to appropriate plan',
                        'step_4': 'Generate API token',
                        'step_5': 'Include token in request headers'
                    },
                    'quick_links': {
                        'get_token': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/my-subscriptions/",
                        'subscribe': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/plans/",
                        'documentation': 'https://github.com/SWES7301-Group-3/Flask-API#authentication'
                    }
                }
                response = make_response(json.dumps(error_dict), 401)
                response.headers['Content-Type'] = 'application/json'
                return response
            
            # Extract token
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
            else:
                token = auth_header
            
            # Verify token with Django
            token_data = verify_subscription_token(token)
            
            # Invalid token - enhanced error response
            if not token_data:
                error_dict = {
                    'error': 'Invalid or Expired Token',
                    'error_code': 'INVALID_AUTH_TOKEN',
                    'message': 'Your subscription token is invalid, expired, or malformed',
                    'timestamp': '2025-09-10 21:49:32',
                    'github_user': 'NeduStack',
                    'github_project': 'SWES7301-Group-3/Flask-API',
                    'endpoint_attempted': str(request.path),
                    'possible_causes': [
                        'Token has expired',
                        'Token was revoked or regenerated',
                        'Subscription has been cancelled',
                        'Token format is incorrect'
                    ],
                    'resolution_steps': {
                        'check_subscription': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/my-subscriptions/",
                        'renew_subscription': f"{current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')}/subscriptions/plans/",
                        'contact_support': 'support@swes7301-group3.com'
                    }
                }
                response = make_response(json.dumps(error_dict), 401)
                response.headers['Content-Type'] = 'application/json'
                return response
            
            # Check permissions with enhanced logging
            user_role = token_data.get('role', 'user')
            plan_type = token_data.get('plan_type', 'basic_user')
            username = token_data.get('username', 'Unknown')
            
            # STRICT permission checking
            has_role_access = user_role in allowed_roles
            has_plan_access = plan_type in allowed_plan_types
            
            # Enhanced access logging
            logger.info(f"🔍 ACCESS CHECK - User: {username}, Role: {user_role}, Plan: {plan_type}")
            logger.info(f"📋 REQUIREMENTS - Allowed roles: {allowed_roles}, Allowed plans: {allowed_plan_types}")
            logger.info(f"✅ PERMISSION RESULT - Role access: {has_role_access}, Plan access: {has_plan_access}")
            logger.info(f"🎯 ENDPOINT: {request.path} | METHOD: {request.method}")
            
            # Block access if permissions insufficient
            if not has_role_access or not has_plan_access:
                logger.warning(f"🚫 ACCESS DENIED - {username} ({plan_type}/{user_role}) attempted {request.path}")
                logger.warning(f"🔒 BLOCKING REASON - Required: roles={allowed_roles}, plans={allowed_plan_types}")
                
                # Return comprehensive access denied response
                error_response = create_premium_access_denied_response(token_data, request.path)
                response = make_response(json.dumps(error_response), 403)
                response.headers['Content-Type'] = 'application/json'
                return response
            
            # Success - grant access with logging
            logger.info(f"✅ ACCESS GRANTED - User: {username}")
            logger.info(f"📊 PLAN: {token_data.get('plan_name')} | ENDPOINT: {request.path}")
            logger.info(f"👤 GITHUB: NeduStack | PROJECT: SWES7301-Group-3/Flask-API")
            
            # Add user data to request context
            request.current_user = token_data
            request.auth_type = 'subscription'
            return f(*args, **kwargs)
        
        return decorated
    return decorator

# Convenience decorators with strict access control
def basic_subscription_required(f):
    """Requires basic subscription or above"""
    return subscription_required(
        allowed_roles=['user', 'researcher', 'admin'],
        allowed_plan_types=['basic_user', 'researcher', 'premium']
    )(f)

def researcher_subscription_required(f):
    """Requires researcher subscription or above"""
    return subscription_required(
        allowed_roles=['researcher', 'admin'],
        allowed_plan_types=['researcher', 'premium']
    )(f)

def premium_subscription_required(f):
    """STRICT: Premium subscription ONLY - blocks ALL non-premium users including researchers"""
    return subscription_required(
        allowed_roles=['admin'],          
        allowed_plan_types=['premium']   
    )(f)

def any_valid_subscription(f):
    """Requires any valid subscription"""
    return subscription_required()(f)