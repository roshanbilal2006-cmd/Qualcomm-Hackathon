import base64
from io import BytesIO

from PIL import Image, ImageDraw

from ai.engine import VisionInferenceEngine


def image_to_data_url(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=86)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def make_mock_construction_image() -> Image.Image:
    image = Image.new("RGB", (640, 420), "#9fb7c9")
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 300, 640, 420], fill="#b98552")

    for x in range(120, 501, 95):
        draw.rectangle([x, 120, x + 16, 310], fill="#6f7680")
    for y in range(145, 256, 55):
        draw.rectangle([90, y, 540, y + 14], fill="#6f7680")

    draw.line([(90, 105), (540, 285), (540, 105), (90, 285)], fill="#d6b35a", width=6)
    draw.rectangle([420, 250, 505, 305], fill="#c84d32")
    draw.rectangle([445, 225, 479, 250], fill="#f3c24d")
    return image


def make_warm_anime_portrait_image() -> Image.Image:
    image = Image.new("RGB", (640, 420), "#d9a47a")
    draw = ImageDraw.Draw(image)

    for offset in range(0, 640, 36):
        draw.line([(offset, 0), (offset - 180, 420)], fill="#5d3b2f", width=5)
        draw.line([(offset, 0), (offset + 160, 420)], fill="#7a4d36", width=3)

    draw.ellipse([215, 70, 425, 330], fill="#ffd4bf", outline="#111111", width=7)
    draw.polygon([(220, 130), (320, 20), (420, 130), (382, 116), (320, 88), (258, 116)], fill="#22202a")
    draw.ellipse([265, 165, 305, 212], fill="#2ec7ff", outline="#111111", width=5)
    draw.ellipse([335, 165, 375, 212], fill="#2ec7ff", outline="#111111", width=5)
    draw.arc([275, 215, 365, 285], 10, 170, fill="#111111", width=5)
    return image


def test_warm_anime_portrait_is_not_classified_as_construction(monkeypatch, tmp_path):
    monkeypatch.setenv("LANDSENSE_VLM_MODEL_DIR", str(tmp_path))
    engine = VisionInferenceEngine()

    result = engine.predict([image_to_data_url(make_warm_anime_portrait_image())])

    assert result["construction_stage"] == "Unknown"
    assert result["progress_percentage"] == 0
    assert result["site_likelihood"] < 0.35
    assert "irrelevant/non-construction" in result["description"]


def test_mock_construction_image_still_scores_as_site(monkeypatch, tmp_path):
    monkeypatch.setenv("LANDSENSE_VLM_MODEL_DIR", str(tmp_path))
    engine = VisionInferenceEngine()

    result = engine.predict([image_to_data_url(make_mock_construction_image())])

    assert result["construction_stage"] != "Unknown"
    assert result["progress_percentage"] > 0
    assert result["site_likelihood"] >= 0.35
