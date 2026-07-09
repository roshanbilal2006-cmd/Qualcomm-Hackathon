# FastVLM / Qualcomm LiteRT Model Artifacts

Place downloaded Qualcomm AI Hub / LiteRT-LM / QNN model artifacts for the VLM here.

Expected examples:

- `*.litertlm`
- `*.tflite`
- `*.bin`
- `*.so`
- tokenizer/config `*.json`

You can override this path with:

```powershell
$env:LANDSENSE_VLM_MODEL_DIR="C:\path\to\model"
```

Until this folder contains real artifacts, the AI service uses the local visual
triage fallback and will say so in its explanation.
