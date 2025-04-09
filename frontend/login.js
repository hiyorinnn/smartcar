// Elements
const loginForm = document.getElementById('login-form');
const loginEmail = document.getElementById('email');
const loginPassword = document.getElementById('password');
const loginMessage = document.getElementById('login-message');
const loginButton = document.querySelector('button[type="submit"]');

// Handle email-password login
loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const email = loginEmail.value;
  const password = loginPassword.value;

  // Disable login button to prevent multiple clicks
  loginButton.disabled = true;
  loginButton.innerText = "Logging in...";

  try {
    const response = await fetch('http://127.0.0.1:5004/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email,
        password: password
      })
    });

    const data = await response.json();

    if (response.ok) {
      console.log("Login success:", data);

      // Store user details in localStorage
      localStorage.setItem('userName', data.name || 'User');
      localStorage.setItem('userEmail', email);
      localStorage.setItem('userUID', data.user_id);
      localStorage.setItem('loggedIn', true);

      // Redirect to home page
      window.location.href = './index.html';
    } else {
      console.error("Error during login:", data.error);
      loginMessage.innerText = data.error || "Login failed. Please try again.";
    }
  } catch (error) {
    console.error("Error during login:", error.message);
    loginMessage.innerText = "Login failed. Please try again.";
  } finally {
    // Re-enable the login button after handling
    loginButton.disabled = false;
    loginButton.innerText = "Sign In";
  }
});