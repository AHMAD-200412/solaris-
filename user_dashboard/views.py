import json
from django.shortcuts import render , get_object_or_404,redirect
from django.http import JsonResponse,HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from groq import Groq
from django.utils import timezone
from django.db.models import Q
from dashboard.models import SolarPackage, Order, CompanyProfile 
from django.views.decorators.http import require_POST
from .ai import ask_ai
# استدعاء الموديلات مالتنا
from .models import  SavedCalculator 
from django.contrib.auth import get_user_model
from .models import SolarArticle 

User = get_user_model()

def budget_step_to_text(step_value):
    mapping = {"1": "حوالي 2,000,000 دينار", "2": "حوالي 4,000,000 دينار", "3": "حوالي 6,000,000 دينار", "4": "حوالي 8,000,000 دينار", "5": "10,000,000+ دينار"}
    return mapping.get(str(step_value), "غير محدد")


# =====================================================================
# 🏠 المحطة 1: الصفحة الرئيسية للمستخدم (user_home)
# =====================================================================
@login_required(login_url='accounts/login/')
def user_home(request):
    all_tips = SolarArticle.objects.filter(is_published=True).order_by('-created_at')
    context = {'tips': all_tips}
    return render(request, 'user_dashboard/home.html', context)
# =====================================================================
# 🔢 حاسبة الطاقة (solar_calculator) - دالتك الأصلية بدون أي تغيير
# =====================================================================
@login_required(login_url='accounts/login/')
def solar_calculator(request): 
    calc_instance, created = SavedCalculator.objects.get_or_create(
        user=request.user,
        title="الحسبة الرئيسية",
        defaults={'appliances_data': []}  
    )

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            calc_instance.total_kwh_day = data.get('total_kwh_day', 0.0)
            calc_instance.max_surge_watts = data.get('max_surge_watts', 0)
            calc_instance.appliances_data = data.get('devices', []) 
            calc_instance.save()
            
            return JsonResponse({'status': 'success', 'message': 'تم الحفظ بنجاح'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    saved_devices = calc_instance.appliances_data if calc_instance.appliances_data else []
    
    context = {
        'saved_devices_json': json.dumps(saved_devices) 
    }
    return render(request, 'user_dashboard/calculator.html', context)
#//////////////////////////////////////////////////////////////////////
@login_required(login_url='/accounts/login/')
def marketplace_view(request):
    if request.user.user_type != 'user':
        return render(request, 'errors/403.html', status=403)

    import urllib.parse
    from django.db.models import Exists, OuterRef, Q
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    user_orders = Order.objects.filter(
        customer=request.user,
        package=OuterRef('pk'),
        status='pending'
    )

    # جلب الباقات (بدون list حتى تشتغل الفلاتر)
    packages = SolarPackage.objects.filter(
    is_active=True
    ).select_related(
    'company'
    ).prefetch_related(
    'package_components__product'
    ).annotate(
    is_requested=Exists(user_orders)
    ).order_by('-created_at')

    # ==========================
    # الفلاتر
    # ==========================

    amp_filter = request.GET.get('amp')
    is_installment = request.GET.get('is_installment')

    if amp_filter:
        if amp_filter == '20':
            packages = packages.filter(
                Q(title__icontains="20") |
                Q(title__icontains="25") |
                Q(title__icontains="30") |
                Q(title__icontains="40") |
                Q(title__icontains="50")
            )
        else:
            packages = packages.filter(
                Q(title__icontains=f"{amp_filter} امبير") |
                Q(title__icontains=f"{amp_filter}امبير") |
                Q(title__icontains=f"{amp_filter} أمبير") |
                Q(title__icontains=f"{amp_filter}أمبير") |
                Q(title__icontains=f"{amp_filter}A") |
                Q(title__icontains=f"{amp_filter} A")
            )

    if is_installment == 'true':
       packages = packages.filter(is_installment_available=True)
       

    # ==========================
    # تقسيم الباقات بعد الفلترة
    # ==========================

    featured_packages = list(
        packages.filter(is_promoted=True)
    )

    show_featured = len(featured_packages) > 0

    # إزالة المميزة من الباقات العادية
    packages = list(
        packages.exclude(is_promoted=True)
    )

    # ==========================
    # تجهيز روابط الواتساب
    # ==========================

    all_packages = featured_packages + packages

    for package in all_packages:

        company_profile = CompanyProfile.objects.filter(
            user=package.company
        ).first()

        if company_profile and company_profile.whatsapp_number:

            company_name = (
                package.company.company_name
                if hasattr(package.company, 'company_name')
                else package.company
            )

            msg = (
                f"مرحباً شركة {company_name}، "
                f"أنا الزبون {request.user.get_full_name()}، "
                f"مهتم بالباقة {package.title}"
            )

            encoded_msg = urllib.parse.quote(msg)

            clean_number = str(
                company_profile.whatsapp_number
            ).replace('+', '').replace(' ', '')

            package.whatsapp_link = (
                f"https://api.whatsapp.com/send?phone={clean_number}&text={encoded_msg}"
            )

        else:
            package.whatsapp_link = "#"
    return render(request, 'user_dashboard/marketplace.html', {
        'packages': packages,
        'featured_packages': featured_packages,
        'show_featured': show_featured,
    })


@login_required
def request_bundle_view(request, bundle_id):
    if request.method == "POST":
        package = get_object_or_404(SolarPackage, id=bundle_id)
        
        # 1. فحص كوتا الـ 5 طلبات باليوم للزبون ⏳
        today = timezone.now().date()
        orders_count_today = Order.objects.filter(customer=request.user, created_at__date=today).count()
        if orders_count_today >= 5:
            return JsonResponse({
                'status': 'error', 
                'message': 'لقد تجاوزت الحد الأقصى المسموح به للطلبات اليوم (5 طلبات في اليوم). يرجى المحاولة غداً!'
            })
            
        # 2. فحص إذا العرض مطلوب سابقاً ومعلق لمنع التكرار
        already_exists = Order.objects.filter(customer=request.user, package=package, status='pending').exists()
        if already_exists:
            return JsonResponse({'status': 'error', 'message': 'لقد قمت بطلب هذا العرض بالفعل وهو قيد المراجعة.'})
    
        # 3. جلب آخر حاسبة أحمال محفوظة للزبون وربط تقرير الـ AI ⚡️
        # 3. جلب آخر حاسبة أحمال محفوظة للزبون وربط تقرير الـ AI ⚡️
        latest_calc = SavedCalculator.objects.filter(user=request.user).order_by('-created_at').first()
        
        ai_report_text = "لا يوجد تقرير أحمال محفوظ لهذا المستخدم."
        
        if latest_calc:
            if hasattr(latest_calc, 'ai_response') and latest_calc.ai_response:
                ai_report_text = latest_calc.ai_response
            elif hasattr(latest_calc, 'appliances_data') and latest_calc.appliances_data:
                raw_data = latest_calc.appliances_data
                parsed_data = raw_data
                
                # محاولة آمنة 100% لتنظيف النص بدون ما يضرب السيرفر
                # 2. الترتيب النهائي (بناء جدول HTML عصري ومرتب)
                if isinstance(parsed_data, list):
                    # تصميم الجدول مع ألوان وترتيب
                    pretty_text = """
                    <div style="margin-top: 15px; overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; text-align: center; font-family: 'Cairo', sans-serif; min-width: 500px;">
                            <thead style="background-color: #38c172; color: white;">
                                <tr>
                                    <th style="padding: 10px; border: 1px solid #ddd;">#</th>
                                    <th style="padding: 10px; border: 1px solid #ddd;">اسم الجهاز</th>
                                    <th style="padding: 10px; border: 1px solid #ddd;">العدد</th>
                                    <th style="padding: 10px; border: 1px solid #ddd;">السحب (أمبير)</th>
                                    <th style="padding: 10px; border: 1px solid #ddd;">ساعات التشغيل</th>
                                </tr>
                            </thead>
                            <tbody>
                    """
                    for idx, item in enumerate(parsed_data, 1):
                        if isinstance(item, dict):
                            name = item.get('name', 'جهاز')
                            qty = item.get('qty', 1)
                            amp = item.get('amp', 0)
                            hours = item.get('hours', 0)
                            
                            # إضافة صف لكل جهاز (تناوب الألوان)
                            bg_color = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
                            pretty_text += f"""
                                <tr style="background-color: {bg_color};">
                                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">{idx}</td>
                                    <td style="padding: 8px; border: 1px solid #ddd; color: #333; font-weight: bold;">{name}</td>
                                    <td style="padding: 8px; border: 1px solid #ddd;">{qty}</td>
                                    <td style="padding: 8px; border: 1px solid #ddd;">{amp}</td>
                                    <td style="padding: 8px; border: 1px solid #ddd;">{hours}</td>
                                </tr>
                            """
                        else:
                            pretty_text += f"<tr><td colspan='5' style='padding: 8px; border: 1px solid #ddd;'>{str(item)}</td></tr>"
                    
                    pretty_text += """
                            </tbody>
                        </table>
                    </div>
                    """
                    ai_report_text = pretty_text
                else:
                    ai_report_text = f"تفاصيل الأحمال:<br>{str(parsed_data)}"
        # 4. استلام بيانات الموقع من الـ JavaScript
        gps_link = ''
        address_text = ''
        try:
            body_data = json.loads(request.body)
            gps_link = body_data.get('gps_link', '')
            address_text = body_data.get('address_text', '')
        except:
            pass

        # 5. إنشاء الطلب الجديد مع حفظ رقم الهاتف والموقع الجغرافي
        new_order = Order.objects.create(
                    customer_id=request.user.id,
                    company_id=package.company.id,
                    package_id=package.id,
                    status='pending',

                        # 👇 هذا السطر هو الحل
                    payment_method='installment' if package.is_installment_available else 'cash',

                    total_amount=package.total_price,
                    load_calculation=ai_report_text,
                    notes=f"طلب تلقائي لباقة: {package.title}",
                    phone_number=request.user.phone,
                    gps_location_url=gps_link,
                    installation_address=address_text,
        )
        return JsonResponse({'status': 'success', 'message': 'تم إرسال طلبك وحساب أحمال الـ AI بنجاح إلى الشركة!'})
    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})


