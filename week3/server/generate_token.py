import jwt
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Use the same secret and audience as in main.py
JWT_SECRET = os.environ.get("JWT_SECRET", "mcp-secret-key-123")
JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "mcp-weather-client")
JWT_ALGORITHM = "HS256"

def generate_token():
    payload = {
        "sub": "test-user",
        "aud": JWT_AUDIENCE,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600  # Expires in 1 hour
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

if __name__ == "__main__":
    token = generate_token()
    print(f"Generated JWT Token:\n{token}")
    print("\nTo use this with curl:")
    print(f'curl -N http://localhost:8000/mcp/sse -H "Authorization: Bearer {token}"')
