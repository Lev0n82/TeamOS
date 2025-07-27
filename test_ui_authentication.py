"""
Comprehensive Frontend Authentication UI Tests for Birthday Cake Planner
Tests all authentication UI components, user flows, and interactions using Playwright
"""

import pytest
import re
from playwright.sync_api import Page, expect
from tests.config.test_config import TEST_USERS


@pytest.mark.ui_functionality
@pytest.mark.authentication
@pytest.mark.critical
class TestLoginUI:
    """Test login UI functionality"""
    
    def test_login_page_loads(self, page: Page):
        """Test that login page loads correctly"""
        page.goto(f"{page.context.base_url}/login")
        
        # Check page title
        expect(page).to_have_title(re.compile(".*Login.*Birthday Cake.*", re.IGNORECASE))
        
        # Check essential elements are present
        expect(page.locator('[data-testid="email-input"]')).to_be_visible()
        expect(page.locator('[data-testid="password-input"]')).to_be_visible()
        expect(page.locator('[data-testid="login-button"]')).to_be_visible()
        expect(page.locator('[data-testid="register-link"]')).to_be_visible()
        
        # Check Birthday Cake branding
        expect(page.locator('text=🎂')).to_be_visible()
        expect(page.locator('text=Birthday Cake')).to_be_visible()
    
    def test_valid_login_flow(self, page: Page, authenticated_user):
        """Test successful login flow"""
        page.goto(f"{page.context.base_url}/login")
        
        user_data = authenticated_user["user_data"]
        
        # Fill login form
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        
        # Submit form
        page.click('[data-testid="login-button"]')
        
        # Should redirect to dashboard
        expect(page).to_have_url(re.compile(".*/dashboard"))
        
        # Should show welcome message
        expect(page.locator('[data-testid="welcome-message"]')).to_be_visible()
        expect(page.locator(f'text={user_data["username"]}')).to_be_visible()
    
    def test_invalid_login_shows_error(self, page: Page):
        """Test that invalid login shows error message"""
        page.goto(f"{page.context.base_url}/login")
        
        # Fill with invalid credentials
        page.fill('[data-testid="email-input"]', "invalid@example.com")
        page.fill('[data-testid="password-input"]', "wrongpassword")
        
        # Submit form
        page.click('[data-testid="login-button"]')
        
        # Should show error message
        expect(page.locator('[data-testid="error-message"]')).to_be_visible()
        expect(page.locator('text=Invalid credentials')).to_be_visible()
        
        # Should remain on login page
        expect(page).to_have_url(re.compile(".*/login"))
    
    def test_login_form_validation(self, page: Page):
        """Test login form client-side validation"""
        page.goto(f"{page.context.base_url}/login")
        
        # Try to submit empty form
        page.click('[data-testid="login-button"]')
        
        # Should show validation errors
        expect(page.locator('[data-testid="email-error"]')).to_be_visible()
        expect(page.locator('[data-testid="password-error"]')).to_be_visible()
        
        # Test invalid email format
        page.fill('[data-testid="email-input"]', "invalid-email")
        page.click('[data-testid="login-button"]')
        
        expect(page.locator('[data-testid="email-error"]')).to_contain_text("valid email")
    
    def test_password_visibility_toggle(self, page: Page):
        """Test password visibility toggle functionality"""
        page.goto(f"{page.context.base_url}/login")
        
        password_input = page.locator('[data-testid="password-input"]')
        toggle_button = page.locator('[data-testid="password-toggle"]')
        
        # Initially password should be hidden
        expect(password_input).to_have_attribute("type", "password")
        
        # Fill password
        page.fill('[data-testid="password-input"]', "testpassword")
        
        # Click toggle to show password
        toggle_button.click()
        expect(password_input).to_have_attribute("type", "text")
        
        # Click toggle to hide password again
        toggle_button.click()
        expect(password_input).to_have_attribute("type", "password")
    
    def test_remember_me_functionality(self, page: Page):
        """Test remember me checkbox functionality"""
        page.goto(f"{page.context.base_url}/login")
        
        remember_checkbox = page.locator('[data-testid="remember-me"]')
        
        # Checkbox should be present and unchecked by default
        expect(remember_checkbox).to_be_visible()
        expect(remember_checkbox).not_to_be_checked()
        
        # Check the checkbox
        remember_checkbox.check()
        expect(remember_checkbox).to_be_checked()
        
        # Uncheck the checkbox
        remember_checkbox.uncheck()
        expect(remember_checkbox).not_to_be_checked()
    
    def test_login_loading_state(self, page: Page):
        """Test login button loading state during submission"""
        page.goto(f"{page.context.base_url}/login")
        
        # Fill form with valid data
        page.fill('[data-testid="email-input"]', "test@example.com")
        page.fill('[data-testid="password-input"]', "password123")
        
        # Click login button
        login_button = page.locator('[data-testid="login-button"]')
        login_button.click()
        
        # Button should show loading state
        expect(login_button).to_be_disabled()
        expect(page.locator('[data-testid="login-spinner"]')).to_be_visible()
    
    def test_keyboard_navigation(self, page: Page):
        """Test keyboard navigation in login form"""
        page.goto(f"{page.context.base_url}/login")
        
        # Tab through form elements
        page.keyboard.press("Tab")  # Email input
        expect(page.locator('[data-testid="email-input"]')).to_be_focused()
        
        page.keyboard.press("Tab")  # Password input
        expect(page.locator('[data-testid="password-input"]')).to_be_focused()
        
        page.keyboard.press("Tab")  # Remember me checkbox
        expect(page.locator('[data-testid="remember-me"]')).to_be_focused()
        
        page.keyboard.press("Tab")  # Login button
        expect(page.locator('[data-testid="login-button"]')).to_be_focused()
        
        # Test Enter key submission
        page.fill('[data-testid="email-input"]', "test@example.com")
        page.fill('[data-testid="password-input"]', "password123")
        page.locator('[data-testid="password-input"]').press("Enter")
        
        # Should trigger form submission
        expect(page.locator('[data-testid="login-spinner"]')).to_be_visible()


