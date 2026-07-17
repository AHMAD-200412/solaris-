document.addEventListener("DOMContentLoaded", function() {
    var togglePassword = document.getElementById('togglePassword');
    var passwordInput = document.getElementById('passwordInput');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function (e) {
            // تبديل نوع الحقل بين text و password
            var type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // تغيير شكل الأيقونة
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }
});