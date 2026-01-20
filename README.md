# 👁️ VisionSpeak - OCR Text Recognition Application

An Optical Character Recognition (OCR) application that extracts text from images with Text-to-Speech functionality, available in both desktop and mobile versions.

## 📋 Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
  - [Desktop Version](#1-desktop-version-kivy)
  - [Mobile Version](#2-mobile-version-android)
  - [Python Server](#3-python-server)
- [Usage](#usage)
- [Technologies](#technologies)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- 🖼️ **Image-to-Text Conversion**: Extract text from images using advanced OCR
- 🔊 **Text-to-Speech**: Listen to extracted text with built-in TTS functionality
- 💻 **Desktop Application**: Standalone Kivy-based desktop app with local processing
- 📱 **Mobile Application**: Native Android app with server-based processing
- 🔄 **Client-Server Architecture**: Mobile app communicates with Python backend
- 🚀 **Easy Deployment**: Pre-built APK ready for installation

## 📁 Project Structure

```
VisionSpeak/
├── Desktop Version/          # Kivy desktop application
│   └── App.py               # Main desktop application (local OCR processing)
├── VisionSpeak_App/         # Android mobile application
│   └── app-release.apk      # Ready-to-install APK
└── Serveur_Python/          # Python backend server
    └── server.py            # OCR processing server (for mobile app)
```

## 🚀 Installation & Setup

### 1. Desktop Version (Kivy)

The desktop version processes OCR **directly within the application** (no server required).

**Prerequisites:**
```bash
pip install kivy
pip install easyocr
pip install opencv-python
pip install pillow
pip install pyttsx3
```

**Launch:**
```bash
cd "Desktop Version"
python App.py
```

---

### 2. Mobile Version (Android)

⚠️ **IMPORTANT**: The mobile app is **hardcoded** to connect to a specific server IP address. For the app to work, **the Python server MUST be running on the original developer's computer**.

#### 📱 Installing the APK on Android:

**Step 1: Transfer the APK**
1. Connect your Android phone to your PC via **USB cable** (must be a data cable)
2. Copy `VisionSpeak_App/app-release.apk` to your phone's storage

**Step 2: Install**
1. On your phone, open the file manager
2. Navigate to the APK file location
3. Tap on `app-release.apk` to install
4. If prompted, **enable "Install from Unknown Sources"**

**⚠️ Important Notes:**
- You may see a "virus" or security warning - **this is normal** for APKs not published on Google Play Store
- The app is safe to install; this warning appears for all non-Play Store apps
- **The app will ONLY work when connected to the server on the original developer's computer**

---

### 3. Python Server

⚠️ **CRITICAL**: This server **MUST be running** for the mobile app to function. The Android app is configured to send HTTP requests to this specific server.

**Prerequisites:**
```bash
pip install flask
pip install easyocr
pip install opencv-python
pip install pillow
```

**Configuration:**
1. Open `Serveur_Python/server.py`
2. The IP address is already configured in the code
3. **DO NOT change the IP address** unless you rebuild the Android app with the new IP
4. The Android app is hardcoded with this server's IP address in Android Studio

**Launch:**
```bash
cd Serveur_Python
python server.py
```

**Server will run on:** `http://YOUR_CONFIGURED_IP:5000`

---

## 🎯 Usage

### Desktop Application:
1. Launch `App.py`
2. Load an image containing text
3. Click "Extract Text"
4. Text will be processed locally and displayed
5. Use the **Text-to-Speech button** to hear the extracted text

### Mobile Application:
1. **FIRST**: Ensure the Python server is running on the developer's computer
2. Open VisionSpeak app on your Android device
3. **CRITICAL**: Your phone MUST be on the **same WiFi network** as the server computer
4. Capture or select an image
5. The app sends the image to the hardcoded server address
6. Extracted text is returned and displayed
7. Tap the **speaker icon** to hear the text read aloud

---

## 🛠️ Technologies

- **Desktop**: Python, Kivy, EasyOCR, OpenCV, pyttsx3 (TTS)
- **Mobile**: Android (APK) with native TTS, HTTP client
- **Backend**: Flask, EasyOCR, OpenCV, Pillow
- **OCR Engine**: EasyOCR (supports multiple languages)
- **Text-to-Speech**: pyttsx3 (Desktop), Android native TTS (Mobile)

---

## 📝 Architecture

### Desktop Version:
```
User → Kivy App → Local OCR Processing → Display Result → TTS Output
```

### Mobile Version:
```
User → Android App → HTTP GET Request → Developer's PC Server → OCR Processing → HTTP Response → Android App → TTS Output
```

**Network Flow:**
```
Mobile Phone (Same WiFi) → HTTP Request → Server PC (Hardcoded IP) → OCR Processing → Response
```

---

## ⚙️ Troubleshooting

### Desktop app won't start:
- Ensure all dependencies are installed
- Check Python version compatibility with Kivy

### TTS not working on desktop:
- Install espeak on Linux: `sudo apt-get install espeak`
- On Windows/Mac, pyttsx3 should work by default

### Mobile app can't connect to server:
- ✅ **Verify server is running** (`python server.py`) on the developer's computer
- ✅ Check that phone and PC are on the **exact same WiFi network**
- ✅ The server IP is hardcoded in the Android app - cannot be changed without rebuilding
- ✅ Disable firewall on the server PC temporarily to test
- ✅ Check if port 5000 is open on the server PC
- ❌ **DO NOT try to change the server IP** - it's hardcoded in the APK

### "Install blocked" on Android:
- Go to Settings → Security → Enable "Unknown Sources"
- Or Settings → Apps → Special Access → Install Unknown Apps

### TTS not working on mobile:
- Ensure Text-to-Speech is enabled in Android Settings
- Download a TTS engine from Google Play Store if needed

### "Connection refused" or "Timeout" error:
- The server MUST be running before using the mobile app
- Phone and server PC must be on the same local network
- Check Windows Firewall settings on the server PC

---

## 🔧 For Developers

### Modifying the Server IP Address:

If you need to change the server IP address, you must:

1. **Change in Android Studio:**
   - Open the Android project in Android Studio
   - Find the HTTP request configuration (usually in a network/API file)
   - Update the base URL to your new IP address
   - Rebuild the APK

2. **Change in server.py:**
   - Update the IP address in the `app.run()` function
   - Restart the server

**Without rebuilding the APK, the mobile app will NOT work on a different network/IP.**

---

## 📄 License

This project is available for educational purposes.

---

## 👥 Contributors

Developed as part of an academic project.

---

## 🔮 Future Improvements

- [ ] Support for more languages
- [ ] Real-time camera OCR
- [ ] PDF text extraction
- [ ] Multiple voice options for TTS
- [ ] Cloud deployment option
- [ ] Dynamic server IP configuration (without rebuilding APK)
- [ ] Offline mode for mobile app
