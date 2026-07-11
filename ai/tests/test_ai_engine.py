import base64
from io import BytesIO

from PIL import Image, ImageDraw

from ai.engine import VisionInferenceEngine


class FakeMessage:
    def __init__(self, content: str):
        self.content = content


class FakeChoice:
    def __init__(self, content: str):
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content: str):
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, content: str):
        self.content = content
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return FakeResponse(self.content)


class FakeChat:
    def __init__(self, completions: FakeCompletions):
        self.completions = completions


class FakeCirrascaleClient:
    def __init__(self, content: str):
        self.completions = FakeCompletions(content)
        self.chat = FakeChat(self.completions)


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


def test_warm_anime_portrait_is_not_classified_as_construction(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    engine = VisionInferenceEngine()

    result = engine.predict([image_to_data_url(make_warm_anime_portrait_image())])

    assert result["construction_stage"] == "Unknown"
    assert result["progress_percentage"] == 0
    assert result["site_likelihood"] < 0.35
    assert "irrelevant/non-construction" in result["description"]


def test_mock_construction_image_still_scores_as_site(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    engine = VisionInferenceEngine()

    result = engine.predict([image_to_data_url(make_mock_construction_image())])

    assert result["construction_stage"] != "Unknown"
    assert result["progress_percentage"] > 0
    assert result["site_likelihood"] >= 0.35


def test_cirrascale_vision_result_overrides_local_estimate(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test/vision-model")
    engine = VisionInferenceEngine()
    fake_client = FakeCirrascaleClient(
        '{"construction_stage":"Finishing","progress_percentage":88,'
        '"confidence":0.91,"description":"Exterior work appears nearly complete."}'
    )
    engine._llm_client = fake_client

    result = engine.predict([image_to_data_url(make_mock_construction_image())])

    assert result["construction_stage"] == "Finishing"
    assert result["progress_percentage"] == 88
    assert result["confidence"] == 0.91
    assert result["llm_enabled"] is True
    assert result["llm_model"] == "test/vision-model"
    assert result["cirrascale_error"] is None
    assert fake_client.completions.last_kwargs["model"] == "test/vision-model"
    assert fake_client.completions.last_kwargs["messages"][1]["content"][1]["type"] == "image_url"
