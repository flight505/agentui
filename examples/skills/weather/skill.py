"""Weather skill implementation."""

import random  # For demo purposes - replace with real weather API in production


def get_weather(city: str, units: str = "celsius") -> dict:
    """
    Get current weather for a city.

    Args:
        city: City name (e.g., 'Copenhagen', 'New York')
        units: Temperature units ('celsius' or 'fahrenheit')

    Returns:
        Dictionary with current weather information
    """
    # TODO: Replace with real weather API call (e.g., OpenWeatherMap, WeatherAPI)
    # This is a demo implementation that returns random data

    base_temp = random.randint(10, 30)
    if units == "fahrenheit":
        temp = (base_temp * 9 / 5) + 32
        temp_str = f"{temp:.1f}°F"
    else:
        temp_str = f"{base_temp}°C"

    conditions = random.choice(["Sunny", "Partly cloudy", "Cloudy", "Rainy", "Windy"])

    return {
        "city": city,
        "temperature": temp_str,
        "conditions": conditions,
        "humidity": f"{random.randint(40, 80)}%",
        "wind_speed": f"{random.randint(5, 25)} km/h",
        "timestamp": "Demo data - not real-time",
    }


def get_forecast(city: str, days: int = 3) -> dict:
    """
    Get weather forecast for upcoming days.

    Args:
        city: City name
        days: Number of days to forecast (1-7)

    Returns:
        Dictionary with forecast information
    """
    # TODO: Replace with real weather API call
    # This is a demo implementation that returns random data

    if days < 1 or days > 7:
        return {
            "error": "Days must be between 1 and 7",
        }

    forecast_days = []
    day_names = ["Today", "Tomorrow", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]

    for i in range(days):
        conditions = ["Sunny", "Partly cloudy", "Cloudy", "Rainy", "Stormy"]

        forecast_days.append({
            "day": day_names[i],
            "high": f"{random.randint(15, 30)}°C",
            "low": f"{random.randint(5, 15)}°C",
            "conditions": conditions[i % len(conditions)],
            "precipitation": f"{random.randint(0, 80)}%",
        })

    return {
        "city": city,
        "forecast": forecast_days,
        "timestamp": "Demo data - not real-time",
    }
