"""
Main pytest configuration and fixtures for Birthday Cake Planner testing
Provides shared fixtures, utilities, and test setup/teardown
"""

import pytest
import asyncio
import os
import sys
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, Generator, Optional
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'cake-backend', 'src'))

# Import test configuration
from tests.config.test_config import (
    TestConfig, TestEnvironment, test_config,
    TEST_USERS, TEST_TASKS, AI_TEST_RESPONSES
)

# Import application modules
try:
    from main import app, db
    from models.user import User
    from models.task import Task
    from models.gamification import CakePersonality, Achievement
    from services.ai_service import ai_service
    from config.ai_config import ai_config_manager
except ImportError as e:
    print(f"Warning: Could not import application modules: {e}")
    app = None
    db = None

# Playwright imports
try:
    from playwright.sync_api import Browser, BrowserContext, Page
    from playwright.async_api import async_playwright
except ImportError:
    print("Warning: Playwright not installed. UI tests will be skipped.")

# Testing utilities
import requests
import factory
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

fake = Faker()

# ============================================================================
# Session-scoped fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_config_fixture():
    """Provide test configuration for the session."""
    return test_config

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp(prefix="birthday_cake_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

# ============================================================================
# Database fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_database():
    """Create and configure test database."""
    if not db:
        pytest.skip("Database not available")
    
    # Create test database
    test_db_path = os.path.join(tempfile.gettempdir(), "test_birthday_cake.db")
    test_db_url = f"sqlite:///{test_db_path}"
    
    # Configure test database
    app.config['SQLALCHEMY_DATABASE_URI'] = test_db_url
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
    
    # Clean up
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)

@pytest.fixture
def db_session(test_database):
    """Provide a database session for tests."""
    with app.app_context():
        connection = test_database.engine.connect()
        transaction = connection.begin()
        
        # Configure session to use the connection
        session = test_database.session
        session.configure(bind=connection)
        
        yield session
        
        # Rollback transaction
        transaction.rollback()
        connection.close()

# ============================================================================
# Application fixtures
# ============================================================================

@pytest.fixture
def flask_app():
    """Provide Flask application for testing."""
    if not app:
        pytest.skip("Flask app not available")
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        yield app

@pytest.fixture
def client(flask_app):
    """Provide Flask test client."""
    return flask_app.test_client()

@pytest.fixture
def api_client():
    """Provide API client for testing."""
    class APIClient:
        def __init__(self, base_url: str = None):
            self.base_url = base_url or test_config.api.base_url
            self.session = requests.Session()
            self.auth_token = None
        
        def set_auth_token(self, token: str):
            """Set authentication token."""
            self.auth_token = token
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        
        def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
            """Make API request."""
            url = f"{self.base_url}{endpoint}"
            return self.session.request(method, url, **kwargs)
        
        def get(self, endpoint: str, **kwargs) -> requests.Response:
            return self.request('GET', endpoint, **kwargs)
        
        def post(self, endpoint: str, **kwargs) -> requests.Response:
            return self.request('POST', endpoint, **kwargs)
        
        def put(self, endpoint: str, **kwargs) -> requests.Response:
            return self.request('PUT', endpoint, **kwargs)
        
        def delete(self, endpoint: str, **kwargs) -> requests.Response:
            return self.request('DELETE', endpoint, **kwargs)
    
    return APIClient()

# ============================================================================
# User and authentication fixtures
# ============================================================================

@pytest.fixture
def test_user_data():
    """Provide test user data."""
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": "TestPassword123!",
        "cake_mood": "cheerful",
        "cake_sweetness_level": 3
    }

@pytest.fixture
def test_user(db_session, test_user_data):
    """Create a test user in the database."""
    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        cake_mood=test_user_data["cake_mood"],
        cake_sweetness_level=test_user_data["cake_sweetness_level"]
    )
    user.set_password(test_user_data["password"])
    
    db_session.add(user)
    db_session.commit()
    
    return user

