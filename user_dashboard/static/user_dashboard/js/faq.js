document.addEventListener("DOMContentLoaded", () => {
    const faqItems = document.querySelectorAll(".faq-item");

    faqItems.forEach(item => {
        const question = item.querySelector(".faq-question");
        question.addEventListener("click", () => {
            // إغلاق العناصر الأخرى المفتوحة (اختياري)
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove("active");
                }
            });
            // تبديل حالة العنصر الحالي
            item.classList.toggle("active");
        });
    });
});