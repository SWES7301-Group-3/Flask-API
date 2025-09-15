from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_jwt_extended import JWTManager

db = SQLAlchemy()

authorizations = {
    'SubscriptionToken': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Subscription Token: Get your token from Django subscription dashboard. Format: 'Bearer your_subscription_token'"
    }
}

api = Api(
    version='1.0',
    title='Environmental Data API - SWES7301 Group 3',
    description='''
    ## Subscription-Based Environmental Data API
    
    This API provides access to environmental telemetry data with subscription-based authentication.
    
    ### How to Get Access:
    1. **Subscribe**: Visit [Django Subscription Portal](http://localhost:8000/subscriptions/plans/) to choose a plan
    2. **Get Token**: After subscription, visit [My Subscriptions](http://localhost:8000/subscriptions/my-subscriptions/) to get your API token
    3. **Use Token**: Add your token to the Authorization header: `Bearer your_subscription_token`
    
    ### Subscription Tiers:
    - **Basic User**: Access to basic telemetry data (temperature, humidity, coordinates)
    - **Researcher**: Access to detailed environmental data including salinity, pH, pollutants
    - **Premium**: Full access including admin features and advanced analytics
    
    ### Rate Limits:
    - Basic: 1,000 requests/hour
    - Researcher: 5,000 requests/hour  
    - Premium: 10,000 requests/hour
    
    ### Support:
    For subscription issues, visit: [Django Admin](http://localhost:8000/subscriptions/)
    ''',
    doc='/swagger/',
    default='Public',
    default_label='Public endpoints (no subscription required)',
    authorizations=authorizations,
    security='SubscriptionToken'
)

jwt = JWTManager()