from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
# استدعاء الجداول اللي سويناها
from .models import Product, SolarPackage, Order, CompanyProfile,InstallmentPlan,InstallmentPayment,DigitalContract,PackageComponent
import json
from django.contrib import messages
from datetime import timedelta    
from django.utils import timezone 
from django.contrib.auth import get_user_model
import uuid             
from django.http import JsonResponse
from accounts.decorators import approved_company_required
from django.contrib.auth import logout


import re

def extract_power_kw(product):
    """
    استخراج القدرة من اسم القطعة وتحويلها إلى كيلوواط.
    """

    name = product.name.lower().replace(" ", "")

    # مثال: 500w أو 500وات أو 500واط
    w = re.search(r'(\d+(\.\d+)?)(w|وات|واط)', name)

    if w:
        return float(w.group(1)) / 1000

    # مثال: 5kw أو 5كيلوواط
    kw = re.search(r'(\d+(\.\d+)?)(kw|كيلوواط)', name)

    if kw:
        return float(kw.group(1))

    return 0

@login_required(login_url='/accounts/login/')
@approved_company_required
def user_dashboard_view(request):
    # حماية: لو شركة حاولت تدير لوحة الأفراد، نمنعها
    if request.user.user_type != 'user':
        return HttpResponseForbidden("عذراً، هذه اللوحة مخصصة للمستخدمين الأفراد فقط.")
        
    return render(request, 'dashboard/user_dashboard.html', {'user': request.user})


@login_required(login_url='/accounts/login/')
@approved_company_required
def company_dashboard_view(request):
    if request.user.user_type != 'company':
        return HttpResponseForbidden("عذراً، هذه اللوحة مخصصة للشركات والمؤسسات المعتمدة فقط.")
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    
    profile, created = CompanyProfile.objects.get_or_create(user=request.user)

    my_products = Product.objects.filter(company=request.user)
    my_packages = SolarPackage.objects.filter(company=request.user)
    my_orders = Order.objects.filter(company=request.user).order_by('-created_at')

    total_products = my_products.count()
    total_packages = my_packages.count()
    pending_orders_count = my_orders.filter(status='pending').count()
    
    completed_orders = my_orders.filter(status='completed')
    total_earnings = sum(order.total_amount for order in completed_orders)

    # ==========================================
    # برمجة المخططات البيانية الحقيقية (Charts)
    # ==========================================
    
    # 1. حساب الأرباح الشهرية (المخطط الخطي)
    monthly_revenue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # 12 شهر
    for order in completed_orders:
        if order.created_at:
            month_index = order.created_at.month - 1 # جلب رقم الشهر (0-11)
            monthly_revenue[month_index] += float(order.total_amount)

    # 2. حساب الباقات الأكثر مبيعاً (المخطط الدائري)
    package_labels = []
    package_counts = []
    
    # نمر على باقات الشركة ونشوف كم طلب اجا لكل باقة
    for pkg in my_packages:
        count = my_orders.filter(package=pkg).count() # إذا كان حقل الربط اسمه package
        if count > 0:
            package_labels.append(pkg.title)
            package_counts.append(count)
            
    # إذا الشركة جديدة وماكو مبيعات، نعرض شكل فارغ
    if not package_labels:
        package_labels = ["لا توجد مبيعات بعد"]
        package_counts = [1]

    context = {
        'company': request.user,
        'profile': profile,
        'total_products': total_products,
        'total_packages': total_packages,
        'pending_orders_count': pending_orders_count,
        'total_earnings': total_earnings,
        
        # إرسال بيانات المخططات بصيغة JSON لملف الجافاسكربت
        'monthly_revenue_json': json.dumps(monthly_revenue),
        'package_labels_json': json.dumps(package_labels),
        'package_counts_json': json.dumps(package_counts),
    }
        
    return render(request, 'dashboard/company_dashboard.html', context)
