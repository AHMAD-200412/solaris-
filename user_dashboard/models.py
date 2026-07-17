from django.db import models
from django.conf import settings
from dashboard.models import SolarPackage 
# 1. جدول حاسبة الأحمال المحفوظة (Saved Calculator)
class SavedCalculator(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_calculators')
    title = models.CharField(max_length=100, verbose_name="اسم الحسبة (مثلاً: بيتي، المحل، المزرعة)")
    
    # التعديل الهندسي الجديد ⚡️
    total_kwh_day = models.FloatField(default=0.0, verbose_name="إجمالي الاستهلاك اليومي (كيلوواط/ساعة)")
    max_surge_watts = models.IntegerField(default=0, verbose_name="أعلى لود إقلاع لحظي (واط)")
    
    appliances_data = models.JSONField(verbose_name="تفاصيل الأجهزة", help_text="يحفظ الأجهزة بصيغة JSON")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"
#//////////////////////////////////////////////////////////////////
# 2. جدول المفضلة (Wishlist)
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    # ملاحظة: ربطناه باسم التطبيق والموديل مالت الإعلانات اللي راح نسويه بعدين بالشركات
    package = models.ForeignKey(SolarPackage,on_delete=models.CASCADE,related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
       return f"{self.user.username} - {self.package.title}"


# 3. جدول طلبات الخدمات (Service Request)
class ServiceRequest(models.Model):
    SERVICE_TYPES = (
        ('inspection', 'كشف موقعي'),
        ('maintenance', 'صيانة أعطال'),
        ('washing', 'تنظيف ألواح'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('accepted', 'تم القبول'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغى'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests')
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests', limit_choices_to={'user_type': 'company'})
    
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name="نوع الخدمة")
    details = models.TextField(blank=True, null=True, verbose_name="تفاصيل المشكلة أو الطلب")
    location_details = models.CharField(max_length=255, verbose_name="العنوان بالتفصيل (أو القرية)")
    preferred_date = models.DateField(blank=True, null=True, verbose_name="التاريخ المفضل للزيارة")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="حالة الطلب")
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

    package = models.ForeignKey(SolarPackage,on_delete=models.SET_NULL,null=True,blank=True)

    def str(self):
        return f"طلب {self.get_service_type_display()} من {self.user.username}"

# 5. جدول التقييمات (Reviews)
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_reviews', limit_choices_to={'user_type': 'company'})
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="التقييم (1-5 نجوم)")
    comment = models.TextField(blank=True, null=True, verbose_name="التعليق")
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"تقييم {self.rating} نجوم من {self.user.username} لشركة {self.company.company_name}"


# 6. جدول مقالات شمس الموصل (Solar Article - Wiki)
class SolarArticle(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان المقال أو النصيحة")
    content = models.TextField(verbose_name="المحتوى")
    image = models.ImageField(upload_to='wiki_images/', blank=True, null=True, verbose_name="صورة توضيحية")
    is_published = models.BooleanField(default=True, verbose_name="منشور؟")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
#//////////////////////////////////////////////////////////////
from django.db import models
from django.conf import settings
from django.utils import timezone


class AIConversation(models.Model):
    """
    محادثة الذكاء الاصطناعي
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_conversations"
    )

    title = models.CharField(
        max_length=255,
        default="محادثة جديدة"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(default=timezone.now)

    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "محادثة الذكاء الاصطناعي"
        verbose_name_plural = "محادثات الذكاء الاصطناعي"
        ordering = ["-is_pinned", "-last_message_at"]

    def str(self):
        return f"{self.user} - {self.title}"


class AIMessage(models.Model):
    """
    رسائل الذكاء الاصطناعي
    """
    ROLE_CHOICES = (
        ("user", "المستخدم"),
        ("assistant", "الذكاء الاصطناعي"),
        ("system", "النظام"),
    )

    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "رسالة"
        verbose_name_plural = "الرسائل"
        ordering = ["created_at"]

    def str(self):
        return f"{self.role} | {self.created_at:%Y-%m-%d %H:%M}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # تحديث آخر نشاط للمحادثة تلقائياً
        self.conversation.last_message_at = self.created_at
        self.conversation.save(update_fields=["last_message_at"])
#/////////////////////////////////////////
class Feedback(models.Model):
    FEEDBACK_TYPES = (
        ('complaint', 'شكوى'),
        ('suggestion', 'اقتراح'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def str(self):
        return f"{self.get_feedback_type_display()} من {self.user.username}"