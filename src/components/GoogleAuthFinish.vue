<script setup>
import { onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

async function finishGoogleLogin() {
  try {
    const tokenResponse = await fetch('http://localhost:5000/api/google/token', {
      credentials: 'include'
    });

    if (!tokenResponse.ok) {
      alert('Google login token retrieval failed.');
      return;
    }

    const tokenResult = await tokenResponse.json();
    const token = tokenResult.access_token;

    if (!token) {
      alert('Token not found in response.');
      return;
    }

    localStorage.setItem('auth_token', token);

    const userResponse = await fetch('http://localhost:5000/api/user', {
      headers: {
        Authorization: `Bearer ${token}`
      },
      credentials: 'include'
    });

    if (!userResponse.ok) {
      alert('Failed to fetch user details.');
      return;
    }

    const user = await userResponse.json();
    localStorage.setItem('user', JSON.stringify(user));

    const redirectPath = route.query.redirect || '/dashboard';
    router.replace(redirectPath);

  } catch (error) {
    alert('Network error during Google login process.');
    console.error(error);
  }
}

onMounted(() => {
  finishGoogleLogin();
});
</script>

<template>
  <div class="loading-container">
    <div class="glow-spinner"></div>
    <p class="loading-text">Authenticating with Google...</p>
    <p class="loading-subtext">Please do not close this window.</p>
  </div>
</template>

<style scoped>
:root {
  --orange-main: #FF8C00; /* Dark Orange */
  --orange-light: #FFA500; /* Orange */
  --orange-accent: #FFD700; /* Gold */
  --dark-background: #121212;
  --dark-surface: #1E1E1E;
  --text-color-light: #F0F0F0;
  --text-color-faded: #AAAAAA;
}

body {
  background-color: var(--dark-background);
  color: var(--text-color-light);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(145deg, var(--dark-background) 0%, #000000 100%);
}

.glow-spinner {
  width: 80px;
  height: 80px;
  border: 5px solid rgba(255, 140, 0, 0.2);
  border-top-color: var(--orange-light);
  border-radius: 50%;
  animation: spin 1s linear infinite, glow 1.5s ease-in-out infinite alternate;
  margin-bottom: 2rem;
  box-shadow: 0 0 10px rgba(255, 140, 0, 0.5), 0 0 20px rgba(255, 140, 0, 0.3), 0 0 30px rgba(255, 140, 0, 0.1);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes glow {
  0% { box-shadow: 0 0 10px var(--orange-main), 0 0 20px var(--orange-main); }
  100% { box-shadow: 0 0 20px var(--orange-light), 0 0 40px var(--orange-light); }
}

.loading-text {
  font-size: 1.8rem;
  font-weight: 600;
  letter-spacing: 1px;
  margin-bottom: 0.5rem;
  text-shadow: 1px 1px 2px #000000;
  color: var(--text-color-light);
}

.loading-subtext {
  font-size: 1rem;
  color: var(--text-color-faded);
  animation: fade-in 2s ease-in;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

</style>