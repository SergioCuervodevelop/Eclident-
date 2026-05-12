/* === SCRIPTS JAVASCRIPT PARA LA PÁGINA DE INICIO DE ECLIDENT ===
   Este archivo contiene todas las funcionalidades JavaScript interactivas:
   - Control del menú móvil
   - Acordeón de preguntas frecuentes (FAQ)
   - Eventos de click y accesibilidad
*/

// === CONTROL DEL MENÚ MÓVIL ===
// Variables para controlar el menú móvil desplegable
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const mobileMenu = document.getElementById('mobileMenu');
const mobileMenuClose = document.getElementById('mobileMenuClose');

// Evento para abrir el menú móvil al hacer click en el botón toggle
if (mobileMenuToggle && mobileMenu) {
    mobileMenuToggle.addEventListener('click', function () {
        mobileMenu.classList.add('open');
        mobileMenu.setAttribute('aria-hidden', 'false');
    });
}

// Evento para cerrar el menú móvil al hacer click en el botón de cerrar
if (mobileMenuClose && mobileMenu) {
    mobileMenuClose.addEventListener('click', function () {
        mobileMenu.classList.remove('open');
        mobileMenu.setAttribute('aria-hidden', 'true');
    });
}

// Evento global para cerrar el menú al hacer click fuera de él
document.addEventListener('click', function (event) {
    if (!mobileMenu.contains(event.target) && event.target !== mobileMenuToggle && mobileMenu.classList.contains('open')) {
        mobileMenu.classList.remove('open');
        mobileMenu.setAttribute('aria-hidden', 'true');
    }
});

// === FUNCIONALIDAD DEL ACORDEÓN DE PREGUNTAS FRECUENTES (FAQ) ===
// Selecciona todos los botones de preguntas del FAQ
const faqButtons = document.querySelectorAll('.faq-question');

// Agrega evento click a cada botón del FAQ
faqButtons.forEach(button => {
    button.addEventListener('click', function () {
        const item = this.closest('.faq-item'); // Encuentra el elemento padre del FAQ
        const isOpen = item.classList.contains('active'); // Verifica si está abierto

        // Cierra otros elementos FAQ que estén abiertos
        document.querySelectorAll('.faq-item.active').forEach(activeItem => {
            if (activeItem !== item) {
                activeItem.classList.remove('active');
                activeItem.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
            }
        });

        // Alterna el estado del elemento actual
        if (isOpen) {
            item.classList.remove('active');
            this.setAttribute('aria-expanded', 'false');
        } else {
            item.classList.add('active');
            this.setAttribute('aria-expanded', 'true');
        }
    });
});
