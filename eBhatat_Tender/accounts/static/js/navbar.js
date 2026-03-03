document.addEventListener("DOMContentLoaded", function () {

    const mobileMenu = document.getElementById("mobileMenu");
    const mobileBtn = document.getElementById("mobileMenuBtn");
    const closeBtn = document.getElementById("closeMobileMenu");
    const overlay = document.getElementById("mobileOverlay");

    mobileBtn.addEventListener("click", function () {
        mobileMenu.classList.remove("translate-x-full");
        overlay.classList.remove("hidden");
    });

    closeBtn.addEventListener("click", function () {
        mobileMenu.classList.add("translate-x-full");
        overlay.classList.add("hidden");
    });

    overlay.addEventListener("click", function () {
        mobileMenu.classList.add("translate-x-full");
        overlay.classList.add("hidden");
    });

});