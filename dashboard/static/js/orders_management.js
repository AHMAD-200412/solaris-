document.addEventListener("DOMContentLoaded", function () {
    // استخدمنا الـ Event Delegation حتى يشتغل على كل الأزرار حتى لو تحملت الصفحة بعدين
    document.addEventListener('click', function (e) {

        // 1️⃣ التعامل مع زر "تحديث الطلب" (المودل القديم)
        const updateBtn = e.target.closest('.btn-update-order');
        if (updateBtn) {
            const orderId = updateBtn.dataset.id;
            const form = document.getElementById('updateOrderForm');
            // تم تصحيح علامات التنصيص (Backticks) للرابط
            if (form) form.action = `/dashboard/orders/update/${orderId}/`;

            const statusSelect = document.getElementById('modalOrderStatus');
            if (statusSelect) statusSelect.value = updateBtn.dataset.status;

            // 1. دالة فك التشفير (خليها بأي مكان فارغ فوك بملف الجافاسكربت)
            function decodeHtml(html) {
                var txt = document.createElement("textarea");
                txt.innerHTML = html;
                return txt.value;
            }

            // 2. الكود اللي يتنفذ من تدوس على زر "تحديث"
            const loadCalcArea = document.getElementById('modalLoadCalc');
            if (loadCalcArea) {
                // نجيب البيانات المشفرة من الزر (استخدمنا dataset.loadcalc)
                let rawData = updateBtn.dataset.loadcalc || '';

                // نفك التشفير ونعرضه كـ HTML حقيقي داخل الـ div
                loadCalcArea.innerHTML = decodeHtml(rawData);
            }
            const extraFeesInput = document.getElementById('modalExtraFees');
            if (extraFeesInput) extraFeesInput.value = updateBtn.dataset.extrafees || '0';

            const extraReasonInput = document.getElementById('modalExtraReason');
            if (extraReasonInput) extraReasonInput.value = updateBtn.dataset.reason || '';

            const techReportArea = document.getElementById('modalTechReport');
            if (techReportArea) techReportArea.value = updateBtn.dataset.report || '';

            const modalElement = document.getElementById('updateOrderModal');
            if (modalElement) {
                let modalInstance = bootstrap.Modal.getInstance(modalElement);
                if (!modalInstance) modalInstance = new bootstrap.Modal(modalElement);
                modalInstance.show();
            }
        }

        // 2️⃣ 🌟 السحر الجديد: التعامل مع زر "توليد خطة الأقساط"
        const generateBtn = e.target.closest('.btn-generate-plan');
        if (generateBtn) {
            const orderId = generateBtn.dataset.orderId;
            const customerName = generateBtn.dataset.customer;
            const totalAmount = generateBtn.dataset.total;

            // تحديث رابط الـ form ليأخذ آي دي الطلب
            const form = document.getElementById('generatePlanForm');
            if (form) form.action = `/dashboard/orders/generate-plan/${orderId}/`;

            // ملء الحقول تلقائياً بالمعلومات الجاهزة
            const nameInput = document.getElementById('planCustomerName');
            if (nameInput) nameInput.value = customerName;

            const totalInput = document.getElementById('planTotalAmount');
            if (totalInput) totalInput.value = totalAmount;

            // تصفير حقول الإدخال (المقدمة والأشهر) حتى المدير يكتبها من جديد
            const downPaymentInput = document.getElementById('planDownPayment');
            if (downPaymentInput) downPaymentInput.value = "";

            const monthsInput = document.getElementById('planMonths');
            if (monthsInput) monthsInput.value = "";

            // إظهار المودل الجديد الخاص بالأقساط
            const modalElement = document.getElementById('generatePlanModal');
            if (modalElement) {
                let modalInstance = bootstrap.Modal.getInstance(modalElement);
                if (!modalInstance) modalInstance = new bootstrap.Modal(modalElement);
                modalInstance.show();
            }
        }
    });
});