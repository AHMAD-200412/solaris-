document.addEventListener("DOMContentLoaded", function() {
    const userCard = document.getElementById('userCard');
    const companyCard = document.getElementById('companyCard');

    // تأثير تفاعلي خفيف عند النقر لتأكيد الحركة قبل الانتقال
    if (userCard && companyCard) {
        [userCard, companyCard].forEach(card => {
            card.addEventListener('click', function() {
                this.style.transform = 'scale(0.98)';
                this.style.transition = '0.1s ease';
            });
        });
    }
});