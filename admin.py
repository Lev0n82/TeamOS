from flask import Blueprint, jsonify, request
from datetime import datetime
from src.routes.auth import token_required
from src.config.ai_config import ai_config_manager, SubjectMatter, AIProvider, AIModelConfig, SubjectMatterConfig
from src.services.ai_service import ai_service
import asyncio

admin_bp = Blueprint('admin', __name__)

def run_async(coro):
    """Helper to run async functions in Flask routes"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

@admin_bp.route('/admin/ai/config', methods=['GET'])
@token_required
def get_ai_configuration(current_user):
    """Get complete AI configuration"""
    try:
        # Get all subject configurations
        configs = {}
        for subject in SubjectMatter:
            config = ai_config_manager.get_subject_config(subject)
            if config:
                configs[subject.value] = {
                    'subject': subject.value,
                    'primary_model': {
                        'provider': config.primary_model.provider.value,
                        'model_name': config.primary_model.model_name,
                        'max_tokens': config.primary_model.max_tokens,
                        'temperature': config.primary_model.temperature,
                        'timeout': config.primary_model.timeout
                    },
                    'fallback_model': {
                        'provider': config.fallback_model.provider.value if config.fallback_model else None,
                        'model_name': config.fallback_model.model_name if config.fallback_model else None
                    } if config.fallback_model else None,
                    'system_prompt': config.system_prompt,
                    'context_template': config.context_template,
                    'cache_responses': config.cache_responses,
                    'cache_duration_hours': config.cache_duration_hours
                }
        
        # Get service status
        service_status = ai_service.get_service_status()
        
        return jsonify({
            'success': True,
            'message': 'AI configuration retrieved',
            'data': {
                'subject_configurations': configs,
                'service_status': service_status,
                'available_providers': [provider.value for provider in AIProvider],
                'available_subjects': [subject.value for subject in SubjectMatter]
            },
            'errors': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get AI configuration',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@admin_bp.route('/admin/ai/config/<subject>', methods=['PUT'])
@token_required
def update_subject_configuration(current_user, subject):
    """Update configuration for a specific subject matter"""
    try:
        # Validate subject
        try:
            subject_enum = SubjectMatter(subject)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid subject matter',
                'data': None,
                'errors': [{'field': 'subject', 'message': f'Subject must be one of: {[s.value for s in SubjectMatter]}'}]
            }), 422
        
        data = request.get_json()
        
        # Get current configuration
        current_config = ai_config_manager.get_subject_config(subject_enum)
        if not current_config:
            return jsonify({
                'success': False,
                'message': 'Subject configuration not found',
                'data': None,
                'errors': []
            }), 404
        
        # Update primary model if provided
        if 'primary_model' in data:
            model_data = data['primary_model']
            try:
                provider = AIProvider(model_data.get('provider', current_config.primary_model.provider.value))
                current_config.primary_model = AIModelConfig(
                    provider=provider,
                    model_name=model_data.get('model_name', current_config.primary_model.model_name),
                    api_key=model_data.get('api_key', current_config.primary_model.api_key),
                    api_base=model_data.get('api_base', current_config.primary_model.api_base),
                    max_tokens=model_data.get('max_tokens', current_config.primary_model.max_tokens),
                    temperature=model_data.get('temperature', current_config.primary_model.temperature),
                    timeout=model_data.get('timeout', current_config.primary_model.timeout)
                )
            except ValueError as e:
                return jsonify({
                    'success': False,
                    'message': 'Invalid provider',
                    'data': None,
                    'errors': [{'field': 'provider', 'message': str(e)}]
                }), 422
        
        # Update other configuration fields
        if 'system_prompt' in data:
            current_config.system_prompt = data['system_prompt']
        if 'context_template' in data:
            current_config.context_template = data['context_template']
        if 'cache_responses' in data:
            current_config.cache_responses = data['cache_responses']
        if 'cache_duration_hours' in data:
            current_config.cache_duration_hours = data['cache_duration_hours']
        
        # Save updated configuration
        ai_config_manager.update_subject_config(subject_enum, current_config)
        
        return jsonify({
            'success': True,
            'message': f'Configuration updated for {subject}',
            'data': {
                'subject': subject,
                'updated_at': datetime.utcnow().isoformat()
            },
            'errors': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to update configuration',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@admin_bp.route('/admin/ai/test/<subject>', methods=['POST'])
@token_required
def test_subject_ai(current_user, subject):
    """Test AI generation for a specific subject"""
    try:
        # Validate subject
        try:
            subject_enum = SubjectMatter(subject)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid subject matter',
                'data': None,
                'errors': [{'field': 'subject', 'message': f'Subject must be one of: {[s.value for s in SubjectMatter]}'}]
            }), 422
        
        data = request.get_json() or {}
        test_context = data.get('context', {})
        force_ai = data.get('force_ai', True)
        
        # Generate test response
        ai_response = run_async(ai_service.generate_response(subject_enum, test_context, force_ai))
        
        return jsonify({
            'success': True,
            'message': f'AI test completed for {subject}',
            'data': {
                'subject': subject,
                'test_context': test_context,
                'ai_response': ai_response.to_dict(),
                'timestamp': datetime.utcnow().isoformat()
            },
            'errors': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'AI test failed',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@admin_bp.route('/admin/ai/connectivity', methods=['GET'])
@token_required
def check_ai_connectivity(current_user):
    """Check connectivity to all AI providers"""
    try:
        connectivity_results = run_async(ai_service.test_connectivity())
        
        return jsonify({
            'success': True,
            'message': 'Connectivity check completed',
            'data': {
                'connectivity_results': connectivity_results,
                'timestamp': datetime.utcnow().isoformat()
            },
            'errors': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Connectivity check failed',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@admin_bp.route('/admin/ai/sync', methods=['POST'])
@token_required
def sync_ai_fallbacks(current_user):
    """Sync fallback responses with AI models"""
    try:
        data = request.get_json() or {}
        force_sync = data.get('force', False)
        subjects = data.get('subjects', [])
        
        if subjects:
            # Sync specific subjects
            sync_results = {}
            for subject_name in subjects:
                try:
                    subject_enum = SubjectMatter(subject_name)
                    # This would need to be implemented in ai_service
                    sync_results[subject_name] = "synced"
                except ValueError:
                    sync_results[subject_name] = "invalid_subject"
        else:
            # Sync all subjects
            sync_results = run_async(ai_service.sync_with_ai(force=force_sync))
        
        return jsonify({
            'success': True,
            'message': 'AI sync completed',
            'data': {
                'sync_results': sync_results,
                'force_sync': force_sync,
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

@admin_bp.route('/admin/ai/cache', methods=['DELETE'])
@token_required
def clear_ai_cache(current_user):
    """Clear AI response cache"""
    try:
        ai_config_manager.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'AI cache cleared successfully',
            'data': {
                'timestamp': datetime.utcnow().isoformat()
            },
            'errors': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to clear cache',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@admin_bp.route('/admin/ai/fallbacks', methods=['GET'])
@token_required
def get_fallback_responses(current_user):
    """Get all fallback responses"""
    try:
        fallbacks = {}
        for subject, responses in ai_config_manager.fallback_responses.items():
            fallbacks[subject.value] = [
                {
                    'context_type': r.context_type,
                    'mood': r.mood,
                    'response_text': r.response_text,
                    'animation_type': r.animation_type,
                    'weight': r.weight,
                    'created_at': r.created_at.isoformat() if r.created_at else None
                }
                for r in responses
            ]
        
        return jsonify({
            'success': True,
            'message': 'Fallback responses retrieved',
            'data': {
                'fallback_responses': fallbacks,
                'total_responses': sum(len(responses) for responses in ai_config_manager.fallback_responses.values())
            },
            'errors': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get fallback responses',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

@admin_bp.route('/admin/ai/status', methods=['GET'])
@token_required
def get_ai_system_status(current_user):
    """Get comprehensive AI system status"""
    try:
        service_status = ai_service.get_service_status()
        connectivity_results = run_async(ai_service.test_connectivity())
        
        return jsonify({
            'success': True,
            'message': 'AI system status retrieved',
            'data': {
                'service_status': service_status,
                'connectivity_results': connectivity_results,
                'system_health': 'operational' if all(
                    result.get('status') in ['connected', 'always_available'] 
                    for result in connectivity_results.values()
                ) else 'degraded',
                'timestamp': datetime.utcnow().isoformat()
            },
            'errors': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get system status',
            'data': None,
            'errors': [{'message': str(e)}]
        }), 500

