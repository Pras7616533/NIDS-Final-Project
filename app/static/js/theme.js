document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark") {
        document.body.classList.add("dark");
    }

    updateLogo();
    updateBaner();
});

/* ===============================
   UPDATE LOGO BASED ON THEME
================================ */
function updateLogo() {
    const img = document.getElementById("logo");
    if (!img) return; // prevent errors if logo not on page

    img.src = document.body.classList.contains("dark")
        ? "/static/images/logo_dark.jpeg"
        : "/static/images/logo.jpeg";
}

function updateBaner() {
    const img = document.getElementById("baner");
    if (!img) return; // prevent errors if baner not on page
    img.src = document.body.classList.contains("dark")
        ? "/static/images/baner_dark.jpeg"
        : "/static/images/baner.jpeg";
}

/* ===============================
   TOGGLE THEME
================================ */
function toggleTheme() {
    document.body.classList.toggle("dark");

    localStorage.setItem(
        "theme",
        document.body.classList.contains("dark") ? "dark" : "light"
    );

    updateLogo();
    updateBaner();
}
