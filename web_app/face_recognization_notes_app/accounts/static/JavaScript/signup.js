// DEBUG: Verify file load
console.log("DEBUG: Signup.js v7 STARTING");
// alert("DEBUG: Signup.js v7 LOADED.");

document.addEventListener('DOMContentLoaded', function () {
    console.log("DEBUG: DOMContentLoaded fired");
    const submitBtn = document.getElementById('submit-btn');

    if (!submitBtn) {
        alert("CRITICAL: submit-btn component NOT FOUND");
        console.error("CRITICAL: submit-btn component NOT FOUND");
        return;
    }
    console.log("DEBUG: Button found:", submitBtn);

    submitBtn.addEventListener('click', function (event) {
        console.log("DEBUG: Button Clicked");

        // Just in case
        event.preventDefault();
        event.stopPropagation();

        try {
            const usernameInput = document.getElementById('username');
            const imageData = localStorage.getItem('image');
            const username = usernameInput ? usernameInput.value : "N/A";

            if (!usernameInput || usernameInput.value.trim() === "") {
                alert("Please enter a username!");
                return;
            }

            // Check if image was captured
            if (!imageData) {
                alert("Please take a photo first! Click the camera button to capture your face.");
                return;
            }

            console.log("DEBUG: Image data length:", imageData.length);
            console.log("DEBUG: Username:", username);

            const datatosend = JSON.stringify({ imageData, username });
            console.log("DEBUG: Data to send (first 200 chars):", datatosend.substring(0, 200));

            const csrfTokenLink = document.querySelector('[name=csrfmiddlewaretoken]');
            const csrfToken = csrfTokenLink ? csrfTokenLink.value : '';
            console.log("DEBUG: CSRF Token found:", csrfToken ? "Yes" : "No");

            console.log("DEBUG: Sending POST request to /signup/...");
            fetch('/signup/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: datatosend
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
                    if (data.status === 'success' && data.redirect) {
                        // Clear the stored image and redirect to home
                        localStorage.removeItem('image');
                        window.location.href = data.redirect;
                    } else {
                        alert("Response: " + (data.message || JSON.stringify(data)));
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                    alert("Failed to send data.");
                });


        } catch (error) {
            console.error("DEBUG: Error in handler:", error);
            alert("Error: " + error.message);
        }
    });

    console.log("DEBUG: Click listener attached");
});