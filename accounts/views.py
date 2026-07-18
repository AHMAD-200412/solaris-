import random
import requests
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages  
# استدعاء الفورمات والموديلز الخاصة بك
from .forms import UserRegisterForm, CompanyRegisterForm
from .models import CustomUser


# ==========================================
# 🚀 1. دالة إرسال الرمز عبر الـ API (Brevo)
# ==========================================
def send_otp_via_api(email, username, otp, purpose="register"):
    """
    إرسال رمز OTP عبر Brevo API مع رسالة مخصصة حسب الغرض.
    
    الأغراض المدعومة:
    - register: تفعيل حساب جديد
    - email_change: تغيير البريد الإلكتروني
    - phone_change: تغيير رقم الهاتف
    - password_reset: إعادة تعيين كلمة المرور
    """
    url = "https://api.brevo.com/v3/smtp/email"
    api_key = "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"
    sender_email = "ahmad2004asa@gmail.com"

    # تخصيص العنوان والمحتوى حسب الغرض
    purposes = {
        "register": {
            "title": "رمز تفعيل حسابك - Solaris",
            "heading": f"مرحباً {username}",
            "description": "شكراً لتسجيلك في منظومة الطاقة الشمسية في العراق.",
            "code_label": "رمز تفعيل الحساب الخاص بك هو:"
        },
        "email_change": {
            "title": "رمز تغيير البريد الإلكتروني - Solaris",
            "heading": f"مرحباً {username}",
            "description": "لقد طلبت تغيير بريدك الإلكتروني. استخدم الرمز أدناه لتأكيد العملية.",
            "code_label": "رمز تغيير البريد الإلكتروني هو:"
        },
        "phone_change": {
            "title": "رمز تغيير رقم الهاتف - Solaris",
            "heading": f"مرحباً {username}",
            "description": "لقد طلبت تغيير رقم هاتفك. استخدم الرمز أدناه لتأكيد العملية.",
            "code_label": "رمز تغيير رقم الهاتف هو:"
        },
        "password_reset": {
            "title": "رمز إعادة تعيين كلمة المرور - Solaris",
            "heading": f"مرحباً {username}",
            "description": "لقد طلبت إعادة تعيين كلمة المرور. استخدم الرمز أدناه لإكمال العملية.",
            "code_label": "رمز إعادة تعيين كلمة المرور هو:"
        },
    }

    purpose_data = purposes.get(purpose, purposes["register"])

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    payload = {
        "sender": {"name": "Solaris", "email": sender_email},
        "to": [{"email": email, "name": username}],
        "subject": purpose_data["title"],
        "htmlContent": f"""
            <div style='direction: rtl; text-align: center; font-family: Arial, sans-serif; padding: 20px;'>
                <h2 style='color: #f59e0b;'>{purpose_data['heading']}</h2>
                <p style='font-size: 16px; color: #334155;'>{purpose_data['description']}</p>
                <p style='font-size: 16px; color: #334155;'>{purpose_data['code_label']}</p>
                <div style='background: #1e293b; color: #f59e0b; font-size: 32px; font-weight: bold; padding: 15px; border-radius: 10px; display: inline-block; letter-spacing: 5px; margin: 20px 0;'>
                    {otp}
                </div>
                <p style='font-size: 12px; color: #94a3b8;'>إذا لم تكن أنت من طلب هذا الرمز، يرجى تجاهل هذا البريد.</p>
            </div>
        """
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code in [200, 201, 202]
    except Exception:
        return False


# ==========================================
# 👤 2. تسجيل المستخدم العادي
# ==========================================
def register_user(request): # تم التعديل من Def إلى def (البايثون حساس للأحرف الكبيرة)
    
    # 1️⃣ توجيه المستخدمين اللي مسجلين دخول مسبقاً (حتى ما يشوفون صفحة التسجيل)
    if request.user.is_authenticated:
        if getattr(request.user, 'user_type', '') == 'company':
            return redirect('/dashboard/company/')
        # 🔥 [تعديل التوجيه]: هنا ربطناه بالواجهة اللي صممناها اليوم!
        return redirect('/user/home/') 
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            
            # جلب الإيميل وفحصه في قاعدة البيانات قبل حفظ الحساب
            email = form.cleaned_data.get('email')
            if email and CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'هذا البريد الإلكتروني مرتبط بحساب آخر بالفعل!')
                return render(request, 'accounts/user_register.html', {'form': form})
            
            # 🔥 [تعديل المشكلة]: نزلنا هذا السطر هنا حتى البايثون يقراه صح ويحل الـ NameError
            user = form.save(commit=False)
            
            user.user_type = 'user' 
            user.is_active = False   
            
            # جلب الاسم بصيغة آمنة جداً
            user.first_name = form.cleaned_data.get('full_name', '') 
            
            # حماية الإيميل الفارغ
            email_prefix = str(user.email).split('@')[0] if user.email else 'user' 
            user.username = f"{email_prefix}_{random.randint(1000, 9999)}" 
            
            user.save() 

            # توليد وإرسال الـ OTP
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp
            request.session['user_id'] = user.id 

            send_otp_via_api(user.email, user.first_name, otp) 

            # يروح يوثق حسابه، ومن يكمل توثيق (بدالة الـ verify) لازم هناك هم توجهه لـ /dashboard/user/home/
            return redirect('/accounts/verify-otp/') 
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/user_register.html', {'form': form})
# ==========================================
# 🏢 3. تسجيل الشركة
# ==========================================

