"""
AI Service Layer for Birthday Cake Planner
Handles AI model interactions with fallback mechanisms
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

from src.config.ai_config import (
    ai_config_manager, 
    AIProvider, 
    SubjectMatter, 
    AIModelConfig,
    FallbackResponse
)

# Configure logging
logger = logging.getLogger(__name__)

class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass

class AIResponse:
    """Standardized AI response object"""
    
    def __init__(self, text: str, animation_type: str = "bounce", 
                 mood: str = "cheerful", source: str = "ai", 
                 metadata: Dict = None):
        self.text = text
        self.animation_type = animation_type
        self.mood = mood
        self.source = source  # 'ai', 'fallback', 'cache'
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'animation_type': self.animation_type,
            'mood': self.mood,
            'source': self.source,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

class OpenAIProvider:
    """OpenAI API provider implementation"""
    
    def __init__(self, config: AIModelConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            import openai
            
            # Set API configuration
            if self.config.api_key:
                openai.api_key = self.config.api_key
            if self.config.api_base:
                openai.api_base = self.config.api_base
            
            self.client = openai
            logger.info("OpenAI client initialized successfully")
            
        except ImportError:
            logger.error("OpenAI package not installed")
            raise AIServiceError("OpenAI package not available")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise AIServiceError(f"OpenAI initialization failed: {e}")
    
    async def generate_response(self, system_prompt: str, user_prompt: str, 
                              context: Dict = None) -> AIResponse:
        """Generate response using OpenAI API"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Add context if provided
            if context:
                context_str = f"Context: {json.dumps(context, default=str)}"
                messages.append({"role": "user", "content": context_str})
            
            # Make API call with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.ChatCompletion.create,
                    model=self.config.model_name,
                    messages=messages,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                ),
                timeout=self.config.timeout
            )
            
            # Extract response text
            response_text = response.choices[0].message.content.strip()
            
            # Parse mood and animation from response if structured
            mood, animation = self._parse_response_metadata(response_text)
            
            return AIResponse(
                text=response_text,
                animation_type=animation,
                mood=mood,
                source="ai",
                metadata={
                    "model": self.config.model_name,
                    "provider": "openai",
                    "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
                }
            )
            
        except asyncio.TimeoutError:
            logger.warning(f"OpenAI API timeout after {self.config.timeout}s")
            raise AIServiceError("AI service timeout")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise AIServiceError(f"AI generation failed: {e}")
    
    def _parse_response_metadata(self, response_text: str) -> tuple:
        """Parse mood and animation hints from response text"""
        mood = "cheerful"
        animation = "bounce"
        
        # Simple keyword-based parsing
        if any(word in response_text.lower() for word in ["amazing", "incredible", "fantastic"]):
            mood = "excited"
            animation = "celebration_bounce"
        elif any(word in response_text.lower() for word in ["gentle", "soft", "calm"]):
            mood = "gentle"
            animation = "gentle_sway"
        elif any(word in response_text.lower() for word in ["celebrate", "party", "woohoo"]):
            mood = "celebratory"
            animation = "confetti_explosion"
        
        return mood, animation

