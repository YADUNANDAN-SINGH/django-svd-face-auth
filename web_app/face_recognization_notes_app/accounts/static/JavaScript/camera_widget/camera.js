const cameraStream = document.getElementById('camera-stream');
const takeShotBtn = document.getElementById('take-shot-btn');
const warningMsg = document.getElementById('face-warning-msg');
let isFrozen = false;

function toggleFaceWarning(show) {
    if (show) {
        warningMsg.classList.remove('warning-hidden');
    } else {
        warningMsg.classList.add('warning-hidden');
    }
}

async function setupCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        cameraStream.srcObject = stream;
    } catch (err) {
        console.error("Error accessing camera: ", err);
    }
}

function takeShot() {
    if (isFrozen) {
        // --- RETAKE MODE ---
        // If already frozen, unfreeze so user can retake
        cameraStream.play();
        isFrozen = false;

        // CLEANUP: Remove the old image from storage so we don't accidentally submit it
        localStorage.removeItem('image');
        console.log("Camera unfrozen, old image cleared.");

    } else {
        // --- CAPTURE MODE ---
        const video = cameraStream;
        const guideBox = document.querySelector('.face-guide-box');
        const container = document.querySelector('.camera-container');

        if (!guideBox || !container) {
            console.error("Guide box or container not found");
            return;
        }

        // --- 1. CALCULATE CROP DIMENSIONS ---
        const vw = video.videoWidth;
        const vh = video.videoHeight;
        const cw = container.clientWidth;
        const ch = container.clientHeight;

        const vidRect = container.getBoundingClientRect();
        const boxRect = guideBox.getBoundingClientRect();

        const boxLeft = boxRect.left - vidRect.left;
        const boxTop = boxRect.top - vidRect.top;
        const boxWidth = boxRect.width;
        const boxHeight = boxRect.height;

        const scaleX = cw / vw;
        const scaleY = ch / vh;
        const scale = Math.max(scaleX, scaleY);

        const renderW = vw * scale;
        const renderH = vh * scale;

        const offsetX = (renderW - cw) / 2;
        const offsetY = (renderH - ch) / 2;

        const sourceX = (offsetX + boxLeft) / scale;
        const sourceY = (offsetY + boxTop) / scale;
        const sourceW = boxWidth / scale;
        const sourceH = boxHeight / scale;

        // --- 2. DRAW IMAGE TO CANVAS ---
        const canvas = document.createElement('canvas');
        canvas.width = sourceW;
        canvas.height = sourceH;

        const context = canvas.getContext('2d');
        context.drawImage(video, sourceX, sourceY, sourceW, sourceH, 0, 0, canvas.width, canvas.height)

        // --- 3. PERFORM CHECKS (Brightness) ---
        let imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        let data = imageData.data;
        let r, g, b;
        let avg = 0;

        for (let i = 0; i < data.length; i += 4) {
            r = data[i];
            g = data[i + 1];
            b = data[i + 2];

            let pixelBrightness = (0.299 * r) + (0.587 * g) + (0.114 * b);
            avg += pixelBrightness;
        }

        let totalPixels = data.length / 4;
        let avgBrightness = avg / totalPixels;

        if (avgBrightness < 50) {
            toggleFaceWarning(true);
            alert('The image is too dark');
            return; // Stop here, do not save, do not freeze
        }
        if (avgBrightness > 200) {
            toggleFaceWarning(true);
            alert('The image is too bright');
            return; // Stop here
        }

        // If we get here, the image is good!
        toggleFaceWarning(false);
        console.log('The image is perfect');

        // --- 4. EXTRACT & SAVE THE IMAGE ---
        // We create the URL here, where the variable is valid
        const imageDataURL = canvas.toDataURL('image/png');
        console.log("Cropped Image extracted:", imageDataURL);

        // SAVE TO LOCAL STORAGE NOW
        try {
            localStorage.setItem('image', imageDataURL);
            console.log("Success: Image saved to local storage!");
        } catch (e) {
            console.error("Failed to save image to storage:", e);
        }

        // --- 5. FREEZE CAMERA ---
        cameraStream.pause();
        isFrozen = true;
    }
}

takeShotBtn.addEventListener('click', takeShot);

setupCamera();