# CAKE Planner Web App - API Specifications

## Overview

This document outlines the REST API endpoints for the CARROT Planner Web App. The API follows RESTful conventions and returns JSON responses.

**Base URL:** `http://localhost:5000/api`

**Authentication:** JWT tokens in Authorization header: `Bearer <token>`

## Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": {},
  "message": "Success message",
  "errors": []
}
```

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "carrot_personality_level": 1,
      "total_xp": 0
    },
    "token": "jwt_token_here"
  }
}
```

### POST /auth/login
Authenticate user and return JWT token.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

### POST /auth/logout
Logout user (invalidate token).

### GET /auth/me
Get current user profile information.

## User Management

### GET /users/profile
Get current user's detailed profile.

### PUT /users/profile
Update user profile information.

**Request Body:**
```json
{
  "username": "string",
  "timezone": "string",
  "carrot_attitude_level": 3,
  "notification_preferences": {},
  "theme_preferences": {}
}
```

### GET /users/stats
Get user's productivity statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_xp": 1250,
    "current_streak": 7,
    "longest_streak": 15,
    "tasks_completed": 45,
    "projects_completed": 3,
    "achievements_unlocked": 8
  }
}
```

## Task Management

### GET /tasks
Get user's tasks with filtering and pagination.

**Query Parameters:**
- `status`: pending, in_progress, completed, cancelled
- `priority`: low, medium, high, urgent
- `project_id`: Filter by project
- `due_date`: Filter by due date
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

### POST /tasks
Create a new task.

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "due_date": "2024-01-15T10:00:00Z",
  "priority": "medium",
  "category": "work",
  "estimated_duration": 60,
  "difficulty": 3,
  "project_id": 1
}
```

### GET /tasks/{id}
Get specific task details.

### PUT /tasks/{id}
Update task information.

### DELETE /tasks/{id}
Delete a task.

### POST /tasks/{id}/complete
Mark task as completed.

### POST /tasks/{id}/dependencies
Add task dependency.

**Request Body:**
```json
{
  "depends_on_id": 5
}
```

## Project Management

### GET /projects
Get user's projects.

### POST /projects
Create a new project.

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-03-31T23:59:59Z",
  "priority": "high",
  "color": "#3B82F6",
  "is_team_project": false
}
```

### GET /projects/{id}
Get specific project details.

### PUT /projects/{id}
Update project information.

### DELETE /projects/{id}
Delete a project.

### GET /projects/{id}/tasks
Get all tasks in a project.

### POST /projects/{id}/members
Add member to project.

**Request Body:**
```json
{
  "user_id": 2,
  "role": "member"
}
```

## Team Collaboration

### GET /teams
Get user's teams.

### POST /teams
Create a new team.

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "is_public": false,
  "max_members": 50
}
```

### GET /teams/{id}
Get team details.

### PUT /teams/{id}
Update team information.

### DELETE /teams/{id}
Delete a team.

### POST /teams/{id}/invite
Invite user to team.

**Request Body:**
```json
{
  "email": "user@example.com",
  "role": "member",
  "message": "Join our team!"
}
```

### POST /teams/join/{invite_code}
Join team using invite code.

### GET /teams/{id}/members
Get team members.

### PUT /teams/{id}/members/{user_id}
Update team member role/permissions.

### DELETE /teams/{id}/members/{user_id}
Remove team member.

## Gamification

### GET /achievements
Get all available achievements.

### GET /achievements/user
Get user's unlocked achievements.

### GET /carrot/personality
Get CARROT's current personality state.

### POST /carrot/interact
Record user interaction with CARROT.

**Request Body:**
```json
{
  "interaction_type": "task_completed",
  "context_data": {
    "task_id": 1,
    "completion_time": 45
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": {
      "text": "Well, well! Look who actually finished something!",
      "animation": "bounce",
      "mood": "sarcastic"
    },
    "rewards": {
      "xp_gained": 15,
      "achievements_unlocked": []
    }
  }
}
```

### GET /streaks
Get user's productivity streaks.

### GET /leaderboard
Get productivity leaderboard (if user opts in).

## Analytics

### GET /analytics/productivity
Get productivity analytics.

**Query Parameters:**
- `period`: day, week, month, year
- `start_date`: Start date for analysis
- `end_date`: End date for analysis

**Response:**
```json
{
  "success": true,
  "data": {
    "completion_rate": 85.5,
    "average_task_duration": 42,
    "productivity_trend": "increasing",
    "peak_hours": [9, 10, 14, 15],
    "category_breakdown": {
      "work": 60,
      "personal": 25,
      "learning": 15
    }
  }
}
```

### GET /analytics/habits
Get habit analysis and recommendations.

### GET /analytics/team/{team_id}
Get team analytics (for team members).

## Real-time Features

### WebSocket: /ws/notifications
Real-time notifications for:
- Task reminders
- Team updates
- Achievement unlocks
- CARROT personality responses

**Message Format:**
```json
{
  "type": "notification",
  "category": "task_reminder",
  "data": {
    "task_id": 1,
    "title": "Complete project proposal",
    "due_in_minutes": 30
  },
  "timestamp": "2024-01-15T09:30:00Z"
}
```

## Error Handling

### Error Response Format
```json
{
  "success": false,
  "data": null,
  "message": "Error description",
  "errors": [
    {
      "field": "email",
      "message": "Email is required"
    }
  ]
}
```

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting

- Authentication endpoints: 5 requests per minute
- General API endpoints: 100 requests per minute
- WebSocket connections: 1 per user

## Data Validation

### Task Validation
- Title: Required, max 200 characters
- Priority: Must be one of: low, medium, high, urgent
- Difficulty: Integer between 1-5
- Estimated duration: Positive integer (minutes)

### Project Validation
- Name: Required, max 200 characters
- Color: Valid hex color code
- Dates: End date must be after start date

### User Validation
- Email: Valid email format, unique
- Username: 3-50 characters, alphanumeric + underscore
- Password: Minimum 8 characters

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

**Response Headers:**
- `X-Total-Count`: Total number of items
- `X-Page-Count`: Total number of pages
- `X-Current-Page`: Current page number

## Filtering and Sorting

**Common Query Parameters:**
- `sort`: Field to sort by
- `order`: asc or desc
- `search`: Text search in relevant fields

**Example:**
```
GET /api/tasks?sort=due_date&order=asc&status=pending&search=project
```

This API specification provides a comprehensive foundation for the CARROT Planner Web App, supporting all the features outlined in the application specifications including personality-driven interactions, gamification, team collaboration, and advanced analytics.

