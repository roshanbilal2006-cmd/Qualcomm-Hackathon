# On-Device AI Model

This directory should contain the TensorFlow Lite model file.

## Required File
- `construction_model.tflite` — A quantized image classifier for construction stages.

## How to Get a Model

### Option A: Use a pre-trained MobileNet model
1. Download a MobileNetV3 model from TensorFlow Hub:
   https://tfhub.dev/google/lite-model/imagenet/mobilenet_v3_large_100_224/classification/5/default/1
2. Rename it to `construction_model.tflite`
3. Place it in this `assets/` directory

### Option B: Train your own (recommended for hackathon)
1. Collect ~50-100 images per construction stage category
2. Use Google Teachable Machine (https://teachablemachine.withgoogle.com/)
3. Export as "TensorFlow Lite (Quantized)"
4. Place the `.tflite` file here as `construction_model.tflite`

## Without a Model
If no model file is present, the app will gracefully show "Mock Stage (LiteRT model missing)" instead of crashing. All other features continue to work normally.
