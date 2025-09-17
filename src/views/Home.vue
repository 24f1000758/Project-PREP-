<template>
  <!-- Gradient strip filling the top space -->
  <div class="navbar-bg-strip"></div>
  <div class="navbar-wrapper">
    <nav class="navbar-pill d-flex align-items-center justify-content-between px-4 py-3">
      <!-- Brand Left -->
      <div class="brand">Prepp ✏️</div>
      <!-- Hamburger (mobile only, aligned right) -->
      <button class="hamburger" @click="toggleMenu" aria-label="menu">
        <span></span><span></span><span></span>
      </button>
      <!-- Collapsible Nav Links -->
      <div class="nav-links" :class="{ open: menuOpen }">
        <router-link class="nav-link" to="#">What's Included</router-link>
        <a href="#stories-section" class="nav-link" @click.prevent="openStorySubmission">Stories</a>
        <a href="#our-why-section" class="nav-link" @click.prevent="scrollToOurWhy">Our Why</a>
        <a href="#faq-section" class="nav-link" @click.prevent="scrollToFaq">FAQs</a>
        <a href="#" class="nav-link" @click.prevent="openLoginModal">Login</a>
        <a href="#" class="btn btn-start" @click.prevent="openLoginModal" >Start Testing</a>
      </div>
    </nav>
  </div>

  <div class="hero-section">
    <div class="container">
      <div class="content">
        <!-- Small Tagline -->
        <p class="tagline">Your AI-Powered Competitive Exam Preparation Companion</p>
        <!-- Main Heading -->
        <h1 class="display-4 fw-bold">Prep: Smarter Learning for UPSC, SSC, Banking, CAT & More</h1>
        <!-- Subheading -->
        <p class="lead mt-3 mb-4">
          Prep is an innovative AI-powered platform that helps you study smarter and more efficiently. Upload your notes, get personalized quizzes and learning paths, access mock tests, and track your progress—all tailored to your exam goals.
        </p>
        <!-- CTA Buttons -->
        <div class="d-flex justify-content-center gap-3">
        <a href="#" class="btn btn-start" @click.prevent="openLoginModal" >
          Start Learning
        </a>
          <button class="btn btn-start">Discover More</button>
        </div>
      </div>
    </div>
  </div>


  <!-- Login Modal -->
  <div v-if="loginModalOpen" class="modal-overlay" @click.self="closeLoginModal">
    <div class="modal-content">
      <button class="modal-close" @click="closeLoginModal" aria-label="Close">&times;</button>
      <h3 class="modal-title text-center">Login to Continue</h3>
      <button class="btn btn-email" @click="showModal = true">Continue with Email</button>
      <button class="btn btn-google" @click="googleLogin">
        <img src="../assets/pic-2.png" alt="Google Logo" class="google-logo" />
        Continue with Google
      </button>
      <p class="switch-form-text">
          New user? <a href="#" @click.prevent="openRegisterModal">Register here</a>
      </p>
    </div>
  </div>
  <!-- Modal for Email/Password -->
    <div v-if="showModal" class="email-registration-overlay">
      <div class="email-registration-box">
        <h3 class="text-white">Login</h3>
        <input v-model="emailLoginForm.email" type="email" placeholder="Email" />
        <input v-model="emailLoginForm.password" type="password" placeholder="Password" />
        <button class="email-registration-btn-login" @click="continueWithEmail">
          Login
        </button>
        <button class="email-registration-btn-close" @click="showModal = false">
          Close
        </button>
      </div>
    </div>
  <!-- Register Modal -->
  <div v-if="registerModalOpen" class="modal-overlay" @click.self="registerModalOpen = false">
    <div :class="['modal-content','register-large']">
      <button class="modal-close" @click="registerModalOpen = false" aria-label="Close">&times;</button>
      <h3 class="modal-title text-center">Register New Account</h3>
      <form @submit.prevent="submitRegistration">
        <input type="text" v-model="registerForm.name" placeholder="Name" required />
        <input type="tel" v-model="registerForm.phone" placeholder="Phone Number" required />
        <input type="email" v-model="registerForm.email" placeholder="Email" required />
        <input type="password" v-model="registerForm.password" placeholder="Password" required />
        <button type="submit" class="btn btn-start">Register</button>
      </form>
      <p class="switch-form-text">
        Already have an account? <a href="#" @click.prevent="openLoginModalFormRegister">Login here</a>
      </p>
    </div>
  </div>
  <!-- Available Exams Section -->
  <section class="available-exams">
    <h2 class="section-title">Available Exams</h2>
    <div class="logo-slider">
      <div class="logo-track">
        <img v-for="(logo, index) in logos" :key="'logo1-'+index" :src="logo" class="logo" />
        <img v-for="(logo, index) in logos" :key="'logo2-'+index" :src="logo" class="logo" />
      </div>
    </div>
  </section>
    <!-- FAQ SECTION -->
    <section id="faq-section" class="faq-section">
      <h2 class="section-title">FAQs</h2>
      <div class="faq-content">
        <ul>
          <li><strong>Q1:</strong> How does this platform work?</li>
          <li><strong>A1:</strong> We provide smart quizzes, daily practice, progress tracking and insights.</li>
          <li><strong>Q2:</strong> Is it free?</li>
          <li><strong>A2:</strong> Basic access is free with premium options available.</li>
        </ul>
      </div>
    </section>
    <!-- Our Why Section -->
    <section id="our-why-section" class="our-why-section">
      <div class="content">
        <h2 class="section-title">Our Why</h2>
        <p>
          At Prep, we believe every student deserves smarter, personalized, and efficient exam preparation. Powered by Artificial Intelligence, our platform transforms traditional studying by adapting to your unique learning style—helping you focus on what matters most.
        </p>
        <p>
          We connect concepts, track your progress, and provide tailored learning paths so you can prepare confidently for competitive exams like UPSC, SSC, Banking, and CAT. Our mission is to empower learners with cutting-edge AI tools that make exam success achievable, engaging, and stress-free.
        </p>
      </div>
    </section>
    <!-- Stories Section with Share Button -->
    <section id="stories-section" class="stories-section">
      <div class="content">
        <h2 class="section-title">Our Stories</h2>
        <p class="lead">
          While Prep is a new journey, <strong>you</strong> are the heart of our story.  
          This is your chance to share your experiences, challenges, and successes as part of our growing community.  
          Become a part of <em>Our Stories</em> by contributing your journey and inspiring others!
        </p>
        <button class="btn btn-start" @click="openStorySubmission">
          Share Your Story
        </button>
      </div>
    </section>
    <!-- Story Submission Modal -->
    <div v-if="storyModalOpen" class="modal-overlay" @click.self="closeStoryModal">
      <div class="modal-content story-modal">
        <button class="modal-close" @click="closeStoryModal" aria-label="Close">&times;</button>
        <h3 class="modal-title text-center">Share Your Story</h3>
        <form @submit.prevent="submitStory">
          <input type="text" v-model="storyForm.name" placeholder="Your Name" required />
          <input type="text" v-model="storyForm.exam" placeholder="Cleared Exam" required />
          <textarea v-model="storyForm.experience" placeholder="Your Experience with Prep" rows="5" required></textarea>
          <button type="submit" class="btn btn-start">Send</button>
        </form>
      </div>
    </div>
    <!-- FOOTER -->
    <footer class="footer d-flex flex-wrap justify-content-between align-items-start px-5 py-5">
    <!-- Left: About & Contact -->
    <div class="footer-left mb-4" style="flex:1; min-width: 320px; max-width: 600px;">
      <h3 class="footer-title mb-4">About Prep</h3>
      <p class="footer-description mb-4">
        Prep is your AI-powered competitive exam companion. Personalized quizzes, mock tests, and smart revision tools to help you stay ahead and succeed in all your exams.
      </p>
      <div class="contact-icons d-flex gap-4">
        <a href="https://instagram.com/yourprofile" target="_blank" aria-label="Instagram" class="contact-link d-flex align-items-center gap-2">
          <i class="bi bi-instagram fs-4"></i> <span>Instagram</span>
        </a>
        <a href="https://wa.me/yourwhatsappnumber" target="_blank" aria-label="WhatsApp" class="contact-link d-flex align-items-center gap-2">
          <i class="bi bi-whatsapp fs-4"></i> <span>WhatsApp</span>
        </a>
        <a href="tel:+1234567890" aria-label="Phone" class="contact-link d-flex align-items-center gap-2">
          <i class="bi bi-telephone fs-4"></i> <span>+1 234 567 890</span>
        </a>
      </div>
    </div>

    <!-- Right: Legal Links -->
    <div class="footer-right d-flex flex-column align-items-start" style="min-width: 220px;">
      <h3 class="footer-title mb-3">Legal</h3>
      <ul class="list-unstyled footer-legal-list">
        <li><a href="/terms" class="footer-link">Terms & Conditions</a></li>
        <li><a href="/privacy" class="footer-link">Privacy Policy</a></li>
      </ul>
    </div>
  </footer>


