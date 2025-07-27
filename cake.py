from flask import Blueprint, jsonify, request
from datetime import datetime
import random
import asyncio
from src.models.user import db
from src.models.gamification import CakePersonality, UserInteraction
from src.routes.auth import token_required
from src.services.ai_service import ai_service
from src.config.ai_config import SubjectMatter, ai_config_manager

cake_bp = Blueprint('cake', __name__)

def run_async(coro):
    """Helper to run async functions in Flask routes"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

def get_cake_response_ai(category, user_mood='cheerful', user_level=1, context=None):
    """Get Birthday Cake AI response using the new AI service"""
    context = context or {}
    
    # Map category to SubjectMatter
    subject_mapping = {
        'task_created': SubjectMatter.TASK_CREATION,
        'task_completed': SubjectMatter.TASK_COMPLETION,
        'task_overdue': SubjectMatter.MOTIVATION,
        'streak_milestone': SubjectMatter.CELEBRATION,
        'level_up': SubjectMatter.CELEBRATION,
        'encouragement': SubjectMatter.ENCOURAGEMENT,
        'motivation': SubjectMatter.MOTIVATION,
        'productivity_tips': SubjectMatter.PRODUCTIVITY_TIPS
    }
    
    subject = subject_mapping.get(category, SubjectMatter.ENCOURAGEMENT)
    
    # Enhance context with user information
    enhanced_context = {
        **context,
        'user_mood': user_mood,
        'user_level': user_level,
        'category': category,
        'context_type': context.get('context_type', 'general')
    }
    
    try:
        # Use AI service to generate response
        ai_response = run_async(ai_service.generate_response(subject, enhanced_context))
        
        return {
            'text': ai_response.text,
            'mood': ai_response.mood,
            'animation': ai_response.animation_type,
            'category': category,
            'source': ai_response.source,
            'metadata': ai_response.metadata
        }
    except Exception as e:
        # Fallback to static responses if AI service fails
        return get_cake_response_static(category, user_mood, user_level)

def get_cake_response_static(category, user_mood='cheerful', user_level=1):
    """Fallback to static responses"""
    CAKE_RESPONSES = {
        'task_created': {
            'cheerful': [
                "🎂 Wonderful! A new task to celebrate! Let's make this one extra sweet! ✨",
                "🍰 Oh my! Another delicious challenge awaits! I'm so excited to see you succeed! 🎉"
            ]
        },
        'task_completed': {
            'cheerful': [
                "🎂 Sweet success! You've earned another slice of productivity! Time to celebrate! 🍰",
                "🎉 Magnificent! That task is now perfectly baked and ready to enjoy! Well done! ✨"
            ]
        },
        'encouragement': {
            'supportive': [
                "🎂 Remember, every expert baker started with their first cupcake! You're doing great! 💪",
                "🍰 Productivity is like baking - it takes time, patience, and lots of love! 💕"
            ]
        }
    }
    
    # Simple fallback logic
    category_responses = CAKE_RESPONSES.get(category, CAKE_RESPONSES['encouragement'])
    mood_responses = list(category_responses.values())[0]
    response_text = random.choice(mood_responses)
    
    return {
        'text': response_text,
        'mood': user_mood,
        'animation': 'bounce',
        'category': category,
        'source': 'static_fallback'
    }

def get_animation_for_mood(mood):
    """Get animation type based on mood"""
    animations = {
        'cheerful': 'bounce',
        'encouraging': 'glow',
        'excited': 'celebration_bounce',
        'celebratory': 'confetti_explosion',
        'gentle': 'gentle_sway',
        'motivating': 'pulse',
        'supportive': 'warm_glow'
    }
    return animations.get(mood, 'bounce')

@cake_bp.route('/cake/personality', methods=['GET'])
@token_required
def get_cake_personality(current_user):
    """Get Birthday Cake AI's current personality state"""
    try:
        # Calculate dynamic mood based on recent activity
        recent_completions = current_user.current_streak
        personality_level = current_user.cake_personality_level
        
        # Determine current mood
        if recent_completions >= 7:
            current_mood = 'excited'
        elif recent_completions >= 3:
            current_mood = 'cheerful'
        elif recent_completions >= 1:
            current_mood = 'encouraging'
        else:
            current_mood = 'gentle'
        
        # Update user's cake mood if it's different
        if current_user.cake_mood != current_mood:
            current_user.cake_mood = current_mood
            db.session.commit()
        
        # Get greeting using AI service
        greeting_context = {
            'context_type': 'greeting',
            'streak': recent_completions,
            'level': personality_level
        }
        greeting = get_cake_response_ai('encouragement', current_mood, personality_level, greeting_context)
        
        personality_state = {
            'mood': current_mood,
            'sweetness_level': current_user.cake_sweetness_level,
            'personality_level': personality_level,
            'current_streak': recent_completions,
            'total_celebration_points': current_user.total_celebration_points,
            'next_level_points': (personality_level * 1000) - current_user.total_celebration_points,
            'greeting': greeting
        }
        
        return jsonify({
            'success': True,
            'message': 'Birthday Cake AI personality retrieved',
            'data': {
                'personality': personality_state
            },
            'errors': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get cake personality',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@cake_bp.route('/cake/interact', methods=['POST'])
@token_required
def interact_with_cake(current_user):
    """Record user interaction with Birthday Cake AI and get response"""
    try:
        data = request.get_json()
        
        interaction_type = data.get('interaction_type')
        context_data = data.get('context_data', {})
        
        if not interaction_type:
            return jsonify({
                'success': False,
                'message': 'Interaction type is required',
                'data': None,
                'errors': [{'field': 'interaction_type', 'message': 'Interaction type is required'}]
            }), 422
        
        # Get appropriate response using AI service
        cake_response = get_cake_response_ai(
            interaction_type, 
            current_user.cake_mood, 
            current_user.cake_personality_level,
            context_data
        )
        
        # Calculate rewards based on interaction type
        rewards = calculate_interaction_rewards(interaction_type, context_data, current_user)
        
        # Apply rewards
        if rewards['celebration_points'] > 0:
            level_up = current_user.add_celebration_points(rewards['celebration_points'])
            rewards['level_up'] = level_up
            
            # Special response for level up
            if level_up:
                cake_response = get_cake_response_ai('level_up', 'excited', current_user.cake_personality_level)
        
        # Record the interaction
        interaction = UserInteraction(
            user_id=current_user.id,
            interaction_type=interaction_type,
            context_data=context_data,
            user_reaction=data.get('user_reaction')
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Interaction recorded successfully',
            'data': {
                'response': cake_response,
                'rewards': rewards,
                'personality_update': {
                    'mood': current_user.cake_mood,
                    'level': current_user.cake_personality_level,
                    'total_points': current_user.total_celebration_points
                }
            },
            'errors': []
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to process interaction',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

def calculate_interaction_rewards(interaction_type, context_data, user):
    """Calculate rewards for different interaction types"""
    rewards = {
        'celebration_points': 0,
        'achievements_unlocked': [],
        'level_up': False
    }
    
    if interaction_type == 'task_completed':
        rewards['celebration_points'] = 10
        difficulty = context_data.get('difficulty', 1)
        rewards['celebration_points'] += (difficulty - 1) * 5
        
        if context_data.get('completed_on_time', True):
            rewards['celebration_points'] += 5
        
        if user.current_streak >= 7:
            rewards['celebration_points'] += 20
        elif user.current_streak >= 3:
            rewards['celebration_points'] += 10
    
    elif interaction_type == 'streak_milestone':
        streak_length = context_data.get('streak_length', 0)
        rewards['celebration_points'] = streak_length * 5
    
    elif interaction_type == 'project_completed':
        rewards['celebration_points'] = 50
    
    return rewards

@cake_bp.route('/cake/config', methods=['GET'])
@token_required
def get_ai_config(current_user):
    """Get AI configuration status"""
    try:
        status = ai_service.get_service_status()
        return jsonify({
            'success': True,
            'message': 'AI configuration retrieved',
            'data': status,
            'errors': []
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get AI configuration',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@cake_bp.route('/cake/config/test', methods=['POST'])
@token_required
def test_ai_connectivity(current_user):
    """Test AI provider connectivity"""
    try:
        results = run_async(ai_service.test_connectivity())
        return jsonify({
            'success': True,
            'message': 'Connectivity test completed',
            'data': {
                'connectivity_results': results,
                'timestamp': datetime.utcnow().isoformat()
            },
            'errors': []
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Connectivity test failed',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@cake_bp.route('/cake/config/sync', methods=['POST'])
@token_required
def sync_ai_responses(current_user):
    """Sync fallback responses with AI models"""
    try:
        data = request.get_json() or {}
        force_sync = data.get('force', False)
        
        results = run_async(ai_service.sync_with_ai(force=force_sync))
        
        return jsonify({
            'success': True,
            'message': 'AI sync completed',
            'data': {
                'sync_results': results,
                'timestamp': datetime.utcnow().isoformat()
            },
            'errors': []
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'AI sync failed',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@cake_bp.route('/cake/mood', methods=['PUT'])
@token_required
def update_cake_mood(current_user):
    """Update Birthday Cake AI mood preferences"""
    try:
        data = request.get_json()
        
        new_mood = data.get('mood')
        sweetness_level = data.get('sweetness_level')
        
        valid_moods = ['cheerful', 'encouraging', 'excited', 'gentle']
        
        if new_mood and new_mood not in valid_moods:
            return jsonify({
                'success': False,
                'message': 'Invalid mood',
                'data': None,
                'errors': [{'field': 'mood', 'message': f'Mood must be one of: {", ".join(valid_moods)}'}]
            }), 422
        
        if sweetness_level and (sweetness_level < 1 or sweetness_level > 5):
            return jsonify({
                'success': False,
                'message': 'Invalid sweetness level',
                'data': None,
                'errors': [{'field': 'sweetness_level', 'message': 'Sweetness level must be between 1 and 5'}]
            }), 422
        
        # Update user preferences
        if new_mood:
            current_user.cake_mood = new_mood
        if sweetness_level:
            current_user.cake_sweetness_level = sweetness_level
        
        db.session.commit()
        
        # Get updated personality response using AI service
        updated_response = get_cake_response_ai('encouragement', current_user.cake_mood, current_user.cake_personality_level)
        
        return jsonify({
            'success': True,
            'message': 'Cake personality updated successfully',
            'data': {
                'updated_personality': {
                    'mood': current_user.cake_mood,
                    'sweetness_level': current_user.cake_sweetness_level,
                    'response': updated_response
                }
            },
            'errors': []
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update cake personality',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@cake_bp.route('/cake/celebrate', methods=['POST'])
@token_required
def trigger_celebration(current_user):
    """Trigger a special celebration response"""
    try:
        data = request.get_json()
        celebration_type = data.get('type', 'general')
        
        # Map celebration types to categories
        celebration_mapping = {
            'general': 'encouragement',
            'milestone': 'streak_milestone',
            'achievement': 'level_up'
        }
        
        category = celebration_mapping.get(celebration_type, 'encouragement')
        context = {
            'context_type': 'celebration',
            'celebration_type': celebration_type
        }
        
        response = get_cake_response_ai(category, 'excited', current_user.cake_personality_level, context)
        
        return jsonify({
            'success': True,
            'message': 'Celebration triggered',
            'data': {
                'celebration': response,
                'confetti': True,
                'special_animation': 'party_mode'
            },
            'errors': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to trigger celebration',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

