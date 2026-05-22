import os
import requests

RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

def verify_recaptcha(token : str) -> bool:
    """Verify the reCAPTCHA token with Google's API."""
    url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        "secret": RECAPTCHA_SECRET_KEY,
        "response": token
    }
    response = requests.post(url, data=payload)
    result = response.json()
    return result.get("success", False)