</template>

<script setup>
import { ref } from "vue";
import { useRouter } from 'vue-router';
import logo1 from '../assets/pic-3.png';
import logo2 from '../assets/pic-4.png';
import logo3 from '../assets/pic-5.png';
import logo4 from '../assets/pic-6.png';
import logo5 from '../assets/pic-7.png';
import logo6 from '../assets/pic-8.png';
import logo7 from '../assets/pic-9.png';

const logos = [logo1, logo2, logo3, logo4, logo5, logo6, logo7];
const router = useRouter();
const menuOpen = ref(false);
const loginModalOpen = ref(false);
const registerModalOpen = ref(false);
const storyModalOpen = ref(false);
const showModal = ref(false);


const storyForm = ref({
  name:'',
  exam:'',
  experience:''
});
const registerForm = ref({
  name: '',
  phone: '',
  email: '',
  password: ''
});
const emailLoginForm = ref({
  email: '',
  password: ''
});
//function submitRegistration() {
  //const formData = { ...registerForm.value };
  //const jsonData = JSON.stringify(formData);
  //console.log('Registering user with data:', jsonData);
  //registerForm.value = { name: '', phone: '', email: '', password: '' };
  //registerModalOpen.value = false;
//}
function toggleMenu() {
  menuOpen.value = !menuOpen.value;
}

