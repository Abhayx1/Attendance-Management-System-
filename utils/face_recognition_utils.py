import os
import cv2
import numpy as np
import base64
from deepface import DeepFace

USERS_DB_PATH = os.path.join(os.getcwd(), 'models', 'users')

# Ensure the DB directory exists
if not os.path.exists(USERS_DB_PATH):
    os.makedirs(USERS_DB_PATH)

def decode_base64_image(base64_string):
    """Decodes a base64 image string into an OpenCV image (numpy array BGR format)."""
    # Remove prefix if present, e.g., 'data:image/jpeg;base64,'
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def register_face(employee_id, base64_string):
    """
    Registers a face by checking its liveness first, then saving it to the users DB.
    Returns: dict {'success': bool, 'message': str, 'path': str}
    """
    img = decode_base64_image(base64_string)
    if img is None:
        return {'success': False, 'message': 'Invalid image format.'}
    
    try:
        # Check if it's a valid face and preferably real (anti-spoofing)
        # DeepFace v0.0.86+ supports anti_spoofing. If we have to fall back, we wrap in try/except.
        faces = DeepFace.extract_faces(img_path=img, detector_backend='opencv', enforce_detection=True, anti_spoofing=True)
        
        if not faces:
            return {'success': False, 'message': 'No face detected in the image.'}
            
        face_obj = faces[0]
        # Check liveness if "is_real" is returned by DeepFace
        if 'is_real' in face_obj and face_obj['is_real'] is False:
             return {'success': False, 'message': 'Spoofing attempt detected. Face does not appear live.'}

        # Clear existing models' pkl cache so DeepFace updates its embeddings
        pkl_path = os.path.join(USERS_DB_PATH, "representations_vgg_face.pkl")
        if os.path.exists(pkl_path):
            os.remove(pkl_path)
            
        # Save the full image to the DB directory
        file_path = os.path.join(USERS_DB_PATH, f"{employee_id}.jpg")
        cv2.imwrite(file_path, img)
        return {'success': True, 'message': 'Face registered successfully.', 'path': file_path}

    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print("Registration Error:", error_msg)
        return {'success': False, 'message': f'Error extracting face: {error_msg}'}

def recognize_face(base64_string):
    """
    Recognizes a face against the registered DB.
    Includes anti-spoofing check.
    Returns: dict {'success': bool, 'identity': str, 'message': str, 'is_spoof': bool}
    """
    img = decode_base64_image(base64_string)
    if img is None:
        return {'success': False, 'message': 'Invalid image format.', 'is_spoof': False}
    
    # Fast check if directory is empty
    if not os.listdir(USERS_DB_PATH):
        return {'success': False, 'message': 'No registered users available.', 'is_spoof': False}

    try:
        # Anti-Spoofing Check First
        faces = DeepFace.extract_faces(img_path=img, detector_backend='opencv', enforce_detection=False, anti_spoofing=True)
        if faces and len(faces) > 0:
            face_obj = faces[0]
            if 'is_real' in face_obj and face_obj['is_real'] is False:
                return {'success': False, 'message': 'Spoofing attempt detected. Face does not appear live.', 'identity': None, 'is_spoof': True}
        else:
             return {'success': False, 'message': 'No face detected in feed.', 'is_spoof': False}

        # Recognition against DB
        # Silent output to keep console clean, anti_spoofing=True automatically implemented inside DeepFace.find if extracted
        results = DeepFace.find(img_path=img, db_path=USERS_DB_PATH, enforce_detection=False, silent=True)
        
        if results and len(results) > 0:
            df = results[0]
            if not df.empty:
                # Get the top match
                matched_path = df.iloc[0]['identity'] # returns the matched file path e.g. /models/users/EMP001.jpg
                # Extract employee ID from path
                basename = os.path.basename(matched_path)
                employee_id = os.path.splitext(basename)[0]
                return {'success': True, 'identity': employee_id, 'message': 'Face recognized successfully.', 'is_spoof': False}
                
        return {'success': False, 'identity': None, 'message': 'Face not recognized.', 'is_spoof': False}

    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print("Recognition Error:", error_msg)
        return {'success': False, 'message': f'DeepFace internal error: {error_msg}', 'is_spoof': False}
