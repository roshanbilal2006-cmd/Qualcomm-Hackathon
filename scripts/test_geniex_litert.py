import sys
try:
    from geniex import AutoModelForCausalLM
    print("Geniex imported successfully")
    
    # Try loading the directory instead of the file
    model_dir = r"C:\Landsense\ai\models\vlm"
    model = AutoModelForCausalLM.from_pretrained(model_dir)
    print("Successfully loaded model!")
    print(type(model))
    
except Exception as e:
    print(f"Error: {e}")