function openLoginModal() {
  loginModalOpen.value = true;
  //console.log('Modal should open');
}

function closeLoginModal() {
  loginModalOpen.value = false;
}

async function continueWithEmail() {
    const payload = {
        email: emailLoginForm.value.email,
        password: emailLoginForm.value.password
    };

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();

        if (response.ok) {
            console.log('Login successful:');
            
            // Store the token and user data
            localStorage.setItem('auth_token', result.access_token);

            // Check if the response contains a 'user' object (for regular users)
            // or just the role (for admins)
            if (result.user) {
                localStorage.setItem('user', JSON.stringify(result.user));
            } else {
                // Clear any old user data for the admin session
                localStorage.removeItem('user');
            }

            // Determine the redirect path based on the 'role' from the backend
            let redirectPath;
            if (result.role === 'admin') {
                redirectPath = '/adashboard';
            } else {
                // If the user was trying to access a specific page before logging in,
                // redirect them there. Otherwise, go to the default dashboard.
                redirectPath = router.currentRoute.value.query.redirect || '/dashboard';
            }

            // Close the login modal and clear form
            loginModalOpen.value = false;
            emailLoginForm.value = { email: '', password: '' };
            showModal.value = false;

            // Perform the redirection
            router.push(redirectPath);

        } else {
            // Login failed
            alert('Login failed: ' + result.error);
        }
    } catch (error) {
        // Network error
        console.error('Network error during login:', error);
        alert('Network error during login. Please try again.');
    }
}

