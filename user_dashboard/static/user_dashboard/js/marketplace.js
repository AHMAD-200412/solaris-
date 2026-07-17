document.addEventListener('DOMContentLoaded', function () {
    // ==========================================
    // عناصر الصفحة
    // ==========================================
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const tabs = document.querySelectorAll('.tab');
    const productCards = document.querySelectorAll('.product-list .product-card');
    const featuredWrapper = document.getElementById('featuredWrapper');
    const featuredSlider = document.getElementById('featuredSlider');
    const nearMeBtn = document.getElementById('nearMeBtn');
    const packagesCounter = document.getElementById('packagesCounter');
    const noResultsMsg = document.getElementById('noResultsMsg');

    let activeCategory = "الكل";

    // ==========================================
    // 1) فلترة الباقات + إخفاء العروض المميزة عند البحث
    // ==========================================
    function normalizeText(value) {
        return (value || "").toString().trim().toLowerCase();
    }

    function updateFeaturedVisibility(searchTerm) {
        if (!featuredWrapper) return;
        if (searchTerm.length > 0) {
            featuredWrapper.style.display = 'none';
        } else {
            featuredWrapper.style.display = 'block';
        }
    }

    function updateSearchClearButton(searchTerm) {
        if (!clearSearchBtn) return;
        if (searchTerm.length > 0) {
            clearSearchBtn.style.display = 'flex';
        } else {
            clearSearchBtn.style.display = 'none';
        }
    }

    function filterCards() {
        const searchTerm = normalizeText(searchInput ? searchInput.value : "");

        updateFeaturedVisibility(searchTerm);
        updateSearchClearButton(searchTerm);

        let visibleCount = 0;

        productCards.forEach(card => {
            const title = normalizeText(card.getAttribute('data-title'));
            const company = normalizeText(card.getAttribute('data-company'));
            const isInstallment = card.getAttribute('data-installment') === 'true';

            const matchesSearch = title.includes(searchTerm) || company.includes(searchTerm);

            let matchesCategory = false;
            if (activeCategory === "الكل") {
                matchesCategory = true;
            } else if (activeCategory === "اقساط") {
                matchesCategory = isInstallment;
            } else {
                matchesCategory = category === activeCategory;
            }

            if (matchesSearch && matchesCategory) {
                card.style.display = "flex";
                visibleCount++;
            } else {
                card.style.display = "none";
            }
        });

        if (packagesCounter) {
            packagesCounter.innerText = visibleCount + " باقات";
        }

        if (noResultsMsg) {
            noResultsMsg.style.display = (visibleCount === 0) ? "block" : "none";
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterCards);
    }

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            if (searchInput) {
                searchInput.value = '';
                filterCards();
            }
        });
    }

    
    // ==========================================
    // 2) تقليب العروض المميزة تلقائياً
    // ==========================================
    if (featuredSlider && featuredSlider.children.length > 1) {
        setInterval(() => {
            let maxScroll = featuredSlider.scrollWidth - featuredSlider.clientWidth;
            if (Math.abs(featuredSlider.scrollLeft) >= maxScroll - 15) {
                featuredSlider.scrollTo({ left: 0, behavior: 'smooth' });
            } else {
                let cardWidth = featuredSlider.querySelector('.feat-card').offsetWidth + 12;
                featuredSlider.scrollBy({ left: -cardWidth, behavior: 'smooth' });
            }
        }, 6000);
    }

    // ==========================================
    // 3) تحديد موقع الشركات (GPS)
    // ==========================================
    if (nearMeBtn) {
        nearMeBtn.addEventListener('click', function () {
            if ("geolocation" in navigator) {
                let originalText = this.innerHTML;
                this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> جاري التحديد...';
                this.style.pointerEvents = "none";

                navigator.geolocation.getCurrentPosition(
                    function (position) {
                        window.location.href=`?lat=${position.coords.latitude}&lon=${position.coords.longitude}`;
                    },
                    function (error) {
                        alert("يرجى السماح بالوصول لموقعك لعرض الشركات القريبة.");
                        nearMeBtn.innerHTML = originalText;
                        nearMeBtn.style.pointerEvents = "auto";
                    },
                    { enableHighAccuracy: true, timeout: 10000 }
                );
            } else {
                alert("متصفحك لا يدعم تحديد الموقع.");
            }
        });
    }
});

// ==========================================
// 4) التحكم بالنافذة المنبثقة (Modal)
// ==========================================
const bundleModal = document.getElementById('bundleModal');

