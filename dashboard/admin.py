from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.utils.html import format_html
from .models import (CompanyProfile, Product, SolarPackage, Order, 
                     InstallmentPlan, InstallmentPayment, DigitalContract, CompletedProject)

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'support_phone', 'whatsapp_number']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'company', 'price', 'stock']
    list_filter = ['category', 'company']
    search_fields = ['name', 'company__username']

@admin.action(description='✅ موافقة وتفعيل الترويج (لمدة 15 يوم)')
def approve_promotion_15_days(modeladmin, request, queryset):
    updated = queryset.update(
    is_promoted=True,
    promotion_request=False,
    promotion_end_date=timezone.now() + timedelta(days=15)
    )
    modeladmin.message_user(request, f"تم تفعيل الترويج لـ {updated} باقة بنجاح لمدة 15 يوم!", messages.SUCCESS)

@admin.action(description='✅ موافقة وتفعيل الترويج (لمدة 7 أيام)')
def approve_promotion_7_days(modeladmin, request, queryset):
    updated = queryset.update(
    is_promoted=True,
    promotion_request=False,
    promotion_end_date=timezone.now() + timedelta(days=15)
    )
    modeladmin.message_user(request, f"تم تفعيل الترويج لـ {updated} باقة بنجاح لمدة 7 أيام!", messages.SUCCESS)

@admin.action(description='❌ رفض طلب الترويج (وإلغاء الوصل)')
def reject_promotion(modeladmin, request, queryset):
    updated = queryset.update(
    is_promoted=False,
    promotion_request=False,
    promotion_receipt=None,
    promotion_end_date=None
    )
    modeladmin.message_user(request, f"تم رفض طلب الترويج لـ {updated} باقة.", messages.WARNING)

@admin.action(description='🚫 إيقاف الترويج الفعال حالياً')
def stop_active_promotion(modeladmin, request, queryset):
    updated = queryset.update(
        is_promoted=False,
        promotion_end_date=None
    )
    modeladmin.message_user(request, f"تم إيقاف الترويج لـ {updated} باقة.", messages.INFO)

@admin.register(SolarPackage)
class SolarPackageAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_company_name', 'is_promotion_pending_status', 'is_promoted', 'is_active', 'promotion_end_date', 'view_receipt']
    list_filter = ['promotion_request', 'is_promoted', 'is_active']
    list_editable = ['is_promoted', 'is_active']
    actions = [approve_promotion_15_days, approve_promotion_7_days, reject_promotion, stop_active_promotion]
    
    def get_company_name(self, obj):
        # نحاول نجيب اسم الشركة الحقيقي من حقل company_name إذا موجود
        if hasattr(obj.company, 'company_name') and obj.company.company_name:
            return obj.company.company_name
        return obj.company.username
    get_company_name.short_description = 'اسم الشركة'

    def is_promotion_pending_status(self, obj):
      if obj.promotion_request:
          return format_html(
            '<span style="color:red;font-weight:bold;">⏳ بانتظار الموافقة</span>'
          )
      return format_html(
        '<span style="color:green;">✔️ لا توجد طلبات</span>'
      )

    def view_receipt(self, obj):
        if obj.promotion_receipt:
            return format_html('<a href="{}" target="_blank" style="background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 4px; text-decoration: none;">🖼️ عرض الوصل</a>', obj.promotion_receipt.url)
        return "-"
    view_receipt.short_description = 'وصل الدفع'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'company', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_method']

@admin.register(CompletedProject)
class CompletedProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'completion_date']
    
admin.site.register(InstallmentPlan)
admin.site.register(InstallmentPayment)
admin.site.register(DigitalContract)