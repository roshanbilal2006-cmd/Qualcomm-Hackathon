# LandSense AI: Android & Kotlin Beginner's Guide

Welcome to Android development! Since this is your first time seeing Kotlin and Android code, this guide will walk you through setting up your environment, understanding the code, and how the LandSense AI app works.

---

## 1. Setting Up Your Environment (Android Studio)

To run and edit this code, you need **Android Studio**, the official Integrated Development Environment (IDE) for Android.

### Installation & Setup
1. **Download Android Studio**: Go to [developer.android.com/studio](https://developer.android.com/studio) and download the latest version for Windows.
2. **Install**: Run the installer and stick to the default settings (it will install the Android SDK and necessary build tools).
3. **Open the Project**:
   - Open Android Studio.
   - Click **Open** (or File > Open).
   - Navigate to your project folder: `c:\Users\harsh\Desktop\Web Dev\Qualcomm-Hackathon` and select it.
   - **Wait for Gradle Sync**: Android Studio uses a build tool called **Gradle**. The first time you open the project, it will download hundreds of dependencies (like Kotlin, Compose, Google Maps). This can take 5-10 minutes. Look at the bottom right corner for a loading bar. Wait until it says "Gradle sync finished".

### Running the App
1. **Set up a Device**:
   - **Physical Device (OnePlus 15)**: Enable "Developer Options" on your phone (tap Build Number 7 times in Settings), then enable "USB Debugging". Plug it into your PC.
   - **Emulator**: In Android Studio, go to the top right and click **Device Manager** > **Create Device**. Pick a phone (e.g., Pixel 7) and download a system image (API 34 is good).
2. **Hit Play**: At the top of Android Studio, you'll see a green "Play" button (▶). Click it to build and install the app on your phone/emulator.

---

## 2. A Quick Primer on Kotlin

Kotlin is a modern, concise language developed by JetBrains and is the official language for Android. Here are the basics you'll see in this project:

- **Variables**: 
  - `val` is read-only (immutable, like `const` in JavaScript).
  - `var` is mutable (can be changed, like `let` in JavaScript).
- **Data Classes**: Used to hold data. The compiler automatically generates useful functions like `toString()` and `copy()`. You'll see these in [ApiModels.kt](file:///c:/Users/harsh/Desktop/Web%20Dev/Qualcomm-Hackathon/app/src/main/java/com/landsense/ai/data/network/ApiModels.kt).
  ```kotlin
  data class ObservationRequest(val latitude: String, val longitude: String)
  ```
- **Coroutines (`suspend fun`)**: Kotlin's way of doing asynchronous programming (like `async/await` in JS). Network calls are "suspended" so they don't freeze the app.

---

## 3. How the UI Works (Jetpack Compose)

In the past, Android UIs were built using XML files. Now, we use **Jetpack Compose**, which builds UIs entirely in Kotlin code using a declarative approach (very similar to React).

- **Composables**: A function annotated with `@Composable` represents a piece of UI. 
- Example from [ResultScreen.kt](file:///c:/Users/harsh/Desktop/Web%20Dev/Qualcomm-Hackathon/app/src/main/java/com/landsense/ai/ui/screens/ResultScreen.kt):
  ```kotlin
  @Composable
  fun ReportCard(title: String, value: String) {
      Card { // A pre-built Material Design container
          Text(text = title)
          Text(text = value)
      }
  }
  ```
- **State**: When a variable (State) changes, Compose automatically redraws (recomposes) the UI that depends on that variable.

---

## 4. App Architecture (MVVM)

This project uses **Model-View-ViewModel (MVVM)**, a standard architecture to keep code organized:

1. **Model (Data Layer)**: Handles getting data (from APIs or databases).
   - Located in the `data` folder (e.g., `ApiService.kt`, `ObservationRepository.kt`).
2. **View (UI Layer)**: The visual screens the user interacts with. 
   - Located in the `ui.screens` folder (e.g., `CaptureScreen.kt`).
3. **ViewModel (The Brains)**: Connects the View and the Model. It holds the "State" (like whether an image is uploading) and executes logic when the user clicks a button.
   - Located in `presentation.capture` (e.g., `CaptureViewModel.kt`).

---

## 5. Tour of the Project Structure

Here is where everything lives in `app/src/main/java/com/landsense/ai/`:

- **`MainActivity.kt`**: The entry point of the app. It opens, applies the theme, and loads the Navigation Graph.
- **`ui/navigation/NavGraph.kt`**: The "router" of the app. It decides which screen to show based on the route (e.g., "home" vs "capture").
- **`ui/screens/`**: Contains the code for all the visible pages:
  - `HomeScreen.kt`: The main dashboard.
  - `CaptureScreen.kt`: The page that asks for permissions and captures data.
  - `ResultScreen.kt`: Displays the AI results beautifully.
  - `HeatmapScreen.kt`: Shows the Google Map.
- **`presentation/capture/CaptureViewModel.kt`**: Contains the logic that runs when you hit "Take Photo" or "Submit". It gathers the GPS location and calls the API.
- **`data/network/`**:
  - `ApiModels.kt`: The exact shape of the JSON that goes to and from your Backend.
  - `ApiService.kt`: The Retrofit interface defining your `POST /observation` and `GET /heatmap` endpoints.
- **`di/` (Dependency Injection)**: Uses a library called **Hilt**. It acts like a factory that automatically creates complex objects (like Network Clients) and hands them to the ViewModels when needed.

---

## 6. What You Need to Do Next

To get the app fully working for your hackathon demo, you'll need to do a few minor setups:

1. **Add your Google Maps API Key**:
   - Go to [AndroidManifest.xml](file:///c:/Users/harsh/Desktop/Web%20Dev/Qualcomm-Hackathon/app/src/main/AndroidManifest.xml).
   - Find the `<meta-data android:name="com.google.android.geo.API_KEY"` block.
   - Replace `${MAPS_API_KEY}` with a real key from the Google Cloud Console.
2. **Point the App to your Backend**:
   - Go to [NetworkModule.kt](file:///c:/Users/harsh/Desktop/Web%20Dev/Qualcomm-Hackathon/app/src/main/java/com/landsense/ai/di/NetworkModule.kt).
   - Find `BASE_URL = "https://api.landsense.ai/v1/"` and replace it with your actual backend URL (e.g., `http://192.168.1.5:8000/`).
3. **Implement the actual Camera Preview (Optional but recommended)**:
   - In `CaptureScreen.kt`, there is a placeholder box for the camera (`Text("CameraX Preview Placeholder")`). Implementing a live camera feed requires a bit more boilerplate using Android's `PreviewView`. Since we only have a placeholder right now, the "Take Photo" button just simulates a photo. If you want, I can help you write the code for the actual live camera feed next!