#///////////////////////////////////////////////////////////
@login_required(login_url='/accounts/login/')
@approved_company_required
def company_store_view(request):
    if request.user.user_type != 'company':
        return HttpResponseForbidden("عذراً، هذه اللوحة مخصصة للشركات فقط.")
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    
    # 📥 هنا السيستم يستلم البيانات من النافذة المنبثقة ويحفظها بالقاعدة
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category = request.POST.get('category')
        image = request.FILES.get('image') # لاستلام الصورة
        
        # إنشاء القطعة الجديدة في قاعدة البيانات
        Product.objects.create(
            company=request.user, # ربط القطعة بالشركة اللي ضافتها
            name=name,
            price=price,
            stock=stock,
            category=category,
            image=image
        )
        # بعد الحفظ، يسوي إعادة توجيه لنفس الصفحة حتى تظهر القطعة فوراً كدام عينه 😍
        return redirect('company_store') # type: ignore
    
    # 📤 هنا جلب القطع المضافة مسبقاً لعرضها بالصفحة
    products = Product.objects.filter(company=request.user).order_by('-created_at')
    
    context = {
        'company': request.user,
        'products': products,
    }
    return render(request, 'dashboard/store_items.html', context)
#/////////////////////////////////////////////////////////////////
def delete_product(request, product_id):
    
    # نجيب القطعة ونحذفها
    product = Product.objects.get(id=product_id)
    product.delete()
    # نرجع لصفحة المخزن
    return redirect('company_store')
#/////////////////////////////////////////////////////////////////
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        
        # إذا رفع صورة جديدة نحدثها، وإذا عافها فارغة تبقى القديمة
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
            
        product.save() # حفظ التعديلات
        
    return redirect('company_store') # يرجعك فوراً للمخزن وتشوف التعديل محدث تلقائياً
#///////////////////////////////////////////////////////////////
def safe_float(val):
    if not val:
        return 0.0
    try:
        # تحويل الفاصلة العادية إلى نقطة عشرية برمجية لكي يفهمها دجانغو
        return float(str(val).replace(',', '.'))
    except ValueError:
        return 0.0
#////////////////////////////////////////
import traceback
@login_required(login_url='/accounts/login/')
@approved_company_required
def create_bundle_view(request):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request)
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    
    products = Product.objects.filter(company=request.user)
    packages = SolarPackage.objects.filter(company=request.user).prefetch_related('package_components__product').order_by('-id')
    promotions_count = SolarPackage.objects.filter(company=request.user, views_count__gt=0).count()
    is_free_applicable = promotions_count < 3

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        total_price = request.POST.get('total_price')
        selected_components = request.POST.getlist('components')
        quantities = request.POST.getlist('quantities')
        
        is_installment = request.POST.get('is_installment_available') == 'on'
        down_payment = request.POST.get('down_payment') if is_installment else 0
        monthly_installment = request.POST.get('monthly_installment') if is_installment else 0
        duration_months = request.POST.get('duration_months') if is_installment else 0
        package_image = request.FILES.get('package_image') or None

        if not title or not total_price:
            messages.error(request, "الرجاء ملء الحقول الأساسية (العنوان والسعر)!")
            return redirect('create_bundle')

        try:
            new_package = SolarPackage.objects.create(
                company=request.user,
                title=title,
                description=description,
                total_price=safe_float(total_price),
                is_installment_available=is_installment,
                down_payment=safe_float(down_payment),
                monthly_installment=safe_float(monthly_installment),
                duration_months=int(duration_months) if duration_months else 0,
                package_image=package_image
            )
            
            if selected_components and quantities:
                from decimal import Decimal
                panel_power = Decimal('0')
                for prod_id, qty in zip(selected_components, quantities):
                    if prod_id and qty:
                        try:
                            product = Product.objects.get(id=prod_id, company=request.user)
                            qty_int = int(qty)
                            PackageComponent.objects.create(
                                package=new_package,
                                product=product,
                                quantity=qty_int
                            )
                            # حساب قدرة الألواح
                            if product.power_watt and product.power_watt > 0:
                                kw = Decimal(product.power_watt) / Decimal('1000')
                            else:
                                kw = Decimal(extract_power_kw(product))
                            panel_power += kw * qty_int
                        except Product.DoesNotExist:
                            continue
                
                daily_production = panel_power * Decimal('5')  # 5 ساعات شمس ذروة
                new_package.total_panel_power = panel_power
                new_package.daily_production = daily_production
                new_package.save(update_fields=["total_panel_power", "daily_production"])
                
            messages.success(request, "تم إضافة الباقة الجاهزة الجديدة بنجاح للمتجر! 🚀")
            return redirect('create_bundle')
        except Exception as e:
            traceback.print_exc()
            print("الخطأ:", e)
            raise
    
    return render(request, 'dashboard/create_bundle.html', {
        'company': request.user,
        'products': products,
        'packages': packages,
        'promotions_count': promotions_count,
        'is_free_applicable': is_free_applicable
    })


