from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import requests
from dashboard.models import InstallmentPlan # استيراد الموديل المستقر

class Command(BaseCommand):
    help = 'إرسال تذكيرات الأقساط للزبائن وتنبيهات تفصيلية للمدراء تلقائياً غداً عبر الواتساب'

    def handle(self, *args, **options):
        # 1. حساب تاريخ يوم غد بدقة لمعرفة المستحقين
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        # 2. جلب الأقساط غير المكتملة
        active_installments = InstallmentPlan.objects.filter(is_completed=False) #
        
        # 3. بيانات بوابة Whapi المستقرة مالتك
        whatsapp_api_url = "https://gate.whapi.cloud/messages/text"
        api_token = "3IKKgla24ae0lXOwMdGav8NZBS6EPOrR"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }

        sent_customers = 0
        sent_managers = 0

        for installment in active_installments:
            # 4. الحسبة التلقائية للأيام ومضاعفات الـ 30 يوماً
            created_date = installment.created_at.date() #
            days_diff = (tomorrow - created_date).days
            
            if days_diff > 0 and days_diff % 30 == 0:
                current_month_number = int(days_diff / 30)
                
                customer_phone = None
                customer_name = "زبون محترم"
                company_name = None
                manager_phone = None

                if installment.order: #
                    order_obj = installment.order #
                    
                    # أ- جلب بيانات الزبون ديناميكياً
                    customer_phone = getattr(order_obj, 'customer_phone', None) or getattr(order_obj, 'phone', None)
                    if hasattr(order_obj, 'customer_name') and order_obj.customer_name:
                        customer_name = order_obj.customer_name

                    # ب- جلب اسم ورقم هاتف المدير (الشركة) الحقيقي المسجل بالسيستم
                    if hasattr(order_obj, 'company') and order_obj.company:
                        company_name = getattr(order_obj.company, 'name', None) or getattr(order_obj.company, 'company_name', None)
                        manager_phone = getattr(order_obj.company, 'phone', None)
                    
                    # ج- إذا كان منشئ الطلب هو حساب الشركة نفسه (fallback)
                    if not company_name and hasattr(order_obj, 'user') and order_obj.user:
                        if getattr(order_obj.user, 'user_type', None) == 'company':
                            company_name = order_obj.user.get_full_name() or order_obj.user.username
                            manager_phone = getattr(order_obj.user, 'phone', None) #

                # تخطي القسط إذا لم يرتبط بشركة (لأننا لا نعرف من المدير ومن صاحب القسط)
                if not company_name:
                    continue

                amount = installment.monthly_amount #

                # 5. تنظيف وتصحيح رقم هاتف الزبون للصيغة الدولية
                if customer_phone and customer_phone != '-':
                    c_phone_str = str(customer_phone).strip().replace(" ", "").replace("+", "")
                    if c_phone_str.startswith("0"):
                        c_phone_str = "964" + c_phone_str[1:]
                    elif not c_phone_str.startswith("964"):
                        c_phone_str = "964" + c_phone_str
                    
                    customer_recipient = f"{c_phone_str}@s.whatsapp.net"
                    
                    # ✉️ صياغة رسالة الزبون اللطيفة والمريحة
                    customer_message = (
                        f"السلام عليكم ورحمة الله وبركاته،\n"
                        f"عزيزنا الأخ/الأخت *{customer_name}* المحترم،🌻\n\n"f"نود إحاطتكم علماً من (*شركة {company_name} للطاقة الشمسية*) "
                        f"بأن موعد استحقاق قسطكم الشهري المترتب عليكم (الشهر رقم {current_month_number}) هو يوم غدٍ بإذن الله.\n\n"
                        f"💵 *المبلغ المستحق:* {amount:,} د.ع\n\n"
                        f"شاكرين لكم جداً التزامكم وحرصكم الدائم.. طاب يومكم بكل خير وبركة! ☀️✨"
                    )

                    # إرسال للزبون
                    try:
                        res_c = requests.post(whatsapp_api_url, json={"to": customer_recipient, "body": customer_message}, headers=headers, timeout=25)
                        if res_c.status_code in [200, 201]:
                            sent_customers += 1
                    except requests.exceptions.RequestException as e:
                        self.stderr.write(f"فشل إرسال رسالة الزبون: {e}")

                # 6. 👔 صياغة وإرسال رسالة التقرير للمدير (إذا توفر رقم هاتف الشركة)
                if manager_phone and manager_phone != '-':
                    m_phone_str = str(manager_phone).strip().replace(" ", "").replace("+", "")
                    if m_phone_str.startswith("0"):
                        m_phone_str = "964" + m_phone_str[1:]
                    elif not m_phone_str.startswith("964"):
                        m_phone_str = "964" + m_phone_str
                    
                    manager_recipient = f"{m_phone_str}@s.whatsapp.net"

                    # ✉️ رسالة المدير الإدارية المفصلة والواضحة
                    manager_message = (
                        f"🔔 *إشعار نظام الأقساط التلقائي* 🔔\n\n"
                        f"مرحباً بحضرة المدير، نود إعلامكم بأن هناك قسطاً مستحقاً يوم غدٍ تابع لشركتكم:\n\n"
                        f"👤 *اسم الزبون الكامل:* {customer_name}\n"
                        f"📱 *رقم موبايل الزبون:* {customer_phone}\n"
                        f"📅 *القسط المستحق:* (الشهر رقم {current_month_number})\n"
                        f"💵 *مبلغ القسط:* {amount:,} د.ع\n\n"
                        f"النظام قام بإرسال رسالة تذكيرية للزبون تلقائياً لمتابعة الدفع. تحياتنا لك المستمرة بالنجاح! 💼📈"
                    )

                    # إرسال للمدير
                    try:
                        res_m = requests.post(whatsapp_api_url, json={"to": manager_recipient, "body": manager_message}, headers=headers, timeout=25)
                        if res_m.status_code in [200, 201]:
                            sent_managers += 1
                    except requests.exceptions.RequestException as e:
                        self.stderr.write(f"فشل إرسال تنبيه المدير: {e}")

        self.stdout.write(self.style.SUCCESS(
            f'⚙️ اكتمل الفحص النهائي! الرسائل المرسلة للزبائن: {sent_customers} | التنبيهات المرسلة للمدراء: {sent_managers}'
        ))