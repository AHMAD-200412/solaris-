// ========================================================
// 💳 ملف إدارة الأقساط المطور والآمن (installments.js)
// ========================================================

document.addEventListener("DOMContentLoaded", function () {
    // 1️⃣ منطق البحث الذكي في الجدول
    const searchInput = document.getElementById("searchInstallments");
    if (searchInput) {
        searchInput.addEventListener("keyup", function () {
            let filter = this.value.toLowerCase();
            let rows = document.querySelectorAll(".installment-row");

            rows.forEach(row => {
                let customer = row.dataset.customer ? row.dataset.customer.toLowerCase() : '';
                let order = row.dataset.order ? row.dataset.order.toLowerCase() : '';
                let phone = row.dataset.phone ? row.dataset.phone.toLowerCase() : '';

                // ✅ تم تصحيح الشرط وإضافة علامات الـ OR المنطقية || بشكل صحيح
                if (customer.includes(filter) || order.includes(filter) || phone.includes(filter)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        });
    }
});

// ========================================================
// 🔴 الدالات بالخارج (خارج الـ DOMContentLoaded) لكي يراها الـ HTML
// ========================================================

// 1️⃣ دالات نافذة الإضافة (Add Modal)
function openModal() {
    const modal = document.getElementById("addModal");
    if (modal) {
        modal.style.display = "block";
        document.body.style.overflow = "hidden"; // منع سكرول الصفحة الخلفية
    }
}

function closeModal() {
    const modal = document.getElementById("addModal");
    if (modal) {
        modal.style.display = "none";
        document.body.style.overflow = "auto"; // إعادة السكرول لطبيعته
    }
}

// 2️⃣ دالة كشف الحساب الكامل (زر العين) - استدعاء AJAX
function openDetailsModal(planId) {
    const modal = document.getElementById("detailsModal")
    const tableBody = document.getElementById("detailsTableBody");

    // ✅ تم تصحيح الشرط المنطقي هنا أيضاً باستخدام ||
    if (!modal || !tableBody) return;

    // رسالة مؤقتة لحين تحميل البيانات
    tableBody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:15px; color:#999;">جاري تحميل كشف الحساب الكامل...</td></tr>`;
    modal.style.display = "block";

    // طلب البيانات من سيرفر جانغو
    fetch(`/dashboard/installments/plan/${planId}/`)
        .then(response => {
            if (!response.ok) throw new Error("Network error");
            return response.json();
        })
        .then(data => {
            // جلب عناصر واجهة الـ HTML
            const customerName = document.getElementById("detCustomerName");
            const customerPhone = document.getElementById("detCustomerPhone");
            const purchasedItems = document.getElementById("detPurchasedItems"); // 🌟 العنصر الجديد
            const totalAmount = document.getElementById("detTotalAmount").textContent=formatMoney(data.total_amount);
            const deleteContainer = document.getElementById("deleteActionContainer");

            // حقن البيانات المستلمة في الواجهة
            if (customerName) customerName.innerText = data.customer_name;
            if (customerPhone) customerPhone.innerText = data.phone;
            if (purchasedItems) purchasedItems.innerText = data.purchased_items; // 🌟 عرض تفاصيل المشتريات
            if (totalAmount) totalAmount.innerText = data.total_amount;

            // تفريغ الجدول وبنائه من جديد بناءً على الدفعات
            tableBody.innerHTML = "";
            data.payments.forEach(p => {
                let badgeClass = p.status === "paid" ? "paid" : (p.status === "late" ? "late" : "pending");
                tableBody.innerHTML +=
                    `<tr>
                        <td>الشهر ${p.month_number}</td>
                        <td>${formatMoney(p.amount)}</td>
                        <td>${p.due_date}</td>
                        <td><span class="status-badge ${badgeClass}">${p.status_ar}</span></td>
                    </tr>`;
            });// 💡 الشرط السحري: إذا دافع كلشي، نظهر زر الحذف وتصفية الحساب
            if (deleteContainer) {
                if (data.all_paid) {
                    deleteContainer.className = "delete-container"; // تفعيل الستايل الخاص بالحذف
                    deleteContainer.innerHTML = 
                       `<div class="alert-success-clear">🎉 هذا المشترك أكمل سداد جميع الأقساط بنجاح!</div>
                        <a href="/dashboard/installments/delete/${data.plan_id}/" 
                        class="btn-delete-customer" 
                        onclick="return confirm('⚠️ تحذير: هل أنت متأكد من حذف هذا المشترك نهائياً من قاعدة البيانات وصفحة الأقساط؟')">
                           <i class="fas fa-trash-alt"></i> حذف المشترك وتصفية الحساب
                        </a>`;
                } else {
                    deleteContainer.innerHTML = "";
                    deleteContainer.className = ""; // إخفاء الستايل إذا لم يسدد بالكامل بعد
                }
            }
        })
        .catch(error => {
            console.error("Error fetching installment details:", error);
            tableBody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#ef4444; padding:15px;">حدث خطأ أثناء تحميل البيانات</td></tr>`;
        });
}

// 3️⃣ دالة إغلاق نافذة التفاصيل
function closeDetailsModal() {
    const modal = document.getElementById("detailsModal");
    if (modal) {
        modal.style.display = "none";
    }
}

// 4️⃣ إغلاق النوافذ تلقائياً عند الضغط في أي مكان خارج صندوق الـ Modal
window.addEventListener("click", function (event) {
    const detailsModal = document.getElementById("detailsModal");
    const addModal = document.getElementById("addModal");

    if (event.target === detailsModal) closeDetailsModal();
    if (event.target === addModal) closeModal();
});
function formatMoney(amount) {
    amount = Math.floor(Number(amount));

    const millions = Math.floor(amount / 1000000);
    const thousands = Math.floor((amount % 1000000) / 1000);
    const dinars = amount % 1000;

    let parts = [];

    if (millions) parts.push(`${millions} مليون`);
    if (thousands) parts.push(`${thousands} ألف`);
    if (dinars) parts.push(`${dinars} دينار`);

    return parts.length ? parts.join(" و") : "0 دينار";
}