// script.js

document.addEventListener("DOMContentLoaded", function () {
    const container = document.querySelector('.container');
    const btnSignIn = document.querySelector('.btnSign-in');
    const btnSignUp = document.querySelector('.btnSign-up');

    if (btnSignIn) {
        btnSignIn.addEventListener('click', () => {
            container.classList.add('active');
        });
    }

    if (btnSignUp) {
        btnSignUp.addEventListener('click', () => {
            container.classList.remove('active');
        });
    }
});
