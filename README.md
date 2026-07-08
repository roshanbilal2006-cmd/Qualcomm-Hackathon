# LandSense AI - Qualcomm Hackathon

Welcome to the **LandSense AI** project, built for the Qualcomm Snapdragon Multiverse Hackathon!

This repository contains the Android application, designed specifically for the OnePlus 15 (Snapdragon 8 Elite).

## Features
- **Capture Construction Site**: Uses CameraX to snap up to 4 photos per site.
- **Location Auto-tagging**: Silently captures high-accuracy GPS coordinates via `FusedLocationProviderClient`.
- **Optional Voice Queries**: Includes audio logging placeholders using Android Speech Recognition.
- **Smart Insights**: Displays AI-generated construction reports containing Progress, Confidence, Dust/Noise metrics, and a Development Score.
- **Community Heatmap**: Integrated Google Maps Compose SDK for viewing local construction density.

## Tech Stack
- Kotlin
- Jetpack Compose (Material 3)
- MVVM Architecture + Clean Code Principles
- CameraX
- Retrofit & OkHttp
- Dagger Hilt (Dependency Injection)
- Google Maps SDK
- Kotlinx Serialization

## Setup Instructions
1. Open this repository in **Android Studio**.
2. Let Gradle sync and download all dependencies.
3. Add your Google Maps API Key in `AndroidManifest.xml` (replace `${MAPS_API_KEY}`).
4. Update the backend API URL in `NetworkModule.kt`.
5. Connect your device (OnePlus 15 recommended) and run!

*Note: This app strictly communicates with backend APIs and does not process AI tasks locally to keep the client ultra-lightweight.*