function openModal(btn) {
    // 1. جلب البيانات الأساسية
    const title = btn.getAttribute('data-title');
    const desc = btn.getAttribute('data-desc');
    const price = btn.getAttribute('data-price');
    const company = btn.getAttribute('data-company');

    // 2. جلب بيانات الأقساط والمكونات
    const hasInstallments = btn.getAttribute('data-installments') === 'true';
    const downPayment = btn.getAttribute('data-down-payment');
    const monthly = btn.getAttribute('data-monthly');
    const months = btn.getAttribute('data-months');
    const componentsStr = btn.getAttribute('data-components') || '';
    // 🌍 توجيه الزبون لموقع الشركة عبر GPS
    const gpsCoordinates = btn.getAttribute('data-gps');
    const locationLink = document.getElementById('mLocationLink');

    if (locationLink) {
        if (gpsCoordinates && gpsCoordinates.trim() !== '') {
            // إذا الشركة مسجلة موقعها، نخلي الرابط يروح للإحداثيات مباشرة ونظهر الزر
            locationLink.href = `https://www.google.com/maps?q=${encodeURIComponent(gpsCoordinates.trim())}`;
            locationLink.style.display = 'flex';
        } else {
            // إذا الشركة مامسجلة موقعها، نخفي الزر حتى ما يطلع للزبون ويضغط عليه على الفاضي
            locationLink.style.display = 'none';
        }
    }
    // 3. تعبئة البيانات الأساسية في الواجهة
    document.getElementById('mTitle').innerHTML = '<i class="fa-solid fa-solar-panel"></i> ' + title;
    document.getElementById('mDesc').innerText = desc;
    document.getElementById('mPrice').innerText = price;
    document.getElementById('mCompany').innerText = company;

    // 4. معالجة وعرض مكونات المنظومة (عناصر الباقة)
    const compBox = document.getElementById('mComponentsBox');
    const compList = document.getElementById('mComponentsList');
    compList.innerHTML = ''; // تنظيف المكونات القديمة

    if (componentsStr.trim() !== '') {
        const componentsArray = componentsStr.split(',');
        componentsArray.forEach(compName => {
            if (compName.trim()) {
                const badge = document.createElement('span');
                badge.className = 'component-badge';
                // تصميم الباج مال المكونات
                badge.innerHTML = `<i class="fa-solid fa-circle-check text-gold" style="color:var(--gold); margin-left:5px;"></i> ${compName.trim()}`;
                compList.appendChild(badge);
            }
        });
        compBox.style.display = 'block';
    } else {
        compBox.style.display = 'none';
    }
    const instBox = document.getElementById('mInstallmentsBox');
    if (hasInstallments) {
        document.getElementById('mDownPayment').innerText = downPayment;
        document.getElementById('mMonthly').innerText = monthly;
        document.getElementById('mMonths').innerText = months + ' أشهر';
        instBox.style.display = 'grid';
    } else {
        instBox.style.display = 'none';
    }

    // إظهار المودال (التصحيح هنا: نستخدم كلاس show حتى يتطابق وية الـ CSS)
    document.getElementById('bundleModal').classList.add('show');
}

function closeModal() {
    if (bundleModal) {
        bundleModal.classList.remove('show');
    }
}

if (bundleModal) {
    bundleModal.addEventListener('click', function (e) {
        if (e.target === bundleModal) closeModal();
    });
}

// ==========================================
// 5) طلب الباقات وإلغائها (AJAX)
// ==========================================
function getCSRFToken() {
    const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return tokenInput ? tokenInput.value : '';
}


let currentOrderBundleId = null;

function requestBundle(bundleId) {
    currentOrderBundleId = bundleId;

    // إذا المتصفح يدعم Permissions API
    if (navigator.permissions) {
        navigator.permissions.query({ name: 'geolocation' }).then(function(result) {

            // المستخدم سامح بالموقع
            if (result.state === "granted") {
                getLocationAndSend();
            }

            // أول مرة أو ما مختار شيء
            else if (result.state === "prompt") {
                getLocationAndSend();
            }

            // المستخدم رافض
            else {
                openManualAddressModal();
            }

        });
    } else {
        // إذا المتصفح ما يدعم Permissions API
        getLocationAndSend();
    }
}
function getLocationAndSend() {

    navigator.geolocation.getCurrentPosition(

        function(position) {

            document.getElementById('gpsLat').value = position.coords.latitude;
            document.getElementById('gpsLng').value = position.coords.longitude;

            submitOrder();

        },

        function(error) {

            // إذا رفض أو فشل
            openManualAddressModal();

        },

        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }

    );

}


function openManualAddressModal() {

    document.getElementById('gpsLat').value = '';
    document.getElementById('gpsLng').value = '';
    document.getElementById('manualAddress').value = '';

    document.getElementById('orderConfirmModal').style.display = 'flex';

}

function closeOrderModal() {
    document.getElementById('orderConfirmModal').style.display = 'none';
    currentOrderBundleId = null;
}


function submitOrder() {
    if (!currentOrderBundleId) return;
    
    const lat = document.getElementById('gpsLat').value;
    const lng = document.getElementById('gpsLng').value;
    const manualAddr = document.getElementById('manualAddress').value.trim();
    
    // شرط ذكي: لازم يا إما محدد GPS أو كاتب عنوان
    if (!lat && !lng && manualAddr === '') {
        alert('عذراً عزيزي، يرجى تحديد موقعك بالـ GPS أو كتابة العنوان يدوياً لتتمكن الشركة من الوصول إليك بسهولة! 🙏');
        return;
    }
    
    // تجهيز البيانات للإرسال
    let payload = {};
    if (lat && lng) {
        payload.gps_link = `https://www.google.com/maps?q=${lat},${lng}`;
    }
    if (manualAddr !== '') {
        payload.address_text = manualAddr;
    }
    
    const btn = document.getElementById('confirmOrderBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = 'جاري الإرسال... 🚀';
    btn.disabled = true;

    fetch(`/user/marketplace/request/${currentOrderBundleId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || "تم إرسال الطلب وتحديد الموقع بنجاح! 🎊");
        if (data.status === "success") {
            closeOrderModal();
            location.reload();
        } else {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    })
    .catch(() => {
        alert("حدث خطأ أثناء إرسال الطلب، يرجى المحاولة مرة أخرى.");
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}


function cancelBundle(bundleId) {
    if (!confirm("هل أنت متأكد من رغبتك في إلغاء هذا الطلب؟ 🛑")) return;

    fetch(`/user/marketplace/cancel/${bundleId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/json"
        }
    })
        .then(res => res.json())
        .then(data => {
            alert(data.message || "تم إلغاء الطلب");
            if (data.status === "success") {
                location.reload();
            }
        })
        .catch(() => {
            alert("حدث خطأ أثناء الإلغاء.");
        });
}
