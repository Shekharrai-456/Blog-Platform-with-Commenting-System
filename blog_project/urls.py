"""
URL configuration for blog_project project.

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
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(),name ="schema"),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'),name ="swagger-ui"),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'),name ="redoc"),
    
    # Django admin
    path("admin/", admin.site.urls),

    # Blog app endpoints (posts, categories, tags, comments)
    path("api/blog/", include("blog.urls")),

    # User app endpoints (register, login, profile, etc.)
    path("api/user/", include("user.urls")),

    # Optional: DRF’s browsable API login/logout (session-based auth)
    # You’ll mainly use token authentication, but this helps when testing in the browser.
    path("api/auth/", include("rest_framework.urls")),
]
