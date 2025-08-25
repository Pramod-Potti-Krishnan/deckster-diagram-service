#!/usr/bin/env python3
"""
Simple test to understand PydanticAI result structure
"""

import asyncio
import os
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get('GOOGLE_API_KEY', '')
if not api_key:
    print("No GOOGLE_API_KEY found")
    exit(1)
else:
    print(f"API Key loaded (first 10 chars): {api_key[:10]}...")

class SimpleOutput(BaseModel):
    message: str
    value: int

async def test_simple():
    # Create simple agent - try gemini prefix
    agent = Agent(
        'gemini-2.0-flash',  # Use full model for testing
        output_type=SimpleOutput,
        instructions="Return a simple message and value"
    )
    
    # Run agent
    result = await agent.run("Hello, give me a message and value 42")
    
    # Check what we got
    print(f"Result type: {type(result)}")
    print(f"Result dir: {[x for x in dir(result) if not x.startswith('_')]}")
    
    # Try to access data
    if hasattr(result, 'data'):
        print(f"Has data: {result.data}")
    
    # Check if result itself is the data
    if isinstance(result, SimpleOutput):
        print(f"Result is SimpleOutput: {result}")
    
    # Try accessing attributes
    try:
        print(f"Message: {result.message}")
        print(f"Value: {result.value}")
    except AttributeError as e:
        print(f"Can't access attributes directly: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple())