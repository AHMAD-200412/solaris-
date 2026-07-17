document.addEventListener("DOMContentLoaded", () => {

    const modeOptions = document.querySelectorAll(".mode-option");
    const startBtn = document.getElementById("startRecommendation");

    let selectedMode = "economic"; // افتراضي

    // اختيار النمط
    modeOptions.forEach(option => {
        option.addEventListener("click", () => {
            modeOptions.forEach(item => item.classList.remove("selected"));
            option.classList.add("selected");
            selectedMode = option.dataset.mode;
        });
    });

    // عند الضغط على زر البدء
    startBtn.addEventListener("click", function () {
        const baseUrl = this.dataset.url; // {% url 'best_recmmendation' %}
        const url = `${ baseUrl }?mode = ${ selectedMode }`;
        window.location.href = url;
    });

});