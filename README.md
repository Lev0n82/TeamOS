# Team OS: Birthday Cake Planner 🎂

A celebration-themed task management and productivity platform featuring a delightful Birthday Cake AI assistant that makes productivity sweet and rewarding.

## Overview

Team OS: Birthday Cake Planner transforms the mundane task of productivity management into a joyful celebration. With our charming Birthday Cake AI assistant, every completed task becomes a reason to celebrate, every milestone becomes a party, and every achievement unlocks sweet rewards.

## Features

### 🎂 Birthday Cake AI Assistant
- **Delightful Personality**: A cheerful, encouraging AI that celebrates your successes
- **Dynamic Responses**: Context-aware reactions that adapt to your productivity patterns
- **Sweetness Levels**: Customizable personality sweetness from gentle encouragement to enthusiastic celebration
- **Mood System**: The cake's mood changes based on your productivity and achievements

### 🎉 Celebration-Themed Gamification
- **Celebration Points**: Earn points for completing tasks and achieving goals
- **Achievement System**: Unlock special badges and rewards for productivity milestones
- **Streak Tracking**: Build and maintain productivity streaks with daily celebrations
- **Level Progression**: Advance through personality levels to unlock new cake features

### 📋 Advanced Task Management
- **Smart Task Creation**: AI-powered suggestions for task categorization and priority
- **Project Organization**: Hierarchical project structure with team collaboration
- **Dependency Management**: Link tasks with dependencies for complex workflows
- **Progress Tracking**: Visual progress indicators and completion analytics

### 👥 Team Collaboration
- **Shared Projects**: Collaborate on projects with team members
- **Role-Based Permissions**: Flexible permission system for team management
- **Real-time Updates**: Live synchronization across all team members
- **Team Analytics**: Comprehensive insights into team productivity

### 📊 Analytics & Insights
- **Productivity Metrics**: Detailed analytics on completion rates and patterns
- **Habit Analysis**: AI-powered insights into productive and counterproductive habits
- **Goal Tracking**: Monitor progress toward long-term objectives
- **Custom Reports**: Generate reports for personal or team review

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **API**: RESTful API with comprehensive endpoints
- **Real-time**: WebSocket support for live updates

### Frontend
- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS with custom birthday cake theme
- **State Management**: Redux Toolkit with RTK Query
- **Animation**: Framer Motion for delightful interactions
- **PWA**: Progressive Web App capabilities

### Infrastructure
- **CORS**: Cross-origin resource sharing enabled
- **Security**: Password hashing, secure JWT implementation
- **Scalability**: Designed for horizontal scaling
- **Deployment**: Docker-ready with production configurations

## Project Structure

```
birthday-cake-planner/
├── cake-backend/                 # Flask backend application
│   ├── src/
│   │   ├── models/              # Database models
│   │   │   ├── user.py          # User model with cake personality
│   │   │   ├── task.py          # Task model with celebration points
│   │   │   ├── project.py       # Project and collaboration models
│   │   │   ├── gamification.py  # Achievement and cake personality
│   │   │   └── team.py          # Team collaboration models
│   │   ├── routes/              # API route handlers
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── user.py          # User management endpoints
│   │   │   └── task.py          # Task management endpoints
│   │   ├── database/            # Database files
│   │   └── main.py              # Application entry point
│   ├── venv/                    # Python virtual environment
│   └── requirements.txt         # Python dependencies
├── cake-frontend/               # React frontend application
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utility functions
│   │   └── assets/              # Static assets
│   ├── public/                  # Public assets
│   └── package.json             # Node.js dependencies
├── API_SPECIFICATIONS.md        # Comprehensive API documentation
├── README.md                    # Project documentation
└── todo.md                      # Development progress tracking
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- npm or pnpm

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd birthday-cake-planner/cake-backend
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install flask flask-sqlalchemy flask-cors PyJWT python-dotenv
   ```

4. Start the development server:
   ```bash
   python src/main.py
   ```

The backend will be available at `http://localhost:5000`

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd birthday-cake-planner/cake-frontend
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

3. Start the development server:
   ```bash
   pnpm run dev
   ```

The frontend will be available at `http://localhost:3000`

## API Documentation

Comprehensive API documentation is available in [API_SPECIFICATIONS.md](./API_SPECIFICATIONS.md).

### Key Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `GET /api/tasks` - Get user tasks
- `POST /api/tasks` - Create new task
- `POST /api/tasks/{id}/complete` - Complete task and earn celebration points
- `GET /api/cake/personality` - Get Birthday Cake AI state
- `POST /api/cake/interact` - Interact with Birthday Cake AI

## Database Schema

### Core Models
- **User**: User accounts with cake personality settings
- **Task**: Tasks with celebration point rewards
- **Project**: Project organization and team collaboration
- **CakePersonality**: Birthday Cake AI responses and moods
- **Achievement**: Gamification achievements and rewards
- **Team**: Team collaboration and management

### Key Features
- **Celebration Points**: Reward system for task completion
- **Cake Personality Levels**: Progressive AI personality unlocks
- **Streak Tracking**: Daily productivity streak monitoring
- **Team Collaboration**: Shared projects and permissions

## Development Roadmap

### Phase 1: Project Rebranding and Architecture ✅
- [x] Complete rebranding from CARROT to Birthday Cake theme
- [x] Database schema design and implementation
- [x] API specification documentation
- [x] Backend architecture setup

### Phase 2: Core Backend API Development 🚧
- [x] Authentication system with JWT
- [x] Task management CRUD operations
- [ ] Project management endpoints
- [ ] User profile management
- [ ] Comprehensive API testing

### Phase 3: Frontend React Application
- [ ] React app setup with Teams OS interface
- [ ] Authentication UI components
- [ ] Task management interface
- [ ] Birthday Cake AI personality display
- [ ] Responsive design implementation

### Phase 4: Birthday Cake AI Personality System
- [ ] AI personality engine implementation
- [ ] Dynamic response generation
- [ ] Mood system based on productivity
- [ ] Celebration animations and interactions

### Phase 5: Gamification and Celebrations
- [ ] Achievement system implementation
- [ ] Celebration points and rewards
- [ ] Streak tracking and bonuses
- [ ] Leaderboards and social features

### Phase 6: Team Collaboration
- [ ] Team creation and management
- [ ] Real-time collaboration features
- [ ] Permission management system
- [ ] Team analytics dashboard

### Phase 7: Analytics and Insights
- [ ] Productivity analytics engine
- [ ] Habit analysis and recommendations
- [ ] Custom reporting system
- [ ] Data visualization components

### Phase 8: Testing and Deployment
- [ ] Comprehensive testing suite
- [ ] Performance optimization
- [ ] Production deployment
- [ ] Monitoring and error tracking

## Contributing

This project follows a structured development approach with clear phases and milestones. Each phase builds upon the previous one to create a comprehensive productivity platform.

### Development Guidelines
- Follow the existing code structure and naming conventions
- Maintain the birthday cake theme throughout all features
- Ensure all API endpoints follow the established response format
- Write comprehensive tests for new functionality
- Update documentation for any API changes

## License

This project is part of Teams OS and follows the established licensing terms.

## Support

For questions, issues, or feature requests, please refer to the project documentation or contact the development team.

---

*Making productivity sweet, one task at a time! 🎂✨*