@login_required
def cancel_bundle_view(request, bundle_id):
    if request.method == "POST":
        package = get_object_or_404(SolarPackage, id=bundle_id)
        
        # إلغاء الطلب المعلق ليعود كارت الباقة لوضعه الطبيعي
        order = Order.objects.filter(customer=request.user, package=package, status='pending').first()
        if order:
            order.delete()
            return JsonResponse({'status': 'success', 'message': 'تم إلغاء الطلب بنجاح وعاد العرض قابلاً للشراء.'})
        return JsonResponse({'status': 'error', 'message': 'لم يتم العثور على طلب معلق لهذا العرض.'})
    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})
#/////////////////////////////////////////////////////////////////////////////
@login_required(login_url='/accounts/login/')
def ai_assistant_home(request):
    if request.user.user_type != 'user':
        return HttpResponseForbidden("هذه الصفحة مخصصة للمستخدمين فقط.")

    return render(request, 'user_dashboard/assistant.html')
#///////////////////////////////////////////////////////////////////
@login_required(login_url='accounts/login/')
def assistant_home(request):
    return render(request, "user_dashboard/assistant.html")
#////////////////////////////////////////////////////////////////////
@login_required(login_url='accounts/login/')
def recmmendation(request):

    calculator = SavedCalculator.objects.filter(user=request.user).last()

    if calculator:
        context = {
            "total_kwh": calculator.total_kwh_day,
            "max_surge": calculator.max_surge_watts,
            "device_count": len(calculator.appliances_data or []),
            "devices": calculator.appliances_data or [],
        }
    else:
        context = {
            "total_kwh": 0,
            "max_surge": 0,
            "device_count": 0,
            "devices": [],
        }
    return render(
        request,
        "user_dashboard/recmmendation.html",
        context
    )
