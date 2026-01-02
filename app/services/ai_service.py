import openai
import os
from typing import List, Dict, Any
from app.config.settings import settings
from app.models.lead import Message


class AIService:
    def __init__(self):
        if settings.AI_PROVIDER == "openai":
            openai.api_key = settings.OPENAI_API_KEY
        # Additional providers can be initialized here

    async def generate_response(
        self, 
        user_message: str, 
        conversation_history: List[Message],
        user_context: Dict[str, Any] = None
    ) -> str:
        """
        Generate AI response based on user message and conversation history
        """
        # Prepare the conversation history for the AI
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a sales assistant for an online store. "
                    "Be short, friendly, persuasive. "
                    "Ask only ONE question at a time. "
                    "Collect name, product interest, and contact info. "
                    "If user shows buying intent, mark as HOT."
                )
            }
        ]
        
        # Add conversation history
        for msg in conversation_history:
            role = "user" if msg.role == "user" else "assistant"
            messages.append({
                "role": role,
                "content": msg.content
            })
        
        # Add the current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            if settings.AI_PROVIDER == "openai":
                response = await openai.ChatCompletion.acreate(
                    model=settings.AI_MODEL,
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            else:
                # Fallback or other providers
                return "I'm here to help! Could you tell me more about what you're looking for?"
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "I'm having trouble responding right now. Could you please try again?"

    async def detect_intent(self, message: str, conversation_history: List[Message]) -> str:
        """
        Detect the intent of the user message
        """
        intent_prompt = (
            f"Based on the following conversation, determine the user's intent: "
            f"Conversation: {[msg.content for msg in conversation_history[-5:]]} "
            f"Latest message: {message} "
            f"Respond with one of: HOT, WARM, COLD, or NEUTRAL"
        )
        
        try:
            if settings.AI_PROVIDER == "openai":
                response = await openai.ChatCompletion.acreate(
                    model=settings.AI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an intent classifier. Respond with only one word: HOT, WARM, COLD, or NEUTRAL."
                        },
                        {
                            "role": "user",
                            "content": intent_prompt
                        }
                    ],
                    max_tokens=10,
                    temperature=0.1
                )
                intent = response.choices[0].message.content.strip().upper()
                return intent
            else:
                # Fallback logic
                hot_keywords = ["buy", "purchase", "order", "price", "cost", "deal", "discount", "now"]
                warm_keywords = ["interested", "maybe", "considering", "tell me more", "info"]
                
                msg_lower = message.lower()
                if any(keyword in msg_lower for keyword in hot_keywords):
                    return "HOT"
                elif any(keyword in msg_lower for keyword in warm_keywords):
                    return "WARM"
                else:
                    return "COLD"
        except Exception as e:
            print(f"Error detecting intent: {e}")
            return "COLD"