#!/usr/bin/env python3
"""
Seed script for Birthday Cake AI personality responses
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.models.gamification import CakePersonality, Achievement
from src.main import app

def seed_cake_personality():
    """Seed the database with Birthday Cake AI personality responses"""
    
    cake_responses = [
        # Task Created Responses
        {
            'category': 'task_created',
            'mood': 'cheerful',
            'attitude_level': 3,
            'text_response': "🎂 Wonderful! A new task to celebrate! Let's make this one extra sweet! ✨",
            'animation_type': 'bounce',
            'min_personality_level': 1,
            'max_personality_level': 10
        },
        {
            'category': 'task_created',
            'mood': 'encouraging',
            'attitude_level': 3,
            'text_response': "🎂 Every great celebration starts with a single task! You're on your way! 🚀",
            'animation_type': 'glow',
            'min_personality_level': 1,
            'max_personality_level': 10
        },
        {
            'category': 'task_created',
            'mood': 'excited',
            'attitude_level': 5,
            'text_response': "🎂 OH MY FROSTING! Another task! This is going to be AMAZING! 🎊",
            'animation_type': 'celebration_bounce',
            'min_personality_level': 5,
            'max_personality_level': 10
        },
        
        # Task Completed Responses
        {
            'category': 'task_completed',
            'mood': 'cheerful',
            'attitude_level': 3,
            'text_response': "🎂 Sweet success! You've earned another slice of productivity! Time to celebrate! 🍰",
            'animation_type': 'bounce',
            'min_personality_level': 1,
            'max_personality_level': 10
        },
        {
            'category': 'task_completed',
            'mood': 'encouraging',
            'attitude_level': 3,
            'text_response': "🎂 Look at you go! Every completed task makes the celebration sweeter! 💪",
            'animation_type': 'glow',
            'min_personality_level': 1,
            'max_personality_level': 10
        },
        {
            'category': 'task_completed',
            'mood': 'excited',
            'attitude_level': 5,
            'text_response': "🎂 INCREDIBLE! AMAZING! SPECTACULAR! You absolutely CRUSHED that task! 🎊",
            'animation_type': 'confetti_explosion',
            'min_personality_level': 5,
            'max_personality_level': 10
        },
        
        # Task Overdue Responses
        {
            'category': 'task_overdue',
            'mood': 'gentle',
            'attitude_level': 2,
            'text_response': "🎂 Hey there, sweet friend! That task is waiting for some love. No worries though! 💕",
            'animation_type': 'gentle_sway',
            'min_personality_level': 1,
            'max_personality_level': 10
        },
        {
            'category': 'task_overdue',
            'mood': 'motivating',
            'attitude_level': 4,
            'text_response': "🎂 Time to turn that overdue task into a sweet victory! You've got this! 💪",
            'animation_type': 'pulse',
            'min_personality_level': 3,
            'max_personality_level': 10
        },
        
        # Streak Milestone Responses
        {
            'category': 'streak_milestone',
            'mood': 'celebratory',
            'attitude_level': 5,
            'text_response': "🎂 STREAK MILESTONE! You're on fire! This deserves the biggest cake celebration! 🔥",
            'animation_type': 'confetti_explosion',
            'min_personality_level': 1,
            'max_personality_level': 10
        },
        
        # Level Up Responses
        {
            'category': 'level_up',
            'mood': 'excited',
            'attitude_level': 5,
            'text_response': "🎂 LEVEL UP! You've unlocked new layers of sweetness! Welcome to the next tier! 🎊",
            'animation_type': 'celebration_bounce',
            'min_personality_level': 1,
            'max_personality_level': 10
        },
        
        # Encouragement Responses
        {
            'category': 'encouragement',
            'mood': 'supportive',
            'attitude_level': 3,
            'text_response': "🎂 Remember, every expert baker started with their first cupcake! You're doing great! 💪",
            'animation_type': 'warm_glow',
            'min_personality_level': 1,
            'max_personality_level': 10
        },
        {
            'category': 'encouragement',
            'mood': 'supportive',
            'attitude_level': 3,
            'text_response': "🍰 Productivity is like baking - it takes time, patience, and lots of love! 💕",
            'animation_type': 'warm_glow',
            'min_personality_level': 1,
            'max_personality_level': 10
        }
    ]
    
    print("Seeding Birthday Cake AI personality responses...")
    
    for response_data in cake_responses:
        # Check if response already exists
        existing = CakePersonality.query.filter_by(
            category=response_data['category'],
            mood=response_data['mood'],
            text_response=response_data['text_response']
        ).first()
        
        if not existing:
            response = CakePersonality(**response_data)
            db.session.add(response)
    
    db.session.commit()
    print(f"Added {len(cake_responses)} Birthday Cake AI personality responses!")

def seed_achievements():
    """Seed the database with celebration-themed achievements"""
    
    achievements = [
        {
            'name': 'First Slice',
            'description': 'Complete your very first task! Every celebration starts with a single slice! 🍰',
            'icon': 'cake-slice',
            'category': 'milestone',
            'requirement_type': 'tasks_completed',
            'requirement_value': 1,
            'celebration_points_reward': 50,
            'rarity': 'common'
        },
        {
            'name': 'Sweet Streak',
            'description': 'Maintain a 3-day productivity streak! You\'re on a roll! 🔥',
            'icon': 'fire',
            'category': 'streak',
            'requirement_type': 'streak_days',
            'requirement_value': 3,
            'celebration_points_reward': 100,
            'rarity': 'common'
        },
        {
            'name': 'Cake Master',
            'description': 'Complete 50 tasks! You\'re becoming a true productivity baker! 👨‍🍳',
            'icon': 'chef-hat',
            'category': 'milestone',
            'requirement_type': 'tasks_completed',
            'requirement_value': 50,
            'celebration_points_reward': 500,
            'rarity': 'rare'
        },
        {
            'name': 'Birthday Celebration',
            'description': 'Maintain a 7-day streak! Time for a proper birthday party! 🎉',
            'icon': 'party',
            'category': 'streak',
            'requirement_type': 'streak_days',
            'requirement_value': 7,
            'celebration_points_reward': 300,
            'rarity': 'rare'
        },
        {
            'name': 'Frosting Legend',
            'description': 'Earn 5000 celebration points! You\'re a legendary productivity baker! 🏆',
            'icon': 'trophy',
            'category': 'points',
            'requirement_type': 'celebration_points_earned',
            'requirement_value': 5000,
            'celebration_points_reward': 1000,
            'rarity': 'epic'
        },
        {
            'name': 'Perfect Week',
            'description': 'Complete at least one task every day for a week! Consistency is key! ⭐',
            'icon': 'star',
            'category': 'consistency',
            'requirement_type': 'perfect_week',
            'requirement_value': 1,
            'celebration_points_reward': 400,
            'rarity': 'rare'
        },
        {
            'name': 'Speed Demon',
            'description': 'Complete 10 tasks in a single day! You\'re on fire! ⚡',
            'icon': 'lightning',
            'category': 'speed',
            'requirement_type': 'daily_tasks',
            'requirement_value': 10,
            'celebration_points_reward': 200,
            'rarity': 'rare'
        },
        {
            'name': 'Team Player',
            'description': 'Complete your first team project! Collaboration makes everything sweeter! 🤝',
            'icon': 'handshake',
            'category': 'collaboration',
            'requirement_type': 'team_projects_completed',
            'requirement_value': 1,
            'celebration_points_reward': 150,
            'rarity': 'common'
        }
    ]
    
    print("Seeding celebration achievements...")
    
    for achievement_data in achievements:
        # Check if achievement already exists
        existing = Achievement.query.filter_by(name=achievement_data['name']).first()
        
        if not existing:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)
    
    db.session.commit()
    print(f"Added {len(achievements)} celebration achievements!")

def main():
    """Main seeding function"""
    with app.app_context():
        print("🎂 Starting Birthday Cake Planner database seeding...")
        
        # Create tables if they don't exist
        db.create_all()
        
        # Seed data
        seed_cake_personality()
        seed_achievements()
        
        print("🎉 Database seeding completed successfully!")
        print("Your Birthday Cake AI is now ready to celebrate with users!")

if __name__ == '__main__':
    main()

