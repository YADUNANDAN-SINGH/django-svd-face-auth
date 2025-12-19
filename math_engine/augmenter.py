import cv2
import numpy as np
import os


def generate_variations(image_path, username):
    """
    Takes 1 real photo and automatically creates 8 'fake' variations
    to build a robust dataset for SVD training.
    """
    # 1. Load the original image
    img = cv2.imread(image_path)

    # Safety Check: Did the image load?
    if img is None:
        print(f"Error: Could not load image at {image_path}")
        return False

    # Get dimensions (Height and Width)
    rows, cols = img.shape[:2]

    # Get the folder path so we save fakes in the same place
    folder = os.path.dirname(image_path)

    # --- HELPER FUNCTION ---
    # Saves a new image with a specific suffix (e.g., "john_flip.jpg")
    def save_img(suffix, image_data):
        filename = f"{username}_{suffix}.jpg"
        save_path = os.path.join(folder, filename)
        cv2.imwrite(save_path, image_data)

    print(f"Generating variations for {username}...")

    # --- VARIATION 1: MIRROR FLIP ---
    # Helps the model understand symmetry
    flip = cv2.flip(img, 1)
    save_img("flip", flip)

    # --- VARIATION 2: INCREASE BRIGHTNESS ---
    # Creates a matrix of 40s and adds it to the image
    M_bright = np.ones(img.shape, dtype="uint8") * 40
    bright = cv2.add(img, M_bright)
    save_img("bright", bright)

    # --- VARIATION 3: DECREASE BRIGHTNESS (DARK) ---
    # Creates a matrix of 40s and subtracts it
    M_dark = np.ones(img.shape, dtype="uint8") * 40
    dark = cv2.subtract(img, M_dark)
    save_img("dark", dark)

    # --- VARIATION 4: ADD NOISE (GRAINY) ---
    # Simulates a bad camera sensor
    noise = np.random.normal(0, 20, img.shape).astype('uint8')
    noisy = cv2.add(img, noise)
    save_img("noise", noisy)

    # --- VARIATION 5: BLUR ---
    # Simulates out-of-focus shots
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    save_img("blur", blur)

    # --- VARIATION 6: ROTATE LEFT (5 Degrees) ---
    # Simulates head tilt
    M_left = cv2.getRotationMatrix2D((cols / 2, rows / 2), 5, 1)
    rot_left = cv2.warpAffine(img, M_left, (cols, rows))
    save_img("rotL", rot_left)

    # --- VARIATION 7: ROTATE RIGHT (5 Degrees) ---
    M_right = cv2.getRotationMatrix2D((cols / 2, rows / 2), -5, 1)
    rot_right = cv2.warpAffine(img, M_right, (cols, rows))
    save_img("rotR", rot_right)

    # --- VARIATION 8: HIGH CONTRAST ---
    # Helps pick out features in flat lighting
    # Convert to YUV color space, equalize the Y channel, convert back
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
    contrast = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    save_img("contrast", contrast)

    print(f"✅ Success: Generated 8 variations for {username}. (Total 9 images)")
    return True