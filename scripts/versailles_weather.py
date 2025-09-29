import os
import requests
import datetime as dt
from datetime import timezone
from typing import Dict, Any, Union
from dotenv import load_dotenv

load_dotenv()

# Versailles Palace coordinates
VERSAILLES_LAT = 48.8049
VERSAILLES_LON = 2.1204

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


def get_current_weather() -> Dict[str, Any]:
    """
    Get current weather for Versailles.

    Returns:
        Dict containing current weather data
    """
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY environment variable is not set")

    url = f"{OPENWEATHER_BASE_URL}/weather"
    params = {
        "lat": VERSAILLES_LAT,
        "lon": VERSAILLES_LON,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"  # Celsius temperatures
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "location": {
                "name": "Palace of Versailles",
                "coordinates": {"lat": VERSAILLES_LAT, "lon": VERSAILLES_LON}
            },
            "weather": {
                "temperature": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"].title(),
                "main": data["weather"][0]["main"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                "clouds": data["clouds"]["all"]
            },
            "timestamp": dt.datetime.now(timezone.utc).isoformat(),
            "status": "success"
        }

    except requests.RequestException as e:
        return {
            "error": f"Failed to fetch current weather: {str(e)}",
            "status": "error"
        }


def get_5day_forecast() -> Dict[str, Any]:
    """
    Get 5-day weather forecast for Versailles.

    Returns:
        Dict containing 5-day forecast with 3-hour intervals
    """
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY environment variable is not set")

    url = f"{OPENWEATHER_BASE_URL}/forecast"
    params = {
        "lat": VERSAILLES_LAT,
        "lon": VERSAILLES_LON,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    forecasts = []
    for item in data["list"]:
        forecast_dt = dt.datetime.fromtimestamp(item["dt"], tz=timezone.utc)
        forecasts.append({
            "datetime": forecast_dt.isoformat(),
            "date": forecast_dt.date().isoformat(),
            "time": forecast_dt.strftime("%H:%M"),
            "temperature": round(item["main"]["temp"]),
            "feels_like": round(item["main"]["feels_like"]),
            "description": item["weather"][0]["description"].title(),
            "main": item["weather"][0]["main"],
            "humidity": item["main"]["humidity"],
            "wind_speed": item.get("wind", {}).get("speed", 0),
            "clouds": item.get("clouds", {}).get("all", 0)
        })

    return {
        "location": {
            "name": "Palace of Versailles",
            "coordinates": {"lat": VERSAILLES_LAT, "lon": VERSAILLES_LON}
        },
        "forecasts": forecasts,
        "total_forecasts": len(forecasts)
    }


def get_daily_forecast() -> Dict[str, Any]:
    """
    Get daily weather forecast for Versailles (aggregated from 5-day forecast).

    Returns:
        Dict containing daily summaries for the next 5 days
    """
    forecast_data = get_5day_forecast()

    # Group forecasts by date
    daily_groups = {}
    for forecast in forecast_data["forecasts"]:
        date = forecast["date"]
        if date not in daily_groups:
            daily_groups[date] = []
        daily_groups[date].append(forecast)

    # Create daily summaries
    daily_forecasts = []
    for date, day_forecasts in daily_groups.items():
        temps = [f["temperature"] for f in day_forecasts]
        conditions = [f["main"] for f in day_forecasts]

        # Get the most common condition
        main_condition = max(set(conditions), key=conditions.count)

        daily_forecasts.append({
            "date": date,
            "min_temp": min(temps),
            "max_temp": max(temps),
            "avg_temp": round(sum(temps) / len(temps)),
            "main_condition": main_condition,
            "forecasts_count": len(day_forecasts),
            "detailed_forecasts": day_forecasts
        })

    return {
        "location": {
            "name": "Palace of Versailles",
            "coordinates": {"lat": VERSAILLES_LAT, "lon": VERSAILLES_LON}
        },
        "daily_forecasts": daily_forecasts,
        "total_days": len(daily_forecasts)
    }


def get_versailles_weather(visit_date: Union[str, dt.date, dt.datetime]) -> Dict[str, Any]:
    """
    Get weather forecast for Versailles for a specific visit date.

    Args:
        visit_date: The date of the visit. Can be:
            - String in YYYY-MM-DD format (e.g., "2025-01-15")
            - datetime.date object
            - datetime.datetime object

    Returns:
        Dict containing weather forecast for the specific date
    """
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY environment variable is not set")

    # Parse visit date
    if isinstance(visit_date, str):
        try:
            parsed_date = dt.datetime.strptime(visit_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Date string must be in YYYY-MM-DD format")
    elif isinstance(visit_date, dt.datetime):
        parsed_date = visit_date.date()
    elif isinstance(visit_date, dt.date):
        parsed_date = visit_date
    else:
        raise ValueError("visit_date must be a string, date, or datetime object")

    today = dt.date.today()
    days_until_visit = (parsed_date - today).days

    # Handle today's weather (use current weather API)
    if days_until_visit == 0:
        current_data = get_current_weather()
        if current_data["status"] == "success":
            return {
                "visit_date": parsed_date.isoformat(),
                "days_until_visit": days_until_visit,
                "location": current_data["location"],
                "weather": current_data["weather"],
                "forecast_type": "current",
                "status": "success"
            }
        else:
            return {
                "visit_date": parsed_date.isoformat(),
                "days_until_visit": days_until_visit,
                "error": current_data.get("error", "Failed to get current weather"),
                "status": "error"
            }

    # Handle future dates (use forecast API)
    daily_data = get_daily_forecast()

    # Find the specific date
    target_forecast = None
    for daily in daily_data["daily_forecasts"]:
        if daily["date"] == parsed_date.isoformat():
            target_forecast = daily
            break

    if target_forecast:
        return {
            "visit_date": parsed_date.isoformat(),
            "days_until_visit": days_until_visit,
            "location": daily_data["location"],
            "forecast": target_forecast,
            "forecast_type": "5day" if days_until_visit <= 5 else "seasonal",
            "status": "success"
        }
    else:
        return {
            "visit_date": parsed_date.isoformat(),
            "days_until_visit": days_until_visit,
            "location": daily_data["location"],
            "error": f"No forecast available for {parsed_date}. Forecast only covers next 5 days.",
            "status": "error"
        }



if __name__ == "__main__":
    print("Testing Versailles weather functions:")

    # Test 5-day forecast
    print("\n=== 5-Day Forecast ===")
    try:
        forecast_5day = get_5day_forecast()
        print(f"Total forecasts: {forecast_5day['total_forecasts']}")
        print("First 3 forecasts:")
        for i, f in enumerate(forecast_5day['forecasts'][:3]):
            print(f"  {f['datetime']}: {f['temperature']}°C, {f['description']}")
    except Exception as e:
        print(f"Error: {e}")

    # Test daily forecast
    print("\n=== Daily Forecast ===")
    try:
        forecast_daily = get_daily_forecast()
        print(f"Total days: {forecast_daily['total_days']}")
        for day in forecast_daily['daily_forecasts']:
            print(f"  {day['date']}: {day['min_temp']}-{day['max_temp']}°C, {day['main_condition']}")
    except Exception as e:
        print(f"Error: {e}")

    # Test specific date
    print("\n=== Specific Date ===")
    test_date = (dt.date.today() + dt.timedelta(days=2)).isoformat()
    print(get_versailles_weather(test_date))