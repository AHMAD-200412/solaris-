document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const submitBtn = document.querySelector('button');
    const emailInput = document.querySelector('input[type="email"]');

    if (form) {
        form.addEventListener('submit', function (e) {
            const emailValue = emailInput.value.trim();

            // تحقق بسيط من صحة الإيميل قبل الإرسال للبايثون
            if (!emailValue.includes('@') || !emailValue.includes('.')) {
                e.preventDefault();
                alert('يرجى إدخال بريد إلكتروني صحيح.');
                return;
            }

            // تغيير نص الزر وتعطيله لمنع الضغط المتكرر أثناء إرسال السيرفر للإيميل
            submitBtn.innerText = 'جاري إرسال الرمز...';
            submitBtn.style.pointerEvents = 'none';
            submitBtn.style.opacity = '0.7';
        });
    }
});