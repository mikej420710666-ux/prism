"""
AI Service Integration
Claude, Mistral, and Grok APIs for tweet remixing
"""

from anthropic import Anthropic
from mistralai import Mistral
from openai import OpenAI
from pydantic_settings import BaseSettings
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    anthropic_api_key: str
    mistral_api_key: str
    grok_api_key: str
    grok_base_url: str = "https://api.x.ai/v1"

    class Config:
        env_file = ".env"


settings = Settings()


class AIRemixer:
    """
    AI-powered tweet remixing service
    Supports Claude, Mistral, and Grok
    """

    def __init__(self):
        # Initialize AI clients
        self.claude = Anthropic(api_key=settings.anthropic_api_key)
        self.mistral = Mistral(api_key=settings.mistral_api_key)
        self.grok = OpenAI(
            api_key=settings.grok_api_key,
            base_url=settings.grok_base_url
        )


    def analyze_voice(self, tweets: List[str]) -> Dict:
        """
        Analyze user's writing style and detect niche

        Args:
            tweets: List of user's recent tweets

        Returns:
            {
                "niche": ["tech", "AI", "indie hacking"],
                "tone": "motivational",
                "topics": ["building", "shipping", "growth"],
                "best_content": ["threads", "hot takes"]
            }
        """
        # Truncate tweets if too many (to fit in context)
        sample_tweets = tweets[:50] if len(tweets) > 50 else tweets

        prompt = f"""Analyze these tweets and identify the author's niche, voice, and content strategy.

Tweets:
{chr(10).join(f'- {t}' for t in sample_tweets)}

Return a JSON object with this exact structure:
{{
  "niche": ["primary niche", "secondary niche"],
  "tone": "description of tone (e.g., technical, casual, motivational)",
  "topics": ["common topic 1", "common topic 2", "common topic 3"],
  "best_content": ["content type 1", "content type 2"]
}}

Focus on:
1. What topics/industries they discuss
2. Their writing tone and style
3. Most common themes
4. Best performing content types"""

        try:
            message = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract JSON from response
            response_text = message.content[0].text.strip()

            # Try to parse JSON
            # Sometimes Claude wraps JSON in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            voice_profile = json.loads(response_text)

            logger.info(f"Voice analysis complete: {voice_profile}")

            return voice_profile

        except Exception as e:
            logger.error(f"Error analyzing voice with Claude: {e}")
            # Return default structure
            return {
                "niche": ["general"],
                "tone": "neutral",
                "topics": ["various"],
                "best_content": ["tweets"]
            }


    def remix_tweet(
        self,
        original_content: str,
        voice_profile: Dict,
        model: str = "claude"
    ) -> str:
        """
        Remix a viral tweet in the user's voice

        Args:
            original_content: Original viral tweet
            voice_profile: User's voice characteristics from analyze_voice()
            model: AI model to use (claude, mistral, grok)

        Returns:
            Remixed tweet content
        """
        prompt = f"""
        Remix this viral tweet in the following writing style:

        Original Tweet: {original_content}

        Target Voice Profile:
        - Niche: {voice_profile.get('niche')}
        - Tone: {voice_profile.get('voice_characteristics', {}).get('tone')}
        - Style: {voice_profile.get('voice_characteristics', {}).get('style')}

        Requirements:
        1. Keep the core message/value
        2. Match the target voice perfectly
        3. Max 280 characters
        4. Make it authentic, not robotic

        Return ONLY the remixed tweet text.
        """

        if model == "claude":
            return self._remix_with_claude(prompt)
        elif model == "mistral":
            return self._remix_with_mistral(prompt)
        elif model == "grok":
            return self._remix_with_grok(prompt)
        else:
            raise ValueError(f"Unknown AI model: {model}")


    def _remix_with_claude(self, prompt: str) -> str:
        """Use Claude for remixing"""
        try:
            message = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            remixed_text = message.content[0].text.strip()

            # Ensure it's under 280 characters
            if len(remixed_text) > 280:
                remixed_text = remixed_text[:277] + "..."

            return remixed_text

        except Exception as e:
            logger.error(f"Error remixing with Claude: {e}")
            raise


    def _remix_with_mistral(self, prompt: str) -> str:
        """Use Mistral for remixing"""
        try:
            response = self.mistral.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            remixed_text = response.choices[0].message.content.strip()

            # Ensure it's under 280 characters
            if len(remixed_text) > 280:
                remixed_text = remixed_text[:277] + "..."

            return remixed_text

        except Exception as e:
            logger.error(f"Error remixing with Mistral: {e}")
            raise


    def _remix_with_grok(self, prompt: str) -> str:
        """Use Grok for remixing"""
        try:
            response = self.grok.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            remixed_text = response.choices[0].message.content.strip()

            # Ensure it's under 280 characters
            if len(remixed_text) > 280:
                remixed_text = remixed_text[:277] + "..."

            return remixed_text

        except Exception as e:
            logger.error(f"Error remixing with Grok: {e}")
            raise
