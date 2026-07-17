from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.user_dashboard_view, name='user_dashboard'),
    path('company/', views.company_dashboard_view, name='company_dashboard'),
    
    # عدلنا الاسم هنا حتى يطابق القائمة الجانبية
    path('company/store/', views.company_store_view, name='company_store'), 
    path('company/store/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('company/store/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('company/create-bundle/', views.create_bundle_view, name='create_bundle'),
    path('bundle/edit/<int:bundle_id>/', views.edit_bundle_view, name='edit_bundle'),
    path('bundle/delete/<int:bundle_id>/', views.delete_bundle, name='delete_bundle'),
    path('company/installments/', views.installments_view, name='installments'),
    path('add-offline/', views.add_offline_installment, name='add_offline_installment'),
    path('installments/plan/<int:plan_id>/', views.plan_details_view, name='plan_details'),
    path('installments/collect/<int:payment_id>/', views.collect_installment, name='collect_installment'),
    path('installments/delete/<int:plan_id>/', views.delete_plan_view, name='delete_plan'),
    path('bundle/promote/<int:bundle_id>/', views.promote_bundle_view, name='promote_bundle'),
    path('orders/', views.orders_management_view, name='orders_management'),
    path('orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('orders/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('orders/generate-plan/<int:order_id>/', views.generate_installment_plan, name='generate_installment_plan'),
    path('contracts/', views.contracts_management_view, name='contracts_management'),
    path('contracts/add/', views.add_contract_view, name='add_contract'),
    path('contracts/print/<int:contract_id>/', views.print_contract_view, name='print_contract'),
    path('contracts/verify/<int:contract_id>/', views.verify_contract_public, name='verify_contract_public'),
    path('portfolio/', views.manage_portfolio, name='manage_portfolio'),
    path('portfolio/delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('portfolio/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('settings/', views.settings_view, name='settings_view'),
]
