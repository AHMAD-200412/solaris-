from django.db import models
from django.contrib.auth.models import AbstractUser
from django_resized import ResizedImageField
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'User'),
        ('company', 'Company'),
    )
    accepted_terms = models.BooleanField(default=False, verbose_name="موافق على الشروط")
    
    # قائمة محافظات العراق للفلترة الاحترافية
    GOVERNORATE_CHOICES = (
        ('بغداد', 'بغداد'),
        ('نينوى', 'نينوى'),
        ('البصرة', 'البصرة'),
        ('أربيل', 'أربيل'),
        ('النجف', 'النجف'),
        ('كربلاء', 'كربلاء'),
        ('ذي قار', 'ذي قار'),
        ('بابل', 'بابل'),
        ('السليمانية', 'السليمانية'),
        ('دهوك', 'دهوك'),
        ('كركوك', 'كركوك'),
        ('صلاح الدين', 'صلاح الدين'),
        ('الانبار', 'الانبار'),
        ('ديالى', 'ديالى'),
        ('المثنى', 'المثنى'),
        ('القادسية', 'القادسية'),
        ('واسط', 'واسط'),
        ('ميسان', 'ميسان'),
    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='user'
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    company_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # تحويل المحافظة إلى قائمة منسدلة خيارات لضمان صحة الفلترة مستقبلاً
    governorate = models.CharField(
        max_length=50,
        choices=GOVERNORATE_CHOICES,
        default='بغداد',
        verbose_name="المحافظة"
    )

    # عنوان تفصيلي نصي يكتبه صاحب الشركة (اختياري للشرح)
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="العنوان التفصيلي"
    )

    # الحقل السحري لتخزين إحداثيات الـ GPS (خطوط الطول والعرض) تلقائياً
    gps_coordinates = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="إحداثيات الموقع (GPS)"
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    logo = models.ImageField(ResizedImageField(
        upload_to='company_logos/',
        size=[600, 400],            # أقصى أبعاد (سيتناسب تلقائياً)
        quality=75,                 # جودة ممتازة للويب
        force_format='WEBP', 
     )  
    )
    
    commercial_license = models.ImageField(
        upload_to='commercial_licenses/', 
        size=[600, 400],            # أقصى أبعاد (سيتناسب تلقائياً)
        quality=75,                 # جودة ممتازة للويب
        force_format='WEBP', 
    )
    
    is_approved = models.BooleanField(
        default=False, 
        verbose_name="حالة الموافقة (للشركات)"
    )

    def __str__(self):
        if self.user_type == "company":
           return self.company_name or self.first_name or self.username
        return self.first_name or self.username