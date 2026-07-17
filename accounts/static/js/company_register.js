// 1. كود التأثيرات الحركية (Hover Effect) اللي سويته أنت
const inputs = document.querySelectorAll(".input-box");

inputs.forEach(box => {
    box.addEventListener("mouseenter", () => {
        box.style.transform = "scale(1.03)";
    });

    box.addEventListener("mouseleave", () => {
        box.style.transform = "scale(1)";
    });
});

// 2. كود جلب إحداثيات الموقع (GPS Geolocation)
document.addEventListener('DOMContentLoaded', function() {
    const getLocationBtn = document.getElementById('getLocationBtn');
    if(getLocationBtn) {
        getLocationBtn.addEventListener('click', function() {
            const btn = document.getElementById('getLocationBtn');
            const btnText = document.getElementById('gpsBtnText');
            const gpsInput = document.getElementById('id_gps_coordinates');

            if (navigator.geolocation) {
                btnText.innerText = "جاري تحديد موقعك... ⏳";
                btn.style.opacity = "0.7";

                navigator.geolocation.getCurrentPosition(
                    // في حال نجاح جلب الموقع
                    function(position) {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        
                        // خزن الإحداثيات بصيغة نصية
                        gpsInput.value = lat + "," + lng;
                        
                        // تحديث شكل الزر للنجاح
                        btnText.innerText = "✅ تم تحديد موقع الشركة بنجاح!";
                        btn.style.background = "linear-gradient(135deg, #2ecc71, #27ae60)";
                        btn.style.color = "#fff";
                        btn.style.opacity = "1";
                    },
                    // في حال رفض المستخدم أو حدوث خطأ
                    function(error) {
                        btn.style.background = "linear-gradient(135deg, #e74c3c, #c0392b)";
                        btn.style.color = "#fff";
                        btn.style.opacity = "1";
                        
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                btnText.innerText = "❌ يرجى السماح للتطبيق بالوصول للموقع";
                                break;
                            case error.POSITION_UNAVAILABLE:
                                btnText.innerText = "❌ معلومات الموقع غير متوفرة حالياً";
                                break;
                            case error.TIMEOUT:
                                btnText.innerText = "❌ انتهت مهلة طلب الموقع";
                                break;
                            default:
                                btnText.innerText = "❌ حدث خطأ أثناء تحديد الموقع";
                        }
                    },
                    { enableHighAccuracy: true, timeout: 10000 }
                );
            } else {
                btnText.innerText = "❌ متصفحك لا يدعم خاصية تحديد الموقع GPS";
            }
        });
    }
});