@login_required(login_url='/accounts/login/')
@approved_company_required
def edit_bundle_view(request, bundle_id):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request)
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    
    package = get_object_or_404(SolarPackage, id=bundle_id, company=request.user)
    
    if request.method == 'POST':
        try:
            package.title = request.POST.get('title')
            package.description = request.POST.get('description')
            package.total_price = safe_float(request.POST.get('total_price'))
            
            is_installment = request.POST.get('is_installment_available') == 'on'
            package.is_installment_available = is_installment
            
            if is_installment:
                package.down_payment = safe_float(request.POST.get('down_payment'))
                package.monthly_installment = safe_float(request.POST.get('monthly_installment'))
                dm = request.POST.get('duration_months')
                package.duration_months = int(dm) if dm else 0
            else:
                package.down_payment = 0.0
                package.monthly_installment = 0.0
                package.duration_months = 0
            
            if request.FILES.get('image'):
                package.package_image = request.FILES.get('image')
                
            package.save()
            
            selected_components = request.POST.getlist('components')
            quantities = request.POST.getlist('quantities')
            package.package_components.all().delete()
            
            from decimal import Decimal
            panel_power = Decimal('0')
            for prod_id, qty in zip(selected_components, quantities):
                if prod_id and qty:
                    try:
                        product = Product.objects.get(id=prod_id, company=request.user)
                        qty_int = int(qty)
                        PackageComponent.objects.create(
                            package=package,
                            product=product,
                            quantity=qty_int
                        )
                        if product.power_watt and product.power_watt > 0:
                            kw = Decimal(product.power_watt) / Decimal('1000')
                        else:
                            kw = Decimal(extract_power_kw(product))
                        panel_power += kw * qty_int
                    except Product.DoesNotExist:
                        continue
            
            daily_production = panel_power * Decimal('5')
            package.total_panel_power = panel_power
            package.daily_production = daily_production
            package.save(update_fields=["total_panel_power", "daily_production"])
            
            messages.success(request, f"تم تحديث بيانات باقة ({package.title}) بنجاح! 💾")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء تعديل الباقة: {str(e)}")
            
    return redirect('create_bundle')
#/////////////////////////////////////////
@login_required(login_url='/accounts/login/')
@approved_company_required
def delete_bundle(request, bundle_id):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    """
    دالة حذف الباقة من النظام
    """
    package = get_object_or_404(SolarPackage, id=bundle_id, company=request.user)
    package.delete()
    messages.success(request, "تم حذف الباقة نهائياً من النظام! 🗑")
    return redirect('create_bundle')


@login_required(login_url='/accounts/login/')
@approved_company_required
def promote_bundle_view(request, bundle_id):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request)
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
        
    if request.method == 'POST':
        package = get_object_or_404(SolarPackage, id=bundle_id, company=request.user)
        
        try:
            duration_days = int(request.POST.get('duration_days', 3))
        except ValueError:
            duration_days = 3

        promotions_count = SolarPackage.objects.filter(company=request.user, views_count__gt=0).count()
        receipt_image = request.FILES.get('receipt_image')

        # 🛑 إذا رفع صورة وصل (معناها طلب مدفوع)، مباشرة يروح للآدمن للانتظار
        if receipt_image:
            try:
                package.is_promoted = False
                package.is_promotion_pending = True  # تصبح قيد الانتظار
                package.promotion_receipt = receipt_image
                package.save()
                messages.info(request, "تم إرسال صورة الوصل بنجاح! طلبك الآن معروض على الإدارة للمراجعة والتفعيل. ⏳")
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء رفع طلب الترويج: {str(e)}")
            return redirect('create_bundle')

        # 🛑 إذا ما رفع وصل، نشيك إذا عنده محاولات مجانية وإذا طلب ترويج مجاني (3 أيام)
        if promotions_count < 3:
            if duration_days > 3:
                # إذا اختار 7 أو 15 يوم بس ما رفع وصل!
                messages.error(request, "الباقات المدفوعة تتطلب رفع صورة وصل التحويل!")
                return redirect('create_bundle')
                
            # تفعيل الترويج المجاني
            try:
                package.is_promoted = True
                package.is_promotion_pending = False
                package.promotion_end_date = timezone.now() + timedelta(days=duration_days)
                if package.views_count == 0:
                    package.views_count = 1
                package.save()
                messages.success(request, f"تم تفعيل الترويج المجاني بنجاح للباقة لمدة {duration_days} أيام! 🚀")
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء تفعيل الترويج المجاني: {str(e)}")
        else:
            # إذا خلصت محاولاته المجانية وما رفع وصل
            messages.error(request, "لقد نفدت محاولاتك المجانية المتاحة! يرجى رفع صورة وصل تحويل الرسوم لتفعيل الإعلان.")
            
        return redirect('create_bundle')
