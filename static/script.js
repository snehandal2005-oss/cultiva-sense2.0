
const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", function(event) {

        const phone =
            document.getElementById("phone").value.trim();

        const password =
            document.getElementById("password").value;

        const confirmPassword =
            document.getElementById("confirmPassword").value;

        if (!/^\d{10}$/.test(phone)) {
            event.preventDefault();
            alert("Please enter a valid 10-digit phone number.");
            return;
        }

        if (password.length < 8) {
            event.preventDefault();
            alert("Password must contain at least 8 characters.");
            return;
        }

        if (password !== confirmPassword) {
            event.preventDefault();
            alert("Passwords do not match!");
            return;
        }

    });

}
