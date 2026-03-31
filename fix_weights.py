import urllib.request
import zipfile
import os

zip_url = "https://github.com/serengil/deepface_models/releases/download/v1.0/vgg_face_weights.zip"
zip_path = r"C:\Users\abhay\.deepface\weights\vgg_face_weights.zip"
extract_dir = r"C:\Users\abhay\.deepface\weights"
target_file = r"C:\Users\abhay\.deepface\weights\vgg_face_weights.h5"

if os.path.exists(target_file):
    os.remove(target_file)

print("Downloading ZIP...")
try:
    urllib.request.urlretrieve(zip_url, zip_path)
    print("Unzipping...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("Done! Extracted file size:", os.path.getsize(target_file))
    os.remove(zip_path) # Cleanup
except Exception as e:
    print("Error:", str(e))
