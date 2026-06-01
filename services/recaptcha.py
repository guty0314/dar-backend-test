# services/recaptcha.py
import os
import requests

# ── Configuración ──────────────────────────────────────────
# Podés cambiar el proveedor con la variable CAPTCHA_PROVIDER
# Valores: "recaptcha" (Google) | "turnstile" (Cloudflare)
CAPTCHA_PROVIDER = os.getenv("CAPTCHA_PROVIDER", "recaptcha")

RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY")
SKIP_CAPTCHA = os.getenv("SKIP_CAPTCHA", "false").lower() == "true"

# ──────────────────────────────────────────────────────────

def verify_recaptcha(token: str) -> bool:
    """Verifica el token según el proveedor configurado."""

    if SKIP_CAPTCHA:
        return True

    if CAPTCHA_PROVIDER == "turnstile":
        return _verify_turnstile(token)
    else:
        return _verify_google_recaptcha(token)


def _verify_google_recaptcha(token: str) -> bool:
    """Verifica con Google reCAPTCHA v2."""
    if not RECAPTCHA_SECRET_KEY:
        print("⚠️ RECAPTCHA_SECRET_KEY no configurada")
        return False
    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": RECAPTCHA_SECRET_KEY, "response": token},
            timeout=5,
        )
        result = response.json()
        return result.get("success", False)
    except Exception as e:
        print(f"❌ Error verificando reCAPTCHA: {e}")
        return False


def _verify_turnstile(token: str) -> bool:
    """Verifica con Cloudflare Turnstile."""
    if not TURNSTILE_SECRET_KEY:
        print("⚠️ TURNSTILE_SECRET_KEY no configurada")
        return False
    try:
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": TURNSTILE_SECRET_KEY, "response": token},
            timeout=5,
        )
        result = response.json()
        return result.get("success", False)
    except Exception as e:
        print(f"❌ Error verificando Turnstile: {e}")
        return False