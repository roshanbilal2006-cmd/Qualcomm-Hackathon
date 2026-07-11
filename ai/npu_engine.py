import base64
import json
import logging
import os
import re
import time
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

# Import litert_lm for local NPU execution on Hexagon
try:
    import litert_lm
    from litert_lm.interfaces import NPU
    LITERT_AVAILABLE = True
except ImportError:
    LITERT_AVAILABLE = False

logger = logging.getLogger("landsense.ai.npu_engine")

ALLOWED_STAGES = [
    "Not Started",
    "Site Preparation",
    "Foundation",
    "Structural Work",
    "Brickwork",
    "Finishing",
    "Completed",
    "Unknown",
]


class ImageDecodeError(ValueError):
    pass


class LocalNPUEngine:
    """
    Contract-stable Vision Inference Engine running locally on the Hexagon NPU
    via LiteRT-LM (QNN delegate).
    """

    def __init__(self, model_dir: str = "C:/Landsense/ai/models/vlm/gemma-4-E2B-it_qualcomm_sm8750.litertlm", model_name: str = "Local Gemma-4 NPU"):
        self.model_name = model_name
        self.model_dir = model_dir
        self.loaded = False
        self.device = "Hexagon NPU"
        self.runtime_backend = "litert_lm_qnn"
        self.load_error = None
        
        self.engine = None
        self.conversation = None

        if not LITERT_AVAILABLE:
            self.load_error = "litert_lm is not installed."
            logger.warning(self.load_error)
            return

        # Check if model file exists
        model_path = Path(self.model_dir)
        if not model_path.exists():
            # Try to find a litertlm file in the parent folder if the exact one is missing
            parent_dir = Path("C:/Landsense/ai/models/vlm")
            if parent_dir.exists():
                models = list(parent_dir.glob("*.litertlm"))
                if models:
                    model_path = models[0]
                    self.model_dir = str(model_path)
                else:
                    self.load_error = f"Model file {self.model_dir} not found."
                    logger.warning(self.load_error)
                    return
            else:
                self.load_error = f"Model directory {parent_dir} not found."
                logger.warning(self.load_error)
                return

        started = time.perf_counter()
        
        try:
            # Set up the LiteRT Engine with NPU backend (QNN Provider Handle)
            # Default to Qualcomm's 'burst' mode for optimal latency
            os.environ["QNN_PERFORMANCE_MODE"] = "burst"
            
            self.engine = litert_lm.Engine(
                model_path=str(model_path),
                backend=NPU(),
                htp_performance_mode="burst"
            )
            self.conversation = self.engine.create_conversation()

            self.loaded = True
            load_time_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.info(
                "%s initialized with %s on Hexagon NPU in %.2fms",
                self.model_name,
                self.runtime_backend,
                load_time_ms,
            )
        except Exception as e:
            self.load_error = f"Failed to initialize NPU engine: {e}"
            logger.exception(self.load_error)

    def predict(self, images: list[str]) -> dict:
        started = time.perf_counter()
        if not self.loaded:
            raise RuntimeError(f"Model not loaded. Reason: {self.load_error}")
            
        if not images:
            raise ImageDecodeError("Invalid image")

        # Keep original bytes for the model, decode up to 4 images
        # The model usually expects resizing, but we let litert_lm handle raw bytes or resized bytes.
        raw_image_bytes = []
        for item in images[:4]:
            # We resize and compress slightly to manage context size if needed, then re-encode
            img = self._decode_image(item)
            buf = BytesIO()
            img.save(buf, format="JPEG")
            raw_image_bytes.append(buf.getvalue())
        
        # Apply the Gemma 4 wrappers to enforce verification logic
        prompt = (
            "<|im_start|>\n"
            "Analyze this land or construction-site image for LandSense. "
            "Return only compact JSON with keys construction_stage, progress_percentage, confidence, description. "
            f"Allowed construction_stage values: {', '.join(ALLOWED_STAGES)}. "
            "Use Unknown and 0 progress when the image does not show a construction site. "
            "Keep confidence between 0 and 1. "
            "Verify there is no site obstruction and no face selfies.\n"
            "<|im_end|>\n"
        )
        
        try:
            contents_list = []
            for img_bytes in raw_image_bytes:
                contents_list.append(litert_lm.Content.ImageBytes(img_bytes))
            contents_list.append(litert_lm.Content.Text(prompt))
            
            contents = litert_lm.Contents.of(*contents_list)
            
            response = self.conversation.send_message(contents)
            
            generated_text = ""
            if isinstance(response, dict):
                content_val = response.get("content", "")
                if isinstance(content_val, str):
                    generated_text = content_val
                elif isinstance(content_val, list):
                    for part in content_val:
                        if isinstance(part, dict) and part.get("type") == "text":
                            generated_text += part.get("text", "")
                        elif isinstance(part, str):
                            generated_text += part
            else:
                generated_text = str(response)

            parsed = self._parse_vlm_json(generated_text)
            
            if not parsed:
                raise ValueError("VLM returned unparsable output")
                
            stage = parsed.get("construction_stage", "Unknown")
            progress = parsed.get("progress_percentage", 0)
            confidence = parsed.get("confidence", 0.0)
            description = parsed.get("description", "Analyzed by Local NPU.")
            
        except Exception as e:
            logger.exception("NPU VLM inference failed")
            stage = "Unknown"
            progress = 0
            confidence = 0.0
            description = f"NPU inference error: {str(e)}"
            
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            "NPU Inference completed in %.2fms | confidence=%.2f | image_count=%d",
            elapsed_ms,
            confidence,
            len(raw_image_bytes),
        )

        return {
            "construction_stage": stage,
            "progress_percentage": progress,
            "confidence": confidence,
            "description": description,
            "embedding": [0.0] * 128,  # Dummy embedding
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
            "image_count": len(raw_image_bytes),
            "site_likelihood": 0.0,
            "opencv_analysis": {},
        }

    def _decode_image(self, image_ref: str) -> Image.Image:
        try:
            raw = self._read_image_bytes(image_ref)
            image = Image.open(BytesIO(raw))
            image.verify()
            image = Image.open(BytesIO(raw)).convert("RGB")
            # Resize image to something the VLM expects
            image.thumbnail((448, 448))
            return image
        except (OSError, ValueError, UnidentifiedImageError) as exc:
            raise ImageDecodeError("Invalid image") from exc

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
