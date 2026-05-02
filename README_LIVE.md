# 🚀 NaviRaksha Live Project Guide

Your project has been upgraded from a prototype to a **Live Emergency Grid** architecture using **Firebase** and **Next.js**.

## 🏗️ The New Architecture
1.  **Frontend (Next.js)**: Located in the `/web` directory. This is a high-performance, premium web app with real-time updates.
2.  **Real-time DB (Firestore)**: Your Python backend and Next.js frontend now talk to the same live database.
3.  **Authentication**: Users can sign up anonymously (just providing their name) for quick emergency reporting.

---

## 🛠️ Step 1: Firebase Configuration (Required)

### 1. Get Firebase Config (for Frontend)
1.  Go to [Firebase Console](https://console.firebase.google.com/).
2.  Create a new project named `NaviRaksha`.
3.  Add a **Web App** to the project.
4.  Copy the `firebaseConfig` object.
5.  In the `/web` directory, create a file named `.env.local` and paste your keys:
    ```env
    NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
    NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
    NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
    NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
    NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
    NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
    ```

### 2. Get Service Account Key (for Backend)
1.  In Firebase Console, go to **Project Settings > Service Accounts**.
2.  Click **Generate new private key**.
3.  Rename the downloaded file to `firebase-key.json`.
4.  Move it to the root of your project (`c:\Users\sriya\Desktop\Learner\navi-raksha\firebase-key.json`).

---

## 🚀 Step 2: Running the Live Project

### 1. Start the Intelligent Backend (Python)
The backend now syncs all changes (Ambulance moves, Incident status) to Firestore in real-time.
```bash
.venv\Scripts\activate
python modules\backend\app.py
```

### 2. Start the Live Web Portal (Next.js)
```bash
cd web
npm run dev
```
Visit **http://localhost:3000** to see the Citizen Portal and **http://localhost:3000/dashboard** for the Command Center.

---

## 🌍 Step 3: Deployment

### To Deploy the Frontend to Firebase:
1.  Install Firebase CLI: `npm install -g firebase-tools`
2.  Login: `firebase login`
3.  Initialize: `firebase init` (Select Hosting, use `out` as the public directory)
4.  Deploy: `npm run build && firebase deploy`

### To Deploy the Intelligence API (Python):
The Flask API can be deployed to **Google Cloud Run** using the provided `Dockerfile.backend`. Since it's in the same Google Cloud project as Firebase, it will have seamless access.

---

## ✨ Improvements Made
- **Glassmorphism UI**: High-end visuals with background meshes and kinetic typography.
- **Real-time Synchronization**: Using Firestore listeners for 0ms latency updates.
- **Anonymous Auth**: Optimized for emergency use (identity without friction).
- **Backend Sync**: Injected Firestore triggers into your existing Python service layer.