def register_company(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'user_type', '') == 'company':
            return redirect('/dashboard/company/')  # 🔥 [تعديل] تم تصحيح الرابط لمنع خطأ 404
        return redirect('/')
        
    if request.method == 'POST':
        form = CompanyRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            
            # 🔥 [تعديل ذهبي] جلب الإيميل وفحصه في قاعدة البيانات قبل حفظ الحساب
            email = form.cleaned_data.get('email')
            if email and CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'هذا البريد الإلكتروني مرتبط بحساب آخر بالفعل!')
                return render(request, 'accounts/company_register.html', {'form': form}) # 🔥 [تعديل] اسم القالب الصحيح مالتك
            
            company = form.save(commit=False)
            company.user_type = 'company'
            company.is_active = False  

            email_str = str(company.email) if company.email else 'company'
            email_prefix = email_str.split('@')[0].replace(".", "_")
            generated_username = f"comp_{email_prefix}_{random.randint(1000, 9999)}"
            
            while CustomUser.objects.filter(username=generated_username).exists():
                generated_username = f"comp_{email_prefix}_{random.randint(1000, 9999)}"
            
            company.username = generated_username
            company.save()

            # 🟢 [سطر الأمان الحاسم]: تصفير أي إثبات قديم فوراً لكي تظهر صفحة الرمز غصباً عليه
            if 'otp_verified' in request.session: del request.session['otp_verified']

            otp = str(random.randint(100000, 999999))
            
            request.session['otp'] = otp
            request.session['user_id'] = company.id

            c_name = getattr(company, 'company_name', company.username)
            send_otp_via_api(company.email, c_name, otp)

            return redirect('/accounts/verify-otp/') 
    else:
        form = CompanyRegisterForm()

    return render(request, 'accounts/company_register.html', {'form': form})


# ==========================================
# 🔐 4. التحقق من الرمز المدمج (Verify OTP)
# ==========================================
from django.contrib.auth import login # تأكد إن هاي موجودة فوگ بالملف

