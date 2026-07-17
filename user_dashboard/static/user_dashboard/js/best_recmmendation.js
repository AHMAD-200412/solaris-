document.addEventListener("DOMContentLoaded", function () {
    // ==================== عناصر المودالات ====================
    const requestButtons = document.querySelectorAll(".request-btn");
    const bundleModal = document.getElementById("bundleRequestModal");
    const btnUseGPS = document.getElementById("btnUseGPS");
    const btnManualAddress = document.getElementById("btnManualAddress");
    const manualAddressDiv = document.getElementById("manualAddressDiv");
    const manualAddressInput = document.getElementById("manualAddressInput");
    const btnSubmitManual = document.getElementById("btnSubmitManual");
    const gpsLoadingMessage = document.getElementById("gpsLoadingMessage");
    const btnCancelRequest = document.getElementById("btnCancelRequest");

    // مودال التفعيل
    const locationConsentModal = document.getElementById("locationConsentModal");
    const btnEnableLocation = document.getElementById("btnEnableLocation");
    const btnCancelConsent = document.getElementById("btnCancelConsent");

    // مودال الرسائل (نجاح/خطأ)
    const messageModal = document.getElementById("messageModal");
    const messageModalTitle = document.getElementById("messageModalTitle");
    const messageModalText = document.getElementById("messageModalText");
    const messageModalOk = document.getElementById("messageModalOk");

    let currentPackageId = null;

    // ==================== دوال مساعدة ====================
    function showMessage(title, text, isError = false) {
        messageModalTitle.textContent = title;
        messageModalText.textContent = text;
        messageModalTitle.style.color = isError ? "#ff6b6b" : "#2ecc71";
        messageModal.classList.remove("hidden");
    }

    function hideMessageModal() {
        messageModal.classList.add("hidden");
    }

    messageModalOk?.addEventListener("click", hideMessageModal);
    window.addEventListener("click", (e) => {
        if (e.target === messageModal) hideMessageModal();
    });

    function hideBundleModal() {
        bundleModal.classList.add("hidden");
        manualAddressDiv.classList.add("hidden");
        gpsLoadingMessage.classList.add("hidden");
        manualAddressInput.value = "";
        // لا نلغي currentPackageId هنا، بل نبقيه لأنه قد يُستخدم بعد فتح المودال مرة أخرى
        // currentPackageId = null;
    }

    function hideLocationConsentModal() {
        locationConsentModal.classList.add("hidden");
    }

    // ==================== فتح مودال الطلب ====================
    requestButtons.forEach(btn => {
        btn.addEventListener("click", function () {
            currentPackageId = this.dataset.packageId;
            if (!currentPackageId) {
                showMessage("خطأ", "لم يتم العثور على معرف الباقة.", true);
                return;
            }
            // إخفاء أي شيء سابق
            hideBundleModal();
            hideLocationConsentModal();
            // فتح المودال
            bundleModal.classList.remove("hidden");
            console.log("تم فتح المودال للباقة:", currentPackageId);
        });
    });

    // ==================== إغلاق المودال ====================
    btnCancelRequest?.addEventListener("click", hideBundleModal);
    window.addEventListener("click", (e) => {
        if (e.target === bundleModal) hideBundleModal();
    });

    // ==================== اختيار GPS ====================
    btnUseGPS?.addEventListener("click", function () {
        // إخفاء أي حقل يدوي مفتوح
        manualAddressDiv.classList.add("hidden");
        gpsLoadingMessage.classList.add("hidden");

        // محاولة استخدام GPS مباشرة (بدون شرط HTTPS لنجرب)
        if (!navigator.geolocation) {
            showMessage("تنبيه", "متصفحك لا يدعم تحديد الموقع. استخدم الإدخال اليدوي.", true);
            manualAddressDiv.classList.remove("hidden");
            manualAddressInput.focus();
            return;
        }

        // إظهار مودال التفعيل الإرشادي (يمكن تخطيه بالضغط على "تفعيل")
        locationConsentModal.classList.remove("hidden");
    });
    // عند النقر على "تفعيل" في مودال التفعيل
    btnEnableLocation?.addEventListener("click", function () {
        hideLocationConsentModal();
        startGPSRequest();
    });

    // زر "لاحقاً" في مودال التفعيل
    btnCancelConsent?.addEventListener("click", function () {
        hideLocationConsentModal();
        // العودة إلى الإدخال اليدوي تلقائياً
        manualAddressDiv.classList.remove("hidden");
        manualAddressInput.focus();
    });

    function startGPSRequest() {
        gpsLoadingMessage.classList.remove("hidden");
        navigator.geolocation.getCurrentPosition(
            (position) => {
                // نجاح
                gpsLoadingMessage.classList.add("hidden");
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const gpsLink =`https://maps.google.com/?q=${lat},${lon}`;
                    sendBundleRequest(currentPackageId, gpsLink, "موقعي الحالي (GPS)");
                hideBundleModal();
            },
            (error) => {
                // فشل
                gpsLoadingMessage.classList.add("hidden");
                console.warn("Geolocation error:", error.message);
                let errorMsg = "لم نتمكن من تحديد موقعك. ";
                if (error.code === error.PERMISSION_DENIED) {
                    errorMsg += "تم رفض الإذن. يرجى السماح بالموقع الجغرافي من إعدادات المتصفح.";
                } else if (error.code === error.POSITION_UNAVAILABLE) {
                    errorMsg += "معلومات الموقع غير متوفرة حالياً.";
                } else if (error.code === error.TIMEOUT) {
                    errorMsg += "انتهت مهلة طلب الموقع. حاول مجدداً.";
                } else {
                    errorMsg += "تأكد من اتصال الإنترنت وحاول مرة أخرى.";
                }
                showMessage("عذراً", errorMsg, true);
                // فتح الإدخال اليدوي تلقائياً بعد الخطأ
                manualAddressDiv.classList.remove("hidden");
                manualAddressInput.focus();
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    }

    // ==================== اختيار يدوي ====================
    btnManualAddress?.addEventListener("click", function () {
        console.log("تم النقر على الإدخال اليدوي");
        // إخفاء GPS loading إن وجد
        gpsLoadingMessage.classList.add("hidden");
        // إظهار الحقل اليدوي
        manualAddressDiv.classList.remove("hidden");
        manualAddressInput.focus();
    });

    // ==================== إرسال الطلب اليدوي ====================
    btnSubmitManual?.addEventListener("click", function () {
        const address = manualAddressInput.value.trim();
        if (!address) {
            showMessage("تنبيه", "الرجاء كتابة العنوان.", true);
            return;
        }
        if (!currentPackageId) {
            showMessage("خطأ", "حدث خطأ: لم يتم تحديد الباقة.", true);
            return;
        }
        console.log("إرسال طلب يدوي:", currentPackageId, address);
        sendBundleRequest(currentPackageId, "", address);
        hideBundleModal();
    });

    // ==================== دالة إرسال الطلب ====================
    async function sendBundleRequest(packageId, gpsLink, addressText) {
        if (!packageId) {
            showMessage("خطأ", "معرف الباقة غير صالح.", true);
            return;
        }
        // بناء الرابط (استخدام requestBundlePattern من Django)
        const url = requestBundlePattern.replace('/0/', '/' + packageId + '/');
        console.log("إرسال إلى:", url, { gps_link: gpsLink, address_text: addressText });
        try {
            const res = await fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    gps_link: gpsLink,
                    address_text: addressText
                })
            });
            const data = await res.json();
            if (data.status === "success") {
                showMessage("تم بنجاح", "تم إرسال طلبك! ستتواصل معك الشركة قريباً.", false);
            } else {
                showMessage("خطأ", data.message || "فشل في إرسال الطلب.", true);
            }
        } catch (err) {
            console.error("خطأ في fetch:", err);
            showMessage("خطأ في الاتصال", "حدث خطأ أثناء إرسال الطلب. تحقق من اتصالك بالإنترنت.", true);
        }
    }
});