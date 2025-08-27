from flask_restx import Resource, fields, Namespace
from app import api

# Define a namespace
ns = api.namespace('users', description='User operations')

# Define data model
user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='User ID'),
    'name': fields.String(required=True, description='User name'),
    'email': fields.String(required=True, description='User email')
})

# Sample data
users = [
    {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
    {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'}
]

@ns.route('/')
class UserList(Resource):
    @ns.doc('list_users')
    @ns.marshal_list_with(user_model)
    def get(self):
        """Get all users"""
        return users

    @ns.doc('create_user')
    @ns.expect(user_model)
    @ns.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
        new_user = {
            'id': len(users) + 1,
            'name': api.payload['name'],
            'email': api.payload['email']
        }
        users.append(new_user)
        return new_user, 201

@ns.route('/<int:user_id>')
@ns.param('user_id', 'The user identifier')
@ns.response(404, 'User not found')
class User(Resource):
    @ns.doc('get_user')
    @ns.marshal_with(user_model)
    def get(self, user_id):
        """Get a specific user"""
        user = next((u for u in users if u['id'] == user_id), None)
        if user:
            return user
        api.abort(404, f"User {user_id} not found")

    @ns.doc('delete_user')
    @ns.response(204, 'User deleted')
    def delete(self, user_id):
        """Delete a user"""
        global users
        users = [u for u in users if u['id'] != user_id]
        return '', 204

    @ns.doc('update_user')
    @ns.expect(user_model)
    @ns.marshal_with(user_model)
    def put(self, user_id):
        """Update a user"""
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            api.abort(404, f"User {user_id} not found")
        
        user.update({
            'name': api.payload['name'],
            'email': api.payload['email']
        })
        return user