@pytest.mark.ui_functionality
@pytest.mark.authentication
@pytest.mark.critical
class TestRegistrationUI:
    """Test registration UI functionality"""
    
    def test_registration_page_loads(self, page: Page):
        """Test that registration page loads correctly"""
        page.goto(f"{page.context.base_url}/register")
        
        # Check page title
        expect(page).to_have_title(re.compile(".*Register.*Birthday Cake.*", re.IGNORECASE))
        
        # Check essential elements are present
        expect(page.locator('[data-testid="username-input"]')).to_be_visible()
        expect(page.locator('[data-testid="email-input"]')).to_be_visible()
        expect(page.locator('[data-testid="password-input"]')).to_be_visible()
        expect(page.locator('[data-testid="confirm-password-input"]')).to_be_visible()
        expect(page.locator('[data-testid="register-button"]')).to_be_visible()
        expect(page.locator('[data-testid="login-link"]')).to_be_visible()
        
        # Check Birthday Cake branding
        expect(page.locator('text=🎂')).to_be_visible()
        expect(page.locator('text=Join the Birthday Cake')).to_be_visible()
    
    def test_valid_registration_flow(self, page: Page):
        """Test successful registration flow"""
        page.goto(f"{page.context.base_url}/register")
        
        # Generate unique user data
        import time
        timestamp = str(int(time.time()))
        
        user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPassword123!"
        }
        
        # Fill registration form
        page.fill('[data-testid="username-input"]', user_data["username"])
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.fill('[data-testid="confirm-password-input"]', user_data["password"])
        
        # Submit form
        page.click('[data-testid="register-button"]')
        
        # Should redirect to dashboard or welcome page
        expect(page).to_have_url(re.compile(".*/dashboard|.*/welcome"))
        
        # Should show success message or welcome
        expect(page.locator('[data-testid="welcome-message"]')).to_be_visible()
    
    def test_registration_form_validation(self, page: Page):
        """Test registration form validation"""
        page.goto(f"{page.context.base_url}/register")
        
        # Try to submit empty form
        page.click('[data-testid="register-button"]')
        
        # Should show validation errors for all required fields
        expect(page.locator('[data-testid="username-error"]')).to_be_visible()
        expect(page.locator('[data-testid="email-error"]')).to_be_visible()
        expect(page.locator('[data-testid="password-error"]')).to_be_visible()
        
        # Test username validation
        page.fill('[data-testid="username-input"]', "ab")  # Too short
        page.click('[data-testid="register-button"]')
        expect(page.locator('[data-testid="username-error"]')).to_contain_text("at least 3 characters")
        
        # Test email validation
        page.fill('[data-testid="email-input"]', "invalid-email")
        page.click('[data-testid="register-button"]')
        expect(page.locator('[data-testid="email-error"]')).to_contain_text("valid email")
        
        # Test password validation
        page.fill('[data-testid="password-input"]', "weak")
        page.click('[data-testid="register-button"]')
        expect(page.locator('[data-testid="password-error"]')).to_contain_text("at least 8 characters")
    
    def test_password_confirmation_validation(self, page: Page):
        """Test password confirmation validation"""
        page.goto(f"{page.context.base_url}/register")
        
        # Fill passwords that don't match
        page.fill('[data-testid="password-input"]', "TestPassword123!")
        page.fill('[data-testid="confirm-password-input"]', "DifferentPassword123!")
        
        page.click('[data-testid="register-button"]')
        
        # Should show password mismatch error
        expect(page.locator('[data-testid="confirm-password-error"]')).to_be_visible()
        expect(page.locator('[data-testid="confirm-password-error"]')).to_contain_text("match")
    
    def test_password_strength_indicator(self, page: Page):
        """Test password strength indicator"""
        page.goto(f"{page.context.base_url}/register")
        
        password_input = page.locator('[data-testid="password-input"]')
        strength_indicator = page.locator('[data-testid="password-strength"]')
        
        # Test weak password
        password_input.fill("weak")
        expect(strength_indicator).to_contain_text("Weak")
        expect(strength_indicator).to_have_class(re.compile(".*weak.*"))
        
        # Test medium password
        password_input.fill("MediumPass123")
        expect(strength_indicator).to_contain_text("Medium")
        expect(strength_indicator).to_have_class(re.compile(".*medium.*"))
        
        # Test strong password
        password_input.fill("StrongPassword123!")
        expect(strength_indicator).to_contain_text("Strong")
        expect(strength_indicator).to_have_class(re.compile(".*strong.*"))
    
    def test_duplicate_username_error(self, page: Page, authenticated_user):
        """Test duplicate username error handling"""
        page.goto(f"{page.context.base_url}/register")
        
        # Try to register with existing username
        user_data = authenticated_user["user_data"]
        
        page.fill('[data-testid="username-input"]', user_data["username"])
        page.fill('[data-testid="email-input"]', "different@example.com")
        page.fill('[data-testid="password-input"]', "TestPassword123!")
        page.fill('[data-testid="confirm-password-input"]', "TestPassword123!")
        
        page.click('[data-testid="register-button"]')
        
        # Should show duplicate username error
        expect(page.locator('[data-testid="error-message"]')).to_be_visible()
        expect(page.locator('text=username already exists')).to_be_visible()
    
    def test_cake_personality_selection(self, page: Page):
        """Test Birthday Cake personality selection during registration"""
        page.goto(f"{page.context.base_url}/register")
        
        # Check if personality selection is available
        mood_selector = page.locator('[data-testid="cake-mood-selector"]')
        sweetness_selector = page.locator('[data-testid="cake-sweetness-selector"]')
        
        if mood_selector.is_visible():
            # Test mood selection
            mood_selector.select_option("excited")
            expect(mood_selector).to_have_value("excited")
            
            # Test sweetness level selection
            sweetness_selector.select_option("5")
            expect(sweetness_selector).to_have_value("5")
            
            # Should show personality preview
            expect(page.locator('[data-testid="personality-preview"]')).to_be_visible()
            expect(page.locator('text=🎉')).to_be_visible()  # Excited mood indicator


