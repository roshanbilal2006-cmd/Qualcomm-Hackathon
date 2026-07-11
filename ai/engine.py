import base64
import hashlib
import json
import logging
import math
import os
import re
import time
from dataclasses import dataclass
from io import BytesIO
from statistics import mean
from typing import Iterable

import cv2
import numpy as np
from PIL import Image, ImageStat, UnidentifiedImageError

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - dotenv is optional at runtime
    load_dotenv = None

logger = logging.getLogger("landsense.ai.engine")

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


@dataclass(frozen=True)
class ImageFeatures:
    brightness: float
    contrast: float
    saturation: float
    edge_density: float
    line_density: float
    rectangular_structure: float
    aspect_ratio: float
    concrete_fraction: float
    earth_fraction: float
    sky_fraction: float
    vegetation_fraction: float
    equipment_color_fraction: float
    artificial_color_score: float
    construction_likelihood: float


class ImageDecodeError(ValueError):
    pass


class VisionInferenceEngine:
    """
    Contract-stable OpenRouter + OpenCV vision engine boundary.

    OpenCV extracts deterministic scene metrics for validation and embeddings.
    OpenRouter is the primary VLM path when OPENROUTER_API_KEY is configured;
    if the key or API is unavailable, the service falls back to OpenCV-only
    stage estimation while preserving the same backend contract.
    """

    def __init__(self, model_name: str = "OpenRouter+OpenCV", embedding_size: int = 128):
        if load_dotenv:
            load_dotenv()

        started = time.perf_counter()
        self.model_name = model_name
        self.embedding_size = embedding_size
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.openrouter_vision_model = os.getenv("OPENROUTER_VISION_MODEL", "openai/gpt-5.6-luna")
        self.openrouter_referer = os.getenv("OPENROUTER_HTTP_REFERER")
        self.openrouter_title = os.getenv("OPENROUTER_APP_TITLE", "LandSense")
        self._openrouter_client = None
        self._openrouter_error = None
        if self.openrouter_api_key:
            self.runtime_backend = f"OpenRouter vision + OpenCV ({self.openrouter_vision_model})"
            self.device = "OpenRouter cloud VLM + local OpenCV"
        else:
            self.runtime_backend = "OpenCV fallback (OPENROUTER_API_KEY missing)"
            self.device = "local OpenCV"
        self.loaded = True
        self.load_time_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            "%s initialized with %s in %.2fms",
            self.model_name,
            self.runtime_backend,
            self.load_time_ms,
        )

    def predict(self, images: list[str]) -> dict:
        started = time.perf_counter()
        if not images:
            raise ImageDecodeError("Invalid image")

        decoded = [self._decode_image(item) for item in images[:4]]
        features = [self._extract_features(image) for image in decoded]
        combined = self._combine_features(features)

        stage, progress = self._estimate_stage(combined)
        confidence = self._estimate_confidence(combined, len(decoded))
        vlm_result = self._predict_with_openrouter(decoded, combined, stage, progress, confidence)
        inference_source = "openrouter" if vlm_result else "opencv_fallback"
        if vlm_result:
            stage = vlm_result.get("construction_stage", stage)
            progress = vlm_result.get("progress_percentage", progress)
            confidence = vlm_result.get("confidence", confidence)
        description = self._describe(stage, progress, combined, vlm_result, inference_source)
        embedding = self._build_embedding(decoded, combined)

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            "Inference completed in %.2fms | confidence=%.2f | image_count=%d",
            elapsed_ms,
            confidence,
            len(decoded),
        )

        return {
            "construction_stage": stage,
            "progress_percentage": progress,
            "confidence": confidence,
            "description": description,
            "embedding": embedding,
            "model": self.model_name,
            "device": self.device,
            "runtime_backend": self.runtime_backend,
            "ai_backend": "openrouter_opencv",
            "inference_source": inference_source,
            "model_artifacts_loaded": False,
            "model_load_error": None,
            "openrouter_enabled": bool(self.openrouter_api_key),
            "openrouter_model": self.openrouter_vision_model if self.openrouter_api_key else None,
            "openrouter_error": self._openrouter_error,
            "image_count": len(decoded),
            "site_likelihood": round(combined.construction_likelihood, 2),
            "opencv_analysis": self._analysis_payload(combined),
        }

    def _get_openrouter_client(self):
        if self._openrouter_client is not None:
            return self._openrouter_client
        if not self.openrouter_api_key:
            return None

        try:
            from openai import OpenAI

            headers = {"X-Title": self.openrouter_title}
            if self.openrouter_referer:
                headers["HTTP-Referer"] = self.openrouter_referer
            self._openrouter_client = OpenAI(
                base_url=self.openrouter_base_url,
                api_key=self.openrouter_api_key,
                default_headers=headers,
            )
            return self._openrouter_client
        except Exception as exc:
            self._openrouter_error = str(exc)
            logger.exception("OpenRouter client could not be initialized")
            return None

    def _predict_with_openrouter(
        self,
        images: list[Image.Image],
        features: ImageFeatures,
        fallback_stage: str,
        fallback_progress: int,
        fallback_confidence: float,
    ) -> dict | None:
        client = self._get_openrouter_client()
        if client is None:
            return None

        prompt = (
            "Analyze these land or construction-site images for LandSense. "
            "Return only compact JSON with keys construction_stage, progress_percentage, confidence, description. "
            f"Allowed construction_stage values: {', '.join(ALLOWED_STAGES)}. "
            "Use Unknown and 0 progress when the images do not show a construction site. "
            "Keep confidence between 0 and 1. "
            "Local CV guardrail metrics are: "
            f"site_likelihood={features.construction_likelihood:.2f}, "
            f"concrete={features.concrete_fraction:.2f}, earth={features.earth_fraction:.2f}, "
            f"equipment_cue={self._effective_equipment_signal(features):.2f}, "
            f"line_density={features.line_density:.2f}. "
            f"Fallback estimate: stage={fallback_stage}, progress={fallback_progress}, confidence={fallback_confidence:.2f}."
        )
        content = [{"type": "text", "text": prompt}]
        content.extend(
            {"type": "image_url", "image_url": {"url": self._image_to_data_url(image)}}
            for image in images[:4]
        )

        try:
            response = client.chat.completions.create(
                model=self.openrouter_vision_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise construction progress vision analyst. Output valid JSON only.",
                    },
                    {"role": "user", "content": content},
                ],
                temperature=0.0,
                max_tokens=220,
                response_format={"type": "json_object"},
            )
            text = self._message_content_to_text(response.choices[0].message.content)
            parsed = self._parse_vlm_json(text)
            if not parsed:
                self._openrouter_error = "OpenRouter returned unparsable JSON"
                return None
            self._openrouter_error = None
            return parsed
        except Exception as exc:
            self._openrouter_error = str(exc)
            logger.exception("OpenRouter vision inference failed; falling back to local analysis")
            return None

    def _image_to_data_url(self, image: Image.Image) -> str:
        buffer = BytesIO()
        image.convert("RGB").save(buffer, format="JPEG", quality=85, optimize=True)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"

    def _message_content_to_text(self, content) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    parts.append(str(part.get("text", "")))
                elif hasattr(part, "text"):
                    parts.append(str(part.text))
            return "\n".join(parts)
        return str(content or "")

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
            "description": self._clean_vlm_text(str(data.get("description", ""))),
        }

    def _clean_vlm_text(self, text: str) -> str:
        cleaned = re.sub(r"```(?:json)?|```", "", text or "", flags=re.IGNORECASE).strip()
        cleaned = re.split(r"\n\s*(?:I hope this helps|Let me know|[*_]*Question:|[*_]*Answer:)", cleaned, maxsplit=1)[0]
        cleaned = cleaned.strip(" \n\r\t{}")
        cleaned = re.sub(r'^[\s,"\':;.-]+', "", cleaned)
        if len(cleaned) > 360:
            cleaned = cleaned[:357].rsplit(" ", 1)[0].rstrip(".,;:") + "..."
        return cleaned or "OpenRouter reviewed the uploaded image."

    def _decode_image(self, image_ref: str) -> Image.Image:
        try:
            raw = self._read_image_bytes(image_ref)
            image = Image.open(BytesIO(raw))
            image.verify()
            image = Image.open(BytesIO(raw)).convert("RGB")
            image.thumbnail((512, 512))
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

    def _extract_features(self, image: Image.Image) -> ImageFeatures:
        resized = image.resize((128, 128))
        gray = resized.convert("L")
        stat_gray = ImageStat.Stat(gray)

        brightness = stat_gray.mean[0] / 255.0
        contrast = min(stat_gray.stddev[0] / 96.0, 1.0)
        saturation = self._mean_saturation(resized)
        aspect_ratio = image.width / max(image.height, 1)

        cv_features = self._opencv_scene_features(resized)
        edge_density = cv_features["edge_density"]
        line_density = cv_features["line_density"]
        rectangular_structure = cv_features["rectangular_structure"]
        concrete_fraction = cv_features["concrete_fraction"]
        earth_fraction = cv_features["earth_fraction"]
        sky_fraction = cv_features["sky_fraction"]
        vegetation_fraction = cv_features["vegetation_fraction"]
        equipment_color_fraction = cv_features["equipment_color_fraction"]
        artificial_color_score = cv_features["artificial_color_score"]

        construction_likelihood = self._construction_likelihood(
            concrete_fraction=concrete_fraction,
            earth_fraction=earth_fraction,
            sky_fraction=sky_fraction,
            vegetation_fraction=vegetation_fraction,
            equipment_color_fraction=equipment_color_fraction,
            edge_density=edge_density,
            line_density=line_density,
            rectangular_structure=rectangular_structure,
            contrast=contrast,
            saturation=saturation,
            artificial_color_score=artificial_color_score,
        )

        return ImageFeatures(
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
            edge_density=edge_density,
            line_density=line_density,
            rectangular_structure=rectangular_structure,
            aspect_ratio=aspect_ratio,
            concrete_fraction=concrete_fraction,
            earth_fraction=earth_fraction,
            sky_fraction=sky_fraction,
            vegetation_fraction=vegetation_fraction,
            equipment_color_fraction=equipment_color_fraction,
            artificial_color_score=artificial_color_score,
            construction_likelihood=construction_likelihood,
        )

    def _mean_saturation(self, image: Image.Image) -> float:
        hsv = image.convert("HSV")
        saturation_values = list(hsv.getchannel("S").getdata())
        return mean(saturation_values) / 255.0

    def _opencv_scene_features(self, image: Image.Image) -> dict[str, float]:
        rgb = np.array(image.convert("RGB"))
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, 60, 150)
        edge_density = float(np.count_nonzero(edges) / edges.size)

        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=28,
            minLineLength=24,
            maxLineGap=6,
        )
        line_count = 0 if lines is None else len(lines)
        line_density = min(line_count / 90.0, 1.0)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        image_area = image.width * image.height
        rectangular_hits = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < image_area * 0.006:
                continue
            perimeter = cv2.arcLength(contour, True)
            if perimeter <= 0:
                continue
            approx = cv2.approxPolyDP(contour, 0.035 * perimeter, True)
            x, y, w, h = cv2.boundingRect(approx)
            fill_ratio = area / max(w * h, 1)
            if len(approx) >= 4 and 0.25 <= fill_ratio <= 0.98:
                rectangular_hits += 1
        rectangular_structure = min(rectangular_hits / 10.0, 1.0)

        hue = hsv[:, :, 0]
        sat = hsv[:, :, 1]
        val = hsv[:, :, 2]

        concrete_mask = (sat < 55) & (val > 55) & (val < 225)
        earth_mask = (hue >= 5) & (hue <= 28) & (sat > 45) & (val > 45)
        sky_mask = (hue >= 85) & (hue <= 112) & (sat > 30) & (val > 105)
        vegetation_mask = (hue >= 35) & (hue <= 82) & (sat > 45) & (val > 55)
        equipment_mask = (hue >= 12) & (hue <= 35) & (sat > 85) & (val > 115)
        high_saturation_mask = (sat > 145) & (val > 80)

        total = float(hue.size)
        material_fraction = (
            np.count_nonzero(concrete_mask | earth_mask | equipment_mask) / total
        )
        artificial_color_score = max(
            0.0,
            (np.count_nonzero(high_saturation_mask) / total) - material_fraction,
        )

        return {
            "edge_density": edge_density,
            "line_density": line_density,
            "rectangular_structure": rectangular_structure,
            "concrete_fraction": float(np.count_nonzero(concrete_mask) / total),
            "earth_fraction": float(np.count_nonzero(earth_mask) / total),
            "sky_fraction": float(np.count_nonzero(sky_mask) / total),
            "vegetation_fraction": float(np.count_nonzero(vegetation_mask) / total),
            "equipment_color_fraction": float(np.count_nonzero(equipment_mask) / total),
            "artificial_color_score": float(min(artificial_color_score, 1.0)),
        }

    def _construction_likelihood(
        self,
        concrete_fraction: float,
        earth_fraction: float,
        sky_fraction: float,
        vegetation_fraction: float,
        equipment_color_fraction: float,
        edge_density: float,
        line_density: float,
        rectangular_structure: float,
        contrast: float,
        saturation: float,
        artificial_color_score: float,
    ) -> float:
        equipment_signal = equipment_color_fraction
        if concrete_fraction + rectangular_structure >= 0.12:
            equipment_signal = equipment_color_fraction
        else:
            equipment_signal = min(equipment_color_fraction, 0.08)

        material_signal = min(
            concrete_fraction * 1.35
            + earth_fraction * 1.20
            + equipment_signal * 1.45,
            0.72,
        )
        outdoor_signal = min(sky_fraction * 0.25 + vegetation_fraction * 0.08, 0.18)
        structure_signal = min(
            edge_density * 0.35 + line_density * 0.28 + rectangular_structure * 0.22 + contrast * 0.12,
            0.46,
        )

        raw_score = material_signal + outdoor_signal + structure_signal
        hard_site_signal = concrete_fraction + equipment_signal + rectangular_structure

        # Warm portrait/anime backgrounds and tree branches can look like
        # "earth + lines"; do not let those cues pass without hard site evidence.
        if earth_fraction > 0.55 and concrete_fraction < 0.18 and equipment_signal < 0.18:
            raw_score = min(raw_score, 0.30)
        if line_density > 0.65 and rectangular_structure < 0.18 and concrete_fraction < 0.18:
            raw_score = min(raw_score, 0.32)
        if hard_site_signal < 0.22:
            raw_score = min(raw_score, 0.34)

        if concrete_fraction + earth_fraction + equipment_color_fraction < 0.10:
            raw_score = min(raw_score, 0.24)
        if vegetation_fraction > 0.45 and concrete_fraction + earth_fraction < 0.12:
            raw_score -= 0.12
        if saturation > 0.48 and artificial_color_score > 0.18 and material_signal < 0.18:
            raw_score -= 0.20

        return max(0.0, min(1.0, raw_score))

    def _combine_features(self, features: Iterable[ImageFeatures]) -> ImageFeatures:
        feature_list = list(features)
        return ImageFeatures(
            brightness=mean(f.brightness for f in feature_list),
            contrast=mean(f.contrast for f in feature_list),
            saturation=mean(f.saturation for f in feature_list),
            edge_density=mean(f.edge_density for f in feature_list),
            line_density=mean(f.line_density for f in feature_list),
            rectangular_structure=mean(f.rectangular_structure for f in feature_list),
            aspect_ratio=mean(f.aspect_ratio for f in feature_list),
            concrete_fraction=mean(f.concrete_fraction for f in feature_list),
            earth_fraction=mean(f.earth_fraction for f in feature_list),
            sky_fraction=mean(f.sky_fraction for f in feature_list),
            vegetation_fraction=mean(f.vegetation_fraction for f in feature_list),
            equipment_color_fraction=mean(f.equipment_color_fraction for f in feature_list),
            artificial_color_score=mean(f.artificial_color_score for f in feature_list),
            construction_likelihood=mean(f.construction_likelihood for f in feature_list),
        )

    def _estimate_stage(self, features: ImageFeatures) -> tuple[str, int]:
        if features.construction_likelihood < 0.35:
            return "Unknown", 0

        activity_score = (
            features.edge_density * 0.24
            + features.line_density * 0.22
            + features.rectangular_structure * 0.16
            + features.contrast * 0.20
            + min(features.concrete_fraction + features.earth_fraction, 0.35) * 0.28
            + (1.0 - abs(features.brightness - 0.55)) * 0.10
        )

        progress = int(max(0, min(100, round(10 + activity_score * 82))))

        if progress < 8:
            return "Not Started", progress
        if progress < 22:
            return "Site Preparation", progress
        if progress < 40:
            return "Foundation", progress
        if progress < 68:
            return "Structural Work", progress
        if progress < 82:
            return "Brickwork", progress
        if progress < 96:
            return "Finishing", progress
        return "Completed", progress

    def _estimate_confidence(self, features: ImageFeatures, image_count: int) -> float:
        if features.construction_likelihood < 0.35:
            return round(max(0.12, features.construction_likelihood), 2)

        clarity = (
            features.contrast * 0.28
            + features.edge_density * 0.18
            + features.line_density * 0.16
            + features.rectangular_structure * 0.12
            + 0.20
        )
        multi_view_bonus = min(image_count, 4) * 0.025
        site_bonus = min(features.construction_likelihood * 0.25, 0.18)
        confidence = max(0.55, min(0.96, clarity + multi_view_bonus + site_bonus))
        return round(confidence, 2)

    def _describe(
        self,
        stage: str,
        progress: int,
        features: ImageFeatures,
        vlm_result: dict | None = None,
        inference_source: str = "opencv_fallback",
    ) -> str:
        equipment_cue = self._effective_equipment_signal(features)
        if vlm_result:
            vlm_description = vlm_result.get("description") or "OpenRouter returned a construction-stage assessment."
            return (
                f"{stage} is estimated at {progress}% progress using OpenRouter vision with OpenCV guardrails. "
                f"{vlm_description} "
                f"OpenCV metrics: site-likelihood={features.construction_likelihood:.2f}, "
                f"concrete={features.concrete_fraction:.2f}, earth={features.earth_fraction:.2f}, "
                f"equipment-cue={equipment_cue:.2f}, lines={features.line_density:.2f}."
            )

        if stage == "Unknown":
            return (
                "OpenCV analysis did not find reliable construction-site evidence in the submitted photo set. "
                f"Site-likelihood={features.construction_likelihood:.2f}; "
                f"concrete={features.concrete_fraction:.2f}, earth={features.earth_fraction:.2f}, "
                f"equipment-cue={equipment_cue:.2f}, lines={features.line_density:.2f}. "
                "The upload is treated as irrelevant/non-construction, so construction progress is 0%."
            )

        activity = "active construction cues" if features.line_density > 0.16 or features.edge_density > 0.12 else "limited visible activity"
        return (
            f"{stage} is estimated at {progress}% progress by OpenCV fallback analysis. "
            f"OpenRouter was not used for this request ({inference_source}); the image set shows {activity}. "
            f"OpenCV metrics: site-likelihood={features.construction_likelihood:.2f}, "
            f"concrete={features.concrete_fraction:.2f}, earth={features.earth_fraction:.2f}, "
            f"equipment-cue={equipment_cue:.2f}, lines={features.line_density:.2f}."
        )

    def _analysis_payload(self, features: ImageFeatures) -> dict[str, float]:
        return {
            "site_likelihood": round(features.construction_likelihood, 3),
            "brightness": round(features.brightness, 3),
            "contrast": round(features.contrast, 3),
            "saturation": round(features.saturation, 3),
            "edge_density": round(features.edge_density, 3),
            "line_density": round(features.line_density, 3),
            "rectangular_structure": round(features.rectangular_structure, 3),
            "concrete_fraction": round(features.concrete_fraction, 3),
            "earth_fraction": round(features.earth_fraction, 3),
            "sky_fraction": round(features.sky_fraction, 3),
            "vegetation_fraction": round(features.vegetation_fraction, 3),
            "equipment_color_fraction": round(features.equipment_color_fraction, 3),
            "equipment_cue_fraction": round(self._effective_equipment_signal(features), 3),
            "artificial_color_score": round(features.artificial_color_score, 3),
        }

    def _effective_equipment_signal(self, features: ImageFeatures) -> float:
        if features.concrete_fraction + features.rectangular_structure >= 0.12:
            return features.equipment_color_fraction
        return min(features.equipment_color_fraction, 0.08)

    def _build_embedding(self, images: list[Image.Image], features: ImageFeatures) -> list[float]:
        digest = hashlib.sha256()
        for image in images:
            digest.update(image.resize((32, 32)).tobytes())

        seed = digest.digest()
        base_values = [
            features.brightness,
            features.contrast,
            features.saturation,
            features.edge_density,
            features.line_density,
            features.rectangular_structure,
            min(features.aspect_ratio / 2.0, 1.0),
            features.construction_likelihood,
        ]

        embedding = []
        for idx in range(self.embedding_size):
            byte = seed[idx % len(seed)]
            signal = base_values[idx % len(base_values)]
            value = math.tanh(((byte / 255.0) - 0.5) + signal - 0.5)
            embedding.append(round(value, 6))

        return embedding
