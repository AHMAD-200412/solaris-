document.addEventListener("DOMContentLoaded", function() {
    // 1. جلب العناصر والبيانات من الـ HTML
    var reviewDataElement = document.getElementById('reviewData');
    
    if (reviewDataElement) {
        var userId = reviewDataElement.getAttribute('data-user-id');
        var dashboardUrl = reviewDataElement.getAttribute('data-dashboard-url');

        // 2. الفحص التلقائي كل 5 ثواني
        if (userId) {
            setInterval(function() {
                var checkUrl = '/accounts/check-status/' + userId + '/';

                fetch(checkUrl)
                    .then(function(response) { 
                        return response.json(); 
                    })
                    .then(function(data) {
                        // 🔥 [تعديل] الفحص بناءً على الـ status الذي يرسله الدجانجو (approved)
                        if (data.status === 'approved') {
                            window.location.href = dashboardUrl;
                        }
                    })
                    .catch(function(error) { 
                        console.error('خطأ في الاتصال بالخادم:', error); 
                    });
            }, 5000);
        }
    }
});