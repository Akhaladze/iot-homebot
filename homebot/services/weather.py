import requests
from datetime import datetime, date

class WeatherService:
    def __init__(self):
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"
        self.historical_url = "https://archive-api.open-meteo.com/v1/archive"

    def _get_coordinates(self, city):
        """Resolves a city name to latitude and longitude."""
        try:
            params = {"name": city, "count": 1, "language": "en", "format": "json"}
            response = requests.get(self.geocoding_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data and data["results"]:
                result = data["results"][0]
                return result["latitude"], result["longitude"]
            return None, None
        except Exception as e:
            print(f"Error geocoding city {city}: {e}")
            return None, None

    def get_weather(self, city, target_date=None):
        """
        Fetches weather for a specific city.
        If target_date is None or today, fetches current weather.
        If target_date is in the past, fetches historical data.
        target_date should be a datetime object or a string 'YYYY-MM-DD'.
        """
        lat, lon = self._get_coordinates(city)
        if not lat or not lon:
            return {"error": f"Could not find coordinates for {city}"}

        # Normalize date
        if isinstance(target_date, str):
            try:
                target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        today = date.today()
        is_historical = target_date and target_date < today

        try:
            if is_historical:
                # Historical Weather
                date_str = target_date.strftime("%Y-%m-%d")
                params = {
                    "latitude": lat,
                    "longitude": lon,
                    "start_date": date_str,
                    "end_date": date_str,
                    "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
                    "timezone": "auto"
                }
                response = requests.get(self.historical_url, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                
                daily = data.get("daily", {})
                return {
                    "city": city,
                    "date": date_str,
                    "temp_max": daily.get("temperature_2m_max", [None])[0],
                    "temp_min": daily.get("temperature_2m_min", [None])[0],
                    "precipitation": daily.get("precipitation_sum", [None])[0],
                    "source": "Open-Meteo Historical"
                }

            else:
                # Current/Forecast Weather
                params = {
                    "latitude": lat,
                    "longitude": lon,
                    "current": ["temperature_2m", "relative_humidity_2m", "is_day", "precipitation", "weather_code"],
                    "timezone": "auto"
                }
                response = requests.get(self.forecast_url, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                
                current = data.get("current", {})
                return {
                    "city": city,
                    "scanned_at": current.get("time"),
                    "temp_c": current.get("temperature_2m"),
                    "humidity": current.get("relative_humidity_2m"),
                    "is_day": current.get("is_day"),
                    "precipitation": current.get("precipitation"),
                    "weather_code": current.get("weather_code"),
                    "source": "Open-Meteo"
                }
                
        except Exception as e:
            return {"error": str(e)}
