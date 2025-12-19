import cv2
import numpy as np
import os
import pickle

# CONFIGRATION

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FACES_DIR = os.path.join(CURRENT_DIR, '..', 'web_app', 'face_recognization_notes_app', 'media', 'faces')

# Definign the standard size, if image not maches this size then our math breaks

IMG_WIDTH = 100
IMG_HEIGHT = 100

# FINALLY WRITING THE LOGIC TO TRAIN THE MODEL

def train_model():
    print('STARTING TRAINING')

    faces_matrix = []
    names_index = []

    if not os.path.exists(FACES_DIR):
        print('No faces directory found')
        return False

#     it will get all .jpg and .png files
    files = [f for f in os.listdir(FACES_DIR) if f.endswith('.jpg') or f.endswith('.png')]

    if len(files) == 0:
        print("❌ ERROR: No images found. Run the Signup/Augmenter first.")
        return False

    print(f" Found {len(files)} images. Processing...")

    for filename in files:
        path = os.path.join(FACES_DIR, filename)

        # 1. Read in Grayscale (Colors are noise for SVD)
        img = cv2.imread(path, 0)

        if img is None: continue

#         NOW RESIZING THE IMAGE TO 100*100PX

        img_resized = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))

#         CONVERTING 2D SQUARE INTO 1 LONG LINE (10000 NUMBERS)

        img_flat = img_resized.flatten()

        faces_matrix.append(img_flat)

        name_part = filename.split('_')[0]

        names_index.append(name_part)

#     converting list into numpy array.

    data_matrix = np.array(faces_matrix)

#     Taking transpose

    data_matrix = data_matrix.T

#     Calculating the mean face

    mean_face = data_matrix.mean(axis=1).reshape(-1, 1)

    centered_matrix = data_matrix - mean_face

    U, S, Vt = np.linalg.svd(centered_matrix, full_matrices=False)

    weights = np.dot(U.T, centered_matrix)

    print("Calculation completed.")

    model_data = {
        "mean_face": mean_face,
        "eigenfaces": U,
        "weights": weights,
        "labels": names_index
    }

    save_path = os.path.join(CURRENT_DIR, 'face_model.pkl')

    with open(save_path, 'wb') as f:
        pickle.dump(model_data, f)

    print(f"✅ Success: Model saved to: {save_path}")
    print("--------------------------------------")
    return True


if __name__ == "__main__":
    train_model()