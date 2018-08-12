"""myImageTransform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.views.static import serve

from myImageTransform import settings
from myImageResize.views import ResizeImage

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # media resource
    url(r'^media/(?P<path>.*)$', serve,{'document_root':settings.MEDIA_ROOT}),

    # image resize
    url(r'^(?P<transform_params>.*?)/(?P<image_url>.+)', ResizeImage.as_view(), name='resize-image')
]
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)