from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.user_home, name='user_home'),
    path('calculator/', views.solar_calculator, name='solar_calculator'),  
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('assistant/', views.assistant_home, name='assistant_home'),
    path('recmmendation/', views.recmmendation, name='recmmendation'),
    path('best_recmmendation/', views.best_recmmendation, name='best_recmmendation'),
    path("feasibility-study/",views.feasibility_study,name="feasibility_study"),
    path("ai-assistant/",views.assistant,name="assistant"),
    path("assistant/create/",views.create_conversation,name="create_conversation"),
    path("assistant/list/",views.conversation_list,name="conversation_list"), 
    path("assistant/send/",views.send_message,name="send_message"),
    path("assistant/<int:conversation_id>/",views.get_conversation,name="get_conversation"),
    path("assistant/<int:conversation_id>/delete/",views.delete_conversation,name="delete_conversation"),
    path("assistant/<int:conversation_id>/rename/",views.rename_conversation,name="rename_conversation"),
    path("assistant/latest/",views.latest_conversation,name="latest_conversation"),
    path("assistant/search/",views.search_conversations,name="search_conversations"),
    path("assistant/clear/",views.clear_all_conversations,name="clear_all_conversations"),
    path('account-user/', views.account, name='account-user'),  
    path("account/update-name/", views.update_name, name="update_name"),
    path("account/send-email-otp/", views.send_email_otp, name="send_email_otp"),
    path("account/verify-email-otp/", views.verify_email_otp, name="verify_email_otp"),
    path("account/send-phone-otp/", views.send_phone_otp, name="send_phone_otp"),
    path("account/verify-phone-otp/", views.verify_phone_otp, name="verify_phone_otp"),
    path("account/change-password/", views.change_password, name="change_password"),
    path("account/delete/", views.delete_account, name="delete_account"),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('my-orders/delete/<int:order_id>/', views.delete_my_order, name='delete_my_order'),
    path('send-feedback/', views.send_feedback, name='send_feedback'),
    path('faq/', views.faq, name='faq'),
    path('page/<str:page_name>/', views.static_page, name='static_page'),
    path('accept-terms/', views.accept_terms, name='accept_terms'),
    #///////////////////////////////////////////
    path("assistant/<int:conversation_id>/pin/",views.toggle_pin_conversation,name="toggle_pin_conversation"),

       # أكشن إرسال الطلب وإلغائه (Ajax / JsonResponse لحركات سريعة بدون ريفريش)
    path('marketplace/request/<int:bundle_id>/', views.request_bundle_view, name='request_bundle'),
    path('marketplace/cancel/<int:bundle_id>/', views.cancel_bundle_view, name='cancel_bundle'),
   
]