#!/usr/bin/env python3
"""
Simple Agent Demo

A basic agent that can search for weather and do calculations.
Works with both the Go TUI and CLI fallback.

Run:
    # With CLI fallback (no Go TUI needed)
    python examples/simple_agent.py
    
    # With full TUI (after building)
    make build-tui
    python examples/simple_agent.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentui import AgentApp

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Create the app
app = AgentApp(
    name="weather-assistant",
    provider="claude",
    system_prompt="""You are a helpful weather and calculation assistant.
    
Use the available tools to help users:
- get_weather: Get current weather for a city
- calculate: Perform calculations

Always be friendly and concise. When you use a tool, explain what you found.""",
    theme="catppuccin-mocha",
    tagline="Weather & Calculator",
    debug=False,  # Set to True for verbose logging
)


@app.tool(
    name="get_weather",
    description="Get current weather for a city. Returns temperature, conditions, and humidity.",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name (e.g., 'Copenhagen', 'New York', 'Tokyo')"
            }
        },
        "required": ["city"]
    }
)
def get_weather(city: str) -> dict:
    """Mock weather lookup - returns simulated weather data."""
    # Simulated weather data for demo
    weather_data = {
        "copenhagen": {"temp": 8, "conditions": "Cloudy", "humidity": 75, "wind": "15 km/h NW"},
        "new york": {"temp": 15, "conditions": "Sunny", "humidity": 45, "wind": "10 km/h E"},
        "tokyo": {"temp": 20, "conditions": "Partly Cloudy", "humidity": 60, "wind": "5 km/h S"},
        "london": {"temp": 10, "conditions": "Rainy", "humidity": 85, "wind": "20 km/h W"},
        "paris": {"temp": 12, "conditions": "Overcast", "humidity": 70, "wind": "8 km/h N"},
        "sydney": {"temp": 25, "conditions": "Sunny", "humidity": 55, "wind": "12 km/h SE"},
    }
    
    city_lower = city.lower().strip()
    
    if city_lower in weather_data:
        data = weather_data[city_lower]
        return {
            "city": city.title(),
            "temperature_celsius": data["temp"],
            "temperature_fahrenheit": round(data["temp"] * 9/5 + 32),
            "conditions": data["conditions"],
            "humidity_percent": data["humidity"],
            "wind": data["wind"],
            "source": "Demo Weather Service",
        }
    
    # Return generic data for unknown cities
    return {
        "city": city.title(),
        "temperature_celsius": 18,
        "temperature_fahrenheit": 64,
        "conditions": "Unknown",
        "humidity_percent": 50,
        "wind": "Variable",
        "note": "This is simulated data for demo purposes",
        "source": "Demo Weather Service",
    }


@app.tool(
    name="calculate",
    description="Perform a mathematical calculation. Supports basic arithmetic (+, -, *, /, %), parentheses, and common functions.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5', '(100 - 20) / 4')"
            }
        },
        "required": ["expression"]
    }
)
def calculate(expression: str) -> dict:
    """Safe calculator with basic math operations."""
    import re
    
    # Clean the expression
    expression = expression.strip()
    
    # Validate - only allow safe characters
    if not re.match(r'^[\d\s\+\-\*\/\%\.\(\)]+$', expression):
        return {
            "error": "Invalid expression. Only numbers and basic operators (+, -, *, /, %, parentheses) are allowed.",
            "expression": expression,
        }
    
    try:
        # Evaluate safely
        result = eval(expression, {"__builtins__": {}}, {})
        
        # Format result
        if isinstance(result, float):
            # Round to reasonable precision
            if result == int(result):
                result = int(result)
            else:
                result = round(result, 10)
        
        return {
            "expression": expression,
            "result": result,
            "formatted": f"{expression} = {result}",
        }
    except ZeroDivisionError:
        return {
            "error": "Division by zero",
            "expression": expression,
        }
    except Exception as e:
        return {
            "error": f"Calculation error: {str(e)}",
            "expression": expression,
        }


async def main():
    """Run the weather assistant."""
    print("=" * 50)
    print("Weather & Calculator Assistant")
    print("=" * 50)
    print()
    print("This demo shows a simple agent with two tools:")
    print("  • get_weather - Get weather for any city")
    print("  • calculate - Perform math calculations")
    print()
    print("Try asking things like:")
    print("  • What's the weather in Copenhagen?")
    print("  • Calculate 15% of 280")
    print("  • How's the weather in Tokyo and New York?")
    print()
    print("Type 'quit' or press Ctrl+C to exit.")
    print("=" * 50)
    print()
    
    try:
        await app.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")


if __name__ == "__main__":
    asyncio.run(main())
