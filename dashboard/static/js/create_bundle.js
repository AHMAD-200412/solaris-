document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // إظهار وإخفاء حقل الكمية
    // =========================
    function toggleQuantity(checkbox) {
        const qty = checkbox.parentElement.querySelector(".quantity-input");

        if (!qty) return;

        if (checkbox.checked) {
            qty.disabled = false;
            qty.style.display = "block";
        } else {
            qty.disabled = true;
            qty.style.display = "none";
            qty.value = 1;
        }
    }

    document.querySelectorAll(".add-component-checkbox").forEach(cb => {
        cb.addEventListener("change", function () {
            toggleQuantity(this);
        });
    });

    document.querySelectorAll(".edit-component-checkbox").forEach(cb => {
        cb.addEventListener("change", function () {
            toggleQuantity(this);
        });
    });

    // =====================================
    // البحث الفوري
    // =====================================
    const searchInput = document.getElementById("package-search");

    if (searchInput) {

        searchInput.addEventListener("input", function (e) {

            const searchTerm = e.target.value.toLowerCase().trim();

            document.querySelectorAll(".package-item-card").forEach(card => {

                const title = card.getAttribute("data-title") || "";

                card.style.display = title.includes(searchTerm) ? "" : "none";

            });

        });

    }

    // =====================================
    // الأقساط
    // =====================================

    const addSwitch = document.getElementById("addIsInstallment");
    const addContainer = document.getElementById("addInstallmentFieldsContainer");

    if (addSwitch && addContainer) {

        addSwitch.addEventListener("change", function () {

            addContainer.style.display = this.checked ? "flex" : "none";

        });

    }

    const editSwitch = document.getElementById("editIsInstallment");
    const editContainer = document.getElementById("editInstallmentFieldsContainer");

    if (editSwitch && editContainer) {

        editSwitch.addEventListener("change", function () {

            editContainer.style.display = this.checked ? "flex" : "none";

        });

    }

    // =====================================
    // أحداث الأزرار
    // =====================================

    document.addEventListener("click", function (e) {

        // ==========================
        // زر تعديل
        // ==========================

        const editBtn = e.target.closest(".btn-edit-package");

        if (editBtn) {

            const id = editBtn.dataset.id;

            const form = document.getElementById("editPackageForm");

            if (form)
                form.action = `/dashboard/bundle/edit/${ id }/`;

            document.getElementById("editTitle").value = editBtn.dataset.title || "";
            document.getElementById("editTotalPrice").value = editBtn.dataset.price || "";
            document.getElementById("editDescription").value = editBtn.dataset.description || "";

            const isInstallment = editBtn.dataset.installment === "true";

            editSwitch.checked = isInstallment;

            editContainer.style.display = isInstallment ? "flex" : "none";

            document.getElementById("editDownPayment").value = editBtn.dataset.downpayment || "0";
            document.getElementById("editMonthlyInstallment").value = editBtn.dataset.monthly || "0";
            document.getElementById("editDurationMonths").value = editBtn.dataset.duration || "0";

            // ==========================
            // تصفير جميع القطع والكميات
            // ==========================

            document.querySelectorAll(".edit-component-checkbox").forEach(cb => {

                cb.checked = false;

                const qty = cb.parentElement.querySelector(".quantity-input");
                if (qty) {
                    qty.value = 1;
                    qty.disabled = true;
                    qty.style.display = "none";
                }

            });

            // ==========================
            // تعبئة القطع والكميات
            // الصيغة:
            // 2:6,8:1,15:4
            // ==========================

            const components = editBtn.dataset.components
                ? editBtn.dataset.components.split(",")
                : [];

            components.forEach(item => {

                const parts = item.split(":");

                if (parts.length !== 2) return;

                const productId = parts[0];
                const quantity = parts[1];

                const checkbox = document.getElementById(`edit_comp_${ productId }`);

                if (!checkbox) return;

                checkbox.checked = true;

                const qty = checkbox.parentElement.querySelector(".quantity-input");

                if (qty) {
                    qty.disabled = false;
                    qty.style.display = "block";
                    qty.value = quantity;
                }

            });

            const editModalElement = document.getElementById("editPackageModal");

            if (editModalElement) {

                let modalInstance = bootstrap.Modal.getInstance(editModalElement);

                if (!modalInstance)
                    modalInstance = new bootstrap.Modal(editModalElement);

                modalInstance.show();

            }

            return;
        }

        // ==========================
        // زر الترويج
        // ==========================

        const promoteBtn = e.target.closest(".btn-promote-package");

        if (promoteBtn) {

            const id = promoteBtn.dataset.id;
            const title = promoteBtn.dataset.title;

            const form = document.getElementById("promotePackageForm");

            if (form)
                form.action = `/dashboard/bundle/promote/${ id }/`;

            document.getElementById("promotePackageTitle").innerText = title;

            const promoteModalElement = document.getElementById("promotePackageModal");

            if (promoteModalElement) {

                let modalInstance = bootstrap.Modal.getInstance(promoteModalElement);

                if (!modalInstance)
                    modalInstance = new bootstrap.Modal(promoteModalElement);

                modalInstance.show();

            }

        }

    });

});