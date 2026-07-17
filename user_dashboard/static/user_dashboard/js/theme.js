document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light") {
        document.body.classList.add("light-mode");
    }
    // إذا كانت القيمة "dark" أو لا توجد قيمة، يبقى الداكن (الافتراضي)
});

function toggleTheme() {
    const body = document.body;
    if (body.classList.contains("light-mode")) {
        body.classList.remove("light-mode");
        localStorage.setItem("theme", "dark");
    } else {
        body.classList.add("light-mode");
        localStorage.setItem("theme", "light");
    }
}