function openRegisterModal() {
  loginModalOpen.value = false;
  registerModalOpen.value = true;
}
function openLoginModalFormRegister() {
  registerModalOpen.value = false;
  loginModalOpen.value = true;
}
function scrollToFaq() {
  const faqSection = document.getElementById('faq-section');
  if (faqSection){
    faqSection.scrollIntoView({ behavior:'smooth'});
  }
}
function scrollToOurWhy() {
  const ourWhySection = document.getElementById('our-why-section');
  if (ourWhySection){
    ourWhySection.scrollIntoView({ behavior:'smooth' });
  }
}
function openStorySubmission() {
  const story = document.getElementById('stories-section');
  if (story) {
    story.scrollIntoView({ behavior: 'smooth' });
  }
  storyModalOpen.value = true;
}
function closeStoryModal(){
  storyModalOpen.value = false;
}
function googleLogin() {
  window.location.href = '/api/google/login';
}
async function finishGoogleLogin() {
  try {
    const response = await fetch('/api/google/token', {
      credentials: 'include'  // Use this if backend uses cookies, otherwise remove
    });
    if (response.ok) {
      const result = await response.json();
      localStorage.setItem('auth_token', result.access_token);
      const redirectPath = router.currentRoute.value.query.redirect || '/dashboard';
      router.push(redirectPath);
    } else {
      alert('Google login token retrieval failed.');
    }
  } catch (error) {
    alert('Network error during Google login token retrieval.');
  }
}


function submitStory(){
  const storyData = { ...storyForm.value};
  const jsonData = JSON.stringify(storyData);
  console.log('User Story Submitted: ',jsonData);

  //clear form
  storyForm.value = {
    name:'',
    exam:'',
    experience:''
  };
  closeStoryModal();
}
async function submitRegistration() {
  const formData = {
    full_name: registerForm.value.name,
    email: registerForm.value.email,
    password: registerForm.value.password,
    phone: registerForm.value.phone,
    login_method: "email"
  };

  try {
    const response = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });

    const result = await response.json();

    if (response.ok) {
      console.log('Registration successful:', result);
      // Reset form and close modal
      registerForm.value = { name: '', phone: '', email: '', password: '' };
      registerModalOpen.value = false;
    } else {
      // Show error to user
      console.error('Registration error:', result.error);
      alert('Registration failed: ' + result.error);
    }
  } catch (error) {
    console.error('Network error:', error);
    alert('Network error occurred during registration.');
  }
}

</script>

<style scoped>
/* Section Styling */
.email-registration-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.email-registration-box {
  background-color: #333333; /* light black / dark gray */
  border: 1px solid #555555;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  padding: 2.5rem 3rem;
  border-radius: 12px;
  min-width: 320px;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: white;
  text-shadow: 0 0 4px rgba(255, 255, 255, 0.3);
}


