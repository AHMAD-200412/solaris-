// accounts/static/js/verify_otp.js

document.addEventListener("DOMContentLoaded", function () {
    const otpInput = document.querySelector('.otp-input');
    const otpForm = document.querySelector('form');

    if (!otpInput) return;

    // تنظيف الرمز مباشرة عند اللصق أو الإدخال
    otpInput.addEventListener('input', function () {
        // إزالة أي شيء ليس برقم
        this.value = this.value.replace(/[^0-9]/g, '');
    });

    // قبل إرسال النموذج، تأكد من نظافة الرمز
    otpForm.addEventListener('submit', function(e) {
        const cleanValue = otpInput.value.replace(/[^0-9]/g, '');
        otpInput.value = cleanValue; // تأكيد النظافة
        
        if (cleanValue.length !== 6) {
            e.preventDefault();
            alert('الرجاء إدخال رمز مكون من 6 أرقام.');
            otpInput.focus();
        }
    });

    // تأثير لوني اختياري
    otpInput.addEventListener('keyup', function () {
        const val = this.value.replace(/[^0-9]/g, '');
        if (val.length === 6) {
            this.style.borderColor = '#10b981';
        } else {
            this.style.borderColor = '#f59e0b';
        }
    });
});