def generate_installments(plan, total_amount, months):
    monthly_amount = total_amount / months
    start_date = timezone.now().date()
    
    for i in range(1, months + 1):
        due_date = start_date + timedelta(days=30 * i)
        # افتراض أن لديك مودل InstallmentPayment
        plan.payments.create(
            month_number=i,
            due_date=due_date,
            amount=monthly_amount,
            status='pending'
        )

# ========================================================
# 1️⃣ قسم إدارة الأقساط (Installments Management)
# ========================================================
@login_required(login_url='/accounts/login/')
@approved_company_required
def installments_view(request):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    # جلب الدفعات مع بيانات الطلب والزبون ورقم الهاتف
    payments = InstallmentPayment.objects.select_related('plan__order', 'plan__order__customer').filter(
        plan__order__company=request.user
    ).order_by('due_date')

    plans_count = InstallmentPlan.objects.filter(order__company=request.user).count()
    pending_count = InstallmentPayment.objects.filter(plan__order__company=request.user, status='pending').count()
    late_count = InstallmentPayment.objects.filter(plan__order__company=request.user, status='late').count()

    context = {
        'company': request.user,
        'payments': payments,
        'plans_count': plans_count,
        'pending_count': pending_count,
        'late_count': late_count,
    }
    
    return render(request, 'dashboard/installments.html', context)


@login_required(login_url='/accounts/login/')
@approved_company_required
def add_offline_installment(request):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    """ إضافة مشترك أوفلاين بمعزل عن طلبات التركيب الميداني (CRM) """
    if request.method == 'POST':
        try:
            customer_name = request.POST.get('customer_name')
            # تم تعديل الاسم ليطابق حقل total_amount في الـ HTML
            amount = float(request.POST.get('total_amount')) 
            months = int(request.POST.get('months'))
            phone_number = request.POST.get('phone_number')
            purchased_items = request.POST.get('purchased_items') # 👈 جلب تفاصيل المشتريات
            
            # 1️⃣ إنشاء حساب "أوفلاين" مخفي للزبون
            User = get_user_model()
            random_username = f"offline_{uuid.uuid4().hex[:6]}"
            
            offline_customer = User.objects.create(
                username=random_username,
                first_name=customer_name,
            )
            
            # 2️⃣ إنشاء الطلب وعزله عن الـ CRM باستخدام is_offline_sale
            new_order = Order.objects.create(
                company=request.user,
                customer=offline_customer,
                phone_number=phone_number,
                total_amount=amount,
                status='completed',
                is_offline_sale=True,            # 👈 السحر هنا: عزله عن لوحة الكشف الموقعي
                purchased_items=purchased_items  # 👈 حفظ مشترياته (بطارية، انفرتر..)
            )
            
            # 3️⃣ إنشاء الخطة
            plan = InstallmentPlan.objects.create(
                order=new_order,
                total_months=months,
                monthly_amount=amount / months,
                down_payment_paid=True
            )
            
            # 4️⃣ توليد الدفعات
            generate_installments(plan=plan, total_amount=amount, months=months)
            
            messages.success(request, f"تم تسجيل المشترك ({customer_name}) وتوليد الأقساط بنجاح!")
        except Exception as e:
            print("❌ الخطأ:", str(e))
            messages.error(request, f"حدث خطأ أثناء الإضافة: {str(e)}")
            
        return redirect('installments') 
        
    return redirect('installments')


