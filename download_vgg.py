import traceback

print("Building face models using DeepFace...")
try:
    from deepface import DeepFace
    print("Building VGG-Face...")
    model = DeepFace.build_model("VGG-Face")
    print("VGG-Face built successfully.")
except Exception as e:
    print("FAILED:", str(e))
    traceback.print_exc()
