import sys
import logging
from ai.npu_engine import SnapdragonVisionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_npu")

def main():
    logger.info("Initializing SnapdragonVisionEngine...")
    engine = SnapdragonVisionEngine()
    
    if not engine.loaded:
        logger.error(f"Engine failed to load: {engine.load_error}")
        sys.exit(1)
        
    logger.info("Engine loaded successfully! Ready for inference.")
    
    # We create a dummy 512x512 JPEG image in base64 to test the predict payload
    from PIL import Image
    from io import BytesIO
    import base64
    
    img = Image.new('RGB', (512, 512), color = 'white')
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('ascii')
    payload = f"data:image/jpeg;base64,{img_str}"
    
    logger.info("Running predict on dummy image...")
    try:
        result = engine.predict([payload])
        logger.info(f"Predict Result: {result}")
    except Exception as e:
        logger.error(f"Predict failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
