<template>
  <div class="admin-dashboard-container">
    <header class="dashboard-header">
      <h1>Admin Dashboard</h1>
      <button @click="logout" class="logout-button">Logout</button>
    </header>

    <div class="dashboard-main">
      <aside class="sidebar">
        <nav>
          <ul>
            <li><a href="#">Manage Questions</a></li>
            <li><a href="#">Manage Users</a></li>
            <li><a href="#">View Analytics</a></li>
            <li><a href="#">Settings</a></li>
          </ul>
        </nav>
      </aside>

      <main class="content-area">
        <div class="content-card">
          <h2>Welcome, Admin!</h2>
          <p>This is your central control panel. Use the sidebar to navigate through administrative tasks.</p>
        </div>
        
        <div class="content-card">
          <h3>Recent Activity</h3>
          <p>Recent user sign-ups, new question submissions, and system logs will be displayed here.</p>
        </div>
        
        </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const logout = () => {
  // 1. Remove the authentication token from local storage
  localStorage.removeItem('auth_token');
  
  // 2. Also remove any other user-specific data to ensure a clean session
  localStorage.removeItem('user_role');
  localStorage.removeItem('user'); 
  
  // 3. Redirect the user to the home page or login page
  router.push('/');
};
</script>

<style scoped>
.admin-dashboard-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f4f7f6;
  font-family: Arial, sans-serif;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #334d6e;
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.logout-button {
  background-color: #e74c3c;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.logout-button:hover {
  background-color: #c0392b;
}

.dashboard-main {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: #ecf0f1;
  padding-top: 2rem;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar li {
  padding: 1rem 2rem;
  border-bottom: 1px solid #3e5872;
}

.sidebar a {
  text-decoration: none;
  color: #ecf0f1;
  display: block;
  font-size: 1.1rem;
  transition: color 0.3s ease;
}

.sidebar a:hover {
  color: #3498db;
}

.content-area {
  flex: 1;
  padding: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  align-content: start;
}

.content-card {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.content-card h2, .content-card h3 {
  color: #334d6e;
}
</style>