@login_required(login_url='/accounts/login/')
@approved_company_required
def plan_details_view(request, plan_id):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    plan = get_object_or_404(InstallmentPlan, id=plan_id, order__company=request.user)
    payments = plan.payments.all().order_by('month_number')
    
    payments_data = []
    for p in payments:
        status_ar = "مدفوع" if p.status == 'paid' else ("متأخر" if p.status == 'late' else "قيد الانتظار")
        payments_data.append({
            'month_number': p.month_number,
            'amount': float(p.amount),
            'due_date': p.due_date.strftime('%Y-%m-%d'),
            'status': p.status,
            'status_ar': status_ar
        })
    
    all_paid = all(p.status == 'paid' for p in payments) and payments.exists()
    
    # 🌟 التعديل السحري: فصلنا الشرط حتى بايثون ما تتخربط
    details = plan.order.purchased_items
    if not details:
        details = plan.order.package.title if plan.order.package else 'غير محدد'
        
    return JsonResponse({
        'plan_id': plan.id,
        'customer_name': plan.order.customer.first_name,
        'total_amount': float(plan.order.total_amount),
        'phone': plan.order.phone_number or '-',
        'purchased_items': details, # 👈 هسه غصباً عليه تطلع البطارية!
        'payments': payments_data,
        'all_paid': all_paid
    })


@login_required(login_url='/accounts/login/')
@approved_company_required
def collect_installment(request, payment_id):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    payment = get_object_or_404(InstallmentPayment, id=payment_id, plan__order__company=request.user)
    
    if payment.status != 'paid':
        payment.status = 'paid'
        payment.paid_date = timezone.now()
        payment.save()
        messages.success(request, f"تم قبض قسط الشهر {payment.month_number} للمشترك ({payment.plan.order.customer.first_name}) بنجاح! ✅")
    else:
        messages.warning(request, "هذا القسط مدفوع مسبقاً!")
        
    return redirect('installments')


@login_required(login_url='/accounts/login/')
@approved_company_required
def delete_plan_view(request, plan_id):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    plan = get_object_or_404(InstallmentPlan, id=plan_id, order__company=request.user)
    plan.delete()
    messages.success(request, "تم حذف المشترك وتصفية الحساب بنجاح!")
    return redirect('installments') 

# ========================================================
# 2️⃣ قسم إدارة الطلبات الميدانية (CRM Orders)
# ========================================================

@login_required(login_url='/accounts/login/')
@approved_company_required
def orders_management_view(request):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    # 👈 هنا استبعدنا مبيعات الأوفلاين حتى ما تخرب عدادات الكشف الموقعي
    company_orders = Order.objects.filter(company=request.user, is_offline_sale=False).select_related('customer').order_by('-created_at')
    
    active_orders = company_orders.exclude(status__in=['completed', 'canceled'])
    completed_orders = company_orders.filter(status='completed')
    canceled_orders = company_orders.filter(status='canceled')
    stats = {
        'new_pending': active_orders.filter(status='pending').count(),
        'in_survey': active_orders.filter(status='survey').count(),
        'in_progress': active_orders.filter(status__in=['preparing', 'on_way']).count(),
        'completed': completed_orders.count(),
    }
  

    return render(request, 'dashboard/orders_management.html', {
        'company': request.user,
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'canceled_orders': canceled_orders,
        'stats': stats,
    })


@login_required(login_url='/accounts/login/')
@approved_company_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, company=request.user)
        
        new_status = request.POST.get('status')
        extra_fees = request.POST.get('extra_fees')
        extra_fees_reason = request.POST.get('extra_fees_reason')
        tech_report = request.POST.get('technical_report')
        
        try:
            if new_status: 
                order.status = new_status
            
            # حماية كاملة لحقل الرسوم الإضافية
            if extra_fees and extra_fees.strip(): # تأكدنا إنها مو فارغة ومو بس مسافات
                try:
                    order.extra_fees = float(extra_fees)
                except ValueError:
                    pass # إذا فشل التحويل (مثلاً المستخدم كتب حروف)، تجاهلها لا تسوي كراش
            
            if extra_fees_reason: 
                order.extra_fees_reason = extra_fees_reason
            
            if tech_report: 
                order.technical_report = tech_report
            
            order.save()
            messages.success(request, f"تم تحديث بيانات الطلب #{order.id} بنجاح! 💾")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء التحديث: {str(e)}")

    return redirect('orders_management')


