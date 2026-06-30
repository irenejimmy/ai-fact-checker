const form = document.querySelector("form");
const button = document.querySelector("button");

form.addEventListener("submit", () => {
    button.innerText = "Analyzing...";
    button.style.background = "#f59e0b";
    button.disabled = true;
});