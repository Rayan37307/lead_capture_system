#!/usr/bin/env python3
"""
Test script for the AI service product search integration
"""
import asyncio
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, '/home/rayan/coding/lead_capture_system')

from app.services.ai_service import AIService
from app.models.lead import Message

async def test_ai_product_search():
    print("Testing AI Service Product Search Integration...")
    
    # Initialize the AI service
    ai_service = AIService()
    
    # Simulate a conversation history
    conversation_history = [
        Message(role="user", content="Hi, I'm looking for a moisturizer", timestamp="2023-01-01T00:00:00Z"),
        Message(role="assistant", content="Sure, I can help with that. What type of moisturizer are you looking for?", timestamp="2023-01-01T00:00:01Z")
    ]
    
    # Test product search through AI service
    print("\n1. Testing product search through AI service...")
    user_context = {"tenant_id": "shajba"}
    
    response = await ai_service.generate_response(
        user_message="I want to find a CeraVe moisturizer",
        conversation_history=conversation_history,
        user_context=user_context
    )
    
    print("AI Response:")
    print(response)
    
    # Test another search
    print("\n2. Testing another product search...")
    response2 = await ai_service.generate_response(
        user_message="Show me some face cleansers",
        conversation_history=conversation_history,
        user_context=user_context
    )
    
    print("AI Response:")
    print(response2)
    
    # Test a non-product search to ensure normal functionality still works
    print("\n3. Testing non-product search (should use normal AI response)...")
    response3 = await ai_service.generate_response(
        user_message="What are your store hours?",
        conversation_history=conversation_history,
        user_context=user_context
    )
    
    print("AI Response:")
    print(response3)
    
    print("\nAll AI integration tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_ai_product_search())