def verify_otp(request):
    # 🔐 [الحصن الأمني الحاسم]: توجيه المسجلين دخول مسبقاً
    if request.user.is_authenticated:
        # 🔥 تم تصحيح الشرط هنا (شيلنا الـ hasattr الخبيثة)
        if getattr(request.user, 'user_type', '') == 'company':
            return redirect('/dashboard/company/')  
        else:
            return redirect('/user/home/') # 🔥 يروح لواجهة توترز اللي صممناها

    if request.method == 'POST':
        user_otp = str(request.POST.get('otp', '')).strip()
        
        # 🔍 نتحقق هل المستخدم جاء من صفحة "نسيت كلمة المرور" أم تسجيل جديد؟
        is_password_reset = request.session.get('is_password_reset', False)
        
        if is_password_reset:
            session_otp = str(request.session.get('reset_otp', '')).strip()
            email = request.session.get('reset_email')
        else:
            session_otp = str(request.session.get('otp', '')).strip()
            user_id = request.session.get('user_id') or request.session.get('company_id')
        print("========== OTP DEBUG ==========")
        print("User OTP:", user_otp)
        print("Session OTP:", session_otp)
        print("Password Reset:", is_password_reset)
        print("Session:", dict(request.session))
        print("===============================")
        # فحص أن القيم موجودة ومتطابقة
        if user_otp and session_otp and user_otp == session_otp:
            
            # ✨ [حالة نسيت كلمة المرور]
            if is_password_reset:
                if 'reset_otp' in request.session:
                    del request.session['reset_otp']
                messages.success(request, '🔐 تم التحقق من الرمز بنجاح. يرجى كتابة كلمة المرور الجديدة الآن.')
                return redirect('/accounts/reset-password/')
            
            # 📝 [حالة التسجيل الجديد - مستخدم أو شركة]
            try:
                user = CustomUser.objects.get(id=user_id)
                
                # 🏢 [إذا كان الحساب لشركة] -> نوجهه لصفحة المراجعة (بدون hasattr)
                if getattr(user, 'user_type', '') == 'company':
                    user.is_active = False 
                    user.save()
                    
                    request.session['otp_verified'] = True
                    request.session['review_user_id'] = user.id
                    if 'otp' in request.session: 
                        del request.session['otp']
                    
                    return render(request, 'accounts/under_review.html', {
                        'company_name': getattr(user, 'company_name', 'الشركة'),
                        'user_id': user.id  
                    })
                
                # 👤 [إذا كان الحساب مستخدم عادي] -> تفعيل وتسجيل دخول فوري!
                else:
                    user.is_active = True  
                    user.save()
                    
                    # تنظيف الجلسة
                    if 'otp' in request.session: del request.session['otp']
                    if 'user_id' in request.session: del request.session['user_id']
                    
                    # 🔥 تسجيل الدخول التلقائي للمواطن
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    
                    messages.success(request, '☀️ تم تفعيل حسابك بنجاح! أهلاً بك في شمس الموصل.')
                    # 🔥 توجيه للواجهة الجديدة فوراً
                    return redirect('/user/home/') 
                    
            except CustomUser.DoesNotExist:
                return render(request, 'accounts/verify_otp.html', {'error': 'حدث خطأ غير متوقع، الحساب غير موجود.'})
        else:
            return render(request, 'accounts/verify_otp.html', {'error': 'الرمز الذي أدخلته غير صحيح! تأكد من بريدك الإلكتروني.'})
            
    # 🟢 [معالجة طلب الـ GET / الريفريش للأمان الكامل والـ Auto-Login للشركات] 🟢
    
    if 'otp' in request.session:
        return render(request, 'accounts/verify_otp.html')

    if request.session.get('otp_verified') is True:
        review_user_id = request.session.get('review_user_id') or request.session.get('user_id') or request.session.get('company_id')
        if review_user_id:
            try:
                user = CustomUser.objects.get(id=review_user_id)
                
                # 🔥 تصحيح شرط الشركة هنا أيضاً
                if getattr(user, 'user_type', '') == 'company':
                     if user.is_active:
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        
                        if 'review_user_id' in request.session: del request.session['review_user_id'] 
                        if 'user_id' in request.session: del request.session['user_id']
                        if 'company_id' in request.session: del request.session['company_id']
                        if 'otp_verified' in request.session: del request.session['otp_verified']
                        
                        return redirect('/dashboard/company/')
                    
                     return render(request, 'accounts/under_review.html', {
                        'company_name': getattr(user, 'company_name', 'الشركة'),
                        'user_id': user.id  
                    })
            except CustomUser.DoesNotExist:
                pass

    return render(request, 'accounts/verify_otp.html')

