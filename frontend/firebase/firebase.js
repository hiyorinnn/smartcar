
import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js';
import { getAuth, GoogleAuthProvider } from 'https://www.gstatic.com/firebasejs/9.0.0/firebase-auth.js';
import { getFirestore } from 'https://www.gstatic.com/firebasejs/9.0.0/firebase-firestore.js';

const firebaseConfig = {
  apiKey: "AIzaSyAcICSOshZcB7VvTbaYfij-lTNXgg-Zx7w",
  authDomain: "smartcar-g2g6.firebaseapp.com",
  projectId: "smartcar-g2g6",
  storageBucket: "smartcar-g2g6.firebasestorage.app",
  messagingSenderId: "429315535620",
  appId: "1:429315535620:web:5730876e8f5a1180c15651"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
export const db = getFirestore(app);
