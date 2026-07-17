document.addEventListener('DOMContentLoaded', function() {
    // [1] جلب حقل رفع الشعار المخفي وصورة المعاينة (الكود القديم)
    const logoInput = document.querySelector('input[type="file"][name="logo"]');
    const logoPreview = document.getElementById('logoPreview');

    if (logoInput && logoPreview) {
        logoInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    logoPreview.src = e.target.result;
                }
                
                reader.readAsDataURL(file);
            }
        });
    }

    // [2] كود جلب وتحديث إحداثيات الـ GPS الجغرافي للاعدادات (الجديد) 📍
    const getLocationBtn = document.getElementById('getLocationBtn');
    if (getLocationBtn) {
        getLocationBtn.addEventListener('click', function() {
            const btn = document.getElementById('getLocationBtn');
            const btnText = document.getElementById('gpsBtnText');
            const gpsInput = document.getElementById('id_gps_coordinates');

            if (navigator.geolocation) {
                btnText.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> جاري جلب موقعك الحالي بدقة...⏳';
                btn.style.opacity = "0.8";

                navigator.geolocation.getCurrentPosition(
                    // في حال نجاح سحب الإحداثيات
                    function(position) {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        
                        // تخزين الإحداثيات بالحقل المخفي
                        gpsInput.value = lat + "," + lng;
                        
                        // تغيير شكل الزر ليدل على النجاح المتوافق مع الـ Dashboard
                        btnText.innerHTML = '<i class="fa-solid fa-circle-check"></i> تم تحديث الموقع بنجاح! يرجى حفظ التعديلات بالأسفل 💾';
                        btn.style.background = "linear-gradient(135deg, #2ecc71, #27ae60)";
                        btn.style.color = "#fff";
                        btn.style.opacity = "1";
                    },
                    // في حال الفشل أو رفض الصلاحية
                    function(error) {
                        btn.style.background = "linear-gradient(135deg, #e74c3c, #c0392b)";
                        btn.style.color = "#fff";
                        btn.style.opacity = "1";
                        
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                btnText.innerHTML = '<i class="fa-solid fa-hand"></i> يرجى تفعيل صلاحية الموقع للمتصفح';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                btnText.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> عذراً، إشارة الـ GPS غير متوفرة';
                                break;
                            case error.TIMEOUT:
                                btnText.innerHTML = '<i class="fa-solid fa-clock"></i> انتهت مهلة الطلب، حاول مرة ثانية';
                                break;
                            default:
                                btnText.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> حدث خطأ أثناء تحديد اللوكيشن';
                        }
                    },
                    { enableHighAccuracy: true, timeout: 10000 }
                );
            } else {
                btnText.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> متصفحك لا يدعم نظام تحديد المواقع GPS';
            }
        });
    }
});