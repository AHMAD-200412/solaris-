"""
URL configuration for SolarLQ project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
import os
from django.conf import settings         
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('simulator.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('user/', include('user_dashboard.urls')),
]
if settings.DEBUG:
    # 1. تشغيل مجلد شعارات الشركات
    urlpatterns += static('/company_logos/', document_root=os.path.join(settings.BASE_DIR, 'company_logos'))
    
    # 2. تشغيل مجلد الرخص التجارية
    urlpatterns += static('/commercial_licenses/', document_root=os.path.join(settings.BASE_DIR, 'commercial_licenses'))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    