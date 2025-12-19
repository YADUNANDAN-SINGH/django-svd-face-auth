document.addEventListener('DOMContentLoaded', function () {
    console.log("DEBUG: Login.js loaded");

    const loginBtn = document.getElementById('login-btn');

    if (!loginBtn) {
        console.error("CRITICAL: Login button not found");
        return;
    }

    loginBtn.addEventListener('click', function (event) {
        event.preventDefault();
        console.log("DEBUG: Login button clicked");

        const imageData = localStorage.getItem('image');
        if (!imageData) {
            alert("Please take a photo first!");
            return;
        }

        const csrfTokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfToken = csrfTokenInput ? csrfTokenInput.value : '';

        const dataToSend = JSON.stringify({ imageData: imageData });

        fetch('/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: dataToSend
        })
            .then(response => response.json())
            .then(data => {
                console.log("Server Response:", data);
                if (data.status === 'success') {
                    alert("Login Successful! Welcome " + data.username);
                    localStorage.removeItem('image');
                    window.location.href = "/";
                } else {
                    alert("Login Failed: " + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("An error occurred during login.");
            });
    });
});
