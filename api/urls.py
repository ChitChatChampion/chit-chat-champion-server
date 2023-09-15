"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings

# namespace: used when you want to reverse()
urlpatterns = [
    path("admin/", admin.site.urls),
    # user.urls == look at user then the urls directory under user
    path("api/v1/user/", include("user.urls")),
    # path("api/v1/", include("translation.urls")),
    path("api/v1/", include("translation.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# makes media url available in our dev server, so we can test
# uploading images for our translation, without having to set up a
# separate web server for serving these media files

# django doesn't serve media files by default
# so need to manually add these in the urls.py