@pytest.fixture
def authenticated_user(api_client, test_user_data):
    """Create and authenticate a test user."""
    # Register user
    register_response = api_client.post('/api/auth/register', json=test_user_data)
    assert register_response.status_code == 201
    
    # Login user
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    login_response = api_client.post('/api/auth/login', json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()['data']['token']
    api_client.set_auth_token(token)
    
    return {
        "user_data": test_user_data,
        "token": token,
        "client": api_client
    }

# ============================================================================
# Task fixtures
# ============================================================================

@pytest.fixture
def test_task_data():
    """Provide test task data."""
    return {
        "title": fake.sentence(nb_words=4),
        "description": fake.text(max_nb_chars=200),
        "priority": fake.random_int(min=1, max=5),
        "difficulty": fake.random_int(min=1, max=5),
        "estimated_duration": fake.random_int(min=15, max=240),
        "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
    }

@pytest.fixture
def test_task(db_session, test_user, test_task_data):
    """Create a test task in the database."""
    task = Task(
        title=test_task_data["title"],
        description=test_task_data["description"],
        priority=test_task_data["priority"],
        difficulty=test_task_data["difficulty"],
        estimated_duration=test_task_data["estimated_duration"],
        user_id=test_user.id
    )
    
    db_session.add(task)
    db_session.commit()
    
    return task

# ============================================================================
# AI and personality fixtures
# ============================================================================

@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing."""
    with patch('services.ai_service.ai_service') as mock_service:
        # Configure mock responses
        mock_service.generate_response.return_value = Mock(
            text="🎂 Test AI response! ✨",
            mood="cheerful",
            animation_type="bounce",
            source="mock",
            metadata={"test": True}
        )
        
        mock_service.get_service_status.return_value = {
            "ai_service_status": "operational",
            "providers_initialized": ["mock"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        yield mock_service

@pytest.fixture
def ai_test_responses():
    """Provide AI test responses."""
    return AI_TEST_RESPONSES

@pytest.fixture
def cake_personality_data():
    """Provide cake personality test data."""
    return {
        "category": "task_completion",
        "mood": "cheerful",
        "response_text": "🎂 Sweet success! Well done! ✨",
        "animation_type": "celebration_bounce",
        "context_data": {"difficulty": 3, "streak": 5}
    }

# ============================================================================
# Playwright fixtures
# ============================================================================

@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Configure browser launch arguments."""
    return {
        "headless": test_config.playwright.headless,
        "slow_mo": test_config.playwright.slow_mo,
        "args": [
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
    }

@pytest.fixture
def browser_context_args():
    """Configure browser context arguments."""
    return {
        "viewport": {
            "width": test_config.playwright.viewport_width,
            "height": test_config.playwright.viewport_height
        },
        "record_video_dir": "tests/reports/videos" if test_config.playwright.video_on_failure else None,
        "record_har_path": "tests/reports/har/test.har"
    }

@pytest.fixture
def page_with_auth(page: Page, authenticated_user):
    """Provide a page with authenticated user."""
    # Navigate to login page and authenticate
    page.goto(f"{test_config.api.base_url}/login")
    
    # Fill login form
    page.fill('[data-testid="email-input"]', authenticated_user["user_data"]["email"])
    page.fill('[data-testid="password-input"]', authenticated_user["user_data"]["password"])
    page.click('[data-testid="login-button"]')
    
    # Wait for navigation to dashboard
    page.wait_for_url("**/dashboard")
    
    return page

# ============================================================================
# Performance testing fixtures
# ============================================================================

@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests."""
    import psutil
    import time
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.start_memory = None
            self.end_memory = None
            self.process = psutil.Process()
        
        def start(self):
            self.start_time = time.time()
            self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        def stop(self):
            self.end_time = time.time()
            self.end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        def get_metrics(self):
            return {
                "duration_ms": (self.end_time - self.start_time) * 1000 if self.end_time else None,
                "memory_usage_mb": self.end_memory - self.start_memory if self.end_memory else None,
                "peak_memory_mb": self.end_memory if self.end_memory else None
            }
    
    return PerformanceMonitor()

# ============================================================================
# Test data factories
# ============================================================================

class UserFactory(factory.Factory):
    """Factory for creating test users."""
    class Meta:
        model = dict
    
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = "TestPassword123!"
    cake_mood = factory.Faker('random_element', elements=['cheerful', 'encouraging', 'excited'])
    cake_sweetness_level = factory.Faker('random_int', min=1, max=5)

class TaskFactory(factory.Factory):
    """Factory for creating test tasks."""
    class Meta:
        model = dict
    
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=200)
    priority = factory.Faker('random_int', min=1, max=5)
    difficulty = factory.Faker('random_int', min=1, max=5)
    estimated_duration = factory.Faker('random_int', min=15, max=240)

@pytest.fixture
def user_factory():
    """Provide user factory."""
    return UserFactory

@pytest.fixture
def task_factory():
    """Provide task factory."""
    return TaskFactory

# ============================================================================
# Utility fixtures
# ============================================================================

@pytest.fixture
def test_data_loader():
    """Load test data from JSON files."""
    def load_test_data(filename: str) -> Dict[str, Any]:
        filepath = os.path.join(test_config.get_test_data_dir(), filename)
        with open(filepath, 'r') as f:
            return json.load(f)
    
    return load_test_data

@pytest.fixture
def screenshot_helper():
    """Helper for taking screenshots during tests."""
    def take_screenshot(page: Page, name: str):
        screenshot_dir = os.path.join(test_config.get_reports_dir(), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(screenshot_dir, filename)
        
        page.screenshot(path=filepath)
        return filepath
    
    return take_screenshot

@pytest.fixture
def validation_helper():
    """Helper for validation testing."""
    from tests.config.test_config import VALIDATION_RULES
    
    class ValidationHelper:
        @staticmethod
        def validate_field(field_name: str, value: Any) -> Dict[str, Any]:
            """Validate a field value against rules."""
            rules = VALIDATION_RULES.get(field_name, {})
            errors = []
            
            if rules.get('required', False) and not value:
                errors.append(f"{field_name} is required")
            
            if isinstance(value, str):
                if 'min_length' in rules and len(value) < rules['min_length']:
                    errors.append(f"{field_name} must be at least {rules['min_length']} characters")
                
                if 'max_length' in rules and len(value) > rules['max_length']:
                    errors.append(f"{field_name} must be at most {rules['max_length']} characters")
                
                if 'pattern' in rules:
                    import re
                    if not re.match(rules['pattern'], value):
                        errors.append(f"{field_name} format is invalid")
            
            if isinstance(value, (int, float)):
                if 'min_value' in rules and value < rules['min_value']:
                    errors.append(f"{field_name} must be at least {rules['min_value']}")
                
                if 'max_value' in rules and value > rules['max_value']:
                    errors.append(f"{field_name} must be at most {rules['max_value']}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
    
    return ValidationHelper()

# ============================================================================
# Hooks and test lifecycle
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Create reports directory
    reports_dir = test_config.get_reports_dir()
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(os.path.join(reports_dir, "screenshots"), exist_ok=True)
    os.makedirs(os.path.join(reports_dir, "videos"), exist_ok=True)
    os.makedirs(os.path.join(reports_dir, "traces"), exist_ok=True)

def pytest_runtest_makereport(item, call):
    """Generate test reports with additional information."""
    if "page" in item.fixturenames:
        page = item.funcargs["page"]
        if call.when == "call" and call.excinfo is not None:
            # Take screenshot on failure
            screenshot_dir = os.path.join(test_config.get_reports_dir(), "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshot_dir, f"{item.name}_{timestamp}.png")
            page.screenshot(path=screenshot_path)

def pytest_html_report_title(report):
    """Customize HTML report title."""
    report.title = "Birthday Cake Planner - Comprehensive Test Report"

@pytest.fixture(autouse=True)
def test_environment_setup():
    """Set up test environment for each test."""
    # Set test environment variables
    os.environ['TESTING'] = 'true'
    os.environ['FLASK_ENV'] = 'testing'
    
    yield
    
    # Clean up after test
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
    if 'FLASK_ENV' in os.environ:
        del os.environ['FLASK_ENV']

