import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
// If using npm installed bootstrap
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'bootstrap-icons/font/bootstrap-icons.css';


const app = createApp(App)  // ✅ create app instance
app.use(router)             // ✅ register router
app.mount('#app')           // ✅ mount afterwards
