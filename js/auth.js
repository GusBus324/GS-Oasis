document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("register-form");

    registerForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const password = document.getElementById("reg-password").value;
        const passwordRegex = /^(?=.*[0-9].*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{8,}$/;

        if (!passwordRegex.test(password)) {
            alert("Password must be at least 8 characters long, include at least 2 numbers, and 1 special symbol.");
            return;
        }

        alert("Registration successful!");
        registerForm.reset();
    });
});