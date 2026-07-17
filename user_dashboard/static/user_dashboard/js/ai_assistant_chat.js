document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    // ==================== API ====================
    const API = {
        sendMessage: DJANGO_URLS.sendMessage,
        createConversation: DJANGO_URLS.createConversation,
        conversationList: DJANGO_URLS.conversationList,
        latestConversation: DJANGO_URLS.latestConversation,
        searchConversation: DJANGO_URLS.searchConversation,
        clearAllConversations: DJANGO_URLS.clearAllConversations,
        conversation(id) { return `/user/assistant/${id}/`; },
        renameConversation(id) { return `/user/assistant/${id}/rename/`; },
        deleteConversation(id) { return `/user/assistant/${id}/delete/`; },
        csrf: csrfToken
    };

    const state = {
        conversationId: null,
        conversations: [],
        isSending: false,
        sidebarOpened: false,
        lightMode: localStorage.getItem("assistant_theme") === "light"
    };

    const elements = {
        body: document.body,
        sidebar: document.getElementById("chatSidebar"),
        overlay: document.getElementById("sidebarOverlay"),
        menuButton: document.getElementById("menuButton"),
        closeSidebar: document.getElementById("closeSidebar"),
        themeButton: document.getElementById("themeToggle"),
        newChat: document.getElementById("newChatButton"),
        clearAll: document.getElementById("clearAllChatsBtn"),
        conversationList: document.getElementById("conversationList"),
        searchInput: document.getElementById("conversationSearch"),
        messages: document.getElementById("chatMessages"),
        typing: document.getElementById("typingIndicator"),
        messageInput: document.getElementById("messageInput"),
        sendButton: document.getElementById("sendButton"),
        welcome: document.querySelector(".welcome-message"),
        suggestions: document.getElementById("quickSuggestions"),
        userTemplate: document.getElementById("userMessageTemplate"),
        assistantTemplate: document.getElementById("assistantMessageTemplate")
    };
    const deleteAllModal = document.getElementById("deleteAllModal");

    // ==================== Helpers ====================
    const helpers = {
        scrollBottom() {
            elements.messages.scrollTop = elements.messages.scrollHeight;
        },

        // الوقت الحالي بنظام 12 ساعة مع AM/PM بالإنجليزية
        currentTime() {
            return new Date().toLocaleTimeString("en-US", {
                hour: "numeric",
                minute: "2-digit",
                hour12: true
            });
        },

        // تحويل أي صيغة وقت إلى 12 ساعة مع AM/PM
        formatTimeTo12Hour(timeString) {
            if (!timeString) return "";
            try {
                // إذا بصيغة ISO (مثلاً 2025-01-15T12:30:00)
                if (timeString.includes("T") || timeString.includes("Z")) {
                    const date = new Date(timeString);
                    if (!isNaN(date)) {
                        return date.toLocaleTimeString("en-US", {
                            hour: "numeric",
                            minute: "2-digit",
                            hour12: true
                        });
                    }
                }
                // إذا بصيغة HH:MM (24 ساعة) نحولها يدويًا
                const match = timeString.match(/^(\d{1,2}):(\d{2})$/);
                if (match) {
                    let hours = parseInt(match[1], 10);
                    const minutes = match[2];
                    const ampm = hours >= 12 ? "PM" : "AM";
                    hours = hours % 12 || 12;
                    return `${hours}:${minutes} ${ampm}`;
                }
            } catch (e) { }
            return timeString;
        },

        autoResize() {
            if (!elements.messageInput) return;
            elements.messageInput.style.height = "auto";
            elements.messageInput.style.height = elements.messageInput.scrollHeight + "px";
        },
        toggleWelcome(show) {
            if (elements.welcome) elements.welcome.style.display = show ? "" : "none";
            if (elements.suggestions) elements.suggestions.style.display = show ? "" : "none";
        },

        sanitize(text) {
            const div = document.createElement("div");
            div.textContent = text;
            return div.innerHTML;
        }
    };

    // ==================== Sidebar ====================
    function openSidebar() {
        state.sidebarOpened = true;
        elements.sidebar.classList.add("active");
        elements.overlay.classList.add("active");
    }
    function closeSidebar() {
        state.sidebarOpened = false;
        elements.sidebar.classList.remove("active");
        elements.overlay.classList.remove("active");
    }
    elements.menuButton?.addEventListener("click", openSidebar);
    elements.closeSidebar?.addEventListener("click", closeSidebar);
    elements.overlay?.addEventListener("click", closeSidebar);

    // ==================== Theme ====================
    function applyTheme() {
        if (state.lightMode) {
            elements.body.classList.add("light-mode");
            if (elements.themeButton) elements.themeButton.innerHTML = '<i class="fa-solid fa-sun"></i>';
        } else {
            elements.body.classList.remove("light-mode");
            if (elements.themeButton) elements.themeButton.innerHTML = '<i class="fa-regular fa-moon"></i>';
        }
    }
    elements.themeButton?.addEventListener("click", () => {
        state.lightMode = !state.lightMode;
        localStorage.setItem("assistant_theme", state.lightMode ? "light" : "dark");
        applyTheme();
    });
    applyTheme();

    // ==================== Conversations ====================
    function renderConversationItem(conv) {
        const item = document.createElement("div");
        item.className = "conversation-item";
        item.dataset.id = conv.id;
        const safeTitle = helpers.sanitize(conv.title);
        // تحويل التوقيت إلى محلي 12 ساعة مع AM/PM
        const localTime = helpers.formatTimeTo12Hour(conv.updated_at);
        const safeDate = helpers.sanitize(localTime || "");
        item.innerHTML =
            `<div class="conversation-main">
            <div class="conversation-title">
                <div class="conversation-icon">🤖</div>
                <span>${safeTitle}</span>
            </div>
            <div class="conversation-date">${safeDate}</div>
        </div>
        <button class="conversation-menu" data-id="${conv.id}" type="button">
            <i class="fa-solid fa-ellipsis"></i>
        </button>`;

        item.addEventListener("click", (e) => {
            if (e.target.closest(".conversation-menu")) return;
            loadConversation(conv.id);
        });
        return item;
    }

    function renderConversationList(list) {
        elements.conversationList.innerHTML = "";
        if (list.length === 0) {
            elements.conversationList.innerHTML = '<div class="empty-conversations">لا توجد محادثات</div>';
            return;
        }
        list.forEach(conv => elements.conversationList.appendChild(renderConversationItem(conv)));
    }

    async function loadConversationList() {
        try {
            const response = await fetch(API.conversationList);
            const data = await response.json();
            state.conversations = data.conversations || [];
            renderConversationList(state.conversations);
        } catch (error) {
            console.error(error);
        }
    }

    async function loadConversation(id) {
        try {
            const response = await fetch(API.conversation(id));
            const data = await response.json();
            if (!data.success) return;

            state.conversationId = id;
            elements.messages.innerHTML = "";
            helpers.toggleWelcome(false);
            data.messages.forEach(msg => {
                const time = helpers.formatTimeTo12Hour(msg.created_at);
                appendMessage(msg.role, msg.content, time);
            });
            setActiveConversation(id);
            helpers.scrollBottom();
            closeSidebar();
        } catch (error) {
            console.error(error);
        }
    }

    function setActiveConversation(id) {
        document.querySelectorAll(".conversation-item").forEach(item => item.classList.remove("active"));
        const active = document.querySelector(`.conversation-item[data-id="${id}"]`);
        if (active) active.classList.add("active");
    }

    // ==================== Messages ====================
    function appendMessage(role, text, time = null) {
        helpers.toggleWelcome(false);
        const template = role === "user" ? elements.userTemplate : elements.assistantTemplate;
        if (!template) return;
        const node = template.content.firstElementChild.cloneNode(true);
        const textEl = node.querySelector(".message-text");
        if (textEl) textEl.textContent = text;
        const timeEl = node.querySelector(".message-time");
        if (timeEl) timeEl.textContent = time || helpers.currentTime();
        elements.messages.appendChild(node);
        helpers.scrollBottom();
    }

    function showTyping() {
        if (elements.typing) elements.typing.classList.remove("hidden");
        helpers.scrollBottom();
    }
    function hideTyping() {
        if (elements.typing) elements.typing.classList.add("hidden");
    }

    // ==================== Send Message ====================
    async function sendMessage() {
        if (state.isSending) return;
        const message = elements.messageInput.value.trim();
        if (!message) return;
        state.isSending = true;
        appendMessage("user", message);
        elements.messageInput.value = "";
        helpers.autoResize();
        showTyping();

        try {
            const formData = new FormData();
            formData.append("message", message);
            if (state.conversationId) formData.append("conversation_id", state.conversationId);

            const response = await fetch(API.sendMessage, {
                method: "POST",
                headers: { "X-CSRFToken": API.csrf },
                body: formData
            });
            const data = await response.json();
            hideTyping();
            state.isSending = false;

            if (!data.success) {
                appendMessage("assistant", data.reply || "حدث خطأ.");
                return;
            }

            state.conversationId = data.conversation_id;
            // هنا كان الخطأ: formatTimeTo24Hour -> formatTimeTo12Hour
            const time = helpers.formatTimeTo12Hour(data.assistant_message.created_at);
            appendMessage("assistant", data.reply, time);
            await loadConversationList();
            setActiveConversation(state.conversationId);
            closeSidebar();
        } catch (error) {
            console.error(error);
            hideTyping();
            state.isSending = false;
            appendMessage("assistant", "تعذر الاتصال بالخادم.");
        }
    }

    elements.sendButton?.addEventListener("click", sendMessage);
    elements.messageInput?.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    elements.messageInput?.addEventListener("input", helpers.autoResize);

    // ==================== Context Menu ====================
    let contextMenu = null;
    let selectedConversationId = null;

    function createContextMenu() {
        const menu = document.createElement("div");
        menu.className = "conversation-context-menu";
        menu.innerHTML =
            `<div class="context-item rename-chat">
                <i class="fa-solid fa-pen"></i>
                <span>إعادة التسمية</span>
            </div>
            <div class="context-item delete-chat">
                <i class="fa-solid fa-trash"></i>
                <span>حذف المحادثة</span>
            </div>`;
        document.body.appendChild(menu);

        menu.querySelector(".rename-chat").addEventListener("click", async (e) => {
            e.stopPropagation();
            hideContextMenu();
            const conv = state.conversations.find(c => Number(c.id) === Number(selectedConversationId));
            const newTitle = showRenameModal(selectedConversationId, conv?.title || "");
            if (!newTitle) return;
            try {
                const fd = new FormData();
                fd.append("title", newTitle);
                const res = await fetch(API.renameConversation(selectedConversationId), {
                    method: "POST",
                    headers: { "X-CSRFToken": API.csrf },
                    body: fd
                });
                if ((await res.json()).success) loadConversationList();
            } catch (err) { console.error(err); }
        });

        menu.querySelector(".delete-chat").addEventListener("click", async (e) => {
            e.stopPropagation();
            hideContextMenu();
            if (!showDeleteModal(selectedConversationId)) return;
            try {
                const res = await fetch(API.deleteConversation(selectedConversationId), {
                    method: "POST",
                    headers: { "X-CSRFToken": API.csrf }
                });
                if ((await res.json()).success) {
                    if (Number(selectedConversationId) === Number(state.conversationId)) {
                        state.conversationId = null;
                        elements.messages.innerHTML = "";
                        helpers.toggleWelcome(true);
                    }
                    loadConversationList();
                }
            } catch (err) { console.error(err); }
        });

        return menu;
    }

    function showContextMenu(button) {
        if (!contextMenu) contextMenu = createContextMenu();
        selectedConversationId = button.dataset.id;
        const rect = button.getBoundingClientRect();
        const menu = contextMenu;
        menu.classList.add("show"); // إظهار مؤقت لقياس الأبعاد

        const menuWidth = menu.offsetWidth || 180;
        const menuHeight = menu.offsetHeight || 100;
        menu.classList.remove("show"); // إخفاء

        let top = rect.bottom + 5;
        let left = rect.left + rect.width - menuWidth; // محاذاة لليمين (RTL)

        // تصحيح إذا خرجت عن الشاشة
        if (left < 10) left = 10;
        if (left + menuWidth > window.innerWidth - 10) left = window.innerWidth - menuWidth - 10;
        if (top + menuHeight > window.innerHeight - 10) top = rect.top - menuHeight - 5;

        contextMenu.style.top = `${top}px`;
        contextMenu.style.left = `${left}px`;
        contextMenu.classList.add("show");
    }

    function hideContextMenu() {
        if (contextMenu) contextMenu.classList.remove("show");
    }

    document.addEventListener("click", (e) => {
        const menuBtn = e.target.closest(".conversation-menu");
        if (menuBtn) {
            e.preventDefault();
            e.stopPropagation();
            showContextMenu(menuBtn);
        } else {
            hideContextMenu();
        }
    });

    // ==================== Search ====================
    elements.searchInput?.addEventListener("input", async function () {
        const q = this.value.trim();
        if (!q) { loadConversationList(); return; }
        try {
            const response = await fetch(`${API.searchConversation}?q=${encodeURIComponent(q)}`);
            const data = await response.json();
            renderConversationList(data.conversations || []);
        } catch (error) { console.error(error); }
    });

    // ==================== New / Clear All ====================
    elements.newChat?.addEventListener("click", () => {
        state.conversationId = null;
        elements.messages.innerHTML = "";
        helpers.toggleWelcome(true);
        document.querySelectorAll(".conversation-item").forEach(item => item.classList.remove("active"));
        closeSidebar();
    });

    elements.clearAll?.addEventListener("click", async () => {
        showDeleteAllModal();
        document.getElementById("confirmDeleteAll")?.addEventListener("click", () => {
            if (currentModalCallback) currentModalCallback();
        });
        document.getElementById("cancelDeleteAll")?.addEventListener("click", hideModal);
        window.addEventListener("click", (e) => {
            if (e.target === renameModal || e.target === deleteModal || e.target === deleteAllModal) hideModal();
        });
    });

    // ==================== Suggestions ====================
    document.querySelectorAll(".suggestion-card").forEach(card => {
        card.addEventListener("click", function () {
            const question = this.dataset.question;
            if (question) {
                elements.messageInput.value = question;
                helpers.autoResize();
                sendMessage();
            }
        });
    });

    // ==================== Copy Message ====================
    document.addEventListener("click", function (e) {
        const copyBtn = e.target.closest(".copy-message-btn");
        if (!copyBtn) return;
        e.stopPropagation();

        const messageContent = copyBtn.closest(".message-content");
        if (!messageContent) return;

        const messageText = messageContent.querySelector(".message-text");
        if (!messageText) return;

        const textToCopy = messageText.textContent;
        const icon = copyBtn.querySelector("i");
        copyTextToClipboard(textToCopy, icon);
    });

    function copyTextToClipboard(text, iconElement) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text)
                .then(() => showCopySuccess(iconElement))
                .catch(err => {
                    console.warn("Clipboard API failed, trying fallback:", err);
                    fallbackCopyText(text, iconElement);
                });
        } else {
            fallbackCopyText(text, iconElement);
        }
    }

    function fallbackCopyText(text, iconElement) {
        try {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            textArea.style.top = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);

            if (successful) {
                showCopySuccess(iconElement);
            } else {
                console.error("Fallback copy failed");
            }
        } catch (err) {
            console.error("Fallback copy error:", err);
        }
    }

    function showCopySuccess(iconElement) {
        if (!iconElement) return;
        const originalClass = iconElement.className;
        iconElement.className = "fa-solid fa-check";
        iconElement.style.color = "#2ecc71";
        setTimeout(() => {
            iconElement.className = originalClass;
            iconElement.style.color = "";
        }, 1500);
    }
    // ==================== Modals ====================
    let currentModalCallback = null;
    const renameModal = document.getElementById("renameModal");
    const deleteModal = document.getElementById("deleteModal");
    const renameInput = document.getElementById("renameInput");

    function showDeleteAllModal() {
        deleteAllModal.classList.remove("hidden");
        currentModalCallback = async () => {
            try {
                await fetch(API.clearAllConversations, {
                    method: "POST",
                    headers: { "X-CSRFToken": API.csrf }
                });
                state.conversationId = null;
                elements.messages.innerHTML = "";
                helpers.toggleWelcome(true);
                loadConversationList();
            } catch (err) { console.error(err); }
            hideModal();
        };
    }

    function showRenameModal(conversationId, currentTitle) {
        renameInput.value = currentTitle || "";
        renameModal.classList.remove("hidden");
        renameInput.focus();
        currentModalCallback = async () => {
            const newTitle = renameInput.value.trim();
            if (!newTitle) return;
            try {
                const fd = new FormData();
                fd.append("title", newTitle);
                const res = await fetch(API.renameConversation(conversationId), {
                    method: "POST",
                    headers: { "X-CSRFToken": API.csrf },
                    body: fd
                });
                if ((await res.json()).success) loadConversationList();
            } catch (err) { console.error(err); }
            hideModal();
        };
    }

    function showDeleteModal(conversationId) {
        deleteModal.classList.remove("hidden");
        currentModalCallback = async () => {
            try {
                const res = await fetch(API.deleteConversation(conversationId), {
                    method: "POST",
                    headers: { "X-CSRFToken": API.csrf }
                });
                if ((await res.json()).success) {
                    if (Number(conversationId) === Number(state.conversationId)) {
                        state.conversationId = null;
                        elements.messages.innerHTML = "";
                        helpers.toggleWelcome(true);
                    }
                    loadConversationList();
                }
            } catch (err) { console.error(err); }
            hideModal();
        };
    }

    function hideModal() {
        renameModal.classList.add("hidden");
        deleteModal.classList.add("hidden");
        deleteAllModal.classList.add("hidden");
        currentModalCallback = null;
    }

    // أزرار المودال
    document.getElementById("saveRename")?.addEventListener("click", () => {
        if (currentModalCallback) currentModalCallback();
    });
    document.getElementById("cancelRename")?.addEventListener("click", hideModal);
    document.getElementById("confirmDelete")?.addEventListener("click", () => {
        if (currentModalCallback) currentModalCallback();
    });
    document.getElementById("cancelDelete")?.addEventListener("click", hideModal);

    // إغلاق المودال عند النقر خارج المحتوى
    window.addEventListener("click", (e) => {
        if (e.target === renameModal || e.target === deleteModal) hideModal();
    });
    // ==================== Init ====================
    helpers.autoResize();
    elements.messageInput?.focus();
    loadConversationList();
});