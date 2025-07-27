"""
Comprehensive Test Configuration for Birthday Cake Planner
Defines all testing environments, parameters, and settings
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum

class TestEnvironment(Enum):
    """Test environment types"""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    STAGING = "staging"
    PRODUCTION = "production"

class TestSeverity(Enum):
    """Test severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TestCategory(Enum):
    """Test categories for organization"""
    AUTHENTICATION = "authentication"
    USER_MANAGEMENT = "user_management"
    TASK_MANAGEMENT = "task_management"
    AI_PERSONALITY = "ai_personality"
    GAMIFICATION = "gamification"
    API_VALIDATION = "api_validation"
    UI_FUNCTIONALITY = "ui_functionality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    BUSINESS_RULES = "business_rules"
    ERROR_HANDLING = "error_handling"
    DATA_VALIDATION = "data_validation"

@dataclass
class DatabaseConfig:
    """Database configuration for testing"""
    host: str = "localhost"
    port: int = 5432
    name: str = "birthday_cake_test"
    user: str = "test_user"
    password: str = "test_password"
    driver: str = "postgresql"
    
    def get_url(self) -> str:
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass
class APIConfig:
    """API configuration for testing"""
    base_url: str = "http://localhost:5000"
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    auth_endpoint: str = "/api/auth"
    api_version: str = "v1"
    
    def get_endpoint_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

@dataclass
class PlaywrightConfig:
    """Playwright configuration for UI testing"""
    headless: bool = True
    browser: str = "chromium"  # chromium, firefox, webkit
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout: int = 30000
    screenshot_on_failure: bool = True
    video_on_failure: bool = True
    trace_on_failure: bool = True
    slow_mo: int = 0
    
    # Browser contexts
    browsers_to_test: List[str] = None
    
    def __post_init__(self):
        if self.browsers_to_test is None:
            self.browsers_to_test = ["chromium", "firefox", "webkit"]

@dataclass
class AITestConfig:
    """AI system testing configuration"""
    mock_ai_responses: bool = True
    test_openai_integration: bool = False
    test_fallback_mechanisms: bool = True
    ai_response_timeout: int = 10
    fallback_response_count: int = 10
    test_connectivity_failures: bool = True
    
    # AI model configurations for testing
    test_models: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.test_models is None:
            self.test_models = {
                "openai": {
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 150,
                    "temperature": 0.7
                },
                "fallback": {
                    "response_count": 10,
                    "categories": ["task_creation", "task_completion", "motivation"]
                }
            }

@dataclass
class PerformanceConfig:
    """Performance testing configuration"""
    max_response_time_ms: int = 2000
    max_memory_usage_mb: int = 512
    concurrent_users: int = 100
    test_duration_seconds: int = 300
    ramp_up_time_seconds: int = 60
    
    # Load testing scenarios
    load_test_scenarios: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.load_test_scenarios is None:
            self.load_test_scenarios = [
                {
                    "name": "user_registration",
                    "weight": 10,
                    "endpoint": "/api/auth/register"
                },
                {
                    "name": "user_login",
                    "weight": 20,
                    "endpoint": "/api/auth/login"
                },
                {
                    "name": "task_creation",
                    "weight": 30,
                    "endpoint": "/api/tasks"
                },
                {
                    "name": "task_completion",
                    "weight": 25,
                    "endpoint": "/api/tasks/{id}/complete"
                },
                {
                    "name": "ai_interaction",
                    "weight": 15,
                    "endpoint": "/api/cake/interact"
                }
            ]

@dataclass
class ReportingConfig:
    """Test reporting configuration"""
    generate_html_report: bool = True
    generate_json_report: bool = True
    generate_allure_report: bool = True
    generate_coverage_report: bool = True
    
    # Report output directories
    reports_dir: str = "tests/reports"
    html_report_file: str = "test_report.html"
    json_report_file: str = "test_report.json"
    coverage_report_dir: str = "coverage"
    allure_results_dir: str = "allure-results"
    
    # Report customization
    include_screenshots: bool = True
    include_videos: bool = True
    include_traces: bool = True
    group_by_category: bool = True
    show_passed_tests: bool = True

@dataclass
class SecurityConfig:
    """Security testing configuration"""
    test_sql_injection: bool = True
    test_xss_attacks: bool = True
    test_csrf_protection: bool = True
    test_authentication_bypass: bool = True
    test_authorization_flaws: bool = True
    test_sensitive_data_exposure: bool = True
    
    # Security test payloads
    sql_injection_payloads: List[str] = None
    xss_payloads: List[str] = None
    
    def __post_init__(self):
        if self.sql_injection_payloads is None:
            self.sql_injection_payloads = [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users --",
                "1' OR 1=1#"
            ]
        
        if self.xss_payloads is None:
            self.xss_payloads = [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src=x onerror=alert('XSS')>",
                "';alert('XSS');//"
            ]

