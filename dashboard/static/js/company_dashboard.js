document.addEventListener("DOMContentLoaded", function() {
    // ==========================================
    // 2. المخططات البيانية (حقيقية ومربوطة بدجانجو) 🔥
    // ==========================================

    // التأكد من وجود مكتبة Chart بالصفحة لتجنب أي خطأ أحمر يوقف الجافا سكريبت
    if (typeof Chart !== 'undefined') {
        
        Chart.defaults.font.family = "'Cairo', sans-serif";
        Chart.defaults.color = "#64748b";

        // --- المخطط الخطي (أرباح الشركة الحقيقية) ---
        // نتأكد أولاً أن مكان المخطط (الكانفاس) موجود بالصفحة
        const revenueCanvas = document.getElementById('revenueChart');
        if (revenueCanvas) {
            const ctxRevenue = revenueCanvas.getContext('2d');
            const revenueChart = new Chart(ctxRevenue, {
                type: 'line',
                data: {
                    labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'],
                    datasets: [{
                        label: 'الأرباح ($)',
                        // حماية إضافية للبيانات الجاية من دجانجو
                        data: typeof djangoRevenueData !== 'undefined' ? djangoRevenueData : [], 
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#0f172a',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        fill: true,
                        tension: 0.4 
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, grid: { borderDash: [5, 5] } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        // --- المخطط الدائري (الباقات الأكثر مبيعاً الحقيقية) ---
        // نتأكد أولاً أن مكان المخطط الدائري موجود بالصفحة
        const packagesCanvas = document.getElementById('packagesChart');
        if (packagesCanvas) {
            const ctxPackages = packagesCanvas.getContext('2d');
            const packagesChart = new Chart(ctxPackages, {
                type: 'doughnut',
                data: {
                    // حماية إضافية للبيانات الجاية من دجانجو
                    labels: typeof djangoPackageLabels !== 'undefined' ? djangoPackageLabels : [], 
                    datasets: [{
                        data: typeof djangoPackageCounts !== 'undefined' ? djangoPackageCounts : [], 
                        backgroundColor: ['#f59e0b', '#3b82f6', '#10b981', '#0f172a', '#ef4444', '#8b5cf6'],
                        borderWidth: 0,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { padding: 15, font: { size: 12, family: "'Cairo', sans-serif" } } }
                    },
                    cutout: '70%'
                }
            });
        }
    }
});