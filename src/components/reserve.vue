<template>
  <div class="dark-theme-page">
    <div class="greeting-container">
      <h1 class="greeting-headline">{{ greetingMessage }}</h1>
      <h2 class="user-name">{{ userName }}</h2>
    </div>
  </div>
</template>

<script>
export default {
  // We no longer need the userName prop because we're fetching it internally.
  // props: {
  //   userName: {
  //     type: String,
  //   }
  // },
  data() {
    return {
      greetingMessage: '',
      userName: 'Guest' // Default value in case no user data is found
    };
  },
  mounted() {
    this.setGreeting();
    this.fetchUserName();
  },
  methods: {
    setGreeting() {
      const hour = new Date().getHours();
      if (hour < 12) {
        this.greetingMessage = "Good morning,";
      } else if (hour < 18) {
        this.greetingMessage = "Good afternoon,";
      } else {
        this.greetingMessage = "Good evening,";
      }
    },
    fetchUserName() {
      try {
        // Attempt to get the 'user' dictionary from local storage
        const userJson = localStorage.getItem('user');
        if (userJson) {
          // Parse the JSON string back into a JavaScript object
          const user = JSON.parse(userJson);
          // Check if the user object and full_name property exist
          if (user && user.full_name) {
            this.userName = user.full_name;
          }
        }
      } catch (e) {
        console.error("Failed to parse user data from localStorage:", e);
        // Fallback to the default name if there's an error
        this.userName = 'Guest';
      }
    }
  }
};
</script>

<style scoped>
/* Dark Theme Variables */
:root {
  --background-color: #121212;
  --text-color: #e0e0e0;
  --accent-color: #6a1b9a; /* A vibrant purple */
  --shadow-color: rgba(0, 0, 0, 0.5);
}

.dark-theme-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, var(--background-color), #000000);
  color: var(--text-color);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  text-align: center;
  padding: 20px;
}

.greeting-container {
  padding: 40px 60px;
  background-color: rgba(30, 30, 30, 0.8);
  border-radius: 15px;
  box-shadow: 0 10px 30px var(--shadow-color);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}

.greeting-container:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 15px 40px var(--shadow-color);
}

.greeting-headline {
  font-size: 2.5rem;
  font-weight: 300;
  margin-bottom: 0;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #a7a7a7;
  animation: fadeIn 1.5s ease-out;
}

.user-name {
  font-size: 4rem;
  font-weight: 700;
  margin-top: 10px;
  color: var(--accent-color);
  background: linear-gradient(90deg, #bb86fc, #03dac6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: slideIn 1.5s ease-out;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-50px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .greeting-headline {
    font-size: 2rem;
  }
  .user-name {
    font-size: 3rem;
  }
}

@media (max-width: 480px) {
  .greeting-headline {
    font-size: 1.5rem;
  }
  .user-name {
    font-size: 2.5rem;
  }
  .greeting-container {
    padding: 30px;
  }
}
body {
    overflow: hidden;
}
</style>