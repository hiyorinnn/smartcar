
const registerForm = document.getElementById('register-form');
const fullName = document.getElementById("name");
const registerEmail = document.getElementById("email");
const registerPassword = document.getElementById("password");
const registerMessage = document.getElementById("register-message");

// Handle user registration
registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  

  try {
    const response = await fetch('http://127.0.0.1:5004/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: fullName.value,
        email: registerEmail.value,
        password: registerPassword.value
      })
    });

    const data = await response.json();

    if (response.ok) {
      console.log("Registration success:", data);
      
      // Store user details in localStorage
      localStorage.setItem('Name', data.name || 'User');
      localStorage.setItem('userEmail', email);
      localStorage.setItem('userUID', data.user_id);
      localStorage.setItem('loggedIn', true);
      
      // Redirect to home page
      window.location.href = "./index.html";
    } else {
      console.error("Error during registration:", data.error);
      registerMessage.innerText = data.error || "Registration failed. Please try again.";
    }
  } catch (error) {
    console.error("Error during registration:", error.message);
    registerMessage.innerText = "Registration failed. Please try again.";
  }
});

  
 