class AIService:
    """Main AI service that orchestrates model interactions and fallbacks"""
    
    def __init__(self):
        self.providers = {}
        self.config_manager = ai_config_manager
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured AI providers"""
        try:
            # Initialize OpenAI provider if configured
            openai_configs = [
                config.primary_model for config in self.config_manager.subject_configs.values()
                if config.primary_model.provider == AIProvider.OPENAI
            ]
            
            if openai_configs:
                sample_config = openai_configs[0]
                self.providers[AIProvider.OPENAI] = OpenAIProvider(sample_config)
                logger.info("OpenAI provider initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI providers: {e}")
    
    def _generate_cache_key(self, subject: SubjectMatter, context: Dict) -> str:
        """Generate cache key for response caching"""
        context_str = json.dumps(context, sort_keys=True, default=str)
        cache_input = f"{subject.value}:{context_str}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _format_user_prompt(self, subject: SubjectMatter, context: Dict) -> str:
        """Format user prompt using subject configuration template"""
        config = self.config_manager.get_subject_config(subject)
        if not config or not config.context_template:
            return f"Generate a response for {subject.value} with context: {context}"
        
        try:
            return config.context_template.format(**context)
        except KeyError as e:
            logger.warning(f"Missing context key {e} for {subject.value}")
            return f"Generate a response for {subject.value} with available context: {context}"
    
    async def generate_response(self, subject: SubjectMatter, context: Dict = None, 
                              force_ai: bool = False) -> AIResponse:
        """
        Generate AI response with fallback mechanisms
        
        Args:
            subject: The subject matter for the response
            context: Context data for the response
            force_ai: Force AI generation even if cached/fallback available
        
        Returns:
            AIResponse object with the generated response
        """
        context = context or {}
        config = self.config_manager.get_subject_config(subject)
        
        if not config:
            logger.error(f"No configuration found for subject: {subject}")
            return self._get_fallback_response(subject, context)
        
        # Check cache first (unless forcing AI)
        if not force_ai and config.cache_responses:
            cache_key = self._generate_cache_key(subject, context)
            cached_response = self.config_manager.get_cached_response(cache_key)
            if cached_response:
                logger.info(f"Using cached response for {subject.value}")
                cached_response['source'] = 'cache'
                return AIResponse(**cached_response)
        
        # Try primary AI model
        try:
            if not force_ai:
                # Check connectivity first
                provider_available = self.config_manager.check_connectivity(config.primary_model.provider)
                if not provider_available:
                    logger.warning(f"Primary provider {config.primary_model.provider.value} unavailable")
                    return await self._try_fallback_model(subject, context, config)
            
            # Generate AI response
            ai_response = await self._generate_ai_response(config, context)
            
            # Cache the response
            if config.cache_responses:
                cache_key = self._generate_cache_key(subject, context)
                self.config_manager.cache_response(
                    cache_key, 
                    ai_response.to_dict(), 
                    config.cache_duration_hours
                )
            
            logger.info(f"Generated AI response for {subject.value}")
            return ai_response
            
        except AIServiceError as e:
            logger.warning(f"AI generation failed for {subject.value}: {e}")
            return await self._try_fallback_model(subject, context, config)
        except Exception as e:
            logger.error(f"Unexpected error generating AI response: {e}")
            return self._get_fallback_response(subject, context)
    
    async def _generate_ai_response(self, config, context: Dict) -> AIResponse:
        """Generate response using configured AI model"""
        provider = self.providers.get(config.primary_model.provider)
        if not provider:
            raise AIServiceError(f"Provider {config.primary_model.provider.value} not available")
        
        user_prompt = self._format_user_prompt(config.subject, context)
        
        # Retry logic
        last_error = None
        for attempt in range(config.primary_model.retry_attempts):
            try:
                response = await provider.generate_response(
                    config.system_prompt,
                    user_prompt,
                    context
                )
                return response
                
            except AIServiceError as e:
                last_error = e
                if attempt < config.primary_model.retry_attempts - 1:
                    await asyncio.sleep(config.primary_model.retry_delay * (attempt + 1))
                    logger.info(f"Retrying AI generation (attempt {attempt + 2})")
        
        raise last_error or AIServiceError("AI generation failed after retries")
    
    async def _try_fallback_model(self, subject: SubjectMatter, context: Dict, config) -> AIResponse:
        """Try fallback AI model if configured"""
        if config.fallback_model and config.fallback_model.provider != AIProvider.FALLBACK:
            try:
                # Try fallback AI model
                fallback_provider = self.providers.get(config.fallback_model.provider)
                if fallback_provider:
                    user_prompt = self._format_user_prompt(subject, context)
                    response = await fallback_provider.generate_response(
                        config.system_prompt,
                        user_prompt,
                        context
                    )
                    response.source = "fallback_ai"
                    logger.info(f"Used fallback AI model for {subject.value}")
                    return response
            except Exception as e:
                logger.warning(f"Fallback AI model also failed: {e}")
        
        # Use static fallback responses
        return self._get_fallback_response(subject, context)
    
    def _get_fallback_response(self, subject: SubjectMatter, context: Dict) -> AIResponse:
        """Get static fallback response"""
        context_type = context.get('context_type', 'general')
        mood = context.get('mood', 'cheerful')
        
        fallback = self.config_manager.get_fallback_response(subject, context_type, mood)
        
        logger.info(f"Using static fallback response for {subject.value}")
        return AIResponse(
            text=fallback.response_text,
            animation_type=fallback.animation_type,
            mood=fallback.mood,
            source="fallback",
            metadata={
                "fallback_reason": "ai_unavailable",
                "context_type": context_type
            }
        )
    
    def get_service_status(self) -> Dict:
        """Get comprehensive service status"""
        return {
            "ai_service_status": "operational",
            "providers_initialized": list(self.providers.keys()),
            "configuration_status": self.config_manager.get_status_report(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def test_connectivity(self) -> Dict:
        """Test connectivity to all configured providers"""
        results = {}
        
        for provider in AIProvider:
            if provider == AIProvider.FALLBACK:
                results[provider.value] = {"status": "always_available", "response_time": 0}
                continue
            
            start_time = time.time()
            try:
                connected = self.config_manager.check_connectivity(provider)
                response_time = time.time() - start_time
                
                results[provider.value] = {
                    "status": "connected" if connected else "disconnected",
                    "response_time": response_time
                }
            except Exception as e:
                results[provider.value] = {
                    "status": "error",
                    "error": str(e),
                    "response_time": time.time() - start_time
                }
        
        return results
    
    async def sync_with_ai(self, force: bool = False) -> Dict:
        """Sync fallback responses with AI models"""
        sync_results = {}
        
        for subject in SubjectMatter:
            try:
                # Generate fresh responses for common scenarios
                scenarios = [
                    {"context_type": "general", "mood": "cheerful"},
                    {"context_type": "celebration", "mood": "excited"},
                    {"context_type": "encouragement", "mood": "supportive"}
                ]
                
                for scenario in scenarios:
                    response = await self.generate_response(subject, scenario, force_ai=True)
                    if response.source == "ai":
                        # Add as new fallback response
                        fallback = FallbackResponse(
                            subject=subject,
                            context_type=scenario["context_type"],
                            mood=response.mood,
                            response_text=response.text,
                            animation_type=response.animation_type,
                            weight=1
                        )
                        self.config_manager.add_fallback_response(fallback)
                        
                sync_results[subject.value] = "synced"
                
            except Exception as e:
                logger.error(f"Failed to sync {subject.value}: {e}")
                sync_results[subject.value] = f"error: {e}"
        
        return sync_results

# Global AI service instance
ai_service = AIService()

