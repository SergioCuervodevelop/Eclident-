document.addEventListener("DOMContentLoaded", function () {

   const hoy = new Date().getDay(); 

    if (hoy === 0) return; 

    const elemento = document.querySelector(
        '.dia-horario[data-day="' + hoy + '"]'
    );

    if (elemento) {
        elemento.classList.add("highlight-day");
    }

});