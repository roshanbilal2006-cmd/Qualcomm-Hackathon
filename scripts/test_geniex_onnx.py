import sys
try:
    from geniex import AutoModelForCausalLM
    print("Geniex imported successfully")
    
    # Try loading the ONNX model they downloaded
    model_dir = r"C:\Landsense\ai\models\vlm\phi3v\cpu-int4-rtn-block-32-acc-level-4"
    model = AutoModelForCausalLM.from_pretrained(model_dir)
    print("Successfully loaded model!")
    print(type(model))
    
except Exception as e:
    print(f"Error: {e}")
