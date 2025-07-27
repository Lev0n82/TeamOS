"""
Comprehensive End-to-End Integration Tests for Birthday Cake Planner
Tests complete user workflows and system integration scenarios
"""

import pytest
import time
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from tests.config.test_config import TEST_USERS, TEST_TASKS


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.critical
class TestCompleteUserJourney:
    """Test complete user journey from registration to task completion"""
    
    def test_new_user_complete_workflow(self, page: Page):
        """Test complete workflow for a new user"""
        # Generate unique user data
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"e2euser_{timestamp}",
            "email": f"e2e_{timestamp}@example.com",
            "password": "E2EPassword123!"
        }
        
        # 1. User Registration
        page.goto(f"{page.context.base_url}/register")
        
        page.fill('[data-testid="username-input"]', user_data["username"])
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.fill('[data-testid="confirm-password-input"]', user_data["password"])
        
        page.click('[data-testid="register-button"]')
        
        # Should redirect to dashboard or welcome
        expect(page).to_have_url(re.compile(".*/dashboard|.*/welcome"))
        
        # 2. Welcome/Onboarding Experience
        if "welcome" in page.url:
            # Complete onboarding if present
            expect(page.locator('[data-testid="welcome-title"]')).to_be_visible()
            expect(page.locator('text=🎂')).to_be_visible()
            
            # Set cake personality preferences
            if page.locator('[data-testid="mood-selector"]').is_visible():
                page.select_option('[data-testid="mood-selector"]', "excited")
                page.select_option('[data-testid="sweetness-selector"]', "4")
                page.click('[data-testid="save-preferences"]')
            
            # Continue to dashboard
            page.click('[data-testid="continue-to-dashboard"]')
            expect(page).to_have_url(re.compile(".*/dashboard"))
        
        # 3. Dashboard First Visit
        expect(page.locator('[data-testid="dashboard-title"]')).to_be_visible()
        expect(page.locator(f'text={user_data["username"]}')).to_be_visible()
        
        # Should show empty state for new user
        expect(page.locator('[data-testid="empty-tasks-message"]')).to_be_visible()
        expect(page.locator('[data-testid="create-first-task-button"]')).to_be_visible()
        
        # 4. Create First Task
        page.click('[data-testid="create-first-task-button"]')
        
        # Task creation modal/form should open
        expect(page.locator('[data-testid="task-form"]')).to_be_visible()
        
        task_data = {
            "title": "My first birthday cake task",
            "description": "Learning to use the Birthday Cake Planner",
            "priority": "3",
            "difficulty": "2"
        }
        
        page.fill('[data-testid="task-title-input"]', task_data["title"])
        page.fill('[data-testid="task-description-input"]', task_data["description"])
        page.select_option('[data-testid="task-priority-select"]', task_data["priority"])
        page.select_option('[data-testid="task-difficulty-select"]', task_data["difficulty"])
        
        page.click('[data-testid="create-task-button"]')
        
        # 5. Task Created - AI Response
        expect(page.locator('[data-testid="task-created-success"]')).to_be_visible()
        expect(page.locator('[data-testid="cake-ai-response"]')).to_be_visible()
        expect(page.locator('text=🎂')).to_be_visible()
        
        # Close success modal
        page.click('[data-testid="close-success-modal"]')
        
        # 6. Task Appears in Dashboard
        expect(page.locator('[data-testid="task-list"]')).to_be_visible()
        expect(page.locator(f'text={task_data["title"]}')).to_be_visible()
        
        task_card = page.locator('[data-testid="task-card"]').first
        expect(task_card).to_be_visible()
        expect(task_card.locator('[data-testid="task-status"]')).to_contain_text("Pending")
        
        # 7. Complete the Task
        task_card.locator('[data-testid="complete-task-button"]').click()
        
        # Completion confirmation
        expect(page.locator('[data-testid="complete-task-modal"]')).to_be_visible()
        
        # Add actual duration
        page.fill('[data-testid="actual-duration-input"]', "45")
        page.click('[data-testid="confirm-completion-button"]')
        
        # 8. Task Completion - Celebration
        expect(page.locator('[data-testid="celebration-modal"]')).to_be_visible()
        expect(page.locator('[data-testid="celebration-animation"]')).to_be_visible()
        expect(page.locator('[data-testid="points-earned"]')).to_be_visible()
        expect(page.locator('[data-testid="cake-celebration-response"]')).to_be_visible()
        
        # Check celebration points
        points_text = page.locator('[data-testid="points-earned"]').text_content()
        assert "points" in points_text.lower()
        
        page.click('[data-testid="close-celebration-modal"]')
        
        # 9. Updated Dashboard State
        expect(task_card.locator('[data-testid="task-status"]')).to_contain_text("Completed")
        
        # User stats should be updated
        expect(page.locator('[data-testid="user-stats"]')).to_be_visible()
        expect(page.locator('[data-testid="total-points"]')).to_contain_text(re.compile(r"\d+"))
        expect(page.locator('[data-testid="tasks-completed"]')).to_contain_text("1")
        
        # 10. Create Additional Tasks
        page.click('[data-testid="add-task-button"]')
        
        # Create a more complex task
        complex_task = {
            "title": "Advanced birthday cake planning",
            "description": "Plan a complex birthday celebration",
            "priority": "5",
            "difficulty": "4",
            "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        }
        
        page.fill('[data-testid="task-title-input"]', complex_task["title"])
        page.fill('[data-testid="task-description-input"]', complex_task["description"])
        page.select_option('[data-testid="task-priority-select"]', complex_task["priority"])
        page.select_option('[data-testid="task-difficulty-select"]', complex_task["difficulty"])
        page.fill('[data-testid="task-due-date-input"]', complex_task["due_date"])
        
        page.click('[data-testid="create-task-button"]')
        
        # 11. Multiple Tasks Management
        expect(page.locator('[data-testid="task-card"]')).to_have_count(2)
        
        # Filter tasks
        page.click('[data-testid="filter-button"]')
        page.click('[data-testid="filter-pending"]')
        
        expect(page.locator('[data-testid="task-card"]:visible')).to_have_count(1)
        
        # 12. User Profile and Settings
        page.click('[data-testid="user-menu"]')
        page.click('[data-testid="profile-link"]')
        
        expect(page).to_have_url(re.compile(".*/profile"))
        expect(page.locator('[data-testid="profile-form"]')).to_be_visible()
        
        # Update cake personality
        page.select_option('[data-testid="cake-mood-select"]', "celebratory")
        page.select_option('[data-testid="cake-sweetness-select"]', "5")
        page.click('[data-testid="save-profile-button"]')
        
        expect(page.locator('[data-testid="profile-saved-message"]')).to_be_visible()
        
        # 13. Return to Dashboard
        page.click('[data-testid="dashboard-link"]')
        expect(page).to_have_url(re.compile(".*/dashboard"))
        
        # 14. Logout
        page.click('[data-testid="user-menu"]')
        page.click('[data-testid="logout-button"]')
        
        expect(page).to_have_url(re.compile(".*/login"))
        expect(page.locator('[data-testid="logout-success-message"]')).to_be_visible()
    
    def test_returning_user_workflow(self, page: Page, authenticated_user):
        """Test workflow for returning user with existing data"""
        # Login as existing user
        page.goto(f"{page.context.base_url}/login")
        
        user_data = authenticated_user["user_data"]
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        expect(page).to_have_url(re.compile(".*/dashboard"))
        
        # Should show existing user welcome
        expect(page.locator('[data-testid="welcome-back-message"]')).to_be_visible()
        
        # Create multiple tasks quickly
        tasks_to_create = [
            {"title": "Morning task", "priority": "2", "difficulty": "1"},
            {"title": "Afternoon task", "priority": "4", "difficulty": "3"},
            {"title": "Evening task", "priority": "3", "difficulty": "2"}
        ]
        
        for task in tasks_to_create:
            page.click('[data-testid="add-task-button"]')
            page.fill('[data-testid="task-title-input"]', task["title"])
            page.select_option('[data-testid="task-priority-select"]', task["priority"])
            page.select_option('[data-testid="task-difficulty-select"]', task["difficulty"])
            page.click('[data-testid="create-task-button"]')
            
            # Wait for task to be created
            expect(page.locator('[data-testid="task-created-success"]')).to_be_visible()
            page.click('[data-testid="close-success-modal"]')
        
        # Complete tasks in sequence to build streak
        task_cards = page.locator('[data-testid="task-card"]')
        task_count = task_cards.count()
        
        for i in range(min(3, task_count)):
            task_card = task_cards.nth(i)
            task_card.locator('[data-testid="complete-task-button"]').click()
            
            expect(page.locator('[data-testid="complete-task-modal"]')).to_be_visible()
            page.click('[data-testid="confirm-completion-button"]')
            
            # Check for streak recognition in later completions
            if i >= 1:
                celebration_text = page.locator('[data-testid="cake-celebration-response"]').text_content()
                if i >= 2:
                    assert any(word in celebration_text.lower() 
                             for word in ['streak', 'roll', 'momentum'])
            
            page.click('[data-testid="close-celebration-modal"]')
        
        # Check updated stats
        expect(page.locator('[data-testid="current-streak"]')).to_contain_text(re.compile(r"[3-9]|[1-9]\d+"))


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.high
class TestAIIntegrationWorkflows:
    """Test AI integration in complete workflows"""
    
    def test_ai_personality_adaptation_workflow(self, page: Page, authenticated_user):
        """Test AI personality adaptation throughout user interaction"""
        # Login
        page.goto(f"{page.context.base_url}/login")
        user_data = authenticated_user["user_data"]
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        # Create tasks with different characteristics
        task_scenarios = [
            {"title": "Easy morning task", "priority": "1", "difficulty": "1", "expected_mood": "encouraging"},
            {"title": "Challenging project", "priority": "5", "difficulty": "5", "expected_mood": "motivational"},
            {"title": "Quick daily task", "priority": "2", "difficulty": "1", "expected_mood": "cheerful"}
        ]
        
        ai_responses = []
        
        for scenario in task_scenarios:
            # Create task
            page.click('[data-testid="add-task-button"]')
            page.fill('[data-testid="task-title-input"]', scenario["title"])
            page.select_option('[data-testid="task-priority-select"]', scenario["priority"])
            page.select_option('[data-testid="task-difficulty-select"]', scenario["difficulty"])
            page.click('[data-testid="create-task-button"]')
            
            # Capture AI response
            expect(page.locator('[data-testid="cake-ai-response"]')).to_be_visible()
            ai_response = page.locator('[data-testid="cake-ai-response"]').text_content()
            ai_responses.append(ai_response)
            
            page.click('[data-testid="close-success-modal"]')
            
            # Complete task
            task_card = page.locator('[data-testid="task-card"]').last
            task_card.locator('[data-testid="complete-task-button"]').click()
            page.click('[data-testid="confirm-completion-button"]')
            
            # Capture completion response
            completion_response = page.locator('[data-testid="cake-celebration-response"]').text_content()
            ai_responses.append(completion_response)
            
            page.click('[data-testid="close-celebration-modal"]')
        
        # Verify AI responses are contextually appropriate
        assert len(ai_responses) == 6  # 3 creation + 3 completion responses
        
        # High difficulty task should get more enthusiastic responses
        high_difficulty_responses = [ai_responses[2], ai_responses[3]]  # Challenging project
        for response in high_difficulty_responses:
            assert any(word in response.lower() 
                     for word in ['amazing', 'incredible', 'outstanding', 'challenge'])
    
    def test_ai_fallback_recovery_workflow(self, page: Page, authenticated_user):
        """Test AI fallback and recovery in user workflow"""
        # This test would require mocking AI service failures
        # For now, we'll test the UI handles both AI and fallback responses
        
        page.goto(f"{page.context.base_url}/login")
        user_data = authenticated_user["user_data"]
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        # Create task
        page.click('[data-testid="add-task-button"]')
        page.fill('[data-testid="task-title-input"]', "AI fallback test task")
        page.select_option('[data-testid="task-priority-select"]', "3")
        page.select_option('[data-testid="task-difficulty-select"]', "3")
        page.click('[data-testid="create-task-button"]')
        
        # Should get some response (AI or fallback)
        expect(page.locator('[data-testid="cake-ai-response"]')).to_be_visible()
        response_text = page.locator('[data-testid="cake-ai-response"]').text_content()
        
        # Should contain birthday cake themed content
        assert '🎂' in response_text or '🍰' in response_text or '🎉' in response_text
        
        # Check response source indicator if available
        if page.locator('[data-testid="response-source"]').is_visible():
            source = page.locator('[data-testid="response-source"]').text_content()
            assert source in ['AI', 'Fallback']


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.medium
class TestDataPersistenceWorkflows:
    """Test data persistence across sessions"""
    
    def test_data_persistence_across_sessions(self, page: Page, authenticated_user):
        """Test that user data persists across browser sessions"""
        # Session 1: Create data
        page.goto(f"{page.context.base_url}/login")
        user_data = authenticated_user["user_data"]
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        # Create a task
        page.click('[data-testid="add-task-button"]')
        task_title = f"Persistence test task {int(time.time())}"
        page.fill('[data-testid="task-title-input"]', task_title)
        page.select_option('[data-testid="task-priority-select"]', "4")
        page.select_option('[data-testid="task-difficulty-select"]', "3")
        page.click('[data-testid="create-task-button"]')
        page.click('[data-testid="close-success-modal"]')
        
        # Update profile
        page.click('[data-testid="user-menu"]')
        page.click('[data-testid="profile-link"]')
        page.select_option('[data-testid="cake-mood-select"]', "excited")
        page.click('[data-testid="save-profile-button"]')
        
        # Logout
        page.click('[data-testid="user-menu"]')
        page.click('[data-testid="logout-button"]')
        
        # Session 2: Verify data persistence
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        # Task should still exist
        expect(page.locator(f'text={task_title}')).to_be_visible()
        
        # Profile settings should be preserved
        page.click('[data-testid="user-menu"]')
        page.click('[data-testid="profile-link"]')
        expect(page.locator('[data-testid="cake-mood-select"]')).to_have_value("excited")
    
    def test_offline_behavior(self, page: Page, authenticated_user):
        """Test application behavior when offline"""
        # Login first
        page.goto(f"{page.context.base_url}/login")
        user_data = authenticated_user["user_data"]
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        # Go offline
        page.context.set_offline(True)
        
        # Try to create a task
        page.click('[data-testid="add-task-button"]')
        page.fill('[data-testid="task-title-input"]', "Offline test task")
        page.select_option('[data-testid="task-priority-select"]', "3")
        page.select_option('[data-testid="task-difficulty-select"]', "2")
        page.click('[data-testid="create-task-button"]')
        
        # Should show offline message or queue the action
        if page.locator('[data-testid="offline-message"]').is_visible():
            expect(page.locator('[data-testid="offline-message"]')).to_contain_text("offline")
        
        # Go back online
        page.context.set_offline(False)
        
        # Should sync or allow retry
        if page.locator('[data-testid="retry-button"]').is_visible():
            page.click('[data-testid="retry-button"]')


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.performance
class TestPerformanceWorkflows:
    """Test performance in realistic user workflows"""
    
    def test_dashboard_performance_with_many_tasks(self, page: Page, authenticated_user):
        """Test dashboard performance with many tasks"""
        page.goto(f"{page.context.base_url}/login")
        user_data = authenticated_user["user_data"]
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        # Create many tasks quickly
        start_time = time.time()
        
        for i in range(20):
            page.click('[data-testid="add-task-button"]')
            page.fill('[data-testid="task-title-input"]', f"Performance task {i}")
            page.select_option('[data-testid="task-priority-select"]', str((i % 5) + 1))
            page.select_option('[data-testid="task-difficulty-select"]', str((i % 5) + 1))
            page.click('[data-testid="create-task-button"]')
            page.click('[data-testid="close-success-modal"]')
        
        creation_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert creation_time < 60  # 60 seconds for 20 tasks
        
        # Dashboard should still be responsive
        start_time = time.time()
        page.reload()
        expect(page.locator('[data-testid="task-list"]')).to_be_visible()
        load_time = time.time() - start_time
        
        assert load_time < 5  # Should load within 5 seconds
        
        # Filtering should be fast
        start_time = time.time()
        page.click('[data-testid="filter-button"]')
        page.click('[data-testid="filter-high-priority"]')
        filter_time = time.time() - start_time
        
        assert filter_time < 2  # Filtering should be fast
    
    def test_concurrent_user_simulation(self, page: Page):
        """Test behavior under concurrent user load simulation"""
        # This test simulates multiple users by rapid actions
        # In a real scenario, this would be done with multiple browser contexts
        
        # Create user
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"concurrent_{timestamp}",
            "email": f"concurrent_{timestamp}@example.com",
            "password": "ConcurrentTest123!"
        }
        
        page.goto(f"{page.context.base_url}/register")
        page.fill('[data-testid="username-input"]', user_data["username"])
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.fill('[data-testid="confirm-password-input"]', user_data["password"])
        page.click('[data-testid="register-button"]')
        
        # Rapid task creation and completion
        for i in range(10):
            # Create task
            page.click('[data-testid="add-task-button"]')
            page.fill('[data-testid="task-title-input"]', f"Concurrent task {i}")
            page.select_option('[data-testid="task-priority-select"]', "3")
            page.select_option('[data-testid="task-difficulty-select"]', "2")
            page.click('[data-testid="create-task-button"]')
            page.click('[data-testid="close-success-modal"]')
            
            # Complete task immediately
            task_card = page.locator('[data-testid="task-card"]').last
            task_card.locator('[data-testid="complete-task-button"]').click()
            page.click('[data-testid="confirm-completion-button"]')
            page.click('[data-testid="close-celebration-modal"]')
        
        # System should remain stable
        expect(page.locator('[data-testid="dashboard-title"]')).to_be_visible()
        expect(page.locator('[data-testid="user-stats"]')).to_be_visible()


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.security
class TestSecurityWorkflows:
    """Test security aspects in complete workflows"""
    
    def test_session_security_workflow(self, page: Page, authenticated_user):
        """Test session security and timeout behavior"""
        # Login
        page.goto(f"{page.context.base_url}/login")
        user_data = authenticated_user["user_data"]
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        # Verify authenticated state
        expect(page.locator('[data-testid="dashboard-title"]')).to_be_visible()
        
        # Clear session storage (simulate session expiry)
        page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        
        # Try to access protected resource
        page.reload()
        
        # Should redirect to login
        expect(page).to_have_url(re.compile(".*/login"))
        expect(page.locator('[data-testid="session-expired-message"]')).to_be_visible()
    
    def test_xss_protection_workflow(self, page: Page, authenticated_user):
        """Test XSS protection in user workflows"""
        page.goto(f"{page.context.base_url}/login")
        user_data = authenticated_user["user_data"]
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        # Try to create task with XSS payload
        xss_payload = "<script>alert('XSS')</script>Malicious Task"
        
        page.click('[data-testid="add-task-button"]')
        page.fill('[data-testid="task-title-input"]', xss_payload)
        page.select_option('[data-testid="task-priority-select"]', "3")
        page.select_option('[data-testid="task-difficulty-select"]', "2")
        page.click('[data-testid="create-task-button"]')
        
        # Should either reject the input or sanitize it
        if page.locator('[data-testid="task-created-success"]').is_visible():
            page.click('[data-testid="close-success-modal"]')
            
            # Check that script tags are not executed
            task_title = page.locator('[data-testid="task-card"] [data-testid="task-title"]').first.text_content()
            assert '<script>' not in task_title
            assert 'alert(' not in task_title
        else:
            # Should show validation error
            expect(page.locator('[data-testid="validation-error"]')).to_be_visible()


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.accessibility
class TestAccessibilityWorkflows:
    """Test accessibility in complete workflows"""
    
    def test_keyboard_navigation_workflow(self, page: Page, authenticated_user):
        """Test complete workflow using only keyboard navigation"""
        # Login using keyboard
        page.goto(f"{page.context.base_url}/login")
        
        user_data = authenticated_user["user_data"]
        
        # Tab to email input
        page.keyboard.press("Tab")
        page.keyboard.type(user_data["email"])
        
        # Tab to password input
        page.keyboard.press("Tab")
        page.keyboard.type(user_data["password"])
        
        # Tab to login button and press Enter
        page.keyboard.press("Tab")
        page.keyboard.press("Enter")
        
        expect(page).to_have_url(re.compile(".*/dashboard"))
        
        # Navigate to create task using keyboard
        page.keyboard.press("Tab")  # Navigate to add task button
        while not page.locator('[data-testid="add-task-button"]').is_focused():
            page.keyboard.press("Tab")
        
        page.keyboard.press("Enter")  # Open task form
        
        # Fill task form using keyboard
        page.keyboard.type("Keyboard navigation test task")
        page.keyboard.press("Tab")  # Move to description
        page.keyboard.type("Testing keyboard accessibility")
        page.keyboard.press("Tab")  # Move to priority
        page.keyboard.press("ArrowDown")  # Select priority
        page.keyboard.press("Tab")  # Move to difficulty
        page.keyboard.press("ArrowDown")  # Select difficulty
        page.keyboard.press("Tab")  # Move to create button
        page.keyboard.press("Enter")  # Create task
        
        expect(page.locator('[data-testid="task-created-success"]')).to_be_visible()
    
    def test_screen_reader_workflow(self, page: Page, authenticated_user):
        """Test workflow with screen reader considerations"""
        page.goto(f"{page.context.base_url}/login")
        user_data = authenticated_user["user_data"]
        page.fill('[data-testid="email-input"]', user_data["email"])
        page.fill('[data-testid="password-input"]', user_data["password"])
        page.click('[data-testid="login-button"]')
        
        # Check for proper ARIA labels and roles
        expect(page.locator('[role="main"]')).to_be_visible()
        expect(page.locator('[role="navigation"]')).to_be_visible()
        
        # Check for proper heading structure
        expect(page.locator('h1')).to_be_visible()
        
        # Create task and check accessibility
        page.click('[data-testid="add-task-button"]')
        
        # Form should have proper labels
        expect(page.locator('label[for="task-title"]')).to_be_visible()
        expect(page.locator('[data-testid="task-title-input"]')).to_have_attribute("aria-label")
        
        # Error messages should have proper ARIA attributes
        page.click('[data-testid="create-task-button"]')  # Submit empty form
        
        if page.locator('[data-testid="validation-error"]').is_visible():
            expect(page.locator('[data-testid="validation-error"]')).to_have_attribute("role", "alert")

