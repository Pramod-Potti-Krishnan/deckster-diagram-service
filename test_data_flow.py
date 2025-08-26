# Test data flow to understand the issue
import sys
sys.path.insert(0, '/private/tmp/deckster-diagram-service')

# Check what labels the test sends
test_labels = ["High Impact", "Quick Wins", "Fill Ins", "Time Sinks"]
print("Test sends these labels:")
for i, label in enumerate(test_labels):
    print(f"  {i}: {label}")

# Check what the template expects
from agents.svg_agent import SVGAgent
from config import Settings
import asyncio

async def check():
    settings = Settings()
    agent = SVGAgent(settings)
    await agent.initialize()
    
    # Get the placeholders
    placeholders = agent._get_template_placeholders("matrix_2x2")
    print("\nTemplate expects these placeholders:")
    for i, placeholder in enumerate(placeholders):
        print(f"  {i}: {placeholder}")
    
    # Check what the replacement would do
    template = agent.template_cache.get("matrix_2x2")
    if template:
        data_points = [{"label": label} for label in test_labels]
        result = agent._apply_replacements(template, data_points, {}, "matrix_2x2")
        
        # Check if "High / High" is still in the result
        if "High / High" in result:
            print("\n❌ Template still contains 'High / High' after replacement")
        else:
            print("\n✅ Template placeholders were replaced successfully")
            
        # Check what text ended up in Q1
        import re
        q1_text = re.search(r'id="quadrant_1"[^>]*>([^<]*)<', result)
        if q1_text:
            print(f"Q1 text: '{q1_text.group(1).strip()}'")

asyncio.run(check())