#//////////////////////////////////////////////////////////////////////

from dashboard.views import extract_power_kw   # <-- استيراد الدالة الاحتياطية
import urllib.parse
from decimal import Decimal
from django.utils import timezone

@login_required(login_url='accounts/login/')
def best_recmmendation(request):
    calculator = SavedCalculator.objects.filter(user=request.user).last()
    if not calculator or calculator.total_kwh_day <= 0:
        context = {
            'error_message': 'لا توجد بيانات كافية من الحاسبة. يرجى استخدام حاسبة الأحمال أولاً.',
            'devices': [],
            'total_kwh': 0,
            'max_surge': 0,
            'mode': None,
            'recommended_packages': [],
            'user_consumption': 0,
        }
        return render(request, 'user_dashboard/best_recmmendation.html', context)

    mode = request.GET.get('mode', 'economic')
    consumption = Decimal(str(calculator.total_kwh_day))

    if mode == 'economic':
        min_prod = consumption
    elif mode == 'balanced':
        min_prod = consumption * Decimal('1.1')
    elif mode == 'performance':
        min_prod = consumption * Decimal('1.3')
    else:
        min_prod = consumption

    packages = SolarPackage.objects.filter(
        is_active=True,
        daily_production__gte=min_prod
    ).select_related('company').prefetch_related('package_components__product')

    now = timezone.now()
    promoted, normal = [], []
    for pkg in packages:
        if pkg.is_promotion_active and pkg.promotion_end_date and now <= pkg.promotion_end_date:
            promoted.append(pkg)
        else:
            normal.append(pkg)

    promoted.sort(key=lambda x: x.total_price)
    normal.sort(key=lambda x: x.total_price)

    final_packages = promoted[:3]
    if len(final_packages) < 3:
        final_packages += normal[:3 - len(final_packages)]

    for pkg in final_packages:
        surplus = pkg.daily_production - consumption
        pkg.surplus = round(float(surplus), 2)

        # ---- حساب عدد الألواح وقدرة اللوح ----
        panel_count = 0
        panel_watt = 0
        for comp in pkg.package_components.all():
            product = comp.product
            # توسيع الكشف ليشمل أي منتج له علاقة بالألواح
            is_panel = (
                product.category == 'panel' or
                'لوح' in product.name or
                'panel' in product.name.lower() or
                (product.power_watt and product.power_watt > 0)
            )
            if is_panel:
                panel_count += comp.quantity
                if panel_watt == 0:  # نأخذ قدرة أول منتج فقط
                    if product.power_watt and product.power_watt > 0:
                        panel_watt = int(product.power_watt)
                    else:
                        # خطة احتياطية: استخراج الواط من الاسم
                        kw = extract_power_kw(product)
                        if kw > 0:
                            panel_watt = int(kw * 1000)
        pkg.panel_count = panel_count
        pkg.panel_watt = panel_watt

        # للتشخيص المؤقت (احذفها لاحقاً)
        print(f"باقة {pkg.title}: عدد الألواح = {panel_count}, قدرة اللوح = {panel_watt}W")

        # رابط الواتساب
        try:
            profile = CompanyProfile.objects.get(user=pkg.company)
            if profile.whatsapp_number:
                clean = profile.whatsapp_number.replace('+', '').replace(' ', '')
                msg = f"مرحباً {pkg.company.company_name}، أنا {request.user.get_full_name()} مهتم بالباقة {pkg.title}"
                pkg.whatsapp_link = f"https://wa.me/{clean}?text={urllib.parse.quote(msg)}"
            else:
                pkg.whatsapp_link = "#"
        except:
            pkg.whatsapp_link = "#"

    context = {
        'mode': mode,
        'mode_label': {'economic': 'اقتصادي', 'balanced': 'متوازن', 'performance': 'أعلى أداء'}.get(mode, ''),
        'user_consumption': round(float(consumption), 2),
        'total_kwh': round(float(consumption), 2),'max_surge': calculator.max_surge_watts,
        'device_count': len(calculator.appliances_data or []),
        'devices': calculator.appliances_data or [],
        'recommended_packages': final_packages,
        'no_results': len(final_packages) == 0,
    }
    return render(request, 'user_dashboard/best_recmmendation.html', context)