# ==========================================
# 📡 5. دالة فحص حالة الحساب في الخلفية 
# ==========================================
def check_status(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        
        if user.is_active:
            # 🔥 السحر هنا: نسجل دخول المستخدم تلقائياً بالجلسة في متصفحه الخفي فوراً
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            return JsonResponse({'status': 'approved'})
            
        return JsonResponse({'status': 'pending'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

# ==========================================
# 🔑 6. تسجيل الدخول الذكي الموحد (Login)
# ==========================================
def login_view(request):
    # فحص إذا كان المستخدم مسجل دخول أصلاً
    if request.user.is_authenticated:
        if getattr(request.user, 'user_type', '') == 'company':
            # تم تصحيح هذا المسار حتى ما يطلع خطأ 404 مستقبلاً
            return redirect('/dashboard/company/') 
        return redirect('/') # مسار الرئيسية للمستخدمين

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        # الحل الجذري لمشكلة تكرار الإيميل: استخدام filter.first بدلاً من get
        # البحث عن الحساب عن طريق الإيميل
        user_record = CustomUser.objects.filter(email=email).first()

        if user_record:
            if not user_record.is_active:
                if getattr(user_record, 'user_type', '') == 'company':
                    return render(request, 'accounts/under_review.html', {
                        'company_name': getattr(user_record, 'company_name', 'الشركة'),
                        'user_id': user_record.id
                    })
                else:
                    messages.error(request, 'حسابك غير مفعل بعد، يرجى تفعيل الحساب عبر الرمز المرسل لإيميلك.')
                    return redirect('/accounts/login/')

            # تسجيل الدخول الآمن
            user = authenticate(request, username=user_record.username, password=password)

            if user is not None:
                
                # 🛑 --- التفتيش الجديد اللي يمنع الشركة المرفوضة من الدخول ---
                # انتبه: إذا اسم حقل الموافقة مالتك بالـ models يختلف عن 'is_approved'، غير الكلمة هنا
                if user.user_type == 'company' and getattr(user, 'is_approved', True) == False:
                    messages.error(request, 'عذراً، حساب الشركة غير مفعل أو تم إيقاف صلاحيته. يرجى مراجعة الإدارة.')
                    return redirect('/accounts/login/')
                # -------------------------------------------------------------

                login(request, user)
                messages.success(request, f'مرحباً بك مجدداً، {user.username}!')
                
                # 🔄 التوجيه التلقائي الذكي بناءً على نوع الحساب الموثق عندك في الموديل
                if user.user_type == 'company':
                    return redirect('/dashboard/company/')
                else:
                    return redirect('/user/home/')
            else:
                messages.error(request, 'كلمة المرور التي أدخلتها غير صحيحة.')
        else:
            messages.error(request, 'البريد الإلكتروني غير مسجل لدينا، يرجى إنشاء حساب جديد.')

    return render(request, 'accounts/login.html')


# ==========================================
# 🚪 7. تسجيل الخروج (Logout)
# ==========================================
from django.contrib import messages

def logout_view(request):
    logout(request)
    # مسح أي رسائل مخزنة حتى لا تظهر بعد الخروج
    storage = messages.get_messages(request)
    storage.used = True
    return redirect('/accounts/login/')
#////////////////////////////////////////
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # البحث عن المستخدم في قاعدة البيانات
        user_record = CustomUser.objects.filter(email=email).first()
        
        if user_record:
            # توليد رمز عشوائي من 6 أرقام
            otp_code = str(random.randint(100000, 999999))
            
            # حفظ الحالات بالـ Session لصفحة الـ OTP والـ Reset
            request.session['is_password_reset'] = True
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp_code
            
            # استخدام الاسم المناسب: للشركات نفضل company_name، ثم الاسم الشخصي، ثم username
            if user_record.company_name:
               display_name = user_record.company_name
            elif user_record.get_full_name():
               display_name = user_record.get_full_name()
            elif user_record.first_name:
               display_name = user_record.first_name
            else:
               display_name = user_record.username
            is_sent = send_otp_via_api(email, display_name, otp_code, purpose="password_reset")
            
            if is_sent:
                messages.success(request, 'تم إرسال رمز التحقق بنجاح إلى بريدك الإلكتروني.')
            else:
                # حماية احتياطية: لو علق الـ API يطبع الرمز تحت حتى ما توقف تجربتك
                print("\n" + "🔥" * 20)
                print(f"⚠️ فشل الـ API الحقيقي، الرمز للتجربة: {otp_code}")
                print("🔥" * 20 + "\n")
                messages.success(request, 'تم توليد الرمز (يرجى نسخه من الـ Terminal في حال لم يصلك).')
                
            # التوجيه لصفحتك المفتوحة الحالية
            return redirect('/accounts/verify-otp/')
            
        else:
            messages.error(request, 'هذا البريد الإلكتروني غير مسجل لدينا!')
            
    return render(request, 'accounts/forgot_password.html')
#///////////////////////////////////////////////
def reset_password_view(request):
    if not request.session.get('is_password_reset'):
        return redirect('/accounts/login/')
        
    if request.method == 'POST':
        new_password = request.POST.get('password', '').strip()
        email = request.session.get('reset_email')
        
        if new_password and email:
            user = CustomUser.objects.filter(email=email).first()
            if user:
                user.set_password(new_password)
                user.save()
                
                # تنظيف الـ Session
                if 'is_password_reset' in request.session: del request.session['is_password_reset']
                if 'reset_email' in request.session: del request.session['reset_email']
                if 'reset_otp' in request.session: del request.session['reset_otp']
                
                messages.success(request, 'تم إعادة تعيين كلمة المرور بنجاح! يمكنك الآن تسجيل الدخول.')
                return redirect('/accounts/login/')
                
    return render(request, 'accounts/reset_password.html')
#///////////////////////////////////////////
def choose_account_type(request):
    return render(request, 'accounts/choose_account_type.html')
