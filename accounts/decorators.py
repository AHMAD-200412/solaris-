from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from functools import wraps

def approved_company_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # نتأكد اليوزر مسجل دخول ونوعه شركة
        if request.user.is_authenticated and request.user.user_type == 'Company':
            # إذا الإدارة شالت الصح (الموافقة)
            if not request.user.is_approved: 
                # 1. نطرده فوراً (هنا الجلسة القديمة انمسحت)
                logout(request)
                
                # 2. نزرع رسالة الخطأ بالجلسة الجديدة بعد ما طردناه
                messages.error(request, 'عذراً، تم إيقاف أو انتهاء اشتراك شركتك. يرجى التواصل مع الإدارة عبر الرقم 07870105877.')
                
                # 3. نوجهه لصفحة الدخول
                return redirect('login') # تأكد ان اسم مسار تسجيل الدخول بالـ urls هو 'login'
                
        return view_func(request, *args, **kwargs)
    return _wrapped_view