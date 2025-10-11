import hmac
import time
from hashlib import sha256

from django.conf import settings

COOKIE_NAME = "system_monitoring_session"
SESSION_TIME = 24 * 60 * 60  # 1 день


def sign(signing_data: str):
    key = settings.SECRET_KEY.encode("utf-8")
    return hmac.new(key, signing_data.encode("utf-8"), sha256).hexdigest()


# токен сессии без хранения на сервере
def make_session_token(user_id, session_time=SESSION_TIME):
    expiring = int(time.time()) + session_time
    signing_data = f"{user_id}.{expiring}"
    signed_data = sign(signing_data)
    return f"{signing_data}.{signed_data}"


def verify_session_token(token):
    try:
        user_id_str, expires_at, sig = token.split(".")
        signing_data = f"{user_id_str}.{expires_at}"
        if sign(signing_data) != sig:
            return None
        if int(expires_at) < int(time.time()):
            return None
        return int(user_id_str)
    except Exception:
        return None