# 🌟 التحديث السحري الجديد: دالة توليد الأقساط من الطلبات الميدانية 🌟
@login_required(login_url='/accounts/login/')
@approved_company_required
def generate_installment_plan(request, order_id):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    if request.method == 'POST':
        try:
            # جلب الطلب والتأكد أنه يخص نفس الشركة
            order = get_object_or_404(Order, id=order_id, company=request.user)
            
            # جلب القيم من المودل
            total_amount = float(request.POST.get('total_amount'))
            down_payment = float(request.POST.get('down_payment'))
            months = int(request.POST.get('months'))
            
            # اللوجك: حساب المبلغ المتبقي بعد المقدمة
            remaining_amount = total_amount - down_payment
            
            # 1. تحديث إجمالي الطلب (في حال أضاف المدير فلوس إضافية أثناء التوليد)
            order.total_amount = total_amount
            order.save()
            
            # 2. إنشاء خطة الأقساط الذكية
            plan = InstallmentPlan.objects.create(
                order=order,
                total_months=months,
                monthly_amount=remaining_amount / months,
                down_payment_paid=(down_payment > 0)
            )
            
            # 3. توليد الدفعات في الداتابيس بناءً على المبلغ المتبقي
            generate_installments(plan=plan, total_amount=remaining_amount, months=months)
            
            messages.success(request, f"تم خصم المقدمة (${down_payment}) وتوليد الخطة للمشترك ({order.customer.first_name}) بنجاح! 🎉")
            
        except Exception as e:
            print("❌ الخطأ في التوليد:", str(e))
            messages.error(request, f"حدث خطأ أثناء إعداد خطة الأقساط: {str(e)}")
            
    return redirect('orders_management')
@login_required(login_url='/accounts/login/')
@approved_company_required
def delete_order(request, order_id):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    order = get_object_or_404(Order, id=order_id, company=request.user, status='canceled')
    order.delete()
    messages.success(request, "تم حذف الطلب نهائياً 🗑")
    return redirect('orders_management')
#/////////////////////////////////////////////////////////
# ========================================================
# 3️⃣ قسم إدارة العقود والضمانات (Contracts Management)
# ========================================================

@login_required(login_url='/accounts/login/')
@approved_company_required
def contracts_management_view(request):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    """ واجهة إدارة العقود """
    # جلب العقود المصدرة سابقاً لعرضها بالجدول
    contracts = DigitalContract.objects.select_related('order', 'order__customer').filter(
        order__company=request.user
    ).order_by('-issued_at')
    
    # جلب الزبائن الجاهزين (الكاش + الأقساط) لأن كلاهما حالتهم 'completed'
    completed_orders_no_contract = Order.objects.filter(
        company=request.user, 
        status='completed'  
    ).exclude(
        contract__isnull=False # استبعاد اللي عدهم عقد
    ).select_related('customer') # 👈 ضفنا هاي لتسريع جلب أسماء الزبائن

    context = {
        'company': request.user,
        'contracts': contracts,
        'completed_orders': completed_orders_no_contract,
    }
    return render(request, 'dashboard/contracts_management.html', context)


@login_required(login_url='/accounts/login/')
def add_contract_view(request):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    """ دالة استقبال بيانات العقد وحفظها """
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id, company=request.user)
            
            # حفظ العقد مع السيريالات المفصولة
            DigitalContract.objects.create(
                order=order,
                panels_serial=request.POST.get('panels_serial', '').strip(),
                panels_warranty=int(request.POST.get('panels_warranty') or 10),
                
                batteries_serial=request.POST.get('batteries_serial', '').strip(),
                batteries_warranty=int(request.POST.get('batteries_warranty') or 1),
                
                inverter_serial=request.POST.get('inverter_serial', '').strip(),
                inverter_warranty=int(request.POST.get('inverter_warranty') or 1),
                
                legal_terms=request.POST.get('legal_terms')
            )
            messages.success(request, "تم إصدار العقد والضمان الرقمي بنجاح! 🎉")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء حفظ العقد: {str(e)}")
            
    return redirect('contracts_management')


