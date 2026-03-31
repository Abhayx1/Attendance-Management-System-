import requests

url = "https://api.github.com/repos/serengil/deepface_models/releases/tags/v1.0"
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers)

with open("releases.json", "w", encoding="utf-8") as f:
    f.write(resp.text)
