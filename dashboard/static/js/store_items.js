// ========================================================
// 🏪 ملف إدارة منتجات المتجر (store_items.js)
// ========================================================
document.addEventListener("DOMContentLoaded", function() {
    
    // 1. ميزة البحث الفوري الذكي عن المنتجات
    const searchInput = document.getElementById('searchInput');
    const productCards = document.querySelectorAll('.product-card');
    const productsGrid = document.querySelector('.products-grid');

    // إنشاء رسالة "المنتج غير متوفر" برمجياً
    const noResultMessage = document.createElement('div');
    noResultMessage.className = 'empty-state';
    noResultMessage.style.display = 'none';
    noResultMessage.style.gridColumn = '1 / -1';
    noResultMessage.style.textAlign = 'center';
    noResultMessage.style.padding = '40px 20px';
    noResultMessage.innerHTML = '<i class="fa-solid fa-magnifying-glass-minus" style="font-size: 3rem; color: #cbd5e1; margin-bottom: 15px;"></i><p style="color: #64748b; font-size: 1.1rem;">عذراً، هذا المنتج غير متوفر أو لم يتم إضافته بعد!</p>';
    
    if (productsGrid) {
        productsGrid.appendChild(noResultMessage);
    }

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const filterText = searchInput.value.toLowerCase().trim();
            let hasVisibleProducts = false;

            productCards.forEach(function(card) {
                const productNameEle = card.querySelector('.product-name') || card.querySelector('h3');
                
                if (productNameEle) {
                    const productName = productNameEle.textContent.toLowerCase();
                    
                    if (productName.includes(filterText)) {
                        card.style.setProperty('display', '', 'important');
                        hasVisibleProducts = true;
                    } else {
                        card.style.setProperty('display', 'none', 'important');
                    }
                }
            });

            if (filterText !== "" && !hasVisibleProducts) {
                noResultMessage.style.display = 'block';
            } else {
                noResultMessage.style.display = 'none';
            }
        });
    }
});

// 2. دوال فتح وإغلاق نافذة إضافة قطعة
function openAddModal() {
    var modal = document.getElementById('productModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('active');
    }
}

function closeAddModal() {
    var modal = document.getElementById('productModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

// 3. إغلاق النوافذ عند الضغط خارج الصندوق الأبيض
window.addEventListener('click', function(event) {
    var productModal = document.getElementById('productModal');
    if (event.target == productModal) {
        closeAddModal();
    }
});

// 4. تكبير وتصغير الصور
function openImageModal(imgUrl) {
    var modal = document.getElementById("customImageModal");
    var modalImg = document.getElementById("popupExpandedImg");
    if (modal && modalImg) {
        modal.style.display = "block";
        modalImg.src = imgUrl;
    }
}

function closeImageModal() {
    var modal = document.getElementById("customImageModal");
    if (modal) modal.style.display = "none";
}

// 5. فتح وإغلاق نوافذ التعديل
function openEditModal(productId) {
    var editModal = document.getElementById('editModal-' + productId);
    if (editModal) editModal.style.display = 'flex';
}

function closeEditModal(productId) {
    var editModal = document.getElementById('editModal-' + productId);
    if (editModal) editModal.style.display = 'none';
}