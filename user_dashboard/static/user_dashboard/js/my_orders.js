document.addEventListener("DOMContentLoaded", () => {
    // ========== إلغاء الطلب ==========
    const cancelButtons = document.querySelectorAll(".cancel-order-btn");
    const cancelModal = document.getElementById("cancelOrderModal");
    const confirmCancelBtn = document.getElementById("confirmCancelBtn");
    const cancelOrderCancel = document.getElementById("cancelOrderCancel");

    cancelButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            orderToModify = btn.dataset.orderId;
            cancelModal.classList.remove("hidden");
        });
    });

    cancelOrderCancel.addEventListener("click", () => {
        cancelModal.classList.add("hidden");
        orderToModify = null;
    });

    confirmCancelBtn.addEventListener("click", async () => {
        if (!orderToModify) return;
        try {
            const res = await fetch(`/user/marketplace/cancel/${ orderToModify }/`, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken }
            });
            const data = await res.json();
            if (data.status === "success") {
                window.location.reload();
            } else {
                alert(data.message || "فشل الإلغاء");
            }
            cancelModal.classList.add("hidden");
        } catch (e) {
            alert("خطأ في الاتصال");
            cancelModal.classList.add("hidden");
        }
    });

    // ========== حذف الطلب ==========
    const deleteButtons = document.querySelectorAll(".delete-order-btn");
    const deleteModal = document.getElementById("deleteOrderModal");
    const confirmDeleteOrderBtn = document.getElementById("confirmDeleteOrderBtn");
    const deleteOrderCancel = document.getElementById("deleteOrderCancel");

    deleteButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            orderToModify = btn.dataset.orderId;
            deleteModal.classList.remove("hidden");
        });
    });

    deleteOrderCancel.addEventListener("click", () => {
        deleteModal.classList.add("hidden");
        orderToModify = null;
    });

    confirmDeleteOrderBtn.addEventListener("click", async () => {
        if (!orderToModify) return;
        try {
            const res = await fetch(`/user/my-orders/delete/${orderToModify}/`, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken }
            });
            const data = await res.json();
            if (data.status === "success") {
                window.location.reload();
            } else {
                alert(data.message || "فشل الحذف");
            }
            deleteModal.classList.add("hidden");
        } catch (e) {
            alert("خطأ في الاتصال");
            deleteModal.classList.add("hidden");
        }
    });

    // إغلاق المودالات عند النقر خارجها
    window.addEventListener("click", (e) => {
        if (e.target === cancelModal) cancelModal.classList.add("hidden");
        if (e.target === deleteModal) deleteModal.classList.add("hidden");
    });
});