#////////////////////////////////////////////////////////////////////////
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

@login_required(login_url='accounts/login/')
def feasibility_study(request):
    package_id = request.GET.get("package_id")

    package = None
    calculator = SavedCalculator.objects.filter(
        user=request.user
    ).order_by("-id").first()

    context = {
        "package": None,
        "package_price": 0,

        # بيانات المنظومة
        "daily_production": 0,
        "total_panel_power": 0,
        "inverter_capacity": 0,
        "battery_capacity": 0,

        # بيانات المستخدم
        "user_daily_consumption": 0,

        # ثوابت الدراسة
        "system_loss_factor": 0.80,
        "peak_sun_hours": 5.5,
        "system_lifetime": 25,
        "maintenance_rate": 0.01,
    }

    # آخر استهلاك للمستخدم
    if calculator:
        context["user_daily_consumption"] = float(
            calculator.total_kwh_day or 0
        )

    if package_id:
        package = get_object_or_404(
            SolarPackage,
            id=package_id,
            is_active=True
        )

        context.update({
            "package": package,
            "package_price": float(package.total_price or 0),
            "daily_production": float(package.daily_production or 0),
            "total_panel_power": float(package.total_panel_power or 0),
            "inverter_capacity": float(package.inverter_capacity or 0),
            "battery_capacity": float(package.battery_capacity or 0),
        })
    print(package.id)
    print(package.title)
    print(package.total_price)
    print(request.GET.get("package_id"))
    return render(
        request,
        "user_dashboard/feasibility_study.html",
        context
    )
#///////////////////////////////////////////////////////////////////////
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth import authenticate, logout

from .models import AIConversation, AIMessage
from .ai import ask_ai

