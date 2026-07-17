from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

# ==========================================
# 1️⃣ ملف الشركة (Company Profile) - لإعدادات الشركة
# ==========================================
class CompanyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_profile')
    cover_image = models.ImageField(upload_to='company_covers/', null=True, blank=True, verbose_name="صورة الغلاف")
    about_us = models.TextField(null=True, blank=True, verbose_name="نبذة عن الشركة")
    support_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="رقم هاتف الدعم الفني")
    whatsapp_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="رقم الواتساب (للإشعارات والربط)")
    working_hours = models.CharField(max_length=100, null=True, blank=True, verbose_name="ساعات العمل")
    
    class Meta:
        verbose_name = "ملف الشركة"
        verbose_name_plural = "ملفات الشركات"

    def __str__(self):
        return f"ملف - {self.user.company_name}"


# ==========================================
# 2️⃣ المخزن والقطع الفردية (Inventory)
# ==========================================
class Product(models.Model):
    CATEGORY_CHOICES = [
        ("panel", "لوح شمسي"),
        ("inverter", "انفرتر"),
        ("battery", "بطارية"),
        ("structure", "هياكل"),
        ("accessory", "ملحقات"),
    ]

    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products"
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    name = models.CharField(max_length=255)

    brand = models.CharField(max_length=100)

    model_number = models.CharField(max_length=100, blank=True)

    image = models.ImageField(
        upload_to="products_images/",
        blank=True,
        null=True
    )

    # مواصفات عامة
    power_watt = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    voltage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    current = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    efficiency = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    # البطاريات
    battery_capacity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    battery_type = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    # الانفرتر
    inverter_capacity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    warranty_years = models.PositiveIntegerField(default=1)

    country = models.CharField(
        max_length=100,
        blank=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
#///////////////////////////////////////////////////////////////
class PackageComponent(models.Model):
    package = models.ForeignKey('SolarPackage', on_delete=models.CASCADE, related_name='package_components')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="العدد") # 👈 هذا حقل العدد المهم!

    def str(self):
        return f"{self.quantity} x {self.product.name}"
# ==========================================
# 3️⃣ صانع الباقات والترويج (Solar Packages & Boost)
# ==========================================
class SolarPackage(models.Model):

    QUALITY_CHOICES = [
        ("economic", "اقتصادي"),
        ("standard", "متوسط"),
        ("premium", "ممتاز"),
    ]

    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="packages"
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    quality = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        default="standard"
    )

    package_image = models.ImageField(
        upload_to="packages/",
        default="default/default_package.png"
    )

    # بيانات المنظومة
    inverter_capacity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    battery_capacity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    total_panel_power = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    daily_production = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # الأقساط
    is_installment_available = models.BooleanField(default=False)

    down_payment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    monthly_installment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    duration_months = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    # الترويج
    is_promoted = models.BooleanField(default=False)

    promotion_request = models.BooleanField(default=False)

    promotion_receipt = models.ImageField(
        upload_to="promotion_receipts/",
        null=True,
        blank=True
    )

    promotion_end_date = models.DateTimeField(
        null=True,
        blank=True
    )

    # الإحصائيات
    views_count = models.PositiveIntegerField(default=0)

    orders_count = models.PositiveIntegerField(default=0)

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.00
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [
            "-is_promoted",
            "-rating",
            "-orders_count",
            "-created_at"
        ]

    def __str__(self):
        return self.title

    @property
    def is_promotion_active(self):
        return (
            self.is_promoted
            and self.promotion_end_date
            and timezone.now() <= self.promotion_end_date
        )

    @property
    def formatted_price_iqd(self):
        try:
            price = float(self.total_price)

            if price >= 1000000:
                m = price / 1000000
                return f"{round(m,1)} مليون دينار"

            if price >= 1000:
                k = price / 1000
                return f"{round(k,1)} ألف دينار"

            return f"{int(price)} دينار"

        except:
            return "0 دينار"
    @property
    def formatted_down_payment(self):
      if not self.down_payment:
        return "0 "
      try:
         price = float(self.down_payment)
         if price >= 1000000:
            m = price / 1000000
            return f"{round(m,1)} مليون "
         if price >= 1000:
            k = price / 1000
            return f"{round(k,1)} ألف "
         return f"{int(price)} "
      except:
        return "0 "

    @property
    def formatted_monthly(self):
     if not self.monthly_installment:
        return "0 "
     try:
         price = float(self.monthly_installment)
         if price >= 1000000:
            m = price / 1000000
            return f"{round(m,1)} مليون "
         if price >= 1000:
            k = price / 1000
            return f"{round(k,1)} ألف "
         return f"{int(price)} "
     except:
        return "0 "
