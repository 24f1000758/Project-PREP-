<template>
  <div class="container mt-5 px-md-5">
    <div class="row align-items-start">

      <!-- Avatar + Upload Section -->
      <div class="col-md-4 text-center mb-4 position-relative">
        <img 
          :src="profilePictureUrl" 
          class="rounded-circle" 
          style="width: 150px; height: 150px;" 
          alt="User profile picture" 
          @error="onImageError" 
        />

        <label for="fileInput" class="upload-btn position-absolute">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="white" viewBox="0 0 24 24">
            <path d="M5 20h14v-2H5v2zm7-18v10l4-4h-3V2h-2v6H8l4 4z"/>
          </svg>
          <input id="fileInput" type="file" accept="image/*" @change="onFileChange" />
        </label>

        <h5 class="mt-3">{{ user.full_name }}</h5>
      </div>

      <!-- Edit Box -->
      <div class="col-md-8" :class="{ 'edit-mode': editMode }">
        <div class="card shadow-sm">

          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">👤 Profile Details</h5>
            <button class="btn btn-sm btn-outline-primary" @click="toggleEditMode">
              {{ editMode ? 'Cancel' : 'Edit' }}
            </button>
          </div>

          <div class="card-body">

            <!-- Name -->
            <div class="row mb-2">
              <div class="col-5 label-text">Name</div>
              <div class="col-7" :class="{ 'edit-highlight': editMode }">
                <template v-if="editMode">
                  <input type="text" class="form-control" v-model="edit.full_name" />
                </template>
                <template v-else>{{ user.full_name }}</template>
              </div>
            </div>

            <!-- Email -->
            <div class="row mb-2">
              <div class="col-5 label-text">Email</div>
              <div class="col-7">{{ user.email }}</div>
            </div>

            <!-- Qualification -->
            <div class="row mb-2">
              <div class="col-5 label-text">Qualification</div>
              <div class="col-7" :class="{ 'edit-highlight': editMode }">
                <template v-if="editMode">
                  <select class="form-select custom-select" v-model="edit.qualification">
                    <option>Secondary Education</option>
                    <option>Senior Secondary Education</option>
                    <option>Graduate</option>
                    <option>Post-Graduate</option>
                    <option>Masters</option>
                  </select>
                </template>
                <template v-else>{{ user.qualification }}</template>
              </div>
            </div>

            <!-- Gender -->
            <div class="row mb-2">
              <div class="col-5 label-text">Gender</div>
              <div class="col-7" :class="{ 'edit-highlight': editMode }">
                <template v-if="editMode">
                  <select class="form-select custom-select" v-model="edit.gender">
                    <option>Male</option>
                    <option>Female</option>
                    <option>Other</option>
                  </select>
                </template>
                <template v-else>{{ user.gender }}</template>
              </div>
            </div>

            <!-- State -->
            <div class="row mb-2">
              <div class="col-5 label-text">State</div>
              <div class="col-7" :class="{ 'edit-highlight': editMode }">
                <template v-if="editMode">
                  <select class="form-select custom-select" v-model="edit.state">
                    <option v-for="s in states" :key="s" :value="s">{{ s }}</option>
                  </select>
                </template>
                <template v-else>{{ user.state }}</template>
              </div>
            </div>

            <!-- Date of Birth -->
            <div class="row mb-2">
              <div class="col-5 label-text">Date of Birth</div>
              <div class="col-7" :class="{ 'edit-highlight': editMode }">
                <template v-if="editMode">
                  <input type="date" class="form-control" v-model="edit.dob" />
                </template>
                <template v-else>{{ formattedDob }}</template>
              </div>
            </div>

            <!-- Phone -->
            <div class="row mb-2">
              <div class="col-5 label-text">Phone</div>
              <div class="col-7" :class="{ 'edit-highlight': editMode }">
                <template v-if="editMode">
                  <input type="text" class="form-control" v-model="edit.phone" />
                </template>
                <template v-else>{{ user.phone }}</template>
              </div>
            </div>

            <!-- Marital Status -->
            <div class="row mb-2">
              <div class="col-5 label-text">Marital Status</div>
              <div class="col-7" :class="{ 'edit-highlight': editMode }">
                <template v-if="editMode">
                  <select class="form-select custom-select" v-model="edit.married">
                    <option>Single</option>
                    <option>Married</option>
                    <option>Divorced</option>
                    <option>Widowed</option>
                    <option>Other</option>
                  </select>
                </template>
                <template v-else>{{ user.married }}</template>
              </div>
            </div>

            <!-- Save Button -->
            <div v-if="editMode" class="text-end mt-3">
              <button class="btn btn-success" @click="saveChanges" :disabled="!allFieldsFilled">
                Save Changes
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import dummyPic from '../assets/pic-11.jpg';

const CLOUD_NAME = "djt7onfpm"; // ⚡ from Cloudinary dashboard
const UPLOAD_PRESET = "Prepp_pics"; // ⚡ create in Cloudinary settings

const states = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands',
  'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Delhi',
  'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
];

const user = reactive({
  id: '',
  full_name: '',
  email: '',
  qualification: '',
  gender: '',
  state: '',
  dob: '',
  profile_picture: '',
  login_method: '',
  phone: '',
  marital_status: ''
});

const edit = reactive({ ...user });
const editMode = ref(false);

const profilePictureUrl = computed(() => {
  return user.profile_picture || dummyPic;
});

watch(user, (val) => {
  console.log("User object:", val);
}, { deep: true });

