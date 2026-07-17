// accounts/static/js/verify_otp.js

document.addEventListener("DOMContentLoaded", function () {
    const otpInput = document.querySelector('.otp-input');

    // منع إدخال أي شيء عدا الأرقام
    otpInput.addEventListener('input', function (e) {
        this.value = this.value.replace(/[^0-9]/g, '');
    });

    // إضافة تأثير نبضي خفيف عند كتابة الرمز بالكامل
    otpInput.addEventListener('keyup', function () {
        if (this.value.length === 6) {
            this.style.borderColor = '#10b981'; // يتحول للأخضر عند اكتمال 6 أرقام
        } else {
            this.style.borderColor = '#f59e0b';
        }
    });
});