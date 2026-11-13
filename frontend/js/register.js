
document.addEventListener("DOMContentLoaded", function () {

    const registerForm = document.getElementById("registerForm");
    const message = document.getElementById("message");

    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const full_name = document.getElementById("full_name").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const confirm_password =
            document.getElementById("confirm_password").value;

        if (password !== confirm_password) {
            message.textContent = "Passwords do not match!";
            return;
        }

        message.textContent = "Creating account...";

        try {
            const response = await fetch(
                `${API_URL}/api/v1/auth/register`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        full_name: full_name,
                        email: email,
                        password: password
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Registration failed");
            }

            message.textContent =
                "Registration successful! Redirecting to login...";

            registerForm.reset();

            setTimeout(function () {
                window.location.href = "login.html";
            }, 1500);

        } catch (error) {
            message.textContent = error.message;
        }
    });
});
