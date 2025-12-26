import asyncio
import os
import httpx
from typing import Optional
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import time

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("WeatherServer")

# OpenWeatherMap API configuration
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "").strip()
BASE_URL = "https://api.openweathermap.org/data/2.5"

import sys
if not API_KEY:
    print("WARNING: OPENWEATHER_API_KEY is not set.", file=sys.stderr)

async def fetch_weather_data(endpoint: str, params: dict):
    """Helper function to fetch data from OpenWeatherMap API."""
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY environment variable is not set.")
    
    params["appid"] = API_KEY
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "City not found."}
            elif e.response.status_code == 401:
                return {"error": "Invalid API key."}
            elif e.response.status_code == 429:
                return {"error": "Rate limit exceeded."}
            else:
                return {"error": f"HTTP error occurred: {e.response.status_code}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while requesting data: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
async def get_current_weather(city: str, units: str = "metric") -> str:
    """
    Get the current weather for a specific city.
    
    Args:
        city: The name of the city (e.g., 'London', 'New York').
        units: The units of measurement. 'metric' for Celsius, 'imperial' for Fahrenheit. Default is 'metric'.
    """
    data = await fetch_weather_data("weather", {"q": city, "units": units})
    
    if "error" in data:
        return f"Error: {data['error']}"
    
    weather_desc = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    
    unit_symbol = "°C" if units == "metric" else "°F"
    speed_unit = "m/s" if units == "metric" else "mph"
    
    return (
        f"Current weather in {city.capitalize()}:\n"
        f"- Condition: {weather_desc.capitalize()}\n"
        f"- Temperature: {temp}{unit_symbol} (Feels like {feels_like}{unit_symbol})\n"
        f"- Humidity: {humidity}%\n"
        f"- Wind Speed: {wind_speed} {speed_unit}"
    )

@mcp.tool()
async def get_forecast(city: str, units: str = "metric") -> str:
    """
    Get a 5-day weather forecast for a specific city.
    
    Args:
        city: The name of the city.
        units: The units of measurement. 'metric' for Celsius, 'imperial' for Fahrenheit.
    """
    data = await fetch_weather_data("forecast", {"q": city, "units": units})
    
    if "error" in data:
        return f"Error: {data['error']}"
    
    forecast_list = data.get("list", [])
    if not forecast_list:
        return "No forecast data available."
    
    # Group by day and get one entry per day (e.g., at 12:00 PM)
    daily_forecasts = []
    seen_days = set()
    
    for entry in forecast_list:
        date_str = entry["dt_txt"].split(" ")[0]
        if date_str not in seen_days:
            daily_forecasts.append(entry)
            seen_days.add(date_str)
            if len(daily_forecasts) >= 5:
                break
    
    unit_symbol = "°C" if units == "metric" else "°F"
    
    result = f"5-Day Forecast for {city.capitalize()}:\n"
    for day in daily_forecasts:
        date = day["dt_txt"].split(" ")[0]
        temp = day["main"]["temp"]
        desc = day["weather"][0]["description"]
        result += f"- {date}: {temp}{unit_symbol}, {desc.capitalize()}\n"
    
    return result

# --- HTTP/SSE and OAuth2 Configuration ---
app = FastAPI(title="Weather MCP Server (HTTP)")
security = HTTPBearer()

# For demonstration, we use a simple secret and audience.
# In a real app, these would be managed securely.
JWT_SECRET = os.environ.get("JWT_SECRET", "mcp-secret-key-123")
JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "mcp-weather-client")
JWT_ALGORITHM = "HS256"

def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the Bearer token and checks the audience.
    This fulfills the requirement of 'validating token audience'.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            audience=JWT_AUDIENCE, 
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Invalid audience")
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# Initialize SSE transport
sse = SseServerTransport("/messages")

async def mcp_asgi_app(scope, receive, send):
    """
    Raw ASGI app to handle MCP SSE and messages.
    This is necessary because we need access to the 'send' function.
    """
    if scope["type"] != "http":
        return

    # Extract and validate token
    headers = dict(scope.get("headers", []))
    auth_header = headers.get(b"authorization", b"").decode()
    
    if not auth_header.startswith("Bearer "):
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"detail": "Missing or invalid token"}',
        })
        return

    token = auth_header[7:]
    try:
        jwt.decode(token, JWT_SECRET, audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM])
    except Exception as e:
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": f'{{"detail": "{str(e)}"}}'.encode(),
        })
        return

    # Handle routes
    if scope["path"] == "/mcp/sse":
        async with sse.connect_sse(scope, receive, send) as (read_stream, write_stream):
            await mcp._mcp_server.run(
                read_stream,
                write_stream,
                mcp._mcp_server.create_initialization_options()
            )
    elif scope["path"] == "/mcp/messages":
        await sse.handle_post_message(scope, receive, send)
    else:
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"detail": "Not Found"}',
        })

# Mount the ASGI app
app.mount("/mcp", mcp_asgi_app)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "http":
        import uvicorn
        print(f"Starting HTTP server on 0.0.0.0:8000", file=sys.stderr)
        print(f"SSE endpoint: http://localhost:8000/sse", file=sys.stderr)
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Default to STDIO for local use
        mcp.run()
