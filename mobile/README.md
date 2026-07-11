# LandSense AI Mobile

Native Android client for the LandSense AI Qualcomm Hackathon build.

The app captures construction-site evidence on the phone and sends it to the laptop backend. Heavy image reasoning and final report generation stay on the backend/AI services; the mobile app only performs lightweight local feedback and displays fused results.

## Implemented Features

- Splash and onboarding flow.
- Home dashboard with backend health, total scans, average development score, and quick actions.
- Settings screen for the laptop LAN IP. Enter only the IP address; requests are rewritten to `http://<IP>:8000`.
- Live CameraX preview and back-camera photo capture.
- 1-4 construction-site photos per observation.
- Photo compression/resizing to JPEG data URLs before upload.
- GPS tagging with `FusedLocationProviderClient`.
- UTC timestamp and persistent Android owner ID.
- Optional voice query through Android Speech Recognizer.
- Lightweight on-device construction classification with TensorFlow Lite Task Vision using `app/src/main/assets/construction_model.tflite`.
- `POST /observation` upload to the backend.
- Result report for construction stage, progress, confidence, development score, IoT noise/dust, sensor status, RERA matches, summary, GPS, timestamp, and observation ID.
- Android share sheet for reports.
- Previous scans screen using `/history?owner_id=...` with Room cache fallback.
- Community heatmap using `/heatmap`, OSMDroid/OpenStreetMap map markers, list view, and activity filters.
- Chat assistant screen using `POST /chat`.

## Tech Stack

- Kotlin
- Jetpack Compose + Material 3
- MVVM with repository/data layers
- CameraX
- Fused Location Provider
- Retrofit, OkHttp, kotlinx serialization
- Dagger Hilt
- Room
- OSMDroid/OpenStreetMap
- TensorFlow Lite Task Vision
- Coil
- Accompanist permissions

## Backend Contract

The app talks only to the laptop backend on port `8000`.

Implemented endpoints:

```text
GET  /health
POST /observation
GET  /observation/{id}
GET  /history?owner_id=<OWNER_ID>
GET  /heatmap
GET  /nearby?latitude=<LAT>&longitude=<LON>&radius=500
POST /chat
```

The backend IP comes from `SettingsRepository` and the Settings screen. Do not include `http://` or a port in the app setting.

## Run

1. Open `mobile/` in Android Studio, or open the repository and select the `mobile` Gradle project.
2. Let Gradle sync.
3. Start the local backend services from the repository root.
4. Install on a physical Android device or emulator.
5. In Settings, enter the laptop's local Wi-Fi IP address.
6. Grant camera, location, microphone, and network permissions when prompted.

No Google Maps API key is required. The app uses OSMDroid/OpenStreetMap.

## Notes

- The on-device TFLite prediction is a quick local hint. The final construction report is loaded from backend fusion.
- Successful observations are cached locally in Room. Offline scan upload retry is not yet implemented.
- The heatmap My Location button is currently a demo placeholder.
