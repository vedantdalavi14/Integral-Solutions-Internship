# Video Streaming App

A full-stack video streaming application built with React Native (Expo) and Flask.

## 🎯 Features

- **User Authentication**: Signup/Login with JWT tokens
- **Video Dashboard**: Browse featured videos with thumbnails
- **Native Video Player**: Play videos with native controls (no YouTube branding)
- **Secure Streaming**: Short-lived playback tokens, backend video proxy
- **MongoDB Atlas**: Cloud-hosted database

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  React Native   │ ──► │   Flask API     │ ──► │  MongoDB Atlas  │
│   (Expo)        │     │   (Backend)     │     │   (Database)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │    yt-dlp       │
                        │  (Video Proxy)  │
                        └─────────────────┘
```

### Key Design Decisions

1. **API-First**: All business logic lives in the Flask backend
2. **YouTube Hidden**: Video URLs extracted via yt-dlp, proxied through backend
3. **JWT Authentication**: Secure token-based auth with expo-secure-store
4. **Playback Tokens**: Short-lived tokens (5 min) for video streaming security

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── __init__.py       # Flask app factory
│   │   ├── config.py         # Configuration settings
│   │   ├── models/           # MongoDB models
│   │   │   ├── user.py       # User model with bcrypt
│   │   │   └── video.py      # Video model (youtube_id hidden)
│   │   ├── routes/
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   └── video.py      # Video streaming endpoints
│   │   └── utils/
│   │       └── jwt_utils.py  # JWT token utilities
│   ├── requirements.txt
│   └── run.py                # Entry point
│
└── mobile/
    ├── App.js                # Main entry point
    └── src/
        ├── api/
        │   └── apiService.js # Centralized API calls
        ├── components/
        │   └── VideoTile.js  # Video card component
        ├── context/
        │   └── AuthContext.js# Auth state management
        ├── navigation/
        │   └── AppNavigator.js# Navigation setup
        └── screens/
            ├── DashboardScreen.js
            ├── LoginScreen.js
            ├── SignupScreen.js
            ├── SettingsScreen.js
            └── VideoPlayerScreen.js
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB Atlas account (or local MongoDB)
- Expo Go app on your mobile device

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run server
python run.py
```

Server runs on `http://localhost:5000`

### Mobile Setup

```bash
cd mobile

# Install dependencies
npm install

# Start Expo
npx expo start
```

Scan QR code with Expo Go app.

### Configuration

Update `mobile/src/api/apiService.js` with your IP:

```javascript
const API_BASE_URL = 'http://YOUR_IP:5000';
```

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register new user |
| POST | `/auth/login` | Login user |
| GET | `/auth/me` | Get current user profile |
| POST | `/auth/logout` | Logout user |

### Videos

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Get featured videos |
| GET | `/video/:id/stream` | Stream video (requires token) |
| GET | `/video/:id/info` | Get video info |

## 🔒 Security

- **JWT Tokens**: 24-hour access tokens for authentication
- **Playback Tokens**: 5-minute tokens for video streaming
- **Password Hashing**: bcrypt with salt
- **YouTube Hidden**: Video URLs never exposed to client

## 🛠️ Tech Stack

### Frontend
- React Native (Expo SDK 54)
- React Navigation
- expo-video (native video player)
- expo-secure-store (secure token storage)

### Backend
- Flask
- PyMongo (MongoDB driver)
- PyJWT (token generation)
- yt-dlp (video extraction)
- bcrypt (password hashing)

## 📝 License

MIT License
