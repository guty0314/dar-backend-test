import secrets
import time

# Token: { "token": { "username": ..., "expires": ... } }
_reset_tokens: dict = {}

TOKEN_EXPIRY_SECONDS = 900  # 15 minutos

def generate_reset_token(username: str) -> str:
    token = secrets.token_urlsafe(32)
    _reset_tokens[token] = {
        "username": username,
        "expires": time.time() + TOKEN_EXPIRY_SECONDS
    }
    return token

def verify_reset_token(token: str) -> str | None:
    data = _reset_tokens.get(token)
    if not data:
        return None
    if time.time() > data["expires"]:
        _reset_tokens.pop(token, None)
        return None
    return data["username"]

def consume_reset_token(token: str) -> str | None:
    username = verify_reset_token(token)
    if username:
        _reset_tokens.pop(token, None)
    return username