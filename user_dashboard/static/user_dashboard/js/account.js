document.addEventListener("DOMContentLoaded", () => {
    // ========== عناصر المودالات (مع التأكد من وجودها) ==========
    const successModal = document.getElementById("successModal");
    const successIcon = document.getElementById("successIcon");
    const successTitle = document.getElementById("successTitle");
    const successMessage = document.getElementById("successMessage");
    const successOkBtn = document.getElementById("successOkBtn");

    const messageModal = document.getElementById("messageModal");
    const messageModalTitle = document.getElementById("messageModalTitle");
    const messageModalText = document.getElementById("messageModalText");
    const messageModalOk = document.getElementById("messageModalOk");
    const messageIcon = document.getElementById("messageIcon");

    // ========== دوال عامة (آمنة) ==========
    function showSuccess(title, message, icon = "fa-circle-check") {
        if (!successModal || !successTitle || !successMessage || !successIcon) return;
        successTitle.textContent = title;
        successMessage.textContent = message;
        successIcon.className = `fa-solid ${icon}`;
        successModal.classList.remove("hidden");
    }

    function showMessage(title, text, isError = false) {
        if (!messageModal || !messageModalTitle || !messageModalText) return;
        if (messageIcon) {
            const i = messageIcon.querySelector("i");
            if (i) {
                i.className = isError ? "fa-solid fa-circle-exclamation" : "fa-solid fa-circle-info";
            }
            messageIcon.style.color = isError ? "#ff6b6b" : "#f0c878";
        }
        messageModalTitle.textContent = title;
        messageModalText.textContent = text;
        messageModalTitle.style.color = isError ? "#ff6b6b" : "#ffffff";
        messageModal.classList.remove("hidden");
    }

    function hideMessageModal() {
        if (messageModal) messageModal.classList.add("hidden");
    }

    function hideSuccessModal() {
        if (successModal) successModal.classList.add("hidden");
    }

    // ربط أزرار الإغلاق بأمان
    if (successOkBtn) successOkBtn.addEventListener("click", hideSuccessModal);
    if (messageModalOk) messageModalOk.addEventListener("click", hideMessageModal);

    // إغلاق المودالات عند النقر خارجها
    window.addEventListener("click", (e) => {
        if (e.target === successModal) hideSuccessModal();
        if (e.target === messageModal) hideMessageModal();
    });

    // ========== الوضع الداكن ==========
    const darkModeCheckbox = document.getElementById("darkModeCheckbox");
    if (localStorage.getItem("theme") === "light") {
        darkModeCheckbox.checked = false;
    } else {
        darkModeCheckbox.checked = true;
    }
    darkModeCheckbox.addEventListener("change", () => {
        toggleTheme(); // من theme.js
    });

    // ========== دوال المودال العامة ==========
    function openModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.remove("hidden");
    }
    function closeModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.add("hidden");
    }
    document.querySelectorAll("[data-close]").forEach(btn => {
        btn.addEventListener("click", () => closeModal(btn.dataset.close));
    });
    window.addEventListener("click", e => {
        if (e.target.classList.contains("modal-overlay")) closeModal(e.target.id);
    });

    // ========== الشكوى والاقتراح ==========
    const feedbackModal = document.getElementById("feedbackModal");
    const feedbackModalTitle = document.getElementById("feedbackModalTitle");
    const feedbackMessage = document.getElementById("feedbackMessage");
    const sendFeedbackBtn = document.getElementById("sendFeedbackBtn");
    let feedbackType = "complaint";

    const complaintBtn = document.querySelector('a.menu-item:has(.fa-comment-dots)');
    const suggestionBtn = document.querySelector('a.menu-item:has(.fa-lightbulb)');
    function openFeedbackModal(type) {
        feedbackType = type;
        feedbackModalTitle.textContent = type === "complaint" ? "📝 إرسال شكوى" : "💡 إرسال اقتراح";
        feedbackMessage.value = "";
        feedbackModal.classList.remove("hidden");
        feedbackMessage.focus();
    }

    if (complaintBtn) {
        complaintBtn.addEventListener("click", (e) => {
            e.preventDefault();
            openFeedbackModal("complaint");
        });
    }
    if (suggestionBtn) {
        suggestionBtn.addEventListener("click", (e) => {
            e.preventDefault();
            openFeedbackModal("suggestion");
        });
    }

    sendFeedbackBtn.addEventListener("click", async () => {
        const message = feedbackMessage.value.trim();
        if (!message) {
            showMessage("تنبيه", "يرجى كتابة رسالة.", true);
            return;
        }
        try {
            const res = await fetch(sendFeedbackUrl, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json" },
                body: JSON.stringify({ type: feedbackType, message: message })
            });
            const data = await res.json();
            if (data.success) {
                closeModal("feedbackModal");
                showSuccess("تم بنجاح", "تم إرسال رسالتك بنجاح. سنراجعها قريباً.", "fa-paper-plane");
            } else {
                showMessage("خطأ", data.error || "فشل الإرسال", true);
            }
        } catch (e) {
            showMessage("خطأ", "حدث خطأ في الاتصال.", true);
        }
    });

    // ========== تعديل الاسم ==========
    const editNameBtn = document.getElementById("editNameBtn");
    const saveNameBtn = document.getElementById("saveNameBtn");
    if (editNameBtn) editNameBtn.addEventListener("click", () => openModal("editNameModal"));
    if (saveNameBtn) {
        saveNameBtn.addEventListener("click", async () => {
            const nameField = document.getElementById("newName");
            if (!nameField) return;
            const name = nameField.value.trim();
            if (!name) return showMessage("تنبيه", "الرجاء إدخال الاسم.", true);
            try {
                const res = await fetch(updateNameUrl, {
                    method: "POST", headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json" },
                    body: JSON.stringify({ name })
                });
                const data = await res.json();
                if (data.success) {
                    const displayName = document.getElementById("displayName");
                    if (displayName) displayName.textContent = data.name;
                    closeModal("editNameModal");
                    showSuccess("تم بنجاح ✏️", "تم تعديل الاسم بنجاح.", "fa-user-pen");
                } else {
                    showMessage("خطأ", data.error || "فشل التحديث", true);
                }
            } catch (e) {
                showMessage("خطأ", "حدث خطأ في الاتصال. حاول مجدداً.", true);
            }
        });
    }

    // ========== تغيير البريد الإلكتروني ==========
    const changeEmailBtn = document.getElementById("changeEmailBtn");
    if (changeEmailBtn) changeEmailBtn.addEventListener("click", () => openModal("emailOtpModal"));
    const sendEmailOtpBtn = document.getElementById("sendEmailOtpBtn");
    if (sendEmailOtpBtn) {
        sendEmailOtpBtn.addEventListener("click", async () => {
            try {
                const res = await fetch(sendEmailOtpUrl, { method: "POST", headers: { "X-CSRFToken": csrfToken } });
                const data = await res.json();
                if (data.success) {
                    closeModal("emailOtpModal");
                    openModal("emailVerifyModal");
                } else {
                    showMessage("خطأ", data.error || "فشل إرسال الرمز", true);
                    }
            } catch (e) {
                showMessage("خطأ", "حدث خطأ في الاتصال. حاول مجدداً.", true);
            }
        });
    }
    const verifyEmailOtpBtn = document.getElementById("verifyEmailOtpBtn");
    if (verifyEmailOtpBtn) {
        verifyEmailOtpBtn.addEventListener("click", async () => {
            const otpField = document.getElementById("emailOtp");
            const emailField = document.getElementById("newEmail");
            if (!otpField || !emailField) return;
            const otp = otpField.value.trim();
            const email = emailField.value.trim();
            if (!otp || !email) return showMessage("تنبيه", "يرجى إكمال الحقول", true);
            try {
                const res = await fetch(verifyEmailOtpUrl, {
                    method: "POST", headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json" },
                    body: JSON.stringify({ otp, email })
                });
                const data = await res.json();
                if (data.success) {
                    const displayEmail = document.getElementById("displayEmail");
                    if (displayEmail) displayEmail.textContent = data.email;
                    closeModal("emailVerifyModal");
                    showSuccess("تم بنجاح 📧", "تم تغيير البريد الإلكتروني بنجاح.", "fa-envelope-circle-check");
                } else {
                    showMessage("خطأ", data.error || "فشل التحديث", true);
                }
            } catch (e) {
                showMessage("خطأ", "حدث خطأ في الاتصال. حاول مجدداً.", true);
            }
        });
    }

    // ========== تغيير رقم الهاتف ==========
    const changePhoneBtn = document.getElementById("changePhoneBtn");
    if (changePhoneBtn) changePhoneBtn.addEventListener("click", () => openModal("phoneOtpModal"));
    const sendPhoneOtpBtn = document.getElementById("sendPhoneOtpBtn");
    if (sendPhoneOtpBtn) {
        sendPhoneOtpBtn.addEventListener("click", async () => {
            try {
                const res = await fetch(sendPhoneOtpUrl, { method: "POST", headers: { "X-CSRFToken": csrfToken } });
                const data = await res.json();
                if (data.success) {
                    closeModal("phoneOtpModal");
                    openModal("phoneVerifyModal");
                } else {
                    showMessage("خطأ", data.error || "فشل إرسال الرمز", true);
                }
            } catch (e) {
                showMessage("خطأ", "حدث خطأ في الاتصال. حاول مجدداً.", true);
            }
        });
    }
    const verifyPhoneOtpBtn = document.getElementById("verifyPhoneOtpBtn");
    if (verifyPhoneOtpBtn) {
        verifyPhoneOtpBtn.addEventListener("click", async () => {
            const otpField = document.getElementById("phoneOtp");
            const phoneField = document.getElementById("newPhone");
            if (!otpField || !phoneField) return;
            const otp = otpField.value.trim();
            const phone = phoneField.value.trim();
            if (!otp || !phone) return showMessage("تنبيه", "يرجى إكمال الحقول", true);
            try {
                const res = await fetch(verifyPhoneOtpUrl, {
                    method: "POST", headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json" },
                    body: JSON.stringify({ otp, phone })
                });
                const data = await res.json();
                if (data.success) {
                    closeModal("phoneVerifyModal");
                    showSuccess("تم بنجاح 📱", "تم تغيير رقم الهاتف بنجاح.", "fa-mobile-screen-button");
                } else {
                    showMessage("خطأ", data.error || "فشل التحديث", true);
                }
            } catch (e) {
                showMessage("خطأ", "حدث خطأ في الاتصال. حاول مجدداً.", true);
            }
        });
    }
    // ========== تغيير كلمة المرور ==========
    const changePasswordBtn = document.getElementById("changePasswordBtn");
    if (changePasswordBtn) changePasswordBtn.addEventListener("click", () => openModal("changePasswordModal"));
    const changePasswordSubmitBtn = document.getElementById("changePasswordSubmitBtn");
    if (changePasswordSubmitBtn) {
        changePasswordSubmitBtn.addEventListener("click", async () => {
            const current = document.getElementById("currentPassword")?.value;
            const newPass = document.getElementById("newPassword")?.value;
            const confirm = document.getElementById("confirmNewPassword")?.value;
            if (!current || !newPass || !confirm) return showMessage("تنبيه", "يرجى إكمال جميع الحقول", true);
            if (newPass !== confirm) return showMessage("خطأ", "كلمتا المرور غير متطابقتين", true);
            try {
                const res = await fetch(changePasswordUrl, {
                    method: "POST", headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json" },
                    body: JSON.stringify({ current_password: current, new_password: newPass })
                });
                const data = await res.json();
                if (data.success) {
                    closeModal("changePasswordModal");
                    showSuccess("تم بنجاح 🔒", "تم تغيير كلمة المرور بنجاح.", "fa-lock");
                } else {
                    showMessage("خطأ", data.error || "فشل التغيير", true);
                }
            } catch (e) {
                showMessage("خطأ", "حدث خطأ في الاتصال. حاول مجدداً.", true);
            }
        });
    }

    // رابط "نسيت كلمة المرور"
    const forgotPasswordLink = document.querySelector(".forgot-password");
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener("click", (e) => {
            e.preventDefault();
            window.location.href = forgotPasswordUrl;
        });
    }

    // ========== حذف الحساب ==========
    const deleteAccountBtn = document.getElementById("deleteAccountBtn");
    if (deleteAccountBtn) deleteAccountBtn.addEventListener("click", () => openModal("deleteAccountModal"));
    const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener("click", async () => {
            const password = document.getElementById("deletePassword")?.value;
            if (!password) return showMessage("تنبيه", "يرجى إدخال كلمة المرور", true);
            if (!confirm("هل أنت متأكد تماماً؟ لا يمكن التراجع.")) return;
            try {
                const res = await fetch(deleteAccountUrl, {
                    method: "POST", headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json" },
                    body: JSON.stringify({ password })
                });
                const data = await res.json();
                if (data.success) {
                    showSuccess("تم بنجاح 🗑️", "تم حذف الحساب بنجاح. سيتم توجيهك الآن.", "fa-trash-can");
                    setTimeout(() => {
                        window.location.href = data.redirect || "/";
                    }, 2000);
                } else {
                    showMessage("خطأ", data.error || "فشل الحذف", true);
                }
            } catch (e) {
                showMessage("خطأ", "حدث خطأ في الاتصال. حاول مجدداً.", true);
            }
        });
    }

    // ========== تسجيل الخروج ==========
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) logoutBtn.addEventListener("click", () => openModal("logoutModal"));
    const confirmLogoutBtn = document.getElementById("confirmLogoutBtn");
    if (confirmLogoutBtn) {
        confirmLogoutBtn.addEventListener("click", () => {
            window.location.href = logoutUrl;
        });
    }
    // ========== تقييم التطبيق ==========
    const rateApp = document.getElementById("rateApp");
    if (rateApp) {
        rateApp.addEventListener("click", (e) => {
            e.preventDefault();
            window.open("https://play.google.com/store/apps/details?id=com.solaris", "_blank");
        });
    }

    // ========== روابط "قريباً" (فقط للإشعارات واللغة) ==========
    const notificationsLink = document.getElementById("notificationsLink");
    const languageLink = document.getElementById("languageLink");

    function showComingSoon(e) {
        e.preventDefault();
        showMessage("قريباً", "سيتم تفعيل هذه الميزة قريباً.", false);
    }

    if (notificationsLink) notificationsLink.addEventListener("click", showComingSoon);
    if (languageLink) languageLink.addEventListener("click", showComingSoon);
});