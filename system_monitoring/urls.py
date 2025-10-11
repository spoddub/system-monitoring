"""
URL configuration for system_monitoring project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from .views_api import incidents_list, incidents_stream
from .views_ui import incidents_page, login_submit, logout_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ui/login", login_submit, name="ui_login"),
    path("ui/logout", logout_view, name="ui_logout"),
    path("ui/incidents", incidents_page, name="ui_incidents"),
    path("api/incidents", incidents_list, name="api_incidents"),
    path("api/incidents/stream", incidents_stream, name="api_incidents_stream"),
]
