from django.urls import path

from . import views


urlpatterns = [

    path(

        'register/user/',

        views.register_user,

        name='register_user'
    ),

    path(

        'register/company/',

        views.register_company,

        name='register_company'
    ),
    path('verify-otp/', views.verify_otp, name='verify_otp'), 
    path('check-status/<int:user_id>/', views.check_status, name='check_status'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('choose-account-type/', views.choose_account_type, name='choose_account_type'),
]