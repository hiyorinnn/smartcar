import { getAuth, setPersistence, browserLocalPersistence, signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/9.0.0/firebase-auth.js";

const auth = getAuth();
const googleProvider = new GoogleAuthProvider();

// Elements
const loginForm = document.getElementById('login-form');
const googleSignInBtn = document.getElementById('google-signin');
const loginEmail = document.getElementById('email');
const loginPassword = document.getElementById('password');
const loginMessage = document.getElementById('login-message');
const loginButton = document.querySelector('button[type="submit"]');

// Set session persistence to "local" so the session persists even if the browser is closed
setPersistence(auth, browserLocalPersistence)
  .catch((error) => {
    console.error("Error setting persistence:", error.message);
  });

// Handle email-password login
loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const email = loginEmail.value;
  const password = loginPassword.value;

  // Disable login button to prevent multiple clicks
  loginButton.disabled = true;
  loginButton.innerText = "Logging in...";

  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;
    console.log("Email login success:", user);

    // Store user details in localStorage
    localStorage.setItem('userName', user.displayName || 'User');
    localStorage.setItem('userEmail', user.email);
    localStorage.setItem('userUID', user.uid);

    // Redirect to home page
    window.location.href = '../index.html';
  } catch (error) {
    console.error("Error during email login:", error.message);
    // Custom error messages based on the error code
    switch (error.code) {
      case 'auth/invalid-email':
        loginMessage.innerText = "Invalid email format.";
        break;
      case 'auth/user-not-found':
        loginMessage.innerText = "No account found with this email.";
        break;
      case 'auth/wrong-password':
        loginMessage.innerText = "Incorrect password. Please try again.";
        break;
      default:
        loginMessage.innerText = "Login failed. Please try again.";
        break;
    }
  } finally {
    // Re-enable the login button after handling
    loginButton.disabled = false;
  }
});

// Handle Google Sign-In
googleSignInBtn.addEventListener('click', async (event) => {
  event.preventDefault();

  try {
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;
    console.log("Google login success:", user);

    // Store user display name in localStorage
    localStorage.setItem('userName', user.displayName || 'User');
    localStorage.setItem('userEmail', user.email);
    localStorage.setItem('userUID', user.uid);

    // Redirect to home page
    window.location.href = '../index.hmtl';
  } catch (error) {
    console.error("Error during Google Sign-In:", error.message);
    // Display a generic error message for Google Sign-In
    loginMessage.innerText = "Google Sign-In failed. Please try again.";
  }
});