# ----------------------------------------------
# دالة مساعدة للتحقق من أن المستخدم "user" فقط
# ----------------------------------------------
def user_required(view_func):
    decorated_view = login_required(login_url='accounts/login/')(
        user_passes_test(lambda u: u.user_type == 'user', login_url='/403/')(view_func)
    )
    return decorated_view

# ----------------------------------------------
# صفحة المساعد الرئيسية
# ----------------------------------------------
@user_required
def assistant(request):
    conversations = AIConversation.objects.filter(
        user=request.user,
        is_deleted=False
    ).annotate(
        msg_count=Count('messages')
    ).order_by('-is_pinned', '-last_message_at')

    active_conversation = conversations.first()
    messages = []
    if active_conversation:
        messages = AIMessage.objects.filter(
            conversation=active_conversation
        ).order_by('created_at')[:50]  # حد أقصى 50 رسالة أولية

    return render(request, 'user_dashboard/ai_assistant_chat.html', {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'messages': messages
    })

# ----------------------------------------------
# إنشاء محادثة جديدة
# ----------------------------------------------
@user_required
@require_POST
def create_conversation(request):
    conversation = AIConversation.objects.create(
        user=request.user,
        title="محادثة جديدة"
    )
    return JsonResponse({
        "success": True,
        "conversation_id": conversation.id,
        "title": conversation.title
    })

# ----------------------------------------------
# قائمة المحادثات الجانبية (بدون تكرار N+1)
# ----------------------------------------------
@user_required
def conversation_list(request):
    conversations = AIConversation.objects.filter(
        user=request.user,
        is_deleted=False
    ).annotate(
        msg_count=Count('messages')
    ).order_by('-is_pinned', '-last_message_at')

    data = []
    for conv in conversations:
        # تحويل الوقت إلى 12 ساعة مع AM/PM
        last_msg_time = conv.last_message_at
        hour = last_msg_time.hour
        minute = last_msg_time.minute
        ampm = "AM" if hour < 12 else "PM"
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12
        formatted_time = f"{hour_12}:{minute:02d} {ampm}"
        

        data.append({
            "id": conv.id,
            "title": conv.title,
            "updated_at": conv.last_message_at.isoformat(),
            "is_pinned": conv.is_pinned,
            "message_count": conv.msg_count
        })
    return JsonResponse({"success": True, "conversations": data})
# ----------------------------------------------
# إرسال رسالة
# ----------------------------------------------
@user_required
@require_POST
def send_message(request):
    try:
        conversation_id = request.POST.get("conversation_id")
        message = request.POST.get("message", "").strip()

        if not message:
            return JsonResponse({"success": False, "reply": "الرسالة فارغة."})

        # إنشاء محادثة جديدة فقط إذا لم توجد والرسالة غير فارغة
        if conversation_id:
            conversation = get_object_or_404(
                AIConversation,
                id=conversation_id,
                user=request.user,
                is_deleted=False
            )
        else:
            conversation = AIConversation.objects.create(
                user=request.user,
                title="محادثة جديدة"
            )

        # بناء تاريخ المحادثة (آخر 20 رسالة فقط)
        old_messages = AIMessage.objects.filter(
            conversation=conversation
        ).order_by('created_at')[:20]
        history = [{"role": m.role, "content": m.content} for m in old_messages]

        # حفظ رسالة المستخدم
        user_message = AIMessage.objects.create(
            conversation=conversation,
            role="user",
            content=message
        )
        # الاتصال بالذكاء الاصطناعي
        result = ask_ai(message=message, history=history)
        if not result["success"]:
            return JsonResponse(result)

        # حفظ الرد
        ai_message = AIMessage.objects.create(
            conversation=conversation,
            role="assistant",
            content=result["reply"]
        )

        # تحديث العنوان إذا كان جديدًا
        if conversation.title == "محادثة جديدة":
            title = " ".join(message.strip().split()[:6])
            if len(title) > 60:
                title = title[:60]
            # منع تكرار العنوان
            original = title
            number = 2
            while AIConversation.objects.filter(user=request.user, title=title, is_deleted=False).exists():
                title = f"{original} ({number})"
                number += 1
            conversation.title = title
            conversation.save(update_fields=["title"])

        return JsonResponse({
            "success": True,
            "conversation_id": conversation.id,
            "title": conversation.title,
            "reply": ai_message.content,
            "user_message": {
                "id": user_message.id,
                "role": user_message.role,
                "content": user_message.content,
                "created_at": user_message.created_at.isoformat(),
            },
            "assistant_message": {
                "id": ai_message.id,
                "role": ai_message.role,
                "content": ai_message.content,
                "created_at": ai_message.created_at.isoformat()
            }
        })

    except Exception as e:
        print(e)
        return JsonResponse({"success": False, "reply": "حدث خطأ أثناء معالجة الرسالة."})

