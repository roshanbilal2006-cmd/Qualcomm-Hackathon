import os
from huggingface_hub import snapshot_download

def download_model():
    print("Downloading microsoft/Phi-3-vision-128k-instruct-onnx-cpu...")
    # Enable hf_transfer for blazing fast downloads
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    
    # We only need the specific folder inside the repo, so we can use allow_patterns if needed, 
    # but the whole repo is fine. The cpu-int4-rtn-block-32-acc-level-4 folder contains the ONNX.
    local_dir = "C:/Landsense/ai/models/vlm/phi3v"
    
    snapshot_download(
        repo_id="microsoft/Phi-3-vision-128k-instruct-onnx-cpu",
        local_dir=local_dir,
        allow_patterns=["cpu-int4-rtn-block-32-acc-level-4/*"],
        max_workers=8
    )
    print(f"Download complete! Saved to {local_dir}")

if __name__ == "__main__":
    download_model()
