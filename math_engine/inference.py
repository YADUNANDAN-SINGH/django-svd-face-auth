import cv2
import numpy as np
import os
import pickle

# CONFIGURATION
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, 'face_model.pkl')
IMG_WIDTH = 100
IMG_HEIGHT = 100

def recognize_face(image_path, threshold=2000):
    """
    Recognizes a face from an image path using the trained Eigenfaces model.
    Returns the username if recognized, otherwise None.
    """
    if not os.path.exists(MODEL_PATH):
        print("❌ Error: Model not found. Please train the model first.")
        return None

    try:
        with open(MODEL_PATH, 'rb') as f:
            model_data = pickle.load(f)
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

    mean_face = model_data["mean_face"]
    eigenfaces = model_data["eigenfaces"]
    weights = model_data["weights"]
    labels = model_data["labels"]

    # 1. Process Input Image
    img = cv2.imread(image_path, 0)
    if img is None:
        print("❌ Error: Could not read image.")
        return None

    try:
        img_resized = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
        img_flat = img_resized.flatten().reshape(-1, 1)
        
        # 2. Project Input Image
        img_centered = img_flat - mean_face
        
        # Project into Eigenface space: weights_input = U.T * (Input - Mean)
        # Note: In trainer.py, U was calculated on (data - mean).
        # weights stored are U.T * (data - mean)
        
        # Dimensions Check:
        # img_centered: (10000, 1)
        # eigenfaces (U): (10000, N_files) -> if full matrices=False
        # But wait, trainer.py used svd on centered_matrix (10000, N). 
        # U is (10000, K). 
        # weights = U.T . centered_matrix -> (K, N)
        
        # So for input:
        input_weight = np.dot(eigenfaces.T, img_centered) # (K, 1)

        # 3. Find Best Match
        min_dist = float('inf')
        best_match_index = -1

        # weights shape is (K, N_samples)
        num_samples = weights.shape[1]
        
        for i in range(num_samples):
            # Get the weight vector for the i-th training sample
            train_weight = weights[:, i].reshape(-1, 1)
            
            # Euclidean distance
            dist = np.linalg.norm(input_weight - train_weight)
            
            if dist < min_dist:
                min_dist = dist
                best_match_index = i
        
        print(f"🔍 Best match distance: {min_dist}")

        if min_dist < threshold:
            identified_user = labels[best_match_index]
            print(f"✅ Match Found: {identified_user} (Dist: {min_dist:.2f})")
            return identified_user
        else:
            print(f"❌ No match found. Closest was {labels[best_match_index]} with dist {min_dist:.2f}")
            return None

    except Exception as e:
        print(f"❌ Error during recognition: {e}")
        return None
