// === 1. قاموس اللغات ===
const translations = {
    ar: {
        langName: "العربية",
        heroTitle1: "طاقة الشمس",
        heroTitle2: "لمستقبل أفضل",
        heroDesc: "حلول ذكية ومستدامة للطاقة الشمسية<br>من أجل منزل أكثر كفاءة وكوكب أنظف.",
        btnStart: "ابدأ رحلتك",
        feat1Title: "طاقة نظيفة",
        feat1Desc: "طاقة متجددة وصديقة للبيئة",
        feat2Title: "توفير أكبر",
        feat2Desc: "قلل فواتير الكهرباء وزد من كفاءتك",
        feat3Title: "موثوق وآمن",
        feat3Desc: "تقنيات عالية الجودة وضمان طويل الأمد",
        calcTitle: "احسب توفيرك الآن",
        calcDesc: "اكتشف كم يمكنك توفيره باستخدام الطاقة الشمسية",
        aiTitle: "المساعد الذكي",
        aiDesc: "اسأل الذكاء الاصطناعي عن أفضل الحلول لمنزلك",
        pkgTitle: "العروض والباقات",
        pkgDesc: "اختر الباقة الأنسب لاحتياجاتك وميزانيتك",
        navSupport: "الدعم",
        navCalc: "الحاسبة",
        navAi: "المساعد الذكي",
        navHome: "الرئيسية",
        navPackages: "الباقات",
        navAccount: "حسابي",
        direction: "rtl"
    },
    en: {
        langName: "English",
        heroTitle1: "Solar Energy",
        heroTitle2: "For A Better Future",
        heroDesc: "Smart & sustainable solar solutions<br>for a more efficient home and cleaner planet.",
        btnStart: "Start Your Journey",
        feat1Title: "Clean Energy",
        feat1Desc: "Renewable & eco-friendly",
        feat2Title: "Big Savings",
        feat2Desc: "Reduce bills & increase efficiency",
        feat3Title: "Safe & Reliable",
        feat3Desc: "High quality & long-term warranty",
        calcTitle: "Calculate Savings",
        calcDesc: "Discover how much you can save with solar energy",
        aiTitle: "Smart Assistant",
        aiDesc: "Ask AI for the best solutions for your home",
        pkgTitle: "Offers & Packages",
        pkgDesc: "Choose the best package for your needs and budget",
        navSupport: "Support",
        navCalc: "Calculator",
        navAi: "Smart AI",
        navHome: "Home",
        navPackages: "Packages",
        navAccount: "Account",
        direction: "ltr"
    }
};

// === 2. برمجة زر اللغة والقائمة المنسدلة ===
const langBtn = document.getElementById('langSwitchBtn');
const langDropdown = document.getElementById('langDropdown');
const htmlTag = document.getElementById('htmlTag');
const langOptions = document.querySelectorAll('.lang-option');

if (langBtn && langDropdown) {
    langBtn.addEventListener('click', function (e) {
        langDropdown.classList.toggle('show');
        e.stopPropagation();
    });
    document.addEventListener('click', function (e) {
        if (!langBtn.contains(e.target)) {
            langDropdown.classList.remove('show');
        }
    });
}

langOptions.forEach(option => {
    option.addEventListener('click', function () {
        const lang = this.getAttribute('data-lang');
        const t = translations[lang];

        htmlTag.setAttribute('dir', t.direction);
        htmlTag.setAttribute('lang', lang);

        const updateTxt = (id, txt) => { if(document.getElementById(id)) document.getElementById(id).innerHTML = txt; };

        updateTxt('txt-lang-name', t.langName);
        updateTxt('txt-hero-title1', t.heroTitle1);
        updateTxt('txt-hero-title2', t.heroTitle2);
        updateTxt('txt-hero-desc', t.heroDesc);
        updateTxt('txt-btn-start', t.btnStart);
        updateTxt('txt-feat1-title', t.feat1Title);
        updateTxt('txt-feat1-desc', t.feat1Desc);
        updateTxt('txt-feat2-title', t.feat2Title);
        updateTxt('txt-feat2-desc', t.feat2Desc);
        updateTxt('txt-feat3-title', t.feat3Title);
        updateTxt('txt-feat3-desc', t.feat3Desc);
        updateTxt('txt-calc-title', t.calcTitle);
        updateTxt('txt-calc-desc', t.calcDesc);
        updateTxt('txt-ai-title', t.aiTitle);updateTxt('txt-ai-desc', t.aiDesc);
        updateTxt('txt-pkg-title', t.pkgTitle);
        updateTxt('txt-pkg-desc', t.pkgDesc);
        updateTxt('txt-nav-support', t.navSupport);
        updateTxt('txt-nav-calc', t.navCalc);
        updateTxt('txt-nav-ai', t.navAi);
        updateTxt('txt-nav-home', t.navHome);
        updateTxt('txt-nav-packages', t.navPackages);
        updateTxt('txt-nav-account', t.navAccount);

        langDropdown.classList.remove('show');
    });
});

