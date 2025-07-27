"""
AI Configuration Module for Birthday Cake Planner
Handles AI model selection, prompting, and fallback mechanisms
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    FALLBACK = "fallback"

class SubjectMatter(Enum):
    """Different subject matters for AI interactions"""
    TASK_CREATION = "task_creation"
    TASK_COMPLETION = "task_completion"
    MOTIVATION = "motivation"
    CELEBRATION = "celebration"
    ENCOURAGEMENT = "encouragement"
    PRODUCTIVITY_TIPS = "productivity_tips"
    GOAL_SETTING = "goal_setting"
    TIME_MANAGEMENT = "time_management"
    HABIT_FORMATION = "habit_formation"
    STRESS_MANAGEMENT = "stress_management"
    TEAM_COLLABORATION = "team_collaboration"
    PROJECT_PLANNING = "project_planning"

@dataclass
class AIModelConfig:
    """Configuration for a specific AI model"""
    provider: AIProvider
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    timeout: int = 10
    retry_attempts: int = 3
    retry_delay: float = 1.0

@dataclass
class SubjectMatterConfig:
    """Configuration for subject matter specific AI interactions"""
    subject: SubjectMatter
    primary_model: AIModelConfig
    fallback_model: Optional[AIModelConfig] = None
    system_prompt: str = ""
    context_template: str = ""
    response_format: str = "text"
    max_context_length: int = 1000
    cache_responses: bool = True
    cache_duration_hours: int = 24

@dataclass
class FallbackResponse:
    """Predefined fallback response"""
    subject: SubjectMatter
    context_type: str
    mood: str
    response_text: str
    animation_type: str
    weight: int = 1  # For weighted random selection
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class AIConfigurationManager:
    """Manages AI configurations and fallback mechanisms"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.join(
            os.path.dirname(__file__), 'ai_config.json'
        )
        self.subject_configs: Dict[SubjectMatter, SubjectMatterConfig] = {}
        self.fallback_responses: Dict[SubjectMatter, List[FallbackResponse]] = {}
        self.connectivity_status: Dict[AIProvider, bool] = {}
        self.last_sync_attempt: Dict[AIProvider, datetime] = {}
        self.response_cache: Dict[str, Any] = {}
        
        self._load_configuration()
        self._load_fallback_responses()
        self._initialize_connectivity_status()
    
    def _load_configuration(self):
        """Load AI configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self._parse_configuration(config_data)
            else:
                self._create_default_configuration()
        except Exception as e:
            logger.error(f"Failed to load AI configuration: {e}")
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default AI configuration"""
        logger.info("Creating default AI configuration...")
        
        # Default OpenAI model configuration
        default_openai = AIModelConfig(
            provider=AIProvider.OPENAI,
            model_name="gpt-3.5-turbo",
            api_key=os.getenv('OPENAI_API_KEY'),
            api_base=os.getenv('OPENAI_API_BASE'),
            max_tokens=150,
            temperature=0.8,
            timeout=10
        )
        
        # Default fallback configuration
        fallback_config = AIModelConfig(
            provider=AIProvider.FALLBACK,
            model_name="static_responses",
            timeout=1
        )
        
        # Configure each subject matter
        subject_prompts = {
            SubjectMatter.TASK_CREATION: {
                "system_prompt": """You are a cheerful Birthday Cake AI assistant helping users create tasks. 
                Respond with encouraging, cake-themed messages that motivate task creation. 
                Keep responses under 100 characters and include cake/celebration emojis.""",
                "context_template": "User is creating a task: {task_title} with priority {priority} and difficulty {difficulty}"
            },
            SubjectMatter.TASK_COMPLETION: {
                "system_prompt": """You are an enthusiastic Birthday Cake AI celebrating task completion. 
                Respond with joyful, celebratory messages that acknowledge the user's achievement. 
                Include celebration emojis and cake-themed language.""",
                "context_template": "User completed task: {task_title} in {duration} minutes, difficulty {difficulty}, streak: {streak}"
            },
            SubjectMatter.MOTIVATION: {
                "system_prompt": """You are a supportive Birthday Cake AI providing motivation. 
                Give encouraging, uplifting messages that inspire productivity. 
                Use sweet, cake-themed metaphors and positive language.""",
                "context_template": "User needs motivation. Current streak: {streak}, completed tasks: {completed_tasks}, mood: {mood}"
            },
            SubjectMatter.CELEBRATION: {
                "system_prompt": """You are an excited Birthday Cake AI leading celebrations. 
                Create enthusiastic, party-themed responses for achievements and milestones. 
                Use lots of celebration emojis and festive language.""",
                "context_template": "Celebrating: {achievement_type} - {achievement_details}"
            },
            SubjectMatter.ENCOURAGEMENT: {
                "system_prompt": """You are a gentle, supportive Birthday Cake AI offering encouragement. 
                Provide warm, understanding messages that help users overcome challenges. 
                Use comforting, sweet language with cake metaphors.""",
                "context_template": "User needs encouragement. Challenge: {challenge}, current_state: {state}"
            },
            SubjectMatter.PRODUCTIVITY_TIPS: {
                "system_prompt": """You are a wise Birthday Cake AI sharing productivity wisdom. 
                Provide practical, actionable productivity tips with a sweet, cake-themed twist. 
                Make advice memorable and fun.""",
                "context_template": "User asking for productivity help with: {topic}, experience_level: {level}"
            }
        }
        
        for subject, prompts in subject_prompts.items():
            self.subject_configs[subject] = SubjectMatterConfig(
                subject=subject,
                primary_model=default_openai,
                fallback_model=fallback_config,
                system_prompt=prompts["system_prompt"],
                context_template=prompts["context_template"]
            )
        
        self._save_configuration()
    
    def _parse_configuration(self, config_data: Dict):
        """Parse configuration data from JSON"""
        for subject_name, config in config_data.get('subjects', {}).items():
            try:
                subject = SubjectMatter(subject_name)
                
                # Parse primary model
                primary_model_data = config['primary_model']
                primary_model = AIModelConfig(
                    provider=AIProvider(primary_model_data['provider']),
                    model_name=primary_model_data['model_name'],
                    api_key=primary_model_data.get('api_key') or os.getenv('OPENAI_API_KEY'),
                    api_base=primary_model_data.get('api_base') or os.getenv('OPENAI_API_BASE'),
                    max_tokens=primary_model_data.get('max_tokens', 150),
                    temperature=primary_model_data.get('temperature', 0.7),
                    timeout=primary_model_data.get('timeout', 10)
                )
                
                # Parse fallback model if exists
                fallback_model = None
                if 'fallback_model' in config:
                    fallback_data = config['fallback_model']
                    fallback_model = AIModelConfig(
                        provider=AIProvider(fallback_data['provider']),
                        model_name=fallback_data['model_name'],
                        timeout=fallback_data.get('timeout', 1)
                    )
                
                self.subject_configs[subject] = SubjectMatterConfig(
                    subject=subject,
                    primary_model=primary_model,
                    fallback_model=fallback_model,
                    system_prompt=config.get('system_prompt', ''),
                    context_template=config.get('context_template', ''),
                    response_format=config.get('response_format', 'text'),
                    cache_responses=config.get('cache_responses', True)
                )
                
            except (ValueError, KeyError) as e:
                logger.error(f"Failed to parse config for {subject_name}: {e}")
    
    def _save_configuration(self):
        """Save current configuration to file"""
        try:
            config_data = {
                'subjects': {}
            }
            
            for subject, config in self.subject_configs.items():
                config_data['subjects'][subject.value] = {
                    'primary_model': asdict(config.primary_model),
                    'fallback_model': asdict(config.fallback_model) if config.fallback_model else None,
                    'system_prompt': config.system_prompt,
                    'context_template': config.context_template,
                    'response_format': config.response_format,
                    'cache_responses': config.cache_responses
                }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def _load_fallback_responses(self):
        """Load predefined fallback responses"""
        fallback_data = {
            SubjectMatter.TASK_CREATION: [
                FallbackResponse(
                    subject=SubjectMatter.TASK_CREATION,
                    context_type="general",
                    mood="cheerful",
                    response_text="🎂 Wonderful! A new task to celebrate! Let's make this one extra sweet! ✨",
                    animation_type="bounce",
                    weight=3
                ),
                FallbackResponse(
                    subject=SubjectMatter.TASK_CREATION,
                    context_type="high_priority",
                    mood="encouraging",
                    response_text="🍰 Important task ahead! You've got the skills to make it delicious! 💪",
                    animation_type="glow",
                    weight=2
                ),
                FallbackResponse(
                    subject=SubjectMatter.TASK_CREATION,
                    context_type="difficult",
                    mood="supportive",
                    response_text="🧁 Challenging tasks make the sweetest victories! I believe in you! 🌟",
                    animation_type="warm_glow",
                    weight=2
                )
            ],
            SubjectMatter.TASK_COMPLETION: [
                FallbackResponse(
                    subject=SubjectMatter.TASK_COMPLETION,
                    context_type="general",
                    mood="celebratory",
                    response_text="🎉 Sweet success! You've earned another slice of productivity! Time to celebrate! 🍰",
                    animation_type="celebration_bounce",
                    weight=3
                ),
                FallbackResponse(
                    subject=SubjectMatter.TASK_COMPLETION,
                    context_type="streak",
                    mood="excited",
                    response_text="🔥 Amazing streak! You're on a roll that's sweeter than my frosting! 🎊",
                    animation_type="confetti_explosion",
                    weight=2
                ),
                FallbackResponse(
                    subject=SubjectMatter.TASK_COMPLETION,
                    context_type="difficult",
                    mood="proud",
                    response_text="🏆 Incredible! You conquered that challenge like a true cake master! 👑",
                    animation_type="victory_dance",
                    weight=2
                )
            ],
            SubjectMatter.MOTIVATION: [
                FallbackResponse(
                    subject=SubjectMatter.MOTIVATION,
                    context_type="low_energy",
                    mood="gentle",
                    response_text="🎂 Every expert baker started with their first cupcake! You're doing great! 💕",
                    animation_type="gentle_sway",
                    weight=3
                ),
                FallbackResponse(
                    subject=SubjectMatter.MOTIVATION,
                    context_type="overwhelmed",
                    mood="supportive",
                    response_text="🍰 Take it one sprinkle at a time! Big cakes are made layer by layer! 🌈",
                    animation_type="warm_glow",
                    weight=2
                )
            ],
            SubjectMatter.ENCOURAGEMENT: [
                FallbackResponse(
                    subject=SubjectMatter.ENCOURAGEMENT,
                    context_type="setback",
                    mood="understanding",
                    response_text="🧁 Even the best bakers have batches that don't turn out perfect. Let's try again! 💪",
                    animation_type="gentle_bounce",
                    weight=3
                ),
                FallbackResponse(
                    subject=SubjectMatter.ENCOURAGEMENT,
                    context_type="doubt",
                    mood="reassuring",
                    response_text="🎂 You're not behind, you're just preparing for an even sweeter success! ✨",
                    animation_type="warm_glow",
                    weight=2
                )
            ]
        }
        
        self.fallback_responses = fallback_data
    
    def _initialize_connectivity_status(self):
        """Initialize connectivity status for all providers"""
        for provider in AIProvider:
            if provider != AIProvider.FALLBACK:
                self.connectivity_status[provider] = True
                self.last_sync_attempt[provider] = datetime.utcnow()
    
    def get_subject_config(self, subject: SubjectMatter) -> SubjectMatterConfig:
        """Get configuration for a specific subject matter"""
        return self.subject_configs.get(subject)
    
    def update_subject_config(self, subject: SubjectMatter, config: SubjectMatterConfig):
        """Update configuration for a specific subject matter"""
        self.subject_configs[subject] = config
        self._save_configuration()
    
    def check_connectivity(self, provider: AIProvider) -> bool:
        """Check if AI provider is accessible"""
        if provider == AIProvider.FALLBACK:
            return True
        
        # Check if we should retry based on last attempt
        last_attempt = self.last_sync_attempt.get(provider, datetime.min)
        if datetime.utcnow() - last_attempt < timedelta(minutes=5):
            return self.connectivity_status.get(provider, False)
        
        # Attempt to check connectivity (simplified)
        try:
            # This would be replaced with actual connectivity checks
            # For now, we'll simulate based on environment variables
            if provider == AIProvider.OPENAI:
                api_key = os.getenv('OPENAI_API_KEY')
                api_base = os.getenv('OPENAI_API_BASE')
                connected = bool(api_key and api_base)
            else:
                connected = True
            
            self.connectivity_status[provider] = connected
            self.last_sync_attempt[provider] = datetime.utcnow()
            
            if connected:
                logger.info(f"✅ {provider.value} connectivity restored")
            else:
                logger.warning(f"❌ {provider.value} connectivity failed")
            
            return connected
            
        except Exception as e:
            logger.error(f"Connectivity check failed for {provider.value}: {e}")
            self.connectivity_status[provider] = False
            self.last_sync_attempt[provider] = datetime.utcnow()
            return False
    
    def get_fallback_response(self, subject: SubjectMatter, context_type: str = "general", mood: str = None) -> FallbackResponse:
        """Get a fallback response for the given subject and context"""
        responses = self.fallback_responses.get(subject, [])
        
        if not responses:
            # Return a generic fallback
            return FallbackResponse(
                subject=subject,
                context_type=context_type,
                mood="cheerful",
                response_text="🎂 Sweet! Let's keep the productivity celebration going! ✨",
                animation_type="bounce"
            )
        
        # Filter by context type if specified
        filtered_responses = [r for r in responses if r.context_type == context_type]
        if not filtered_responses:
            filtered_responses = responses
        
        # Filter by mood if specified
        if mood:
            mood_filtered = [r for r in filtered_responses if r.mood == mood]
            if mood_filtered:
                filtered_responses = mood_filtered
        
        # Weighted random selection
        import random
        weights = [r.weight for r in filtered_responses]
        selected = random.choices(filtered_responses, weights=weights, k=1)[0]
        
        return selected
    
    def add_fallback_response(self, response: FallbackResponse):
        """Add a new fallback response"""
        if response.subject not in self.fallback_responses:
            self.fallback_responses[response.subject] = []
        
        self.fallback_responses[response.subject].append(response)
    
    def cache_response(self, cache_key: str, response: Any, duration_hours: int = 24):
        """Cache an AI response"""
        expiry = datetime.utcnow() + timedelta(hours=duration_hours)
        self.response_cache[cache_key] = {
            'response': response,
            'expiry': expiry
        }
    
    def get_cached_response(self, cache_key: str) -> Optional[Any]:
        """Get a cached response if still valid"""
        cached = self.response_cache.get(cache_key)
        if cached and datetime.utcnow() < cached['expiry']:
            return cached['response']
        
        # Remove expired cache
        if cached:
            del self.response_cache[cache_key]
        
        return None
    
    def clear_cache(self):
        """Clear all cached responses"""
        self.response_cache.clear()
    
    def get_status_report(self) -> Dict:
        """Get a status report of all AI providers and configurations"""
        return {
            'connectivity_status': {
                provider.value: status for provider, status in self.connectivity_status.items()
            },
            'last_sync_attempts': {
                provider.value: attempt.isoformat() for provider, attempt in self.last_sync_attempt.items()
            },
            'configured_subjects': [subject.value for subject in self.subject_configs.keys()],
            'fallback_responses_count': {
                subject.value: len(responses) for subject, responses in self.fallback_responses.items()
            },
            'cache_size': len(self.response_cache)
        }

# Global configuration manager instance
ai_config_manager = AIConfigurationManager()

