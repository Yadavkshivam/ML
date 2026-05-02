# Fingerprint Blood Group Detection - Setup & Run Guide

## ✅ WHAT'S RUNNING NOW

### Backend Server (Flask API)
- **Status**: ✅ Running
- **URL**: http://localhost:8000
- **IP Address for Phone**: http://10.45.68.58:8000
- **Port**: 8000
- **Endpoints**:
  - `GET /health` - Check model availability
  - `POST /predict` - Predict blood group from fingerprint image
- **Models Loaded**: ResNet50, VGG16

### Frontend Server (Expo Mobile App)
- **Status**: ✅ Running
- **Port**: 8081 (Metro Bundler)
- **Network**: LAN accessible
- **Framework**: React Native + Expo

---

## 📱 HOW TO RUN ON YOUR PHONE

### Prerequisites
- **iPhone** or **Android** phone
- **Expo Go** app installed (free from App Store / Google Play)
- **Same WiFi network** as your computer (10.45.68.58)

### Step 1: Install Expo Go App
- **iOS**: Download [Expo Go from App Store](https://apps.apple.com/us/app/expo-go/id1223554531)
- **Android**: Download [Expo Go from Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)

### Step 2: Connect to Development Server
The Expo development server is already running. You should see a QR code in your terminal.

**Option A: Scan QR Code** (Easiest)
1. Open **Expo Go** app on your phone
2. Tap **Scan QR Code** (or use camera)
3. Point at the QR code shown in your terminal
4. App will download and start automatically

**Option B: Manual Connection**
1. Open **Expo Go** app
2. Tap **Explore**
3. Search for `bloodtype-app` or the connection code shown in terminal
4. Tap to connect

**Option C: Command Line**
```bash
# In terminal, press 's' for Android or 'i' for iOS
# Or paste the connection URL from terminal output
```

### Step 3: Use the App
Once loaded, you'll see:

1. **Home Screen** - Overview of the app
2. **Guidance Screen** - Instructions for fingerprint placement
3. **Camera Screen** - Take a fingerprint photo
   - Align your inked fingerprint in the reticle
   - Tap "CAPTURE" button
4. **Preview Screen** - Review captured image
5. **Result Screen** - Blood group predictions
   - See consensus vote (agreement from multiple models)
   - See individual model predictions
   - Model cards show confidence % and top 3 probabilities

---

## 🔄 API Connection Flow

```
Phone (Expo Go)
    ↓
    (sends fingerprint image via HTTP POST)
    ↓
Backend Server (Flask - 10.45.68.58:8000)
    ↓
    Loads models (ResNet50, VGG16)
    ↓
    Runs inference on image
    ↓
    Returns predictions with confidence
    ↓
Phone displays results with consensus
```

---

## 🛑 IF APP DOESN'T CONNECT

### Issue: "CONNECTION ERROR — CHECK SERVER"

**Check 1: Backend Server Running**
```bash
# In a new terminal, run:
curl http://localhost:8000/health

# Should see JSON with model status
```

**Check 2: Correct IP Address**
- Your computer's IP: **10.45.68.58**
- Phone must be on **same WiFi network**
- Check `.env` file in `/mobile/.env`:
  ```
  EXPO_PUBLIC_API_URL=http://10.45.68.58:8000
  ```

**Check 3: Firewall**
- Allow port 8000 through your firewall
- macOS: System Preferences → Security & Privacy → Firewall

**Check 4: Models Loaded**
```bash
# Check if models exist:
ls -lh code/Resnet34/model_blood_group_detection_resnet.h5
ls -lh code/Vgg16/blood_group_detection.h5

# Check backend logs:
tail -50 backend.log
```

---

## 📊 TESTING WITHOUT PHONE

### Test Backend Directly
```bash
# Health check
curl http://localhost:8000/health

# Predict with sample image
curl -X POST -F "file=@sample_dataset/sample_data.jpg" \
  http://localhost:8000/predict
```

### Test with Sample Fingerprint
Sample fingerprint image available at:
- `/Major_project/sample dataset/sample_data.jpg`
- `/Major_project/test/O- blood group.BMP`

---

## 🔄 RESTART SERVERS (If Needed)

### Kill Existing Processes
```bash
# Kill backend server
pkill -f "python app.py"

# Kill Expo
pkill -f "expo start"
```

### Restart Backend
```bash
cd /Users/shivamyadav/ml\ project/Major_project
source venv/bin/activate
python app.py
```

### Restart Expo
```bash
cd /Users/shivamyadav/ml\ project/Major_project/mobile
npm start
```

---

## 📁 PROJECT FILES

```
/Users/shivamyadav/ml project/Major_project/
├── app.py                          ← Backend Flask server
├── requirements-backend.txt        ← Python dependencies
├── venv/                           ← Python virtual environment
├── mobile/                         ← React Native app
│   ├── .env                        ← API URL configuration
│   ├── App.js                      ← App entry point
│   ├── screens/                    ← Navigation screens
│   └── package.json                ← NPM dependencies
├── code/
│   ├── Resnet34/                   ← ResNet50 model
│   └── Vgg16/                      ← VGG16 model
└── dataset/
    └── dataset_blood_group/        ← Training dataset (6000+ images)
```

---

## 🚀 QUICK START COMMANDS

**Terminal 1: Start Backend**
```bash
cd "/Users/shivamyadav/ml project/Major_project"
source venv/bin/activate
python app.py
```

**Terminal 2: Start Frontend**
```bash
cd "/Users/shivamyadav/ml project/Major_project/mobile"
npm start
```

**Then on Phone**: Open Expo Go → Scan QR Code

---

## 💡 TIPS

- **Fast Iteration**: Changes to JS files auto-reload in Expo
- **Slow Iteration**: Backend model loading takes 10-30 seconds first time
- **Battery**: Scanning takes ~5-10 seconds per image
- **Accuracy**: ResNet50 ~82% accuracy on test set
- **Multiple Models**: Both ResNet50 and VGG16 run on each prediction for consensus

---

## ❓ TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| "Cannot find module" in mobile | Run `npm install` in mobile folder |
| Port 8000 already in use | `lsof -i :8000` then kill old process |
| "Failed to load model" | Check model files exist, check logs |
| Phone can't reach server | Check WiFi, check firewall, verify IP |
| App crashes | Check phone logs: `adb logcat` (Android) or Xcode (iOS) |

---

Generated: May 2, 2026
