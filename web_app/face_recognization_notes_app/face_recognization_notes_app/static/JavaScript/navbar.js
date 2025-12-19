const menu = document.querySelector('.menu-icon');
const navMenu = document.querySelector('.nav-menu');

const menuIcon = document.querySelector('.menu-icon i');

menu.addEventListener('click', () => {
    menuIcon.classList.toggle('fa-times');
    menuIcon.classList.toggle('fa-bars');
    navMenu.classList.toggle('active');
});