@pytest.mark.ui_functionality
@pytest.mark.authentication
@pytest.mark.medium
class TestAuthenticationNavigation:
    """Test authentication-related navigation"""
    
    def test_navigation_between_login_and_register(self, page: Page):
        """Test navigation between login and register pages"""
        # Start on login page
        page.goto(f"{page.context.base_url}/login")
        
        # Click register link
        page.click('[data-testid="register-link"]')
        expect(page).to_have_url(re.compile(".*/register"))
        
        # Click login link
        page.click('[data-testid="login-link"]')
        expect(page).to_have_url(re.compile(".*/login"))
    
    def test_protected_route_redirect(self, page: Page):
        """Test redirect to login for protected routes"""
        # Try to access dashboard without authentication
        page.goto(f"{page.context.base_url}/dashboard")
        
        # Should redirect to login
        expect(page).to_have_url(re.compile(".*/login"))
        
        # Should show message about needing to log in
        expect(page.locator('[data-testid="auth-required-message"]')).to_be_visible()
    
    def test_authenticated_user_redirect(self, page: Page, authenticated_user):
        """Test that authenticated users are redirected from auth pages"""
        # Login first
        page.goto(f"{page.context.base_url}/login")
        user_data = authenticated_user["user_data"]
        
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        # Wait for redirect to dashboard
        expect(page).to_have_url(re.compile(".*/dashboard"))
        
        # Now try to access login page again
        page.goto(f"{page.context.base_url}/login")
        
        # Should redirect back to dashboard
        expect(page).to_have_url(re.compile(".*/dashboard"))
    
    def test_logout_functionality(self, page: Page, authenticated_user):
        """Test logout functionality"""
        # Login first
        page.goto(f"{page.context.base_url}/login")
        user_data = authenticated_user["user_data"]
        
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        # Wait for dashboard
        expect(page).to_have_url(re.compile(".*/dashboard"))
        
        # Click logout
        page.click('[data-testid="logout-button"]')
        
        # Should redirect to login page
        expect(page).to_have_url(re.compile(".*/login"))
        
        # Should show logout success message
        expect(page.locator('[data-testid="logout-message"]')).to_be_visible()
        
        # Try to access protected route
        page.goto(f"{page.context.base_url}/dashboard")
        expect(page).to_have_url(re.compile(".*/login"))


