document.addEventListener("DOMContentLoaded", () => {
    // عناصر الإدخال
    const nationalBill = document.getElementById("nationalBill");
    const generatorBill = document.getElementById("generatorBill");
    const totalBill = document.getElementById("totalBill");
    const createStudy = document.getElementById("createStudy");
    const studyForm = document.getElementById("studyForm");
    const studyResult = document.getElementById("studyResult");
    const requestBundleBtn = document.getElementById("requestBundleBtn");

    // نتائج الدراسة
    const currentMonthlyEl = document.getElementById("currentMonthly");
    const currentYearlyEl = document.getElementById("currentYearly");
    const userConsumptionEl = document.getElementById("userConsumption");
    const realProductionEl = document.getElementById("realProduction");
    const coveragePercentEl = document.getElementById("coveragePercent");
    const dailySurplusEl = document.getElementById("dailySurplus");
    const efficiencyEl = document.getElementById("efficiency");
    const savingMonthlyEl = document.getElementById("savingMonthly");
    const savingYearlyEl = document.getElementById("savingYearly");
    const paybackPeriodEl = document.getElementById("paybackPeriod");
    const profit25YearsEl = document.getElementById("profit25Years");
    const panelInfoEl = document.getElementById("panelInfo");
    const inverterInfoEl = document.getElementById("inverterInfo");
    const batteryInfoEl = document.getElementById("batteryInfo");
    const lifetimeInfoEl = document.getElementById("lifetimeInfo");
    const aiAnalysis = document.getElementById("aiAnalysis");

    // المودالات
    const messageModal = document.getElementById("messageModal");
    const messageModalTitle = document.getElementById("messageModalTitle");
    const messageModalText = document.getElementById("messageModalText");
    const messageModalOk = document.getElementById("messageModalOk");
    const bundleModal = document.getElementById("bundleRequestModal");
    const btnCancelRequest = document.getElementById("btnCancelRequest");
    const manualAddressDiv = document.getElementById("manualAddressDiv");
    const manualAddressInput = document.getElementById("manualAddressInput");
    const gpsLoadingMessage = document.getElementById("gpsLoadingMessage");
    const btnUseGPS = document.getElementById("btnUseGPS");
    const btnManualAddress = document.getElementById("btnManualAddress");
    const btnSubmitManual = document.getElementById("btnSubmitManual");
    const locationConsentModal = document.getElementById("locationConsentModal");
    const btnEnableLocation = document.getElementById("btnEnableLocation");
    const btnCancelConsent = document.getElementById("btnCancelConsent");

    if (!nationalBill || !createStudy) return;

    const currentPackageId = packageIdFromURL || null;
    const priceIQD = packagePrice || 0;

    function formatIQD(value) {
        value = Math.round(value);
        if (value >= 1000000) {
            let million = value / 1000000;
            return (Number.isInteger(million) ? million.toFixed(0) : million.toFixed(1)) + " مليون د.ع";
        }
        if (value >= 1000) return Math.round(value / 1000) + " ألف د.ع";
        return value.toLocaleString("en-US") + " د.ع";
    }

    function formatYears(years) {
        if (years < 1) return Math.ceil(years * 12) + " شهر";
        return years.toFixed(1) + " سنة";
    }

    function getMonthlyBill() {
        const n = parseFloat(nationalBill.value) || 0;
        const g = parseFloat(generatorBill.value) || 0;
        return { national: n, generator: g, total: n + g };
    }

    function updateTotalBill() {
        const bills = getMonthlyBill();
        totalBill.textContent = formatIQD(bills.total);
    }

    nationalBill.addEventListener("input", updateTotalBill);
    generatorBill.addEventListener("input", updateTotalBill);
    updateTotalBill();
    function showMessage(title, text, isError = false) {
        if (!messageModal) return;
        messageModalTitle.textContent = title;
        messageModalText.textContent = text;
        messageModalTitle.style.color = isError ? "#ff6b6b" : "#2ecc71";
        messageModal.classList.remove("hidden");
    }

    function hideMessageModal() { messageModal.classList.add("hidden"); }
    if (messageModalOk) messageModalOk.addEventListener("click", hideMessageModal);
    window.addEventListener("click", e => { if (e.target === messageModal) hideMessageModal(); });

    function hideBundleModal() {
        bundleModal.classList.add("hidden");
        manualAddressDiv.classList.add("hidden");
        gpsLoadingMessage.classList.add("hidden");
        manualAddressInput.value = "";
    }
    if (btnCancelRequest) btnCancelRequest.addEventListener("click", hideBundleModal);
    window.addEventListener("click", e => { if (e.target === bundleModal) hideBundleModal(); });

    function hideLocationConsentModal() { locationConsentModal.classList.add("hidden"); }

    // إنشاء الدراسة
    createStudy.addEventListener("click", () => {
        updateTotalBill();
        const bills = getMonthlyBill();
        if (bills.total <= 0) {
            showMessage("تنبيه", "يرجى إدخال قيمة الفاتورة أولاً.", true);
            return;
        }
        if (priceIQD <= 0) {
            showMessage("تنبيه", "تعذر الحصول على سعر المنظومة.", true);
            return;
        }

        // ==========================
        // الحسابات الحقيقية
        // ==========================

        // الإنتاج الحقيقي بعد خسائر المنظومة
        const realDailyProduction = dailyProduction * systemLossFactor;

        // الاستهلاك اليومي القادم من آخر حاسبة للمستخدم
        const userDailyConsumption = Number(window.userDailyConsumption) || 0;

        // نسبة تغطية المنظومة
        const coverage =
            userDailyConsumption > 0
                ? Math.min((realDailyProduction / userDailyConsumption) * 100, 100)
                : 0;

        // الفائض اليومي
        const surplus = Math.max(
            realDailyProduction - userDailyConsumption,
            0
        );

        // معامل التغطية
        const coverageRatio = coverage / 100;

        // ==========================
        // التوفير المالي
        // ==========================

        // التوفير الشهري
        const monthlySaving = bills.total * coverageRatio;

        // التوفير السنوي
        const yearlySaving = monthlySaving * 12;

        // ==========================
        // استرجاع رأس المال
        // ==========================

        let paybackYears = Infinity;

        if (yearlySaving > 0) {
            paybackYears = Math.ceil(priceIQD / yearlySaving);
        }

        // ==========================
        // الأرباح خلال العمر الافتراضي
        // ==========================

        const remainingYears = Math.max(systemLifetime - paybackYears, 0);

        // صافي الربح
        const totalProfit = remainingYears * yearlySaving;

        console.log({
            priceIQD,
            bills,
            monthlySaving,
            yearlySaving,
            paybackYears,
            remainingYears,
            totalProfit
        });

        // ==========================
        // عرض النتائج
        // ==========================

        currentMonthlyEl.textContent = formatIQD(bills.total);
        currentYearlyEl.textContent = formatIQD(yearlySaving);

        userConsumptionEl.textContent = userDailyConsumption.toFixed(1) + " kWh";
        realProductionEl.textContent = realDailyProduction.toFixed(1) + " kWh";
        coveragePercentEl.textContent = coverage.toFixed(0) + "%";
        dailySurplusEl.textContent = surplus.toFixed(1) + " kWh";
        efficiencyEl.textContent = (systemLossFactor * 100).toFixed(0) + "%";

        savingMonthlyEl.textContent = formatIQD(monthlySaving);
        savingYearlyEl.textContent = formatIQD(yearlySaving);

        paybackPeriodEl.textContent = formatYears(paybackYears);
        profit25YearsEl.textContent = formatIQD(totalProfit);

        panelInfoEl.textContent = totalPanelPower.toFixed(1) + " kWp";
        inverterInfoEl.textContent = inverterCapacity.toFixed(1) + " kW";
        batteryInfoEl.textContent = batteryCapacity.toFixed(1) + " kWh";
        lifetimeInfoEl.textContent = systemLifetime + " سنة";
        // تحليل ذكي
        let analysis = "";
        if (paybackYears <= 3) analysis = "🔥 استثمار ممتاز! تسترد رأس المال في أقل من 3 سنوات.";
        else if (paybackYears <= 5) analysis = "✅ جدوى اقتصادية ممتازة وتوفير كبير على المدى الطويل.";
        else if (paybackYears <= 8) analysis = "☀️ المنظومة مجدية، خصوصاً مع ارتفاع أسعار الكهرباء.";
        else analysis = "ℹ️ فترة الاسترداد طويلة، قد يكون من الأفضل اختيار منظومة بإنتاج أعلى.";
        if (coverage < 80) analysis += " ⚠️ المنظومة لا تغطي كامل استهلاكك، ستحتاج لتقليل الأحمال أو زيادة الإنتاج.";
        aiAnalysis.textContent = analysis;
        studyForm.classList.add("hidden");
        studyResult.classList.remove("hidden");
        studyResult.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    // أزرار المودالات وطلب المنظومة (كما في السابق)
    if (requestBundleBtn) {
        requestBundleBtn.addEventListener("click", () => {
            if (!currentPackageId) { showMessage("تنبيه", "لا توجد باقة محددة.", true); return; }
            bundleModal.classList.remove("hidden");
        });
    }

    if (btnUseGPS) {
        btnUseGPS.addEventListener("click", () => {
            manualAddressDiv.classList.add("hidden");
            gpsLoadingMessage.classList.add("hidden");
            if (!navigator.geolocation) {
                showMessage("تنبيه", "متصفحك لا يدعم تحديد الموقع.", true);
                manualAddressDiv.classList.remove("hidden");
                manualAddressInput.focus();
                return;
            }
            locationConsentModal.classList.remove("hidden");
        });
    }

    if (btnEnableLocation) {
        btnEnableLocation.addEventListener("click", () => {
            hideLocationConsentModal();
            gpsLoadingMessage.classList.remove("hidden");
            navigator.geolocation.getCurrentPosition(
                pos => {
                    gpsLoadingMessage.classList.add("hidden");
                    const gpsLink = `https://maps.google.com/?q=${pos.coords.latitude},${pos.coords.longitude}`;
                    sendBundleRequest(currentPackageId, gpsLink, "موقعي الحالي");
                    hideBundleModal();
                },
                err => {
                    gpsLoadingMessage.classList.add("hidden");
                    showMessage("تنبيه", "تعذر تحديد الموقع. استخدم الإدخال اليدوي.", true);
                    manualAddressDiv.classList.remove("hidden");
                    manualAddressInput.focus();
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        });
    }

    if (btnCancelConsent) btnCancelConsent.addEventListener("click", () => { hideLocationConsentModal(); manualAddressDiv.classList.remove("hidden"); manualAddressInput.focus(); });
    if (btnManualAddress) btnManualAddress.addEventListener("click", () => { gpsLoadingMessage.classList.add("hidden"); manualAddressDiv.classList.remove("hidden"); manualAddressInput.focus(); });
    if (btnSubmitManual) {
        btnSubmitManual.addEventListener("click", () => {
            const addr = manualAddressInput.value.trim();
            if (!addr) { showMessage("تنبيه", "يرجى كتابة العنوان.", true); return; }
            sendBundleRequest(currentPackageId, "", addr);
            hideBundleModal();
        });
    }

    async function sendBundleRequest(packageId, gpsLink, addressText) {
        if (!packageId) return;
        const url = requestBundlePattern.replace('/0/', '/' + packageId + '/');
        try {
            const res = await fetch(url, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json" },
                body: JSON.stringify({ gps_link: gpsLink, address_text: addressText })
            });
            const data = await res.json();
            if (res.ok && data.status === "success") showMessage("تم بنجاح", "تم إرسال طلبك! ستتواصل معك الشركة قريباً.", false);
            else showMessage("خطأ", data.message || "فشل في الإرسال.", true);
        } catch (e) {
            showMessage("خطأ", "تعذر الاتصال بالخادم.", true);
        }
    }
});