# ==========================================
# 4️⃣ إدارة الطلبات والزبائن (Orders & CRM)
# ==========================================
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '🟡 قيد المراجعة والتدقيق الأولي'),
        ('survey', '👨‍🔧 جاري الكشف الموقعي الفني'),
        ('preparing', '🟠 جاري تجهيز المواد والشحن'),
        ('on_way', '🔵 فريق التركيب في الطريق للموقع'),
        ('completed', '🟢 تم التشغيل والتسليم المعتمد'),
        ('canceled', '🔴 ملغي'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'دفع نقدي (كاش) 💵'),
        ('installment', 'نظام الأقساط 💳'),
    ]

    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_orders', verbose_name="الشركة المنفذة")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_orders', verbose_name="الزبون")
    
    # الباقة خليناها blank=True لأن زبون الأوفلاين ممكن يشتري بس بطارية وما يختار باقة
    package = models.ForeignKey('SolarPackage', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الباقة المطلوبة")
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="رقم الهاتف")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="حالة الطلب")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash', verbose_name="طريقة الدفع")
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المبلغ الأساسي للباقة ($)")
    extra_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="مصاريف إضافية بعد الكشف ($)")
    extra_fees_reason = models.TextField(null=True, blank=True, verbose_name="سبب المصاريف الإضافية")
    
    # 🛒 حقول مبيعات الأوفلاين (الجديدة لحل المشكلة)
    is_offline_sale = models.BooleanField(default=False, verbose_name="مبيع أوفلاين (بدون تركيب ميداني)")
    purchased_items = models.CharField(max_length=255, null=True, blank=True, verbose_name="تفاصيل المشتريات المفردة")
    
    # 🛡 الكشف المجاني كعامل جذب تسويقي
    survey_fee_iqd = models.IntegerField(default=0, verbose_name="رسوم الكشف الموقعي (0 = مجاني)")
    is_survey_fee_paid = models.BooleanField(default=True, verbose_name="تمت تسوية الكشف")
    is_customer_approved_fees = models.BooleanField(default=True, verbose_name="موافقة الزبون على الإضافات")

    installation_address = models.TextField(null=True, blank=True, verbose_name="عنوان التركيب بالتفصيل")
    gps_location_url = models.URLField(null=True, blank=True, verbose_name="رابط الموقع (GPS)")
    survey_date = models.DateTimeField(null=True, blank=True, verbose_name="موعد الزيارة")
    
    # 🤖 حقل الذكاء الاصطناعي (يملأ تلقائياً)
    load_calculation = models.TextField(null=True, blank=True, verbose_name="حساب الأحمال والقدرة (AI)")
    
    # 🛠 حقل المهندس (للشركة)
    technical_report = models.TextField(null=True, blank=True, verbose_name="التقرير الهندسي للموقع")
    
    notes = models.TextField(null=True, blank=True, verbose_name="ملاحظات الزبون")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        verbose_name = "طلب زبون"
        verbose_name_plural = "إدارة الطلبات (CRM)"

    def __str__(self): # تم التصحيح هنا
        return f"طلب #{self.id} - {self.customer.first_name} ({self.get_status_display()})"

    @property
    def final_total_amount(self):
        return self.total_amount + self.extra_fees

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # توليد العقد فقط للطلبات الميدانية المكتملة (وليس للأوفلاين)
        if self.status == 'completed' and not self.is_offline_sale and not hasattr(self, 'contract'):
            # تأكد من استدعاء DigitalContract فوق أو كتابة الكود الخاص بها
            pass # مؤقتاً لتجنب الأخطاء إذا DigitalContract مو موجودة بنفس الملف


# ==========================================
# 5️⃣ نظام إدارة الأقساط والتمويل (Installments Tracker)
# ==========================================
class InstallmentPlan(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='installment_plan', verbose_name="الطلب المرتبط")
    down_payment_paid = models.BooleanField(default=False, verbose_name="هل تم دفع المقدمة؟")
    
    total_months = models.PositiveIntegerField(verbose_name="إجمالي أشهر السداد")
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مبلغ القسط الشهري ($)")
    
    is_completed = models.BooleanField(default=False, verbose_name="تم تسديد كافة الأقساط ✅")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "خطة تقسيط"
        verbose_name_plural = "خطط الأقساط والتمويل"

    def __str__(self): # تم التصحيح هنا
        return f"خطة قسط للطلب #{self.order.id} - {self.order.customer.first_name}"