// === 3. برمجة شريط التنقل السفلي ===



// === 4. برمجة الكروت الرئيسية الفوك (تشغيل الحركة التلقائية واليدوية) ===
let activeMainIndex = 0;
let mainInterval;

function rotateMainSlides() {
    const mainSlides = document.querySelectorAll('.main-card-slide');
    const mainDots = document.querySelectorAll('.main-dot');
    
    if (mainSlides.length === 0) return;

    // إخفاء الحالي
    mainSlides[activeMainIndex].classList.remove("active");
    // الانتقال للتالي تلقائياً
    activeMainIndex = (activeMainIndex + 1) % mainSlides.length;
    // إظهار الجديد
    mainSlides[activeMainIndex].classList.add("active");

    // تحديث النقاط
    mainDots.forEach((dot, idx) => {
        if (idx === activeMainIndex) dot.classList.add("active");
        else dot.classList.remove("active");
    });
}

// دالة التحكم اليدوي عند الضغط على النقاط الفوك
function changeMainSlide(n) {
    clearInterval(mainInterval); // إيقاف المؤقت مؤقتاً عند ضغط المستخدم
    
    const mainSlides = document.querySelectorAll('.main-card-slide');
    const mainDots = document.querySelectorAll('.main-dot');

    mainSlides[activeMainIndex].classList.remove("active");
    activeMainIndex = n;
    mainSlides[activeMainIndex].classList.add("active");

    mainDots.forEach((dot, idx) => {
        if (idx === n) dot.classList.add("active");
        else dot.classList.remove("active");
    });

    // إعادة تشغيل الحركة التلقائية بعد 5 ثوانٍ
    mainInterval = setInterval(rotateMainSlides, 8000);
}

// تشغيل عداد الكروت الفوك تلقائياً أول ما تفتح الصفحة
document.addEventListener("DOMContentLoaded", function () {
    mainInterval = setInterval(rotateMainSlides, 8000); 
});


// === 5. برمجة سلايدر النصائح الـ 100 الجوا (حركة تلقائية ويدوية) ===
document.addEventListener("DOMContentLoaded", function () {
    const tipSlides = document.querySelectorAll(".solaris-tip-slide");
    const tipDots = document.querySelectorAll(".tip-dot");
    let activeTipIndex = 0;
    const totalTips = tipSlides.length;

    if (totalTips === 0) return;

    function rotateTips() {
        tipSlides[activeTipIndex].classList.remove("active");
        activeTipIndex = (activeTipIndex + 1) % totalTips;
        tipSlides[activeTipIndex].classList.add("active");

        const dotMap = activeTipIndex % 5;
        tipDots.forEach((dot, idx) => {
            if (idx === dotMap) dot.classList.add("active");
            else dot.classList.remove("active");
        });
    }

    let tipsInterval = setInterval(rotateTips, 8000);

    // التحكم اليدوي لنقاط النصائح الجوا
    tipDots.forEach((dot, index) => {
        dot.addEventListener("click", () => {
            clearInterval(tipsInterval);

            const currentBatch = Math.floor(activeTipIndex / 5);
            let targetIndex = (currentBatch * 5) + index;

            if (targetIndex >= totalTips) targetIndex = index;

            tipSlides[activeTipIndex].classList.remove("active");
            activeTipIndex = targetIndex;
            tipSlides[activeTipIndex].classList.add("active");

            tipDots.forEach(d => d.classList.remove("active"));
            dot.classList.add("active");

            tipsInterval = setInterval(rotateTips, 8000);
        });
    });
});