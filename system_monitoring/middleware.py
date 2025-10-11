from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect

from .auth_utils import COOKIE_NAME, verify_session_token

# куда можно без авторизации
SAFE_PATHS = (
    "/ui/login",
    "/ui/logout",
)


def needs_auth(path):
    if path.startswith("/ui/") or path.startswith("/api/"):
        for p in SAFE_PATHS:
            if path == p or path.startswith(p + "/"):
                return False
        return True
    return False


class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        path = request.path
        if needs_auth(path):
            token = request.COOKIES.get(COOKIE_NAME)
            uid = verify_session_token(token) if token else None
            if not uid:
                if path.startswith("/ui/"):
                    return redirect("/ui/login")
                return JsonResponse({"detail": "unauthorized"}, status=401)
        return self.get_response(request)
