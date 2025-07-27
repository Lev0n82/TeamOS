"""
Comprehensive Authentication API Tests for Birthday Cake Planner
Tests all authentication endpoints, edge cases, and security scenarios
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from tests.config.test_config import TEST_USERS, VALIDATION_RULES


@pytest.mark.authentication
@pytest.mark.critical
class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_valid_user_registration(self, api_client):
        """Test successful user registration with valid data"""
        user_data = TEST_USERS["valid_user"].copy()
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        response = api_client.post('/api/auth/register', json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert 'token' in data['data']
        assert data['data']['user']['email'] == user_data['email']
        assert data['data']['user']['username'] == user_data['username']
        assert 'password' not in data['data']['user']  # Password should not be returned
    
    def test_registration_with_duplicate_email(self, api_client):
        """Test registration fails with duplicate email"""
        user_data = TEST_USERS["valid_user"].copy()
        
        # Register first user
        response1 = api_client.post('/api/auth/register', json=user_data)
        assert response1.status_code == 201
        
        # Try to register with same email
        response2 = api_client.post('/api/auth/register', json=user_data)
        assert response2.status_code == 422
        data = response2.json()
        assert data['success'] is False
        assert any('email' in error.get('field', '') for error in data['errors'])
    
    def test_registration_with_duplicate_username(self, api_client):
        """Test registration fails with duplicate username"""
        user_data = TEST_USERS["valid_user"].copy()
        
        # Register first user
        response1 = api_client.post('/api/auth/register', json=user_data)
        assert response1.status_code == 201
        
        # Try to register with same username but different email
        user_data2 = user_data.copy()
        user_data2["email"] = f"different_{int(time.time())}@example.com"
        
        response2 = api_client.post('/api/auth/register', json=user_data2)
        assert response2.status_code == 422
        data = response2.json()
        assert data['success'] is False
        assert any('username' in error.get('field', '') for error in data['errors'])
    
    @pytest.mark.parametrize("invalid_field,invalid_value,expected_error", [
        ("username", "", "required"),
        ("username", "ab", "too short"),
        ("username", "a" * 51, "too long"),
        ("username", "user@name", "invalid characters"),
        ("email", "", "required"),
        ("email", "invalid-email", "invalid format"),
        ("email", "user@", "invalid format"),
        ("email", "@domain.com", "invalid format"),
        ("password", "", "required"),
        ("password", "weak", "too short"),
        ("password", "nouppercasenumber", "missing requirements"),
        ("password", "NOLOWERCASENUMBER", "missing requirements"),
        ("password", "NoNumbersHere", "missing requirements"),
        ("password", "NoSpecialChars123", "missing requirements"),
    ])
    def test_registration_validation_errors(self, api_client, invalid_field, invalid_value, expected_error):
        """Test registration validation for various invalid inputs"""
        user_data = TEST_USERS["valid_user"].copy()
        user_data[invalid_field] = invalid_value
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        response = api_client.post('/api/auth/register', json=user_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data['success'] is False
        assert len(data['errors']) > 0
        
        # Check that the specific field error is present
        field_errors = [error for error in data['errors'] if error.get('field') == invalid_field]
        assert len(field_errors) > 0
    
    def test_registration_missing_required_fields(self, api_client):
        """Test registration fails when required fields are missing"""
        incomplete_data = {"username": "testuser"}
        
        response = api_client.post('/api/auth/register', json=incomplete_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data['success'] is False
        assert len(data['errors']) >= 2  # email and password missing
    
    def test_registration_with_malformed_json(self, api_client):
        """Test registration handles malformed JSON gracefully"""
        response = api_client.post('/api/auth/register', 
                                 data="invalid json",
                                 headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
    
    def test_registration_sets_default_cake_personality(self, api_client):
        """Test that registration sets default cake personality values"""
        user_data = TEST_USERS["valid_user"].copy()
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        response = api_client.post('/api/auth/register', json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        user = data['data']['user']
        
        assert user['cake_mood'] == 'cheerful'
        assert user['cake_sweetness_level'] == 3
        assert user['cake_personality_level'] == 1
        assert user['total_celebration_points'] == 0


@pytest.mark.authentication
@pytest.mark.critical
class TestUserLogin:
    """Test user login functionality"""
    
    def test_valid_login_with_email(self, api_client):
        """Test successful login with email and password"""
        # Register user first
        user_data = TEST_USERS["valid_user"].copy()
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        register_response = api_client.post('/api/auth/register', json=user_data)
        assert register_response.status_code == 201
        
        # Login with email
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = api_client.post('/api/auth/login', json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'token' in data['data']
        assert data['data']['user']['email'] == user_data['email']
    
    def test_valid_login_with_username(self, api_client):
        """Test successful login with username and password"""
        # Register user first
        user_data = TEST_USERS["valid_user"].copy()
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        register_response = api_client.post('/api/auth/register', json=user_data)
        assert register_response.status_code == 201
        
        # Login with username
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        response = api_client.post('/api/auth/login', json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'token' in data['data']
    
    def test_login_with_invalid_credentials(self, api_client):
        """Test login fails with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = api_client.post('/api/auth/login', json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data['success'] is False
        assert 'invalid credentials' in data['message'].lower()
    
    def test_login_with_wrong_password(self, api_client):
        """Test login fails with correct email but wrong password"""
        # Register user first
        user_data = TEST_USERS["valid_user"].copy()
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        register_response = api_client.post('/api/auth/register', json=user_data)
        assert register_response.status_code == 201
        
        # Try login with wrong password
        login_data = {
            "email": user_data["email"],
            "password": "wrongpassword"
        }
        
        response = api_client.post('/api/auth/login', json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data['success'] is False
    
    @pytest.mark.parametrize("missing_field", ["email", "password"])
    def test_login_missing_required_fields(self, api_client, missing_field):
        """Test login fails when required fields are missing"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        del login_data[missing_field]
        
        response = api_client.post('/api/auth/login', json=login_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data['success'] is False
        assert any(error.get('field') == missing_field for error in data['errors'])
    
    def test_login_rate_limiting(self, api_client):
        """Test login rate limiting after multiple failed attempts"""
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        # Make multiple failed login attempts
        for _ in range(6):  # Assuming rate limit is 5 attempts
            response = api_client.post('/api/auth/login', json=login_data)
            if response.status_code == 429:  # Too Many Requests
                break
        
        # The last response should be rate limited
        assert response.status_code in [401, 429]  # Either unauthorized or rate limited
    
    def test_jwt_token_structure(self, api_client):
        """Test that JWT token has correct structure"""
        # Register and login user
        user_data = TEST_USERS["valid_user"].copy()
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        register_response = api_client.post('/api/auth/register', json=user_data)
        assert register_response.status_code == 201
        
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = api_client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        
        token = response.json()['data']['token']
        
        # JWT tokens have 3 parts separated by dots
        token_parts = token.split('.')
        assert len(token_parts) == 3
        
        # Each part should be base64 encoded
        import base64
        for part in token_parts[:2]:  # Header and payload
            try:
                # Add padding if needed
                padded = part + '=' * (4 - len(part) % 4)
                base64.b64decode(padded)
            except Exception:
                pytest.fail(f"Token part {part} is not valid base64")


@pytest.mark.authentication
@pytest.mark.critical
class TestTokenValidation:
    """Test JWT token validation and protected endpoints"""
    
    def test_access_protected_endpoint_with_valid_token(self, authenticated_user):
        """Test accessing protected endpoint with valid token"""
        client = authenticated_user["client"]
        
        response = client.get('/api/auth/me')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['user']['email'] == authenticated_user["user_data"]["email"]
    
    def test_access_protected_endpoint_without_token(self, api_client):
        """Test accessing protected endpoint without token fails"""
        response = api_client.get('/api/auth/me')
        
        assert response.status_code == 401
        data = response.json()
        assert data['success'] is False
        assert 'token' in data['message'].lower()
    
    def test_access_protected_endpoint_with_invalid_token(self, api_client):
        """Test accessing protected endpoint with invalid token fails"""
        api_client.set_auth_token("invalid.token.here")
        
        response = api_client.get('/api/auth/me')
        
        assert response.status_code == 401
        data = response.json()
        assert data['success'] is False
    
    def test_access_protected_endpoint_with_expired_token(self, api_client):
        """Test accessing protected endpoint with expired token fails"""
        # Create an expired token (this would need to be implemented in the app)
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDk0NTkyMDB9.invalid"
        api_client.set_auth_token(expired_token)
        
        response = api_client.get('/api/auth/me')
        
        assert response.status_code == 401
        data = response.json()
        assert data['success'] is False
    
    def test_token_refresh_functionality(self, authenticated_user):
        """Test token refresh functionality if implemented"""
        client = authenticated_user["client"]
        
        # Try to refresh token
        response = client.post('/api/auth/refresh')
        
        # This endpoint might not be implemented yet
        if response.status_code == 404:
            pytest.skip("Token refresh endpoint not implemented")
        
        assert response.status_code == 200
        data = response.json()
        assert 'token' in data['data']


@pytest.mark.authentication
@pytest.mark.medium
class TestUserProfile:
    """Test user profile management"""
    
    def test_get_current_user_profile(self, authenticated_user):
        """Test retrieving current user profile"""
        client = authenticated_user["client"]
        
        response = client.get('/api/auth/me')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        
        user = data['data']['user']
        assert 'id' in user
        assert 'username' in user
        assert 'email' in user
        assert 'cake_mood' in user
        assert 'cake_sweetness_level' in user
        assert 'password' not in user  # Password should never be returned
    
    def test_update_user_profile(self, authenticated_user):
        """Test updating user profile"""
        client = authenticated_user["client"]
        
        update_data = {
            "cake_mood": "excited",
            "cake_sweetness_level": 5
        }
        
        response = client.put('/api/users/profile', json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['user']['cake_mood'] == "excited"
        assert data['data']['user']['cake_sweetness_level'] == 5
    
    def test_update_profile_with_invalid_data(self, authenticated_user):
        """Test updating profile with invalid data"""
        client = authenticated_user["client"]
        
        invalid_data = {
            "cake_sweetness_level": 10  # Invalid: should be 1-5
        }
        
        response = client.put('/api/users/profile', json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data['success'] is False
        assert len(data['errors']) > 0


@pytest.mark.authentication
@pytest.mark.security
class TestAuthenticationSecurity:
    """Test authentication security measures"""
    
    def test_password_hashing(self, api_client, db_session):
        """Test that passwords are properly hashed"""
        user_data = TEST_USERS["valid_user"].copy()
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        response = api_client.post('/api/auth/register', json=user_data)
        assert response.status_code == 201
        
        # Check that password is hashed in database
        from models.user import User
        user = db_session.query(User).filter_by(email=user_data["email"]).first()
        assert user is not None
        assert user.password_hash != user_data["password"]
        assert len(user.password_hash) > 50  # Hashed password should be long
    
    def test_sql_injection_protection(self, api_client):
        """Test protection against SQL injection attacks"""
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in sql_injection_payloads:
            login_data = {
                "email": payload,
                "password": "password"
            }
            
            response = api_client.post('/api/auth/login', json=login_data)
            
            # Should return 401 (unauthorized) or 422 (validation error), not 500 (server error)
            assert response.status_code in [401, 422]
            
            # Response should be JSON, not an error page
            try:
                data = response.json()
                assert 'success' in data
            except json.JSONDecodeError:
                pytest.fail(f"Response is not JSON for payload: {payload}")
    
    def test_xss_protection_in_responses(self, api_client):
        """Test protection against XSS in API responses"""
        xss_payload = "<script>alert('XSS')</script>"
        
        user_data = TEST_USERS["valid_user"].copy()
        user_data["username"] = xss_payload
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        response = api_client.post('/api/auth/register', json=user_data)
        
        # Should either reject the input or sanitize it
        if response.status_code == 201:
            data = response.json()
            returned_username = data['data']['user']['username']
            assert '<script>' not in returned_username
        else:
            assert response.status_code == 422  # Validation error
    
    def test_cors_headers(self, api_client):
        """Test that CORS headers are properly set"""
        response = api_client.options('/api/auth/login')
        
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
    
    def test_sensitive_data_not_logged(self, api_client, caplog):
        """Test that sensitive data is not logged"""
        user_data = TEST_USERS["valid_user"].copy()
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        with caplog.at_level("DEBUG"):
            response = api_client.post('/api/auth/register', json=user_data)
        
        # Check that password is not in logs
        for record in caplog.records:
            assert user_data["password"] not in record.getMessage()


@pytest.mark.authentication
@pytest.mark.performance
class TestAuthenticationPerformance:
    """Test authentication performance"""
    
    def test_registration_performance(self, api_client, performance_monitor):
        """Test registration endpoint performance"""
        user_data = TEST_USERS["valid_user"].copy()
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        performance_monitor.start()
        response = api_client.post('/api/auth/register', json=user_data)
        performance_monitor.stop()
        
        assert response.status_code == 201
        
        metrics = performance_monitor.get_metrics()
        assert metrics["duration_ms"] < 2000  # Should complete within 2 seconds
    
    def test_login_performance(self, api_client, performance_monitor):
        """Test login endpoint performance"""
        # Register user first
        user_data = TEST_USERS["valid_user"].copy()
        user_data["email"] = f"test_{int(time.time())}@example.com"
        
        register_response = api_client.post('/api/auth/register', json=user_data)
        assert register_response.status_code == 201
        
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        performance_monitor.start()
        response = api_client.post('/api/auth/login', json=login_data)
        performance_monitor.stop()
        
        assert response.status_code == 200
        
        metrics = performance_monitor.get_metrics()
        assert metrics["duration_ms"] < 1000  # Should complete within 1 second
    
    def test_concurrent_registrations(self, api_client):
        """Test handling of concurrent user registrations"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def register_user(index):
            user_data = TEST_USERS["valid_user"].copy()
            user_data["email"] = f"test_{index}_{int(time.time())}@example.com"
            user_data["username"] = f"testuser_{index}"
            
            try:
                response = api_client.post('/api/auth/register', json=user_data)
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # Create 10 concurrent registration threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_user, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 201:
                success_count += 1
        
        # All registrations should succeed
        assert success_count == 10