# ----------------------------------------------
# فتح محادثة (جلب 50 رسالة كحد أقصى)
# ----------------------------------------------
@user_required
def get_conversation(request, conversation_id):
    conversation = get_object_or_404(
        AIConversation,
        id=conversation_id,
        user=request.user,
        is_deleted=False
    )

    messages = AIMessage.objects.filter(
        conversation=conversation
    ).order_by('created_at')[:50]

    data = []
    for msg in messages:
        data.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        })

    return JsonResponse({
        "success": True,
        "conversation": {"id": conversation.id, "title": conversation.title},
        "messages": data
    })

# ----------------------------------------------
# حذف محادثة (soft delete)
# ----------------------------------------------
@user_required
@require_POST
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(
        AIConversation,
        id=conversation_id,
        user=request.user,
        is_deleted=False
    )
    conversation.is_deleted = True
    conversation.save(update_fields=["is_deleted"])
    return JsonResponse({"success": True, "message": "تم حذف المحادثة."})

# ----------------------------------------------
# إعادة تسمية محادثة
# ----------------------------------------------
@user_required
@require_POST
def rename_conversation(request, conversation_id):
    conversation = get_object_or_404(
        AIConversation,
        id=conversation_id,
        user=request.user,
        is_deleted=False
    )
    title = request.POST.get("title", "").strip()
    if not title:
        return JsonResponse({"success": False, "message": "العنوان فارغ."})
    if len(title) > 255:
        title = title[:255]

    # منع التكرار
    original = title
    number = 2
    while AIConversation.objects.filter(user=request.user, title=title, is_deleted=False).exclude(id=conversation.id).exists():
        title = f"{original} ({number})"
        number += 1

    conversation.title = title
    conversation.save(update_fields=["title"])
    return JsonResponse({"success": True, "title": title})
# ----------------------------------------------
# أحدث محادثة
# ----------------------------------------------
@user_required
def latest_conversation(request):
    conversation = AIConversation.objects.filter(
        user=request.user,
        is_deleted=False
    ).order_by('-is_pinned', '-last_message_at').first()

    if not conversation:
        return JsonResponse({"success": False})
    return JsonResponse({
        "success": True,
        "conversation_id": conversation.id,
        "title": conversation.title
    })

# ----------------------------------------------
# بحث في المحادثات
# ----------------------------------------------
@user_required
def search_conversations(request):
    keyword = request.GET.get("q", "").strip()
    conversations = AIConversation.objects.filter(
        user=request.user,
        is_deleted=False,
        title__icontains=keyword
    ).annotate(
        msg_count=Count('messages')
    ).order_by('-is_pinned', '-last_message_at')

    data = []
    for conv in conversations:
        last_msg_time = conv.last_message_at
        hour = last_msg_time.hour
        minute = last_msg_time.minute
        ampm = "AM" if hour < 12 else "PM"
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12
        formatted_time = f"{hour_12}:{minute:02d} {ampm}"

        data.append({
            "id": conv.id,
            "title": conv.title,
            "updated_at": conv.last_message_at.isoformat(),
            "is_pinned": conv.is_pinned
        })
    return JsonResponse({"success": True, "conversations": data})
# ----------------------------------------------
# حذف جميع المحادثات
# ----------------------------------------------
@user_required
@require_POST
def clear_all_conversations(request):
    AIConversation.objects.filter(
        user=request.user,
        is_deleted=False
    ).update(is_deleted=True)
    return JsonResponse({"success": True, "message": "تم حذف جميع المحادثات."})

# ----------------------------------------------
# تثبيت / إلغاء تثبيت محادثة
# ----------------------------------------------
@user_required
@require_POST
def toggle_pin_conversation(request, conversation_id):
    conversation = get_object_or_404(
        AIConversation,
        id=conversation_id,
        user=request.user,
        is_deleted=False
    )
    conversation.is_pinned = not conversation.is_pinned
    conversation.save(update_fields=["is_pinned"])
    return JsonResponse({"success": True, "is_pinned": conversation.is_pinned})

