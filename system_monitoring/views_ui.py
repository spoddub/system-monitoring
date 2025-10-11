from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .auth_utils import COOKIE_NAME, make_session_token
from .models import MonitorUser


@require_http_methods(["GET"])
def login_page(request):
    return render(request, "login.html")


@require_http_methods(["GET", "POST"])
def login_submit(request):
    if request.method == "GET":
        return render(request, "login.html")

    username = (request.POST.get("username") or "").strip()
    password = request.POST.get("password") or ""
    user = MonitorUser.objects.filter(username=username).first()
    if not user or not user.check_password(password):
        return render(
            request,
            "login.html",
            {"error": "Invalid credentials"},
            status=401,
        )
    token = make_session_token(user.pk)
    response = redirect("/ui/incidents")
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        secure=False,
        max_age=24 * 60 * 60,
        path="/",
    )
    return response


@require_http_methods(["GET"])
def logout_view(request):
    response = redirect("/ui/login")
    response.delete_cookie(COOKIE_NAME, path="/")
    return response


@require_http_methods(["GET"])
def incidents_page(request):
    # по умолчанию только активные
    return render(request, "incidents.html", {"defaultActive": "true"})
