import openai
import os
from typing import List, Dict, Any
from app.config.settings import settings
from app.models.lead import Message
from app.services.product_search.product_search_service import ProductSearchService


class AIService:
    def __init__(self):
        if settings.AI_PROVIDER == "openai":
            openai.api_key = settings.OPENAI_API_KEY
        # Additional providers can be initialized here
        self.product_search_service = ProductSearchService()

    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Message],
        user_context: Dict[str, Any] = None
    ) -> str:
        """
        Generate AI response based on user message and conversation history
        """
        # Check if the message is a product search query
        tenant_id = user_context.get('tenant_id') if user_context else None
        product_search_response = await self._handle_product_search(user_message, tenant_id)

        if product_search_response:
            return product_search_response

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

    async def _handle_product_search(self, user_message: str, tenant_id: str) -> str:
        """
        Handle product search queries from users.

        Args:
            user_message: The user's message
            tenant_id: The tenant identifier for multi-tenant isolation

        Returns:
            Formatted product search results or None if not a product search query
        """
        if not tenant_id:
            return None

        # Check if the message contains product search keywords
        search_keywords = [
            "search", "find", "looking for", "want", "need", "product",
            "item", "buy", "price of", "show me", "available", "what do you have"
        ]

        message_lower = user_message.lower()
        is_product_search = any(keyword in message_lower for keyword in search_keywords)

        if not is_product_search:
            return None

        # Extract search query by removing common search phrases
        search_query = user_message
        for keyword in search_keywords:
            if keyword in message_lower:
                # Remove the keyword and any leading/trailing text that might be a question
                search_query = message_lower.replace(keyword, "").strip()
                break

        # Clean up the search query
        search_query = search_query.strip("?.,! ")

        if len(search_query) < 2:  # If the remaining query is too short, use the original message
            search_query = user_message.strip("?.,! ")

        # Perform product search
        try:
            products = self.product_search_service.search_products(
                tenant_id=tenant_id,
                query=search_query,
                limit=5  # Limit to 5 products to avoid overwhelming the user
            )

            if not products:
                return f"Sorry, I couldn't find any products matching '{search_query}'. Could you try a different search term?"

            # Format the response
            response = f"I found {len(products)} product(s) matching your search for '{search_query}':\n\n"
            for i, product in enumerate(products, 1):
                name = product.get('Name', 'N/A')
                price = product.get('Sale price', product.get('Regular price', 'N/A'))
                description = product.get('Description', 'No description available')

                # Truncate description if too long
                if len(description) > 100:
                    description = description[:100] + "..."

                response += f"{i}. {name}\n"
                response += f"   Price: {price}\n"
                response += f"   Description: {description}\n\n"

            response += "Would you like more details about any of these products?"
            return response

        except Exception as e:
            print(f"Error in product search: {e}")
            return None

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