# ----------------------------------------------
# أرشفة / إلغاء أرشفة
# ----------------------------------------------
@user_required
@require_POST
def toggle_archive_conversation(request, conversation_id):
    conversation = get_object_or_404(
        AIConversation,
        id=conversation_id,
        user=request.user,
        is_deleted=False
    )
    conversation.is_archived = not conversation.is_archived
    conversation.save(update_fields=["is_archived"])
    return JsonResponse({"success": True, "is_archived": conversation.is_archived})

# ----------------------------------------------
# معلومات المحادثة (لأغراض إدارية)
# ----------------------------------------------
@user_required
def conversation_info(request, conversation_id):
    conversation = get_object_or_404(
        AIConversation,
        id=conversation_id,
        user=request.user,
        is_deleted=False
    )
    msg_count = conversation.messages.count()
    return JsonResponse({
        "success": True,
        "conversation": {
            "id": conversation.id,
            "title": conversation.title,
            "messages_count": msg_count,
            "created_at": conversation.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": conversation.last_message_at.strftime("%Y-%m-%d %H:%M"),
            "is_pinned": conversation.is_pinned,
            "is_archived": conversation.is_archived
        }
    })
#/////////////////////////////////////////////////////////////
@login_required(login_url='/accounts/login/')
def account(request):
    if request.user.user_type != 'user':
        return HttpResponseForbidden("هذه الصفحة مخصصة للمستخدمين فقط.")

    return render(request, 'user_dashboard/account.html')
#///////////////////////////////////////////////////////////////////
from django.contrib.auth import update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import random, string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@login_required
@require_POST
def update_name(request):
    data = json.loads(request.body)
    name = data.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'الاسم مطلوب'})
    user = request.user
    parts = name.split(' ', 1)
    user.first_name = parts[0]
    user.last_name = parts[1] if len(parts) > 1 else ''
    user.save()
    return JsonResponse({'success': True, 'name': user.get_full_name()})

from accounts.views import send_otp_via_api  # تأكد من وجود هذا الاستيراد

@login_required
@require_POST
def send_email_otp(request):
    user = request.user
    if not user.email:
        return JsonResponse({'success': False, 'error': 'لا يوجد بريد إلكتروني مسجل'})
    otp = generate_otp()
    cache.set(f'email_otp_{user.id}', otp, timeout=600)
    # ✨ تمرير purpose="email_change"
    success = send_otp_via_api(user.email, user.get_full_name() or user.username, otp, purpose="email_change")
    if success:
        return JsonResponse({'success': True, 'message': 'تم إرسال رمز التحقق إلى بريدك الإلكتروني'})
    else:
        return JsonResponse({'success': False, 'error': 'فشل إرسال البريد الإلكتروني، يرجى المحاولة لاحقاً'})



@login_required
@require_POST
def verify_email_otp(request):
    data = json.loads(request.body)
    otp = data.get('otp', '')
    new_email = data.get('email', '').strip()
    if not otp or not new_email:
        return JsonResponse({'success': False, 'error': 'جميع الحقول مطلوبة'})
    cached_otp = cache.get(f'email_otp_{request.user.id}')
    if not cached_otp or cached_otp != otp:
        return JsonResponse({'success': False, 'error': 'رمز التحقق غير صحيح أو منتهي الصلاحية'})
    if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
        return JsonResponse({'success': False, 'error': 'البريد الإلكتروني مستخدم بالفعل'})
    user = request.user
    user.email = new_email
    user.save()
    cache.delete(f'email_otp_{request.user.id}')
    return JsonResponse({'success': True, 'email': new_email})



@login_required
@require_POST
def send_phone_otp(request):
    user = request.user
    if not user.email:
        return JsonResponse({'success': False, 'error': 'لا يوجد بريد إلكتروني مسجل. لا يمكننا إرسال رمز التحقق.'})
    otp = generate_otp()
    cache.set(f'phone_otp_{user.id}', otp, timeout=600)
    # ✨ تمرير purpose="phone_change"
    success = send_otp_via_api(user.email, user.get_full_name() or user.username, otp, purpose="phone_change")
    if success:
        return JsonResponse({'success': True, 'message': 'تم إرسال رمز التحقق إلى بريدك الإلكتروني.'})
    else:
        return JsonResponse({'success': False, 'error': 'فشل إرسال البريد الإلكتروني، يرجى المحاولة لاحقاً'})

