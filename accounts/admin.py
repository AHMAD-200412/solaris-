from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html  # 🔥 [إضافة فخمة] لعرض البادجات والصور بشكل احترافي
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # 1️⃣ الأعمدة التي ستظهر بالجدول (أضفنا بادج ملوّن لنوع الحساب وصورة الشعار المصغرة)
    list_display = ('username', 'email', 'get_user_type_badge', 'company_name', 'get_logo_thumbnail', 'is_approved', 'is_active', 'is_staff')
    
    # ⚡ [ميزة إنتاجية خارقة]: تتيح لك تفعيل/تجميد الحسابات والموافقة عليها مباشرة من الجدول دون دخول الصفحة!
    list_editable = ('is_approved', 'is_active')
    
    # 2️⃣ الفلاتر الجانبية الذكية
    list_filter = ('user_type', 'is_approved', 'is_active', 'is_staff')
    
    # 3️⃣ حقول البحث السريع المحمية
    search_fields = ('username', 'email', 'company_name', 'phone')
    ordering = ('-date_joined',)

    # 4️⃣ كبسات الإجراءات السريعة (الموافقة والرفض) للشركات
    actions = ['approve_companies', 'reject_companies']

    @admin.action(description='⚡️ الموافقة على طلبات الشركات المحددة وتفعيلها')
    def approve_companies(self, request, queryset):
        companies = queryset.filter(user_type='company')
        updated = companies.update(is_approved=True, is_active=True)
        self.message_user(request, f'تم بنجاح تفعيل والموافقة على ({updated}) شركة.')

    @admin.action(description='❌ تجميد / رفض الشركات المحددة')
    def reject_companies(self, request, queryset):
        companies = queryset.filter(user_type='company')
        updated = companies.update(is_approved=False, is_active=False)
        self.message_user(request, f'تم بنجاح تجميد/رفض ({updated}) شركة.')

    # 🟢 حقول معاينة الصور الكبيرة المخصصة لصفحة التعديل (للقراءة فقط لحمايتها)
    readonly_fields = ('logo_preview_large', 'license_preview_large')

    # 5️⃣ تقسيم الحقول وترتيبها بشكل فخم داخل صفحة تعديل البيانات بالداخل
    fieldsets = UserAdmin.fieldsets + (
        ('⚙️ بيانات منظومة الطاقة الشمسية النصية', {
            'fields': ('user_type', 'is_approved', 'company_name', 'phone', 'address', 'description'),
        }),
        ('🖼️ المستندات وشعارات الشركات (معاينة حية ومباشرة)', {
            'fields': ('logo', 'logo_preview_large', 'commercial_license', 'license_preview_large'),
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('⚙️ بيانات منظومة الطاقة الشمسية المخصصة', {
            'fields': ('user_type', 'is_approved', 'company_name', 'phone', 'address', 'description', 'logo', 'commercial_license'),
        }),
    )

    # ✨ [دالة الفخامة 1]: لتوليد بادج (Badge) ملوّن انسيابي لنوع الحساب في الجدول الرئيسي
    def get_user_type_badge(self, obj):
        if obj.user_type == 'company':
            return format_html('<span style="background-color: #2563eb; color: white; padding: 4px 12px; border-radius: 50px; font-weight: bold; font-size: 11px; display: inline-block;">🏢 شركة</span>')
        return format_html('<span style="background-color: #059669; color: white; padding: 4px 12px; border-radius: 50px; font-weight: bold; font-size: 11px; display: inline-block;">👤 مستخدم</span>')
    get_user_type_badge.short_description = 'نوع الحساب'

    # ✨ [دالة الفخامة 2]: لعرض صورة الشعار بشكل دائري صغير داخل الجدول الرئيسي المجمع
    def get_logo_thumbnail(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="width: 38px; height: 38px; border-radius: 50%; object-fit: cover; border: 2px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);" />', obj.logo.url)
        return format_html('<span style="color: #94a3b8; font-size: 11px; font-style: italic;">لا يوجد</span>')
    get_logo_thumbnail.short_description = 'الشعار'

    # ✨ [دالة الفخامة 3]: لمعاينة الشعار بحجم واضح وكبير داخل صفحة تعديل الحساب بالداخل
    def logo_preview_large(self, obj):
        if obj.logo:
            return format_html('<div style="margin-top: 5px;"><img src="{}" style="max-width: 220px; max-height: 220px; border-radius: 12px; border: 1px solid #cbd5e1; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);"/></div>', obj.logo.url)
        return "لا يوجد أي ملف شعار مرفوع حالياً لهذه الشركة."
    logo_preview_large.short_description = 'المعاينة الحالية للشعار'

    # ✨ [دالة الفخامة 4]: لمعاينة وثيقة الرخصة التجارية بوضوح تام للموافقة السريعة
    def license_preview_large(self, obj):
        if obj.commercial_license:
            return format_html('<div style="margin-top: 5px;"><img src="{}" style="max-width: 380px; max-height: 380px; border-radius: 12px; border: 1px solid #cbd5e1; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);"/></div>', obj.commercial_license.url)
        return "لا يوجد ملف رخصة تجارية مرفوع حالياً."
    license_preview_large.short_description = 'المعاينة الحالية للرخصة'