@login_required(login_url='/accounts/login/')
@approved_company_required
def print_contract_view(request, contract_id):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    """ واجهة الطباعة (جاهزة للتصميم) """
    contract = get_object_or_404(DigitalContract, id=contract_id, order__company=request.user)

    return render(request, 'dashboard/print_contract.html', {'contract': contract})
#//////////////////////////////////////
User = get_user_model()

def verify_contract_public(request, contract_id):
    contract = get_object_or_404(DigitalContract, id=contract_id)
    
    # 💡 البحث الدقيق عن منشئ العقد (الشركة الصحيحة فقط):
    company = None
    if hasattr(contract, 'company') and contract.company:
        company = contract.company
    elif hasattr(contract, 'user') and contract.user:  # إذا كان العقد مربوط باليوزر
        company = contract.user
    elif hasattr(contract, 'order') and contract.order: # إذا كان العقد مربوط بالطلب والطلب مربوط باليوزر
        if hasattr(contract.order, 'user') and contract.order.user:
            company = contract.order.user
        elif hasattr(contract.order, 'company') and contract.order.company:
            company = contract.order.company
            
    context = {
        'company': company,
        'contract': contract,
    }
    return render(request, 'dashboard/verify_contract.html', context)
#///////////////////////////////////////////////////////////////////////
from .froms import ProjectForm
from .models import CompletedProject

@login_required
@approved_company_required
def manage_portfolio(request):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    # 1. جلب المشاريع الخاصة بالشركة اللي مسجلة دخول فقط (مرتبة من الأحدث للأقدم)
    projects = CompletedProject.objects.filter(company=request.user).order_by('-created_at')
    
    # 2. معالجة بيانات النافذة المنبثقة (عند الإضافة)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, company=request.user)
        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.company = request.user # السطر السحري: ربط المشروع بالشركة تلقائياً
            new_project.save()
            
            # رسالة نجاح تظهر للمستخدم
            messages.success(request, 'تمت إضافة المشروع لمعرضك بنجاح! 🚀')
            return redirect('manage_portfolio') # تحديث الصفحة حتى يظهر المشروع الجديد
    else:
        # إذا جان يفتح الصفحة بشكل عادي
        form = ProjectForm(company=request.user)
        
    context = {
        'company': request.user,
        'projects': projects,
        'form': form,
    }
    return render(request, 'dashboard/manage_portfolio.html', context)

@login_required
@approved_company_required
def delete_project(request, project_id):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    # جلب المشروع والتأكد إنه تابع للشركة اللي مسجلة دخول
    project = get_object_or_404(CompletedProject, id=project_id, company=request.user)
    project.delete()
    messages.success(request, 'تم حذف المشروع بنجاح!')
    return redirect('manage_portfolio')

# دالة تعديل المشروع
# دالة تعديل المشروع (تستقبل البيانات من النافذة المنبثقة)
@login_required
@approved_company_required
def edit_project(request, project_id):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    project = get_object_or_404(CompletedProject, id=project_id, company=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل تفاصيل المشروع بنجاح! ✏️')
        else:
            messages.error(request, 'حدث خطأ أثناء التعديل، يرجى التأكد من البيانات.')
            
    # بكل الأحوال نرجعه لصفحة المشاريع بعد الحفظ
    return redirect('manage_portfolio')
#/////////////////////////////////////////////////////
from .froms import UserUpdateForm, CompanyProfileForm
from .models import CompanyProfile
from django.db import transaction
@login_required
@approved_company_required
def settings_view(request):
    if request.user.user_type == 'company' and not request.user.is_approved:
        logout(request) # نطرده من الجلسة فوراً
        messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877 .')
        return redirect('/accounts/login/')
    # جلب أو إنشاء بروفايل الشركة تلقائياً إذا ما جان موجود
    profile, created = CompanyProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # ربط الـ POST بالـ Forms
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        p_form = CompanyProfileForm(request.POST, instance=profile)

        # التحقق من صحة البيانات
        if u_form.is_valid() and p_form.is_valid():
            with transaction.atomic():
                u_form.save()
                p_form.save()
            messages.success(request, 'تم تحديث إعدادات الشركة بنجاح!')
            return redirect('settings_view') # غير الاسم حسب الـ URL عندك
    else:
        # عرض البيانات الحالية
        u_form = UserUpdateForm(instance=request.user)
        p_form = CompanyProfileForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'dashboard/settings.html', context)