class InstallmentPayment(models.Model):
    PAYMENT_STATUS = [
        ('pending', '⏳ قيد الانتظار'),
        ('paid', '✅ تم الدفع'),
        ('late', '🚨 متأخر'),
    ]

    plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='payments', verbose_name="خطة التقسيط")
    month_number = models.PositiveIntegerField(verbose_name="رقم القسط (الشهر)")
    due_date = models.DateField(verbose_name="تاريخ الاستحقاق")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ المستحق")
    
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='pending', verbose_name="حالة الدفع")
    paid_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الدفع الفعلي")

    class Meta:
        verbose_name = "دفعة قسط"
        verbose_name_plural = "دفعات الأقساط الشهرية"
        ordering = ['due_date'] # ترتيب الدفعات حسب التاريخ تلقائياً

    def __str__(self): # تم التصحيح هنا
        return f"قسط شهر {self.month_number} - {self.plan.order.customer.first_name} - {self.get_status_display()}"
# ==========================================
# 6️⃣ العقود والضمان الرقمي (Digital Warranty & Contracts)
# ==========================================
class DigitalContract(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='contract', verbose_name="الطلب المرتبط")
    panels_serial = models.TextField(blank=True, null=True, verbose_name="سيريالات الألواح")
    panels_warranty = models.IntegerField(default=10)

    # 2. سيريالات البطاريات
    batteries_serial = models.TextField(blank=True, null=True, verbose_name="سيريالات البطاريات")
    batteries_warranty = models.IntegerField(default=1)

    # 3. سيريال العاكس
    inverter_serial = models.CharField(max_length=255, blank=True, null=True, verbose_name="سيريال العاكس")
    inverter_warranty = models.IntegerField(default=1)

    legal_terms = models.TextField()
    
    contract_pdf = models.FileField(upload_to='contracts/pdfs/', null=True, blank=True, verbose_name="ملف العقد (PDF)")
    customer_signature = models.ImageField(upload_to='contracts/signatures/', null=True, blank=True, verbose_name="توقيع الزبون الرقمي")
    
    panel_warranty_years = models.PositiveIntegerField(default=10, verbose_name="ضمان الألواح (سنوات)")
    battery_warranty_years = models.PositiveIntegerField(default=1, verbose_name="ضمان البطاريات (سنوات)")
    inverter_warranty_years = models.PositiveIntegerField(default=1, verbose_name="ضمان العاكس (سنوات)")
    
    terms_and_conditions = models.TextField(verbose_name="الشروط والأحكام القانونية", default="يخضع هذا العقد لشروط وأحكام الصيانة والضمان المحددة من قبل الشركة المنفذة...")
    issued_at = models.DateField(auto_now_add=True, verbose_name="تاريخ إصدار العقد")

    class Meta:
        verbose_name = "عقد وضمان رقمي"
        verbose_name_plural = "العقود والضمانات الرقمية"

    def __str__(self):
      return f"عقد طلب رقم #{self.order.id}  - الزبون: {self.order.customer.first_name}"


# ==========================================
# 7️⃣ معرض المشاريع الحية (Verified Portfolio)
# ==========================================
class CompletedProject(models.Model):
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolio_projects', verbose_name="الشركة المنفذة")
    package_reference = models.ForeignKey(SolarPackage, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الباقة التي تم تركيبها")
    
    title = models.CharField(max_length=255, verbose_name="عنوان المشروع (مثال: تركيب منظومة 10 أمبير في المنصور)")
    description = models.TextField(verbose_name="وصف المشروع")
    
    main_image = models.ImageField(upload_to='portfolio/projects/', verbose_name="صورة المشروع الحية")
    location = models.CharField(max_length=255, verbose_name="موقع التنفيذ (المدينة/المنطقة)")
    
    customer_feedback = models.TextField(null=True, blank=True, verbose_name="رأي وتقييم الزبون")
    completion_date = models.DateField(verbose_name="تاريخ إنجاز المشروع")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مشروع منجز"
        verbose_name_plural = "معرض المشاريع الحية"

    def __str__(self):
        return f"{self.title} - {self.company.company_name}"
#///////////////////////////////////////////////////////////