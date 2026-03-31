import os
import requests

url = "https://huggingface.co/RaphaelLiu/EvalCrafter-Models/resolve/main/vgg_face_weights.h5"
path = r"C:\Users\abhay\.deepface\weights\vgg_face_weights.h5"

if os.path.exists(path):
    os.remove(path)

print("Starting robust download from Hugging Face Mirror...")
response = requests.get(url, stream=True, allow_redirects=True)
if response.status_code == 200:
    with open(path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    size = os.path.getsize(path)/(1024*1024)
    print(f"Success! Final size: {size:.2f} MB")
else:
    print(f"Failed HTTP {response.status_code}")
