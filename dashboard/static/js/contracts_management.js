document.addEventListener('DOMContentLoaded', function() {
    
    // 1️⃣ منطق فتح وإغلاق المودل الأساسي (متوافق مع الأزرار الجديدة)
    const modal = document.getElementById('customContractModal');
    const openBtn = document.getElementById('openContractModalBtn');
    const closeBtns = document.querySelectorAll('.close-modal-btn, .close-modal-btn-footer');

    if (openBtn && modal) {
        openBtn.addEventListener('click', function(e) {
            e.preventDefault();
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden'; // منع سكرول الصفحة الخلفية
        });
    }

    closeBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
    });

    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });

    // 2️⃣ 🧠 المنطق الديناميكي لإظهار وإخفاء حقول السيريالات وتفعيل الـ Required
    function setupDynamicSection(checkboxId, sectionId) {
        const checkbox = document.getElementById(checkboxId);
        const section = document.getElementById(sectionId);
        
        if (!checkbox || !section) 
            return; // تم تصحيح الـ  هنا

        checkbox.addEventListener('change', function() {
            const inputs = section.querySelectorAll('input, textarea');

            if (this.checked) {
                section.style.display = 'block';
                // تفعيل خاصية الإلزامية (Required) فقط للقطع المختارة
                inputs.forEach(input => input.setAttribute('required', 'true'));
            } else {
                section.style.display = 'none';
                // إلغاء الـ Required وتفريغ الحقول عند إخفاء القسم
                inputs.forEach(input => {
                    input.removeAttribute('required');
                    input.value = ''; 
                });
            }
        });
    }

    // ربط كارتات الاختيار بالأقسام المقابلة لها
    setupDynamicSection('chk-panels', 'group-panels');
    setupDynamicSection('chk-batteries', 'group-batteries');
    setupDynamicSection('chk-inverter', 'group-inverter');

    // 3️⃣ 🔍 البحث والفلترة الفورية الذكية (تبحث بالاسم، رقم الطلب، والأرقام التسلسلية)
    const searchInput = document.getElementById('searchContracts');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const filter = this.value.trim().toLowerCase();
            const rows = document.querySelectorAll('.styled-table tbody tr');
            
            rows.forEach(row => {
                // تخطي أسطر التنبيهات أو حالة الجدول الفارغ
                if (row.classList.contains('empty-state') || row.querySelector('.empty-state'))
                     return; // تم تصحيح الـ  هنا
                
                // جلب نص اسم الزبون، رقم الطلب، وعمود السيريالات
                const customerName = row.cells[0] ? row.cells[0].textContent.toLowerCase() : '';
                const orderId = row.cells[1] ? row.cells[1].textContent.toLowerCase() : '';
                const serialNumbers = row.cells[3] ? row.cells[3].textContent.toLowerCase() : ''; // هنا نقرأ عمود القطع والسيريالات بالكامل
                
                // الفلترة: إذا الموظف كتب أي شي يطابق الاسم أو رقم الطلب أو أي سيريال (لوح، بطارية، عاكس)
                if (customerName.includes(filter) || orderId.includes(filter) || serialNumbers.includes(filter)) {
                    row.style.display = ''; // إظهار السطر
                } else {
                    row.style.display = 'none'; // إخفاء السطر
                }
            });
        });
    }
});