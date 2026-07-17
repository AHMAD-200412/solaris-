// ========================================================
// 🌐 الملف المشترك النهائي (dashboard_shared.js)
// ========================================================
document.addEventListener("DOMContentLoaded", function () {

    // نستخدم التقاط الأحداث (Event Capture) لضمان تنفيذ كودنا أولاً
    document.addEventListener('click', function (e) {
        
        // البحث عن الزر بأي صيغة ممكنة مع وجود (||) للربط الصحيح
        const toggleBtn = e.target.closest('.menu-toggle') ||  e.target.closest('.menu-toggle-btn') || e.target.closest('#menuToggle');

        if (toggleBtn) {
            e.preventDefault(); 
            e.stopPropagation(); // يمنع أي سكريبت ثاني من التدخل والتعطيل
            
            const sidebar = document.querySelector('.sidebar');
            const mainContent = document.querySelector('.main-content');
            
            if (sidebar) {
                // منطق فتح/إغلاق القائمة
                if (window.innerWidth <= 992) {
                    sidebar.classList.toggle('open');
                } else {
                    sidebar.classList.toggle('closed');
                    if (mainContent) mainContent.classList.toggle('expanded');
                }
            }
        }
    }, true); // الـ true هنا هي سر نجاح الكود في الصفحات المعاندة
});