from django.urls import path
from . import views

urlpatterns = [
    path('splash/', views.splash, name='splash'),
    path('', views.home, name='home'),
]