@login_required
@require_POST
def verify_phone_otp(request):
    data = json.loads(request.body)
    otp = data.get('otp', '')
    new_phone = data.get('phone', '').strip()
    if not otp or not new_phone:
        return JsonResponse({'success': False, 'error': 'جميع الحقول مطلوبة'})
    cached_otp = cache.get(f'phone_otp_{request.user.id}')
    if not cached_otp or cached_otp != otp:
        return JsonResponse({'success': False, 'error': 'رمز التحقق غير صحيح أو منتهي الصلاحية'})
    user = request.user
    user.phone = new_phone
    user.save()
    cache.delete(f'phone_otp_{request.user.id}')
    return JsonResponse({'success': True})

@login_required
@require_POST
def change_password(request):
    data = json.loads(request.body)
    current = data.get('current_password', '')
    new_pass = data.get('new_password', '')
    if not current or not new_pass:
        return JsonResponse({'success': False, 'error': 'جميع الحقول مطلوبة'})
    user = authenticate(username=request.user.username, password=current)
    if not user:
        return JsonResponse({'success': False, 'error': 'كلمة المرور الحالية غير صحيحة'})
    if len(new_pass) < 8:
        return JsonResponse({'success': False, 'error': 'كلمة المرور الجديدة يجب أن تكون 8 أحرف على الأقل'})
    user.set_password(new_pass)
    user.save()
    update_session_auth_hash(request, user)  # يحافظ على الجلسة
    return JsonResponse({'success': True})

@login_required
@require_POST
def delete_account(request):
    data = json.loads(request.body)
    password = data.get('password', '')
    if not password:
        return JsonResponse({'success': False, 'error': 'كلمة المرور مطلوبة'})
    user = authenticate(username=request.user.username, password=password)
    if not user:
        return JsonResponse({'success': False, 'error': 'كلمة المرور غير صحيحة'})
    # يمكن إضافة فترة سماح هنا
    user.is_active = False  # أو user.delete()
    user.save()
    logout(request)
    return JsonResponse({'success': True, 'redirect': '/accounts/login/'})
#////////////////////////////////////////////////////////////////////////
import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from dashboard.models import Order

def format_price_iqd(amount):
    """تنسيق السعر بالدينار العراقي"""
    try:
        amount = float(amount)
        if amount >= 1000000:
            million = amount / 1000000
            if million == int(million):
                return f"{int(million)} مليون د.ع"
            return f"{million:.1f} مليون د.ع"
        elif amount >= 1000:
            thousand = amount / 1000
            return f"{int(thousand):,} ألف د.ع"
        else:
            return f"{int(amount):,} د.ع"
    except:
        return "0 د.ع"

@login_required(login_url='accounts/login/')
def my_orders(request):
    orders = Order.objects.filter(
        customer=request.user
    ).select_related('package', 'company').order_by('-created_at')
    
    # إضافة السعر المنسق لكل طلب
    for order in orders:
        order.formatted_price = format_price_iqd(order.total_amount)
    
    return render(request, 'user_dashboard/my_orders.html', {'orders': orders})

@login_required
@require_POST
def delete_my_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    if order.status not in ['canceled', 'completed']:
        return JsonResponse({'status': 'error', 'message': 'لا يمكن حذف طلب نشط. قم بالإلغاء أولاً.'})
    order.delete()
    return JsonResponse({'status': 'success', 'message': 'تم حذف الطلب من السجل.'})
#////////////////////////////////////////////////////////////////////
from .models import Feedback
@login_required(login_url='accounts/login/')
@require_POST
def send_feedback(request):
    try:
        data = json.loads(request.body)
        feedback_type = data.get('type', 'complaint')
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'success': False, 'error': 'يرجى كتابة رسالة.'})
        
        if feedback_type not in ['complaint', 'suggestion']:
            feedback_type = 'complaint'
        
        Feedback.objects.create(
            user=request.user,
            feedback_type=feedback_type,
            message=message
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def faq(request):
    return render(request, 'user_dashboard/faq.html')
#/////////////////////////////////////////////////////////
from django.views.decorators.http import require_POST

def static_page(request, page_name):
    """تعرض الصفحات الثابتة: about, privacy, terms"""
    allowed_pages = ['about', 'privacy', 'terms']
    if page_name not in allowed_pages:
        return redirect('user_home')
    
    titles = {
        'about': 'عن Solaris',
        'privacy': 'سياسة الخصوصية',
        'terms': 'شروط الاستخدام',
    }
    
    context = {
        'page_title': titles.get(page_name, ''),
        'page_name': page_name,
    }
    return render(request, 'user_dashboard/static_page.html', context)

@login_required(login_url='accounts/login/')
@require_POST
def accept_terms(request):
    user = request.user
    user.accepted_terms = True
    user.save()
    return JsonResponse({'success': True})