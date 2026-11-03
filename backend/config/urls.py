"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from api import seo
from config import frontend

urlpatterns = [
    path('api/', include('api.urls')),
    path('sitemap.xml', seo.sitemap),
    path('robots.txt', seo.robots),
    path('django-admin/', admin.site.urls),  # the website's own admin console lives at /admin
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# On a live server Django also gives out the uploaded photos and the built website (see config/frontend.py). Keep these last.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', frontend.media),
    re_path(r'^(?P<path>.*)$', frontend.website),
]
