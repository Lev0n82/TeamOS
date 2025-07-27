"""
Comprehensive Task Management API Tests for Birthday Cake Planner
Tests all task CRUD operations, business rules, validation, and edge cases
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from tests.config.test_config import TEST_TASKS, VALIDATION_RULES


@pytest.mark.task_management
@pytest.mark.critical
class TestTaskCreation:
    """Test task creation functionality"""
    
    def test_create_valid_task(self, authenticated_user, test_task_data):
        """Test creating a task with valid data"""
        client = authenticated_user["client"]
        
        response = client.post('/api/tasks', json=test_task_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['title'] == test_task_data['title']
        assert data['data']['task']['description'] == test_task_data['description']
        assert data['data']['task']['priority'] == test_task_data['priority']
        assert data['data']['task']['difficulty'] == test_task_data['difficulty']
        assert data['data']['task']['status'] == 'pending'
        
        # Check that Birthday Cake AI response is included
        assert 'cake_response' in data['data']
        assert 'text' in data['data']['cake_response']
        assert '🎂' in data['data']['cake_response']['text'] or '🍰' in data['data']['cake_response']['text']
    
    def test_create_task_with_minimal_data(self, authenticated_user):
        """Test creating task with only required fields"""
        client = authenticated_user["client"]
        
        minimal_task = {
            "title": "Minimal task",
            "priority": 3,
            "difficulty": 2
        }
        
        response = client.post('/api/tasks', json=minimal_task)
        
        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['title'] == minimal_task['title']
        assert data['data']['task']['description'] == ""  # Default empty description
        assert data['data']['task']['estimated_duration'] == 60  # Default duration
    
    def test_create_task_with_due_date(self, authenticated_user):
        """Test creating task with due date"""
        client = authenticated_user["client"]
        
        future_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Task with due date",
            "priority": 3,
            "difficulty": 2,
            "due_date": future_date
        }
        
        response = client.post('/api/tasks', json=task_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['due_date'] is not None
    
    @pytest.mark.parametrize("invalid_field,invalid_value", [
        ("title", ""),
        ("title", "A" * 201),  # Too long
        ("priority", 0),
        ("priority", 6),
        ("difficulty", 0),
        ("difficulty", 6),
        ("estimated_duration", -30),
        ("estimated_duration", 1441),  # More than 24 hours
    ])
    def test_create_task_validation_errors(self, authenticated_user, invalid_field, invalid_value):
        """Test task creation validation for invalid inputs"""
        client = authenticated_user["client"]
        
        task_data = {
            "title": "Valid task",
            "priority": 3,
            "difficulty": 2,
            "estimated_duration": 60
        }
        task_data[invalid_field] = invalid_value
        
        response = client.post('/api/tasks', json=task_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data['success'] is False
        assert len(data['errors']) > 0
        
        # Check that the specific field error is present
        field_errors = [error for error in data['errors'] if error.get('field') == invalid_field]
        assert len(field_errors) > 0
    
    def test_create_task_missing_required_fields(self, authenticated_user):
        """Test task creation fails when required fields are missing"""
        client = authenticated_user["client"]
        
        incomplete_data = {"description": "Task without title"}
        
        response = client.post('/api/tasks', json=incomplete_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data['success'] is False
        assert any(error.get('field') == 'title' for error in data['errors'])
    
    def test_create_task_without_authentication(self, api_client, test_task_data):
        """Test task creation fails without authentication"""
        response = api_client.post('/api/tasks', json=test_task_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data['success'] is False
    
    def test_create_task_calculates_celebration_points(self, authenticated_user):
        """Test that task creation calculates celebration points reward"""
        client = authenticated_user["client"]
        
        task_data = {
            "title": "High priority difficult task",
            "priority": 5,
            "difficulty": 5,
            "estimated_duration": 120
        }
        
        response = client.post('/api/tasks', json=task_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        
        task = data['data']['task']
        assert 'celebration_points_reward' in task
        assert task['celebration_points_reward'] > 0
        
        # Higher priority and difficulty should give more points
        assert task['celebration_points_reward'] >= 10


@pytest.mark.task_management
@pytest.mark.critical
class TestTaskRetrieval:
    """Test task retrieval functionality"""
    
    def test_get_user_tasks(self, authenticated_user, test_task):
        """Test retrieving user's tasks"""
        client = authenticated_user["client"]
        
        response = client.get('/api/tasks')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'tasks' in data['data']
        assert len(data['data']['tasks']) > 0
        
        # Check that returned task belongs to the user
        task = data['data']['tasks'][0]
        assert 'id' in task
        assert 'title' in task
        assert 'status' in task
    
    def test_get_tasks_with_filters(self, authenticated_user):
        """Test retrieving tasks with status filter"""
        client = authenticated_user["client"]
        
        # Create tasks with different statuses
        task1_data = {"title": "Pending task", "priority": 3, "difficulty": 2}
        task2_data = {"title": "Another task", "priority": 4, "difficulty": 3}
        
        client.post('/api/tasks', json=task1_data)
        task2_response = client.post('/api/tasks', json=task2_data)
        task2_id = task2_response.json()['data']['task']['id']
        
        # Complete one task
        client.post(f'/api/tasks/{task2_id}/complete')
        
        # Filter by pending status
        response = client.get('/api/tasks?status=pending')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        
        # All returned tasks should be pending
        for task in data['data']['tasks']:
            assert task['status'] == 'pending'
    
    def test_get_tasks_with_pagination(self, authenticated_user):
        """Test task retrieval with pagination"""
        client = authenticated_user["client"]
        
        # Create multiple tasks
        for i in range(15):
            task_data = {
                "title": f"Task {i}",
                "priority": 3,
                "difficulty": 2
            }
            client.post('/api/tasks', json=task_data)
        
        # Get first page
        response = client.get('/api/tasks?page=1&limit=10')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert len(data['data']['tasks']) == 10
        assert 'pagination' in data['data']
        assert data['data']['pagination']['page'] == 1
        assert data['data']['pagination']['total'] >= 15
    
    def test_get_single_task(self, authenticated_user, test_task):
        """Test retrieving a single task by ID"""
        client = authenticated_user["client"]
        
        response = client.get(f'/api/tasks/{test_task.id}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['id'] == test_task.id
        assert data['data']['task']['title'] == test_task.title
    
    def test_get_nonexistent_task(self, authenticated_user):
        """Test retrieving a task that doesn't exist"""
        client = authenticated_user["client"]
        
        response = client.get('/api/tasks/99999')
        
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
    
    def test_get_other_users_task(self, authenticated_user, api_client):
        """Test that users cannot access other users' tasks"""
        # Create another user and task
        other_user_data = {
            "username": "otheruser",
            "email": f"other_{int(time.time())}@example.com",
            "password": "OtherPassword123!"
        }
        
        register_response = api_client.post('/api/auth/register', json=other_user_data)
        assert register_response.status_code == 201
        
        login_response = api_client.post('/api/auth/login', json={
            "email": other_user_data["email"],
            "password": other_user_data["password"]
        })
        other_token = login_response.json()['data']['token']
        
        # Create task as other user
        api_client.set_auth_token(other_token)
        task_response = api_client.post('/api/tasks', json={
            "title": "Other user's task",
            "priority": 3,
            "difficulty": 2
        })
        other_task_id = task_response.json()['data']['task']['id']
        
        # Try to access other user's task with original user
        client = authenticated_user["client"]
        response = client.get(f'/api/tasks/{other_task_id}')
        
        assert response.status_code == 404  # Should not be found for this user


@pytest.mark.task_management
@pytest.mark.critical
class TestTaskUpdate:
    """Test task update functionality"""
    
    def test_update_task_title(self, authenticated_user, test_task):
        """Test updating task title"""
        client = authenticated_user["client"]
        
        update_data = {"title": "Updated task title"}
        
        response = client.put(f'/api/tasks/{test_task.id}', json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['title'] == update_data['title']
    
    def test_update_task_priority_and_difficulty(self, authenticated_user, test_task):
        """Test updating task priority and difficulty"""
        client = authenticated_user["client"]
        
        update_data = {
            "priority": 5,
            "difficulty": 4
        }
        
        response = client.put(f'/api/tasks/{test_task.id}', json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['priority'] == 5
        assert data['data']['task']['difficulty'] == 4
        
        # Celebration points should be recalculated
        assert 'celebration_points_reward' in data['data']['task']
    
    def test_update_task_due_date(self, authenticated_user, test_task):
        """Test updating task due date"""
        client = authenticated_user["client"]
        
        new_due_date = (datetime.utcnow() + timedelta(days=3)).isoformat()
        update_data = {"due_date": new_due_date}
        
        response = client.put(f'/api/tasks/{test_task.id}', json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['due_date'] is not None
    
    def test_update_task_with_invalid_data(self, authenticated_user, test_task):
        """Test updating task with invalid data"""
        client = authenticated_user["client"]
        
        invalid_data = {
            "priority": 10,  # Invalid priority
            "title": ""      # Empty title
        }
        
        response = client.put(f'/api/tasks/{test_task.id}', json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data['success'] is False
        assert len(data['errors']) > 0
    
    def test_update_nonexistent_task(self, authenticated_user):
        """Test updating a task that doesn't exist"""
        client = authenticated_user["client"]
        
        update_data = {"title": "Updated title"}
        
        response = client.put('/api/tasks/99999', json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
    
    def test_partial_task_update(self, authenticated_user, test_task):
        """Test partial task update (only some fields)"""
        client = authenticated_user["client"]
        
        original_title = test_task.title
        update_data = {"description": "Updated description only"}
        
        response = client.put(f'/api/tasks/{test_task.id}', json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['title'] == original_title  # Should remain unchanged
        assert data['data']['task']['description'] == update_data['description']


@pytest.mark.task_management
@pytest.mark.critical
class TestTaskCompletion:
    """Test task completion functionality"""
    
    def test_complete_task(self, authenticated_user, test_task):
        """Test completing a task"""
        client = authenticated_user["client"]
        
        response = client.post(f'/api/tasks/{test_task.id}/complete')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['status'] == 'completed'
        assert data['data']['task']['completed_at'] is not None
        
        # Check celebration response
        assert 'cake_response' in data['data']
        assert 'celebration_points_gained' in data['data']
        assert data['data']['celebration_points_gained'] > 0
        
        # Check for level up
        assert 'level_up' in data['data']
    
    def test_complete_task_with_actual_duration(self, authenticated_user, test_task):
        """Test completing task with actual duration"""
        client = authenticated_user["client"]
        
        completion_data = {"actual_duration": 90}
        
        response = client.post(f'/api/tasks/{test_task.id}/complete', json=completion_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['actual_duration'] == 90
    
    def test_complete_already_completed_task(self, authenticated_user, test_task):
        """Test completing an already completed task"""
        client = authenticated_user["client"]
        
        # Complete the task first
        response1 = client.post(f'/api/tasks/{test_task.id}/complete')
        assert response1.status_code == 200
        
        # Try to complete again
        response2 = client.post(f'/api/tasks/{test_task.id}/complete')
        
        assert response2.status_code == 422
        data = response2.json()
        assert data['success'] is False
        assert 'already completed' in data['message'].lower()
    
    def test_complete_nonexistent_task(self, authenticated_user):
        """Test completing a task that doesn't exist"""
        client = authenticated_user["client"]
        
        response = client.post('/api/tasks/99999/complete')
        
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
    
    def test_task_completion_updates_user_stats(self, authenticated_user, test_task):
        """Test that task completion updates user statistics"""
        client = authenticated_user["client"]
        
        # Get user stats before completion
        profile_response = client.get('/api/auth/me')
        initial_points = profile_response.json()['data']['user']['total_celebration_points']
        initial_streak = profile_response.json()['data']['user']['current_streak']
        
        # Complete task
        response = client.post(f'/api/tasks/{test_task.id}/complete')
        assert response.status_code == 200
        
        # Check updated user stats
        updated_profile = client.get('/api/auth/me')
        updated_points = updated_profile.json()['data']['user']['total_celebration_points']
        updated_streak = updated_profile.json()['data']['user']['current_streak']
        
        assert updated_points > initial_points
        assert updated_streak >= initial_streak
    
    @patch('src.routes.cake.get_cake_response_ai')
    def test_task_completion_ai_integration(self, mock_ai_response, authenticated_user, test_task):
        """Test that task completion integrates with AI system"""
        client = authenticated_user["client"]
        
        # Mock AI response
        mock_ai_response.return_value = {
            'text': '🎂 Fantastic work! Sweet success! ✨',
            'mood': 'celebratory',
            'animation': 'confetti_explosion',
            'source': 'ai'
        }
        
        response = client.post(f'/api/tasks/{test_task.id}/complete')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        
        # Verify AI was called
        mock_ai_response.assert_called_once()
        
        # Check AI response in result
        cake_response = data['data']['cake_response']
        assert cake_response['text'] == '🎂 Fantastic work! Sweet success! ✨'
        assert cake_response['mood'] == 'celebratory'


@pytest.mark.task_management
@pytest.mark.medium
class TestTaskDeletion:
    """Test task deletion functionality"""
    
    def test_delete_task(self, authenticated_user, test_task):
        """Test deleting a task"""
        client = authenticated_user["client"]
        
        response = client.delete(f'/api/tasks/{test_task.id}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        
        # Verify task is deleted
        get_response = client.get(f'/api/tasks/{test_task.id}')
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_task(self, authenticated_user):
        """Test deleting a task that doesn't exist"""
        client = authenticated_user["client"]
        
        response = client.delete('/api/tasks/99999')
        
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
    
    def test_delete_completed_task(self, authenticated_user, test_task):
        """Test deleting a completed task"""
        client = authenticated_user["client"]
        
        # Complete the task first
        complete_response = client.post(f'/api/tasks/{test_task.id}/complete')
        assert complete_response.status_code == 200
        
        # Delete the completed task
        response = client.delete(f'/api/tasks/{test_task.id}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True


@pytest.mark.task_management
@pytest.mark.business_rules
class TestTaskBusinessRules:
    """Test task management business rules"""
    
    def test_overdue_task_detection(self, authenticated_user):
        """Test detection of overdue tasks"""
        client = authenticated_user["client"]
        
        # Create task with past due date
        past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        task_data = {
            "title": "Overdue task",
            "priority": 3,
            "difficulty": 2,
            "due_date": past_date
        }
        
        response = client.post('/api/tasks', json=task_data)
        assert response.status_code == 201
        
        task_id = response.json()['data']['task']['id']
        
        # Get task and check overdue status
        get_response = client.get(f'/api/tasks/{task_id}')
        task = get_response.json()['data']['task']
        
        assert task['is_overdue'] is True
    
    def test_task_priority_affects_celebration_points(self, authenticated_user):
        """Test that task priority affects celebration points calculation"""
        client = authenticated_user["client"]
        
        # Create low priority task
        low_priority_task = {
            "title": "Low priority task",
            "priority": 1,
            "difficulty": 2
        }
        
        # Create high priority task
        high_priority_task = {
            "title": "High priority task",
            "priority": 5,
            "difficulty": 2
        }
        
        low_response = client.post('/api/tasks', json=low_priority_task)
        high_response = client.post('/api/tasks', json=high_priority_task)
        
        low_points = low_response.json()['data']['task']['celebration_points_reward']
        high_points = high_response.json()['data']['task']['celebration_points_reward']
        
        assert high_points > low_points
    
    def test_task_difficulty_affects_celebration_points(self, authenticated_user):
        """Test that task difficulty affects celebration points calculation"""
        client = authenticated_user["client"]
        
        # Create easy task
        easy_task = {
            "title": "Easy task",
            "priority": 3,
            "difficulty": 1
        }
        
        # Create difficult task
        difficult_task = {
            "title": "Difficult task",
            "priority": 3,
            "difficulty": 5
        }
        
        easy_response = client.post('/api/tasks', json=easy_task)
        difficult_response = client.post('/api/tasks', json=difficult_task)
        
        easy_points = easy_response.json()['data']['task']['celebration_points_reward']
        difficult_points = difficult_response.json()['data']['task']['celebration_points_reward']
        
        assert difficult_points > easy_points
    
    def test_streak_bonus_calculation(self, authenticated_user):
        """Test streak bonus calculation for consecutive task completions"""
        client = authenticated_user["client"]
        
        # Complete multiple tasks to build streak
        for i in range(3):
            task_data = {
                "title": f"Streak task {i}",
                "priority": 3,
                "difficulty": 2
            }
            
            create_response = client.post('/api/tasks', json=task_data)
            task_id = create_response.json()['data']['task']['id']
            
            complete_response = client.post(f'/api/tasks/{task_id}/complete')
            assert complete_response.status_code == 200
            
            if i >= 2:  # Third task should have streak bonus
                completion_data = complete_response.json()['data']
                assert completion_data['celebration_points_gained'] > 10  # Base points + bonus
    
    def test_daily_task_limit(self, authenticated_user):
        """Test daily task creation limit if implemented"""
        client = authenticated_user["client"]
        
        # Create many tasks in one day
        created_tasks = 0
        for i in range(100):  # Try to create 100 tasks
            task_data = {
                "title": f"Daily task {i}",
                "priority": 3,
                "difficulty": 2
            }
            
            response = client.post('/api/tasks', json=task_data)
            if response.status_code == 201:
                created_tasks += 1
            elif response.status_code == 429:  # Rate limited
                break
        
        # Should be able to create at least 50 tasks per day
        assert created_tasks >= 50


@pytest.mark.task_management
@pytest.mark.performance
class TestTaskPerformance:
    """Test task management performance"""
    
    def test_task_creation_performance(self, authenticated_user, performance_monitor):
        """Test task creation endpoint performance"""
        client = authenticated_user["client"]
        
        task_data = {
            "title": "Performance test task",
            "priority": 3,
            "difficulty": 2
        }
        
        performance_monitor.start()
        response = client.post('/api/tasks', json=task_data)
        performance_monitor.stop()
        
        assert response.status_code == 201
        
        metrics = performance_monitor.get_metrics()
        assert metrics["duration_ms"] < 1000  # Should complete within 1 second
    
    def test_task_list_performance_with_many_tasks(self, authenticated_user, performance_monitor):
        """Test task list performance with many tasks"""
        client = authenticated_user["client"]
        
        # Create 100 tasks
        for i in range(100):
            task_data = {
                "title": f"Performance task {i}",
                "priority": (i % 5) + 1,
                "difficulty": (i % 5) + 1
            }
            client.post('/api/tasks', json=task_data)
        
        # Test list performance
        performance_monitor.start()
        response = client.get('/api/tasks')
        performance_monitor.stop()
        
        assert response.status_code == 200
        
        metrics = performance_monitor.get_metrics()
        assert metrics["duration_ms"] < 2000  # Should complete within 2 seconds
    
    def test_concurrent_task_operations(self, authenticated_user):
        """Test concurrent task operations"""
        import threading
        import queue
        
        client = authenticated_user["client"]
        results = queue.Queue()
        
        def create_and_complete_task(index):
            try:
                # Create task
                task_data = {
                    "title": f"Concurrent task {index}",
                    "priority": 3,
                    "difficulty": 2
                }
                
                create_response = client.post('/api/tasks', json=task_data)
                if create_response.status_code != 201:
                    results.put(f"Create failed: {create_response.status_code}")
                    return
                
                task_id = create_response.json()['data']['task']['id']
                
                # Complete task
                complete_response = client.post(f'/api/tasks/{task_id}/complete')
                if complete_response.status_code != 200:
                    results.put(f"Complete failed: {complete_response.status_code}")
                    return
                
                results.put("success")
                
            except Exception as e:
                results.put(f"Exception: {str(e)}")
        
        # Create 10 concurrent threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_and_complete_task, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == "success":
                success_count += 1
        
        # Most operations should succeed
        assert success_count >= 8  # Allow for some failures due to concurrency