@pytest.mark.ui_functionality
@pytest.mark.authentication
@pytest.mark.accessibility
class TestAuthenticationAccessibility:
    """Test authentication UI accessibility"""
    
    def test_form_labels_and_aria(self, page: Page):
        """Test form labels and ARIA attributes"""
        page.goto(f"{page.context.base_url}/login")
        
        # Check that inputs have proper labels
        email_input = page.locator('[data-testid="email-input"]')
        password_input = page.locator('[data-testid="password-input"]')
        
        expect(email_input).to_have_attribute("aria-label")
        expect(password_input).to_have_attribute("aria-label")
        
        # Check for associated labels
        expect(page.locator('label[for="email"]')).to_be_visible()
        expect(page.locator('label[for="password"]')).to_be_visible()
    
    def test_error_message_accessibility(self, page: Page):
        """Test error message accessibility"""
        page.goto(f"{page.context.base_url}/login")
        
        # Trigger validation errors
        page.click('[data-testid="login-button"]')
        
        # Check that error messages have proper ARIA attributes
        email_error = page.locator('[data-testid="email-error"]')
        password_error = page.locator('[data-testid="password-error"]')
        
        expect(email_error).to_have_attribute("role", "alert")
        expect(password_error).to_have_attribute("role", "alert")
        
        # Check that inputs reference error messages
        email_input = page.locator('[data-testid="email-input"]')
        expect(email_input).to_have_attribute("aria-describedby")
    
    def test_focus_management(self, page: Page):
        """Test focus management in authentication forms"""
        page.goto(f"{page.context.base_url}/login")
        
        # First focusable element should receive focus
        expect(page.locator('[data-testid="email-input"]')).to_be_focused()
        
        # Test focus trap in modal dialogs (if any)
        # This would test forgot password modal, etc.
    
    def test_color_contrast_and_visibility(self, page: Page):
        """Test color contrast and visibility"""
        page.goto(f"{page.context.base_url}/login")
        
        # Check that text has sufficient contrast
        # This would typically be done with automated accessibility testing tools
        # For now, we'll check that text is visible
        expect(page.locator('text=Email')).to_be_visible()
        expect(page.locator('text=Password')).to_be_visible()
        expect(page.locator('[data-testid="login-button"]')).to_be_visible()
    
    def test_screen_reader_compatibility(self, page: Page):
        """Test screen reader compatibility"""
        page.goto(f"{page.context.base_url}/login")
        
        # Check for proper heading structure
        expect(page.locator('h1')).to_be_visible()
        
        # Check for skip links
        skip_link = page.locator('[data-testid="skip-to-main"]')
        if skip_link.is_visible():
            expect(skip_link).to_have_attribute("href", "#main-content")


