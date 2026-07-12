import json
import logging
import re
import os
import time
from pathlib import Path
import tempfile
import base64
from io import BytesIO

from PIL import Image, UnidentifiedImageError

try:
    from geniex import AutoModelForCausalLM
    GENIEX_AVAILABLE = True
except ImportError:
    GENIEX_AVAILABLE = False

logger = logging.getLogger("landsense.ai.npu_engine")

ALLOWED_STAGES = [
    "Empty Plot",
    "Not Started",
    "Site Preparation",
    "Foundation",
    "Structural Work",
    "Brickwork",
    "Ongoing Building Construction",
    "Finishing",
    "Completed",
    "Developed Construction",
    "House",
    "Building",
    "Unknown",
]

class ImageDecodeError(ValueError):
    pass

class SnapdragonVisionEngine:
    """
    Contract-stable Vision Inference Engine running locally via GenieX on Snapdragon NPU.
    """

    def __init__(self, model_dir: str = "google/gemma-4-E4B-it-qat-q4_0-gguf", model_name: str = "Snapdragon Vision Engine (GenieX)"):
        self.model_name = model_name
        self.model_dir = model_dir
        self.loaded = False
        self.device = "Snapdragon NPU (Hexagon)"
        self.runtime_backend = "geniex"
        self.load_error = None
        
        self.model = None

        if not GENIEX_AVAILABLE:
            self.load_error = "geniex is not installed."
            logger.warning(self.load_error)
            return

        started = time.perf_counter()
        
        try:
            logger.info(f"Initializing GenieX AutoModelForCausalLM with {model_dir}...")
            # Attempt to load GGUF model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_dir,
                precision="Q4_0"
            )

            self.loaded = True
            load_time_ms = round((time.perf_counter() - started) * 1000, 2)

            logger.info(
                "%s initialized with %s on %s in %.2fms",
                self.model_name,
                self.runtime_backend,
                self.device,
                load_time_ms,
            )
        except Exception as e:
            self.load_error = f"Failed to initialize GenieX engine: {e}"
            logger.exception(self.load_error)

    def analyze_frame(self, image_path: str, prompt_text: str = "Describe this image."):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Target frame missing: {image_path}")
            
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image_path},
                {"type": "text", "text": prompt_text}
            ]
        }]
        
        # Generate the raw structured text tokens for the NPU
        prompt = self.model.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Execute local NPU acceleration array pass
        response = self.model.generate(prompt, images=[image_path], max_new_tokens=512)
        return response.text

    def predict(self, images: list[str]) -> dict:
        started = time.perf_counter()
        if not self.loaded:
            raise RuntimeError(f"Model not loaded. Reason: {self.load_error}")
            
        if not images:
            raise ImageDecodeError("Invalid image")

        temp_paths = []
        try:
            for item in images[:4]:
                raw = self._read_image_bytes(item)
                image = Image.open(BytesIO(raw))
                image.verify()
                image = Image.open(BytesIO(raw)).convert("RGB")
                
                # Resize if necessary to save memory
                image.thumbnail((1024, 1024))
                
                fd, temp_path = tempfile.mkstemp(suffix=".jpg")
                os.close(fd)
                image.save(temp_path, format="JPEG")
                temp_paths.append(temp_path)
                
            prompt_text = (
                "Analyze this image. If it is a real estate or construction-site image, it could be an empty plot, ongoing construction, developed construction, building, or house. "
                "If the image is completely unrelated (e.g. a random selfie, an animal, a car, or something else), describe exactly what is in the photo in the 'description' field, but explicitly state that it is NOT a relevant real estate or construction photo. "
                "Return ONLY a raw JSON dictionary without markdown code blocks, with these exact keys: construction_stage, progress_percentage, confidence, description. "
                f"Allowed construction_stage values: {', '.join(ALLOWED_STAGES)}. Use 'Unknown' for unrelated photos. "
                "Keep confidence between 0 and 1. "
                "Verify there is no site obstruction and no face selfies."
            )
            
            logger.info("Generating response with GenieX...")
            # For simplicity, if multiple images are provided we just analyze the first one 
            # since the provided wrapper handles a single image_path well.
            generated_text = self.analyze_frame(temp_paths[0], prompt_text)
            
            logger.info("Raw generated text: %s", generated_text)

            parsed = self._parse_vlm_json(generated_text)
            if not parsed:
                stage = "Unknown"
                progress = 0
                confidence = 0.0
                description = generated_text[:200]
            else:
                stage = parsed.get("construction_stage", "Unknown")
                progress = parsed.get("progress_percentage", 0)
                confidence = parsed.get("confidence", 0.0)
                description = parsed.get("description", "Analyzed by Local NPU Model.")
            
        except Exception as e:
            logger.exception("VLM inference failed")
            stage = "Unknown"
            progress = 0
            confidence = 0.0
            description = f"Inference error: {str(e)}"
        finally:
            for temp_path in temp_paths:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except OSError:
                    pass
            
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            "Inference completed in %.2fms | confidence=%.2f | image_count=%d",
            elapsed_ms,
            confidence,
            len(temp_paths),
        )

        return {
            "construction_stage": stage,
            "progress_percentage": progress,
            "confidence": confidence,
            "description": description,
            "embedding": [0.0] * 128,
            "model": self.model_name,
            "device": self.device,
            "runtime_backend": self.runtime_backend,
            "ai_backend": "npu_vlm",
            "inference_source": "npu",
            "model_artifacts_loaded": self.loaded,
            "model_load_error": self.load_error,
            "openrouter_enabled": False,
            "openrouter_model": None,
            "openrouter_error": None,
            "image_count": len(temp_paths),
            "site_likelihood": 0.0,
            "opencv_analysis": {},
        }

    def _read_image_bytes(self, image_ref: str) -> bytes:
        if not image_ref or not isinstance(image_ref, str):
            raise ImageDecodeError("Invalid image")

        if image_ref.startswith("data:image/"):
            _, encoded = image_ref.split(",", 1)
            return base64.b64decode(encoded, validate=True)

        candidate = Path(image_ref)
        if candidate.exists() and candidate.is_file():
            return candidate.read_bytes()

        return base64.b64decode(image_ref, validate=True)

    def _parse_vlm_json(self, text: str) -> dict | None:
        decoder = json.JSONDecoder()
        data = None
        for match in re.finditer(r"\{", text):
            try:
                candidate, _ = decoder.raw_decode(text[match.start():])
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, dict):
                data = candidate
                break
        if data is None:
            return None

        stage = str(data.get("construction_stage", "Unknown")).strip()
        if stage not in ALLOWED_STAGES:
            stage = "Unknown"

        try:
            progress = int(round(float(data.get("progress_percentage", 0))))
        except (TypeError, ValueError):
            progress = 0
        progress = max(0, min(100, progress))

        try:
            confidence = float(data.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))

        return {
            "construction_stage": stage,
            "progress_percentage": progress,
            "confidence": confidence,
            "description": str(data.get("description", "")),
        }
