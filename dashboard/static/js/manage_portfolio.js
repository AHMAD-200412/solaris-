document.addEventListener('DOMContentLoaded', function() {
    // جلب عناصر نافذة الإضافة
    const addModal = document.getElementById('pmAddProjectModal');
    const openAddBtn = document.getElementById('openModalBtn');
    const closeAddBtn = document.getElementById('closeModalBtn');
    const cancelAddBtn = document.getElementById('cancelModalBtn');

    // 1. فتح نافذة الإضافة
    if (openAddBtn) {
        openAddBtn.addEventListener('click', function() {
            addModal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        });
    }

    // 2. دوال إغلاق نافذة الإضافة
    function closeAddModal() {
        addModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    if (closeAddBtn) closeAddBtn.addEventListener('click', closeAddModal);
    if (cancelAddBtn) cancelAddBtn.addEventListener('click', closeAddModal);

    // 3. إغلاق أي نافذة منبثقة عند الضغط خارجها
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('pm-modal-overlay') || event.target.classList.contains('pm-image-modal-overlay')) {
            event.target.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
});

// =====================================
// دوال نافذة عرض الصورة
// =====================================
function openImagePreview(imageSrc) {
    if(!imageSrc) return; // حماية إذا المشروع بدون صورة
    document.getElementById('pmPreviewImage').src = imageSrc;
    document.getElementById('pmImagePreviewModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeImagePreview() {
    document.getElementById('pmImagePreviewModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// =====================================
// دوال نافذة التعديل
// =====================================
function openEditModal(button) {
    const form = document.getElementById('editProjectForm');
    form.action = button.getAttribute('data-url');
    
    document.getElementById('edit_title').value = button.getAttribute('data-title');
    document.getElementById('edit_location').value = button.getAttribute('data-location');
    document.getElementById('edit_date').value = button.getAttribute('data-date');
    document.getElementById('edit_desc').value = button.getAttribute('data-desc');
    document.getElementById('edit_feedback').value = button.getAttribute('data-feedback');
    
    // سحب قائمة الباقات
    const addSelect = document.querySelector('select[name="package_reference"]');
    const editSelect = document.getElementById('edit_package');
    if(addSelect && editSelect) {
        editSelect.innerHTML = addSelect.innerHTML;
        editSelect.value = button.getAttribute('data-pkg');
    }
    
    document.getElementById('pmEditProjectModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeEditModal() {
    document.getElementById('pmEditProjectModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}