.email-registration-box h3 {
  margin: 0 0 16px 0;
  font-weight: 700;
  font-size: 1.8rem;
  text-align: center;
  color: #333;
}
.email-registration-box input[type="email"],
.email-registration-box input[type="password"] {
  padding: 12px 14px;
  border-radius: 6px;
  border: 1.5px solid #ccc;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  outline: none;
}
.email-registration-box input[type="email"]:focus,
.email-registration-box input[type="password"]:focus {
  border-color: #ff5722;
  box-shadow: 0 0 8px rgba(255, 87, 34, 0.5);
}
.email-registration-btn-login {
  background-color: #ff5722;
  color: white;
  border: none;
  border-radius: 30px;
  padding: 12px 0;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.email-registration-btn-login:hover {
  background-color: #e64a19;
}
.email-registration-btn-close {
  background-color: transparent;
  border: none;
  color: #ff5722;
  font-weight: 700;
  cursor: pointer;
  padding: 10px 0;
  font-size: 1rem;
  text-align: center;
  transition: color 0.3s ease;
}
.email-registration-btn-close:hover {
  color: #b73b14;
}


.footer {
  background: linear-gradient(135deg, #1c1c1c 0%, #2a2a2a 40%, #0d0d0d 70%, #1f1f1f 100%);
  color: white;
  box-sizing: border-box;
  border-radius: 0;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.8);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.5;
}
.footer-title {
  font-weight: 700;
  font-size: 1.8rem;
  letter-spacing: 0.03em;
}
.footer-description {
  font-size: 1rem;
  color: #dcdcdc;
  max-width: 100%;
}

.contact-icons .contact-link {
  color: #ffccbc;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.3s ease;
}
.contact-icons .contact-link:hover,
.contact-icons .contact-link:focus {
  color: #ff5722;
  text-decoration: underline;
}
.contact-icons i {
  color: inherit;
}
.footer-legal-list li {
  margin-bottom: 12px;
}
.footer-link {
  color: #ffccbc;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.3s ease;
}
.footer-link:hover,
.footer-link:focus {
  color: #ff5722;
  text-decoration: underline;
}

/* Responsive adjustments */

@media (max-width: 768px) {
  .footer {
    flex-direction: column;
    text-align: center;
  }
  .footer-left, .footer-right {
    max-width: 100%;
    margin-bottom: 30px;
  }
  .footer-right {
    align-items: center;
  }
  .contact-icons {
    justify-content: center;
  }
}
.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background: linear-gradient(135deg, #1c1c1c 0%, #2a2a2a 40%, #0d0d0d 70%, #1f1f1f 100%);
  z-index: 1500;
  display: flex;
  justify-content: center;
  align-items: center;
}
.footer .content {
  max-width: none; /* or set to 100% */
  width: 100%;
  margin: 0 auto;
  padding: 0;
}
.modal-content.story-modal {
  background: #222;
  padding: 32px 32px 40px 32px;
  border-radius: 10px;
  max-width: 420px;
  width: 90%;
  color: #fff;
  box-shadow: 0 5px 15px rgba(0,0,0,0.4);
  position: relative;
  text-align: center;
}

.modal-close {
  position: absolute;
  top: 12px; right: 12px;
  background: transparent;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
}

.modal-title {
  font-weight: 600;
  font-size: 1.6rem;
  margin-bottom: 24px;
}

.modal-content input,
.modal-content textarea {
  width: 100%;
  padding: 12px 14px;
  margin-bottom: 16px;
  border-radius: 6px;
  border: 1px solid #555;
  background-color: #333;
  color: #eee;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.modal-content input:focus,
.modal-content textarea:focus {
  border-color: #ff5722;
  box-shadow: 0 0 8px #ff5722;
  outline: none;
}

.modal-content button.btn-start {
  background-color: #ff5722;
  font-weight: 700;
  border-radius: 30px;
  padding: 12px 0;
  font-size: 1.1rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.modal-content button.btn-start:hover {
  background-color: #e64a19;
}

.stories-section {
  background: linear-gradient(135deg, #0a0a0a 0%, #1f1f1f 40%, #3a3f47 70%, #1c1c1c 100%);
  color: white;
  padding: 60px 20px;
  text-align: center;
  border-radius: 12px;
  max-width: 900px;
  margin: 60px auto;
  box-shadow: 0 8px 24px rgba(30, 40, 50, 0.6);
}

.stories-section .section-title {
  font-size: 2.5rem;
  margin-bottom: 24px;
  font-weight: 700;
}
.stories-section .lead {
  font-size: 1.2rem;
  margin-bottom: 32px;
  line-height: 1.6;
}
.stories-section .btn-start {
  background-color: #ff5722;
  padding: 12px 36px;
  font-size: 1.1rem;
  border-radius: 30px;
  font-weight: 600;
  transition: background-color 0.3s ease;
}
.stories-section .btn-start:hover {
  background-color: #e64a19;
  cursor: pointer;
}

.our-why-section, .faq-section {
  width: 100vw;
  padding-left: 15px; /* or 20px */
  padding-right: 15px;
  box-sizing: border-box;
}
.our-why-section {
  margin-bottom: 10px;  /* reduce bottom margin */
  padding-bottom: 20px; /* optional: keep some padding */
}
.faq-section {
  margin-top: 10px;     /* reduce top margin */
  padding-top: 20px;    /* optional: keep some padding */
}
.our-why-section {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding-top: 100px;
  min-height: calc(100vh - 100px);
  background: radial-gradient(circle at top right, #1a1a1a, #000);
  color: white;
  position: relative;
  overflow: visible;
  padding-left: 15px;
  padding-right: 15px;
  width: 100vw;
  box-sizing: border-box;
  margin: 40px 0 10px 0;
  border-radius: 0;
  box-shadow: none;
}
.our-why-section .section-title {
  background: linear-gradient(90deg, #ffe259, #ffa751);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent;
  margin-bottom: 24px;
  text-align: center;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 20px;
  font-weight: 700;
  font-size: 2.5rem;
}
.our-why-section .content {
  max-width: 700px;
  margin: 0 auto;
  color: white;
  font-size: 1.1rem;
  line-height: 1.7;
}
.our-why-section::before {
  content: "";
  position: absolute;
  width: 600px;
  height: 600px;
  background: rgba(0, 200, 255, 0.15);
  top: -200px;
  right: -200px;
  border-radius: 50%;
  filter: blur(120px);
  animation: float-hero 6s ease-in-out infinite alternate;
  z-index: 0;
}

.our-why-section::after {
  content: "";
  position: absolute;
  width: 400px;
  height: 400px;
  background: rgba(255, 0, 150, 0.15);
  bottom: -150px;
  left: -150px;
  border-radius: 50%;
  filter: blur(100px);
  animation: float-hero-reverse 8s ease-in-out infinite alternate-reverse;
  z-index: 0;
}

@keyframes float-hero {
  from { transform: translateY(0); }
  to { transform: translateY(30px); }
}

@keyframes float-hero-reverse {
  from { transform: translateY(0); }
  to { transform: translateY(-30px); }
}

.available-exams, .faq-section{
  border: 1px solid red;
  padding-top: 40px;
  padding-bottom: 20px;
}
.faq-section {
  width: 100vw;
  max-width: 100vw;
  padding: 40px 20px;
  background-color: #222;
  color: #fff !important;
  margin: 40px 0;
  border-radius: 0;
  box-shadow: none;
  box-sizing: border-box;
  margin-top: 0px;
  padding-top: 20px;
  padding-bottom: 20px;
}
.faq-section .section-title {
  color: #ff5722;
  margin-bottom: 24px;
  text-align: center;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 20px;
}
.faq-section ul {
  list-style: none;
  padding: 0;
  color: #fff !important;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 20px;
}
.faq-section li {
  margin-bottom: 16px;
  border-bottom: 1px solid #444;
  padding-bottom: 8px;
  color: #fff !important;
}
.faq-section li:last-child {
  border-bottom: none;
}
.faq-content {
  position: static;
  width: auto;
  box-shadow: none;
  margin-top: 0;
  padding: 20px;
  color: #fff;
}
.faq-section, .our-why-section {
  border: 1px solid red;  /* show border to visualize spacing */
  padding-top: 40px;       /* top padding */
  padding-bottom: 20px;    /* bottom padding */
  margin: 0;               /* reset margin for consistent spacing */
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #1c1c1c 0%, #2a2a2a 40%, #0d0d0d 70%, #1f1f1f 100%);
  z-index: 1500;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Increased size modal content */
.modal-content.register-large {
  position: relative;
  background: #222;
  padding: 40px 32px;
  border-radius: 10px;
  max-width: 480px;
  width: 90%;
  color: white;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* Close button top-right */
.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  background: transparent;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
}

/* Modal title */
.modal-title {
  margin: 0;
  font-weight: 600;
  font-size: 1.6rem;
  margin-bottom: 20px;
}

/* Form styling */
.modal-content form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Inputs stacked vertically */
.modal-content input {
  padding: 14px 16px;
  border-radius: 6px;
  border: 1px solid #444;
  background-color: #333;
  color: #eee;
  font-size: 1rem;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

/* Input focus & hover effect */
.modal-content input:focus,
.modal-content input:hover {
  border-color: #ff5722;
  box-shadow: 0 0 8px 0 #ff5722;
  outline: none;
}

/* Submit button overrides */
.modal-content button.btn-start {
  background-color: #ff5722;
  color: white;
  font-weight: 700;
  border-radius: 30px;
  padding: 12px 0;
  font-size: 1.1rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

/* Submit button hover */
.modal-content button.btn-start:hover {
  background-color: #e64a19;
}

/* Switch form text and link */
.switch-form-text {
  margin-top: 20px;
  font-size: 0.9rem;
  color: #fff;
  text-align: center;
}

.switch-form-text a {
  color: #ff5722;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s ease;
}

.switch-form-text a:hover {
  color: #e64a19;
}

.modal-content.register-large {
  max-width: 480px; /* increase width */
  padding: 40px 32px; /* more padding */
}

.switch-form-text a {
  color: #ff5722; /* button orange color */
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s ease;
}

.switch-form-text a:hover {
  color: #e64a19; /* slightly darker orange on hover */
}
.available-exams {
  padding: 80px 20px;
  background: #ffffff;
  color: #000000;
  text-align: center;
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 40px;
  color: #ff5722;
}

.logo-slider {
  overflow: hidden;
  width: 100%;
  position: relative;
}

.logo-track {
  display: flex;
  gap: 60px;
  animation: marquee 10s linear infinite;
  white-space: nowrap;
}

@keyframes marquee {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}


.logo {
  height: 60px;
  width: auto;
  margin: 0 30px;
  flex-shrink: 0;
}

@keyframes scroll-left {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-100%);
  }
}

/* Gradient strip filling the top space */
.btn-start + .btn-start {
  margin-left: 16px;
}

.carousel-item img {
  width: 100%;
  height: auto;
}

.navbar-bg-strip {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 30px;
  background: transparent;
  overflow: visible;
  z-index: 1000;
  pointer-events: none;
  filter: none;
}

.navbar-bg-strip::before,
.navbar-bg-strip::after {
  content: "";
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
  animation-direction: alternate;
  will-change: transform;
}

.navbar-bg-strip::before {
  width: 300px;
  height: 300px;
  background: rgba(0, 200, 255, 1);
  top: -150px;
  right: 10%;
  animation-name: float-navbar;
  animation-duration: 6s;
}

.navbar-bg-strip::after {
  width: 200px;
  height: 200px;
  background: rgba(255, 0, 150, 1);
  bottom: -100px;
  left: 15%;
  animation-name: float-navbar-reverse;
  animation-duration: 8s;
}

@keyframes float-navbar {
  from { transform: translateY(0); }
  to { transform: translateY(20px); }
}

@keyframes float-navbar-reverse {
  from { transform: translateY(0); }
  to { transform: translateY(-20px); }
}

/* Navbar */
.navbar-pill {
  background: transparent;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 40px;
  width: 95%;
  max-width: 1340px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: fixed;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1200;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.navbar-wrapper {
  margin-top: 0;
}

/* Brand */
.brand {
  font-size: 1.55rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
  text-transform: lowercase;
}

/* Links */
.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-link {
  color: #fff !important;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s ease;
}

.nav-link:hover {
  color: #ff5722 !important;
}

.btn-start {
  background: #ff5722;
  color: #fff !important;
  border-radius: 30px;
  padding: 8px 24px;
  font-weight: 600;
  border: none;
  transition: background 0.3s ease;
}

.btn-start:hover {
  background: #e64a19;
}

/* Hamburger */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 36px;
  height: 36px;
  background: transparent;
  border: none;
  cursor: pointer;
  z-index: 1300;
}

.hamburger span {
  display: block;
  width: 24px;
  height: 3px;
  background: #fff;
  margin: 4px 0;
  border-radius: 2px;
  transition: all 0.3s;
}

/* Responsive menu styles */
@media (max-width: 900px) {
  .hamburger {
    display: flex;
    margin-left: auto;
  }
  .hamburger span {
    background: #fffefe; /* Choose a high-contrast color */
    display: block;
    height: 3px;
    margin: 5px 0;
    transition: background 0.3s;
    background-color: #fff;
  }
  .nav-links {
    position: fixed;
    top: 100px;
    left: 0;
    right: 0;
    background: #0d0d0d;
    flex-direction: column;
    align-items: center;
    gap: 14px;
    padding: 20px;
    border-radius: 0 0 30px 30px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.32);
    max-height: 0;
    opacity: 0;
    overflow: hidden;
    transition: max-height 0.3s ease, opacity 0.3s ease;
    z-index: 1400;
  }

  .nav-links.open {
    max-height: 400px;
    opacity: 1;
  }

  .nav-links::before,
  .nav-links::after {
    content: "";
    position: absolute;
    border-radius: 50%;
    filter: blur(100px);
    opacity: 0.1;
    animation-timing-function: ease-in-out;
    animation-iteration-count: infinite;
    animation-direction: alternate;
    will-change: transform;
    pointer-events: none;
  }

  .nav-links::before {
    width: 300px;
    height: 300px;
    background: rgba(0, 200, 255, 0.3);
    top: -150px;
    right: 10%;
    animation-name: float-navbar;
    animation-duration: 6s;
  }

  .nav-links::after {
    width: 200px;
    height: 200px;
    background: rgba(255, 0, 150, 0.3);
    bottom: -100px;
    left: 15%;
    animation-name: float-navbar-reverse;
    animation-duration: 8s;
  }

  .nav-link, .btn-start {
    margin: 8px 0;
  }
}

/* Hero Section */
.hero-section {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding-top: 100px;
  min-height: calc(100vh - 100px);
  background: radial-gradient(circle at top right, #1a1a1a, #000);
  color: white;
  position: relative;
  overflow: visible;
  padding-left: 15px;
  padding-right: 15px;
}

.content {
  max-width: 700px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

/* Floating glow effect */
.hero-section::before {
  content: "";
  position: absolute;
  width: 600px;
  height: 600px;
  background: rgba(0, 200, 255, 0.15);
  top: -200px;
  right: -200px;
  border-radius: 50%;
  filter: blur(120px);
  animation: float-hero 6s ease-in-out infinite alternate;
}

.hero-section::after {
  content: "";
  position: absolute;
  width: 400px;
  height: 400px;
  background: rgba(255, 0, 150, 0.15);
  bottom: -150px;
  left: -150px;
  border-radius: 50%;
  filter: blur(100px);
  animation: float-hero-reverse 8s ease-in-out infinite alternate-reverse;
}

@keyframes float-hero {
  from { transform: translateY(0); }
  to { transform: translateY(30px); }
}

@keyframes float-hero-reverse {
  from { transform: translateY(0); }
  to { transform: translateY(-30px); }
}

.tagline {
  font-size: 1rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #aaa;
}
/* Modal Styles for Login Popup */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1500;
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal-content {
  position: relative;
  background: #222;
  padding: 24px 24px 40px 24px;
  border-radius: 10px;
  max-width: 320px;
  width: 90%;
  color: white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  text-align: center;
}
.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  background: transparent;
  border: none;
  color: white;
  font-size: 1.5rem;
  float: right;
  cursor: pointer;
  margin-bottom: 12px;
}
.modal-title{
  margin: 0;
  font-weight: 600;
  font-size: 1.4rem;
  margin-bottom: 20px;
}
.btn-email, .btn-google {
  width: 100%;
  margin: 8px 0;
  padding: 10px 14px;
  border-radius: 6px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}
.btn-email {
  background-color: #ff5722;
  color: white;
}
.btn-google {
  background-color: #ffffff;
  color: #000;
}
.google-logo {
  width: 30px;
  height: 30px;
}
</style>

<style>
html, body {
  overflow-x: hidden;
}
html, body {
  height: 100%;
  margin: 0;
  overflow-y: auto;  /* enable scrolling on body */
}
/* Prevent nested containers from scrolling */
.some-inner-scrollable-container {
  overflow-y: visible !important; /* or unset */
}
</style>