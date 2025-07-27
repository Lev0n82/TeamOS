from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
from src.models.user import User, db

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    """Decorator to require JWT token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid token format',
                    'data': None,
                    'errors': []
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing',
                'data': None,
                'errors': []
            }), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'Invalid token',
                    'data': None,
                    'errors': []
                }), 401
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token has expired',
                'data': None,
                'errors': []
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token',
                'data': None,
                'errors': []
            }), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        errors = []
        
        for field in required_fields:
            if not data.get(field):
                errors.append({
                    'field': field,
                    'message': f'{field.capitalize()} is required'
                })
        
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'data': None,
                'errors': errors
            }), 422
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'Email already registered',
                'data': None,
                'errors': [{'field': 'email', 'message': 'Email already exists'}]
            }), 422
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': 'Username already taken',
                'data': None,
                'errors': [{'field': 'username', 'message': 'Username already exists'}]
            }), 422
        
        # Validate password strength
        if len(data['password']) < 8:
            return jsonify({
                'success': False,
                'message': 'Password too weak',
                'data': None,
                'errors': [{'field': 'password', 'message': 'Password must be at least 8 characters'}]
            }), 422
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': user.to_dict(),
                'token': token
            },
            'errors': []
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email and password are required',
                'data': None,
                'errors': []
            }), 422
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password',
                'data': None,
                'errors': []
            }), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': user.to_dict(),
                'token': token
            },
            'errors': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@auth_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user profile information"""
    return jsonify({
        'success': True,
        'message': 'User profile retrieved',
        'data': {
            'user': current_user.to_dict()
        },
        'errors': []
    }), 200

@auth_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Logout user (client should discard token)"""
    return jsonify({
        'success': True,
        'message': 'Logout successful',
        'data': None,
        'errors': []
    }), 200

@auth_bp.route('/auth/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """Refresh JWT token"""
    try:
        # Generate new token
        token = generate_token(current_user.id)
        
        return jsonify({
            'success': True,
            'message': 'Token refreshed',
            'data': {
                'token': token
            },
            'errors': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Token refresh failed',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