@pytest.mark.ui_functionality
@pytest.mark.authentication
@pytest.mark.performance
class TestAuthenticationPerformance:
    """Test authentication UI performance"""
    
    def test_page_load_performance(self, page: Page):
        """Test authentication page load performance"""
        import time
        
        start_time = time.time()
        page.goto(f"{page.context.base_url}/login")
        
        # Wait for page to be fully loaded
        expect(page.locator('[data-testid="login-button"]')).to_be_visible()
        
        load_time = time.time() - start_time
        
        # Page should load within 3 seconds
        assert load_time < 3.0
    
    def test_form_submission_performance(self, page: Page):
        """Test form submission performance"""
        page.goto(f"{page.context.base_url}/login")
        
        # Fill form
        page.fill('[data-testid="email-input"]', "test@example.com")
        page.fill('[data-testid="password-input"]', "password123")
        
        import time
        start_time = time.time()
        
        # Submit form
        page.click('[data-testid="login-button"]')
        
        # Wait for response (either success or error)
        page.wait_for_selector('[data-testid="error-message"], [data-testid="welcome-message"]')
        
        response_time = time.time() - start_time
        
        # Should respond within 5 seconds
        assert response_time < 5.0
    
    def test_client_side_validation_performance(self, page: Page):
        """Test client-side validation performance"""
        page.goto(f"{page.context.base_url}/register")
        
        import time
        
        # Test immediate validation feedback
        password_input = page.locator('[data-testid="password-input"]')
        
        start_time = time.time()
        password_input.fill("weak")
        
        # Validation feedback should appear quickly
        expect(page.locator('[data-testid="password-strength"]')).to_be_visible()
        
        validation_time = time.time() - start_time
        
        # Validation should be nearly instantaneous
        assert validation_time < 0.5


@pytest.mark.ui_functionality
@pytest.mark.authentication
@pytest.mark.browser_compatibility
class TestAuthenticationBrowserCompatibility:
    """Test authentication UI across different browsers"""
    
    @pytest.mark.browser_chromium
    def test_chromium_compatibility(self, page: Page):
        """Test authentication in Chromium"""
        page.goto(f"{page.context.base_url}/login")
        
        # Basic functionality should work
        expect(page.locator('[data-testid="email-input"]')).to_be_visible()
        expect(page.locator('[data-testid="password-input"]')).to_be_visible()
        expect(page.locator('[data-testid="login-button"]')).to_be_visible()
    
    @pytest.mark.browser_firefox
    def test_firefox_compatibility(self, page: Page):
        """Test authentication in Firefox"""
        page.goto(f"{page.context.base_url}/login")
        
        # Basic functionality should work
        expect(page.locator('[data-testid="email-input"]')).to_be_visible()
        expect(page.locator('[data-testid="password-input"]')).to_be_visible()
        expect(page.locator('[data-testid="login-button"]')).to_be_visible()
    
    @pytest.mark.browser_webkit
    def test_webkit_compatibility(self, page: Page):
        """Test authentication in WebKit"""
        page.goto(f"{page.context.base_url}/login")
        
        # Basic functionality should work
        expect(page.locator('[data-testid="email-input"]')).to_be_visible()
        expect(page.locator('[data-testid="password-input"]')).to_be_visible()
        expect(page.locator('[data-testid="login-button"]')).to_be_visible()


@pytest.mark.ui_functionality
@pytest.mark.authentication
@pytest.mark.responsive
class TestAuthenticationResponsive:
    """Test authentication UI responsiveness"""
    
    def test_mobile_layout(self, page: Page):
        """Test authentication on mobile viewport"""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{page.context.base_url}/login")
        
        # Elements should be visible and properly sized
        expect(page.locator('[data-testid="email-input"]')).to_be_visible()
        expect(page.locator('[data-testid="password-input"]')).to_be_visible()
        expect(page.locator('[data-testid="login-button"]')).to_be_visible()
        
        # Form should be properly sized for mobile
        form = page.locator('[data-testid="login-form"]')
        form_box = form.bounding_box()
        assert form_box["width"] <= 375  # Should fit in mobile width
    
    def test_tablet_layout(self, page: Page):
        """Test authentication on tablet viewport"""
        # Set tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto(f"{page.context.base_url}/login")
        
        # Elements should be visible and properly sized
        expect(page.locator('[data-testid="email-input"]')).to_be_visible()
        expect(page.locator('[data-testid="password-input"]')).to_be_visible()
        expect(page.locator('[data-testid="login-button"]')).to_be_visible()
    
    def test_desktop_layout(self, page: Page):
        """Test authentication on desktop viewport"""
        # Set desktop viewport
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(f"{page.context.base_url}/login")
        
        # Elements should be visible and properly sized
        expect(page.locator('[data-testid="email-input"]')).to_be_visible()
        expect(page.locator('[data-testid="password-input"]')).to_be_visible()
        expect(page.locator('[data-testid="login-button"]')).to_be_visible()
        
        # Should have proper desktop layout
        form = page.locator('[data-testid="login-form"]')
        form_box = form.bounding_box()
        assert form_box["width"] < 600  # Should be centered, not full width

