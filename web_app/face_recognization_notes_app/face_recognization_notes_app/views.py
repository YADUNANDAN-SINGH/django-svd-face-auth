import json
import base64
import os
import secrets
import sys
from pathlib import Path
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import redirect
from django.conf import settings

# --- 1. ROBUST IMPORT SETUP ---
try:
    # A. Find the Project Root
    # views.py -> face_app -> web_app -> PROJECT_ROOT
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent

    # B. Add the PROJECT ROOT to Python's search path
    # This allows us to say "from math_engine import..."
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

    # Debug logs to verify
    print("--------------------------------------------------")
    print(f"📍 Project Root detected: {project_root}")

    # C. Import using the folder name (More stable)
    from math_engine.augmenter import generate_variations
    from math_engine.trainer import train_model
    from math_engine.inference import recognize_face

    print("✅ SUCCESS: Math Engine loaded via Root Path.")
    print("--------------------------------------------------")

except ImportError as e:
    print("❌ CRITICAL IMPORT ERROR.")
    print(f"   Error: {e}")
    print(f"   Path attempted: {project_root}")
    print("--------------------------------------------------")


    # Dummy functions to prevent server crash
    def generate_variations(*args):
        print("❌ Augmenter not loaded")


    def train_model(*args):
        print("❌ Trainer not loaded")


    def recognize_face(*args):
        print("❌ Inference not loaded")
        return None


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        try:
            print("------------------------------------------------")
            print("🚀 SIGNUP REQUEST STARTED")

            # 1. Parse Data
            data = json.loads(request.body)
            username = data.get('username')
            image_data = data.get('imageData')

            # 2. Validation
            if not username:
                return JsonResponse({'status': 'error', 'message': 'Username is required'})

            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Username taken'})

            # 3. Create User
            print(f"👤 Creating user: {username}")
            random_password = secrets.token_urlsafe(20)
            user = User.objects.create_user(username=username, password=random_password)
            user.save()

            # 4. Handle Image
            if image_data:
                try:
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    decoded_file = base64.b64decode(imgstr)

                    faces_dir = os.path.join(settings.MEDIA_ROOT, 'faces')
                    if not os.path.exists(faces_dir):
                        os.makedirs(faces_dir)

                    file_name = f"{username}.{ext}"
                    file_path = os.path.join(faces_dir, file_name)

                    with open(file_path, 'wb') as f:
                        f.write(decoded_file)
                    print(f"💾 Original photo saved: {file_path}")

                    # --- 5. TRIGGER MATH ENGINE ---
                    try:
                        print("⚡ Starting AI Pipeline...")

                        # Step A: Augment
                        # Note: We pass the full file path
                        generate_variations(file_path, username)

                        # Step B: Train
                        train_model()

                        print("✅ AI Pipeline Complete.")

                    except Exception as ai_error:
                        print(f"❌ AI Engine Failed: {ai_error}")

                except Exception as e:
                    print(f"❌ Image Save Error: {e}")
                    user.delete()
                    return JsonResponse({'status': 'error', 'message': 'Image processing failed'})

            # 5. Log in the user
            auth_login(request, user)
            print(f"✅ User {username} logged in successfully")

            return JsonResponse({'status': 'success', 'message': 'User registered successfully!', 'redirect': '/'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
        except Exception as e:
            print(f"❌ Server Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('imageData')

            # The user might claim to be "alice", or we might just identify them from the face.
            # For security, let's verify the face matches the user.
            claimed_username = data.get('username')

            if not image_data:
                return JsonResponse({'status': 'error', 'message': 'No face detected'})

            # 1. Save the Login Photo (Temporarily)
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            decoded_file = base64.b64decode(imgstr)

            # We save it to a 'temp' folder so we don't clutter the main faces folder
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            temp_filename = f"login_attempt_{secrets.token_hex(4)}.{ext}"
            temp_path = os.path.join(temp_dir, temp_filename)

            with open(temp_path, 'wb') as f:
                f.write(decoded_file)

            # 2. RUN RECOGNITION
            print(f"🕵️ Analyzing face for login: {claimed_username}...")

            # This function returns the name of the person (e.g., "yadunandan") or None
            identified_user = recognize_face(temp_path)

            # Clean up (Delete the temp file)
            if os.path.exists(temp_path):
                os.remove(temp_path)

            # 3. VERDICT
            if identified_user:
                # OPTIONAL: Check if the face matches the typed username
                # If you want password-less login, just log them in as 'identified_user'

                if claimed_username and identified_user != claimed_username:
                     return JsonResponse({'status': 'error', 'message': f"Face recognized as {identified_user}, not {claimed_username}!"})

                try:
                    user = User.objects.get(username=identified_user)
                    auth_login(request, user)
                    print(f"✅ Login Successful! Welcome, {identified_user}")
                    return JsonResponse({'status': 'success', 'username': identified_user})
                except User.DoesNotExist:
                    print(f"❌ User found in model but not in DB: {identified_user}")
                    return JsonResponse({'status': 'error', 'message': 'User recognized but not found in database.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Face not recognized.'})

        except Exception as e:
            print(f"Login Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('/')