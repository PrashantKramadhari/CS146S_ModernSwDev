# Week 3 — Weather MCP Server

This is a Model Context Protocol (MCP) server that provides weather information using the OpenWeatherMap API. It exposes tools to get current weather and a 5-day forecast for any city.

## Features
- **get_current_weather**: Returns current temperature, conditions, humidity, and wind speed.
- **get_forecast**: Returns a 5-day weather forecast.
- **Resilience**: Handles API errors, invalid cities, and missing API keys gracefully.
- **Units**: Supports both metric (Celsius) and imperial (Fahrenheit) units.

## Prerequisites
- Python 3.10 or higher.
- An OpenWeatherMap API key. You can get one for free at [openweathermap.org](https://openweathermap.org/api).

## Setup Instructions

1. **Clone the repository** (if you haven't already).
2. **Navigate to the week3 directory**:
   ```bash
   cd week3
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables**:
   Create a `.env` file in the `week3` directory or set the environment variable directly:
   ```bash
   export OPENWEATHER_API_KEY=your_api_key_here
   ```

## Running the Server

### Local (STDIO)
To run the server locally using STDIO transport:
```bash
python server/main.py
```

### Remote / HTTP (SSE with OAuth2)
To run the server as an HTTP server with Bearer token authentication:
```bash
python server/main.py http

#mine
npx @modelcontextprotocol/inspector /media/ubuntu/Data/tools/miniconda3/envs/cs146/bin/python server/main.py
```
The server will start on `http://localhost:8000`.

#### Authentication (OAuth2)
The HTTP server requires a `Authorization: Bearer <token>` header.
1. **Generate a token**:
   ```bash
   python server/generate_token.py
   ```
2. **Connect via SSE**:
   Use an MCP client that supports SSE and custom headers, or test with `curl`:
   ```bash
   curl -N http://localhost:8000/mcp/sse -H "Authorization: Bearer <your_token>"
   ```

### Configuring with Claude Desktop
To use this server with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/absolute/path/to/week3/server/main.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```
*Replace `/absolute/path/to/week3/server/main.py` with the actual absolute path on your machine.*

## Tool Reference

### `get_current_weather`
- **Description**: Get the current weather for a specific city.
- **Parameters**:
  - `city` (string): The name of the city (e.g., "London", "Tokyo").
  - `units` (string, optional): "metric" (default) or "imperial".
- **Example Input**: `city="Paris", units="metric"`
- **Example Output**:
  ```
  Current weather in Paris:
  - Condition: Clear sky
  - Temperature: 18.5°C (Feels like 17.8°C)
  - Humidity: 45%
  - Wind Speed: 3.2 m/s
  ```

### `get_forecast`
- **Description**: Get a 5-day weather forecast for a specific city.
- **Parameters**:
  - `city` (string): The name of the city.
  - `units` (string, optional): "metric" (default) or "imperial".
- **Example Input**: `city="Berlin"`
- **Example Output**:
  ```
  5-Day Forecast for Berlin:
  - 2023-10-27: 12.4°C, Overcast clouds
  - 2023-10-28: 10.1°C, Light rain
  ...
  ```

## Resilience and Error Handling
- **Invalid City**: Returns a friendly "City not found" message.
- **API Key Issues**: Detects missing or invalid API keys and provides clear error messages.
- **Timeouts**: Implements a 10-second timeout for API requests to prevent hanging.
- **Rate Limiting**: Detects 429 status codes and informs the user.
- **OAuth2 Security**: 
  - Validates JWT tokens using a secret key.
  - **Audience Validation**: Ensures the token was intended for this specific server (`mcp-weather-client`).
  - **Token Isolation**: Never passes the bearer token to the upstream OpenWeatherMap API (which uses its own API key).