class TestConfig:
    """Main test configuration class"""
    
    def __init__(self, environment: TestEnvironment = TestEnvironment.UNIT):
        self.environment = environment
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.playwright = PlaywrightConfig()
        self.ai = AITestConfig()
        self.performance = PerformanceConfig()
        self.reporting = ReportingConfig()
        self.security = SecurityConfig()
        
        # Environment-specific overrides
        self._apply_environment_overrides()
        
        # Load from environment variables
        self._load_from_environment()
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""
        if self.environment == TestEnvironment.E2E:
            self.playwright.headless = False
            self.playwright.slow_mo = 500
            self.api.timeout = 60
            
        elif self.environment == TestEnvironment.PERFORMANCE:
            self.performance.concurrent_users = 500
            self.performance.test_duration_seconds = 600
            self.playwright.headless = True
            
        elif self.environment == TestEnvironment.STAGING:
            self.api.base_url = "https://staging.birthdaycakeplanner.com"
            self.database.host = "staging-db.birthdaycakeplanner.com"
            self.ai.test_openai_integration = True
            
        elif self.environment == TestEnvironment.PRODUCTION:
            self.api.base_url = "https://birthdaycakeplanner.com"
            self.database.host = "prod-db.birthdaycakeplanner.com"
            self.ai.mock_ai_responses = False
            self.ai.test_openai_integration = True
            self.security.test_sql_injection = False  # Don't run destructive tests in prod
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # API Configuration
        self.api.base_url = os.getenv("TEST_API_BASE_URL", self.api.base_url)
        
        # Database Configuration
        self.database.host = os.getenv("TEST_DB_HOST", self.database.host)
        self.database.port = int(os.getenv("TEST_DB_PORT", str(self.database.port)))
        self.database.name = os.getenv("TEST_DB_NAME", self.database.name)
        self.database.user = os.getenv("TEST_DB_USER", self.database.user)
        self.database.password = os.getenv("TEST_DB_PASSWORD", self.database.password)
        
        # Playwright Configuration
        self.playwright.headless = os.getenv("TEST_HEADLESS", "true").lower() == "true"
        self.playwright.browser = os.getenv("TEST_BROWSER", self.playwright.browser)
        
        # AI Configuration
        self.ai.mock_ai_responses = os.getenv("TEST_MOCK_AI", "true").lower() == "true"
        self.ai.test_openai_integration = os.getenv("TEST_OPENAI", "false").lower() == "true"
    
    def get_test_data_dir(self) -> str:
        """Get test data directory path"""
        return os.path.join(os.path.dirname(__file__), "..", "fixtures")
    
    def get_reports_dir(self) -> str:
        """Get reports directory path"""
        return os.path.join(os.path.dirname(__file__), "..", "reports")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "environment": self.environment.value,
            "database": asdict(self.database),
            "api": asdict(self.api),
            "playwright": asdict(self.playwright),
            "ai": asdict(self.ai),
            "performance": asdict(self.performance),
            "reporting": asdict(self.reporting),
            "security": asdict(self.security)
        }
    
    def save_to_file(self, filepath: str):
        """Save configuration to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'TestConfig':
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        config = cls(TestEnvironment(data["environment"]))
        
        # Update configuration with loaded data
        for key, value in data.items():
            if hasattr(config, key) and key != "environment":
                setattr(config, key, value)
        
        return config

# Global test configuration instances
test_config = TestConfig()

# Environment-specific configurations
unit_config = TestConfig(TestEnvironment.UNIT)
integration_config = TestConfig(TestEnvironment.INTEGRATION)
e2e_config = TestConfig(TestEnvironment.E2E)
performance_config = TestConfig(TestEnvironment.PERFORMANCE)
staging_config = TestConfig(TestEnvironment.STAGING)

# Test data constants
TEST_USERS = {
    "valid_user": {
        "username": "testuser",
        "email": "test@birthdaycake.com",
        "password": "SecurePassword123!"
    },
    "admin_user": {
        "username": "admin",
        "email": "admin@birthdaycake.com",
        "password": "AdminPassword123!"
    },
    "invalid_user": {
        "username": "",
        "email": "invalid-email",
        "password": "weak"
    }
}

TEST_TASKS = {
    "valid_task": {
        "title": "Complete project documentation",
        "description": "Write comprehensive documentation for the Birthday Cake Planner",
        "priority": 3,
        "difficulty": 2,
        "estimated_duration": 120
    },
    "urgent_task": {
        "title": "Fix critical bug",
        "description": "Resolve authentication issue",
        "priority": 5,
        "difficulty": 4,
        "estimated_duration": 60
    },
    "invalid_task": {
        "title": "",
        "description": "A" * 1001,  # Too long
        "priority": 6,  # Invalid priority
        "difficulty": 0,  # Invalid difficulty
        "estimated_duration": -30  # Invalid duration
    }
}

# AI test responses
AI_TEST_RESPONSES = {
    "task_creation": [
        "🎂 Wonderful! A new task to celebrate! Let's make this one extra sweet! ✨",
        "🍰 Oh my! Another delicious challenge awaits! I'm so excited to see you succeed! 🎉"
    ],
    "task_completion": [
        "🎂 Sweet success! You've earned another slice of productivity! Time to celebrate! 🍰",
        "🎉 Magnificent! That task is now perfectly baked and ready to enjoy! Well done! ✨"
    ],
    "motivation": [
        "🎂 Remember, every expert baker started with their first cupcake! You're doing great! 💪",
        "🍰 Productivity is like baking - it takes time, patience, and lots of love! 💕"
    ]
}

# Test validation rules
VALIDATION_RULES = {
    "username": {
        "min_length": 3,
        "max_length": 50,
        "pattern": r"^[a-zA-Z0-9_]+$",
        "required": True
    },
    "email": {
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "required": True
    },
    "password": {
        "min_length": 8,
        "max_length": 128,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_digit": True,
        "require_special": True,
        "required": True
    },
    "task_title": {
        "min_length": 1,
        "max_length": 200,
        "required": True
    },
    "task_description": {
        "max_length": 1000,
        "required": False
    },
    "priority": {
        "min_value": 1,
        "max_value": 5,
        "required": True
    },
    "difficulty": {
        "min_value": 1,
        "max_value": 5,
        "required": True
    }
}