const formattedDob = computed(() => {
  if (!user.dob) return '';
  const d = new Date(user.dob);
  return d.toLocaleDateString();
});

const allFieldsFilled = computed(() => {
  return [
    edit.full_name,
    edit.qualification,
    edit.gender,
    edit.state,
    edit.dob,
    edit.phone,
    edit.married
  ].every(field => field && String(field).trim() !== '');
});

function toggleEditMode() {
  Object.assign(edit, user);
  editMode.value = !editMode.value;
}

// 🔹 Upload file to Cloudinary
async function onFileChange(e) {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("upload_preset", UPLOAD_PRESET);

  try {
    const res = await fetch(`https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    if (data.secure_url) {
      user.profile_picture = data.secure_url;
      edit.profile_picture = data.secure_url;
      localStorage.setItem("user", JSON.stringify(user));

      await fetch(`/api/register/${user.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile_picture: data.secure_url })
      });

      alert("Profile picture updated!");
    }
  } catch (err) {
    console.error("Upload failed:", err);
    alert("🚫 Image upload failed");
  }
}

function onImageError(event) {
  if (event.target.src !== dummyPic) {
    event.target.src = dummyPic;
  }
}

async function saveChanges() {
  try {
    const res = await fetch(`/api/register/${user.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(edit)
    });

    const data = await res.json();
    if (res.ok) {
      Object.assign(user, edit);
      localStorage.setItem('user', JSON.stringify(user));
      editMode.value = false;
      alert('✅ Profile updated successfully');
    } else {
      alert(data.error || '❌ Update failed');
    }
  } catch (err) {
    console.error(err);
    alert('🚫 Server error');
  }
}

onMounted(() => {
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    try {
      const parsedUser = JSON.parse(storedUser);
      Object.assign(user, parsedUser);
      Object.assign(edit, parsedUser);
    } catch (e) {
      console.log('Invalid user data in localStorage', e);
    }
  }
});
</script>


<style scoped>
.card {
  background: linear-gradient(135deg, #23272b 65%, #181a1b 100%);
  border-radius: 18px;
  box-shadow: 0 8px 32px rgba(44,44,44,0.33), 0 2px 18px #2227;
  border: 1px solid #2f3237;
}

.card-header {
  background: transparent;
  color: #fff;
  border-bottom: 1px solid #393c41;
  border-radius: 18px 18px 0 0;
  padding-bottom: 0.7rem;
  font-size: 1.15rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.card-body {
  color: #fff;
}

.card-body .row {
  border-bottom: 1px solid #292c30;
  padding: 0.5rem 0;
}

.card-body .row:last-child {
  border-bottom: none;
}

.form-control,
.form-select {
  background: #f9f7f3;
  color: #222;
  border-radius: 9px;
  border: 1.5px solid #ccc;
  font-size: 1rem;
  box-shadow: none;
  margin-bottom: 6px;
  transition: border-color 0.22s ease, box-shadow 0.22s ease;
}

.form-control:focus,
.form-select:focus {
  border-color: #a59e8c;
  box-shadow: 0 0 6px 2px #c8c1b0aa;
  outline: none;
  background: #fefdfb;
}

/* Style for dropdown options */
.form-select.custom-select option {
  color: #222 !important;
  background: #e9f0ff !important;
  font-weight: 600;
}

/* Dropdown arrow */
.form-select.custom-select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml;utf8,<svg fill='white' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/></svg>");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1rem auto;
  padding-right: 2.5rem;
}

/* Editable highlight */
.edit-highlight {
  background: #fefcf8;
  border-radius: 9px;
  box-shadow: 0 3px 14px rgba(200, 190, 170, 0.3);
}

.card-body .row .col-7 {
  transition: background 0.18s ease;
}

.edit-mode .card-body .row .col-7:hover,
.edit-mode .card-body .row .col-7:focus-within {
  background: #f7f5f1;
  cursor: pointer;
  border-radius: 9px;
  box-shadow: 0 0 8px 2px rgba(200, 190, 170, 0.35);
}

/* Buttons */
.btn-outline-primary {
  border-radius: 9px;
  border-width: 2px;
  font-weight: 500;
  letter-spacing: 0.02rem;
  color: #fff;
  border-color: #5c82c2;
  background: transparent;
  transition: background 0.22s ease, color 0.22s ease, border-color 0.22s ease;
}

.btn-outline-primary:hover {
  background: #ff8c00;
  color: #fff;
  border-color: #ff8c00;
  box-shadow: 0 2px 10px 0 rgba(255, 140, 0, 0.42);
}

.btn-success {
  background: linear-gradient(90deg, #ff8c00 70%, #ffb347 100%);
}

.btn-success:hover {
  background: linear-gradient(90deg, #ffb347 30%, #ff8c00 100%);
  box-shadow: 0 2px 14px rgba(255, 140, 0, 0.55);
}

/* Upload button */
.upload-btn {
  background-color: #222629;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  bottom: 30px;
  right: 90px;
  position: absolute;
  box-shadow: 0 2px 10px #203a6fbb;
  border: 2px solid #5c82c2;
  transition: background-color 0.3s, border-color 0.18s;
}

.upload-btn:hover {
  background-color: #ff8c00;
  border-color: #ff8c00;
  box-shadow: 0 4px 12px rgba(255, 140, 0, 0.5);
}

.upload-btn input[type="file"] {
  display: none;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

h5,
.card-header h5 {
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.02rem;
}

.label-text {
  color: #dde7fa;
  font-weight: 600;
}
</style>
