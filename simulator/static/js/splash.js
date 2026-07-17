document.addEventListener("DOMContentLoaded", () => {

    const splash = document.getElementById("splash-screen");
    const page = document.getElementById("page-content");
    const title = document.getElementById("typing-title");

    const appName = "SolarIQ";
    let index = 0;

    // إخفاء الصفحة بالبداية
    if (page) {
        page.style.opacity = "0";
    }

    // كتابة اسم التطبيق
    function typeWriter() {

        if (index < appName.length) {

            title.textContent += appName.charAt(index);

            index++;

            setTimeout(typeWriter, 180);

        }

    }

    setTimeout(typeWriter, 900);

    // تأثير نبضة للشعار
    const logo = document.querySelector(".app-logo");

    setInterval(() => {

        logo.animate([

            {
                transform: "scale(1)"
            },

            {
                transform: "scale(1.08)"
            },

            {
                transform: "scale(1)"
            }

        ], {

            duration: 900

        });

    }, 2000);

    // ظهور النص بالتدريج
    setTimeout(() => {

        document.querySelector(".subtitle").style.opacity = "1";

    }, 2200);

    // تعبئة الخط الذهبي
    setTimeout(() => {

        document.querySelector(".gold-fill").style.width = "100%";

    }, 1200);

    // شريط التحميل
    const progress = document.querySelector(".loading-progress");

    let value = 0;

    const loading = setInterval(() => {

        value++;

        progress.style.width = value + "%";

        if (value >= 100) {

            clearInterval(loading);

        }

    }, 50);

    // تأثير لمعان على الاسم
    setInterval(() => {

        title.animate([

            {
                opacity: .8,
                letterSpacing: "3px"
            },

            {
                opacity: 1,
                letterSpacing: "5px"
            },

            {
                opacity: .8,
                letterSpacing: "3px"
            }

        ], {

            duration: 2500

        });

    }, 2500);

    // حركة عشوائية للجسيمات
    document.querySelectorAll(".floating-particles span").forEach(p => {

        setInterval(() => {

            p.style.left = Math.random() * 100 + "%";

        }, 5000);

    });

    // انتهاء شاشة البداية
    setTimeout(() => {

        splash.classList.add("hide");

        setTimeout(() => {

            splash.remove();

            if (page) {

                page.style.opacity = "1";

            }

        }, 1300);

    }, 5000);

});