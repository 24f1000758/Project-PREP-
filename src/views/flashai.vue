<template>
  <div class="container-fluid py-4 px-3">
    <!-- Main Navigation Toggle -->
    <div class="toggle mb-5 d-flex justify-content-center">
      <div
        class="toggle-group rounded-pill overflow-hidden text-white shadow-lg"
        :data-active="activeView"
      >
        <button
          class="btn toggle-btn rounded-pill"
          :class="{ 'btn-active': activeView === 'decks' }"
          @click="setActiveView('decks')"
        >
          <i class="fas fa-layer-group me-2"></i>My Decks
        </button>
        <button
          class="btn toggle-btn rounded-pill"
          :class="{ 'btn-active': activeView === 'text' }"
          @click="setActiveView('text')"
        >
          <i class="fas fa-font me-2"></i>Text
        </button>
        <button
          class="btn toggle-btn rounded-pill"
          :class="{ 'btn-active': activeView === 'document' }"
          @click="setActiveView('document')"
        >
          <i class="fas fa-file-pdf me-2"></i>Document
        </button>
        <button
          class="btn toggle-btn rounded-pill"
          :class="{ 'btn-active': activeView === 'image' }"
          @click="setActiveView('image')"
        >
          <i class="fas fa-image me-2"></i>Picture
        </button>
        <button
          class="btn toggle-btn rounded-pill"
          :class="{ 'btn-active': activeView === 'video' }"
          @click="setActiveView('video')"
        >
          <i class="fas fa-video me-2"></i>Video
        </button>
      </div>
    </div>

    <!-- My Decks View (Default) -->
    <div
      v-if="activeView === 'decks'"
      class="main-content bg-gradient-dark text-white rounded-4 shadow-lg animate__animated animate__fadeInUp p-4 p-md-5"
    >
      <div class="text-center mb-4">
        <i class="fas fa-layer-group text-primary mb-3" style="font-size: 3rem;"></i>
        <h2 class="h3 fw-bold text-white mb-2">My Flashcard Decks</h2>
        <p class="text-light opacity-75">Manage and review your saved flashcard collections</p>
      </div>

      <div v-if="!decks.length" class="text-center text-secondary py-5">
        <i class="fas fa-plus-circle mb-3" style="font-size: 4rem; opacity: 0.3;"></i>
        <h4 class="text-light mb-2">No decks created yet</h4>
        <p class="mb-0">Start by generating flashcards from text, documents, images, or videos!</p>
      </div>

      <div v-else class="row g-4">
        <div
          v-for="deck in decks"
          :key="deck.id"
          class="col-12 col-md-6 col-lg-4"
        >
          <div class="deck-card bg-secondary rounded-4 p-4 h-100 shadow-sm hover-lift">
            <div class="d-flex align-items-start justify-content-between mb-3">
              <h5 class="fw-bold text-white mb-0 flex-grow-1 me-3">{{ deck.name }}</h5>
              <span class="badge bg-primary rounded-pill">{{ deck.cardCount || 0 }} cards</span>
            </div>
            <div class="d-flex gap-2 flex-wrap">
              <button @click="viewDeck(deck)" class="btn btn-primary btn-sm flex-grow-1">
                <i class="fas fa-eye me-1"></i>View
              </button>
              <button @click="renameDeck(deck)" class="btn btn-outline-light btn-sm">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="deleteDeck(deck)" class="btn btn-outline-danger btn-sm">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Text Input View -->
    <div
      v-if="activeView === 'text'"
      class="main-content bg-gradient-dark text-white rounded-4 shadow-lg animate__animated animate__fadeIn p-4 p-md-5"
    >
      <div class="text-center mb-4">
        <i class="fas fa-font text-info mb-3" style="font-size: 3rem;"></i>
        <h2 class="h3 fw-bold text-white mb-2">Generate from Text</h2>
        <p class="text-light opacity-75">Paste your notes or study material to create flashcards</p>
      </div>

      <div class="row justify-content-center">
        <div class="col-12 col-lg-8">
          <div class="mb-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <label class="form-label text-light fw-semibold">Your Text Content</label>
              <small class="text-warning">
                <span :class="{ 'text-danger': wordCount > 1000 }">{{ wordCount }}/1000 words</span>
              </small>
            </div>
            <textarea
              class="form-control bg-dark text-white border-secondary"
              rows="12"
              placeholder="Paste or write your notes here... (Maximum 1000 words)"
              v-model="textInput"
              :class="{ 'border-danger': wordCount > 1000 }"
            ></textarea>
            <div v-if="wordCount > 1000" class="text-danger small mt-2">
              <i class="fas fa-exclamation-triangle me-1"></i>
              Please reduce your text to 1000 words or less.
            </div>
          </div>
          
          <button
            class="btn w-100 btn-lg btn-gradient-success fw-bold shadow-sm"
            :disabled="!textInput.trim() || wordCount > 1000 || isSending"
            @click="sendTextToBackend"
          >
            <span
              v-if="isSending"
              class="spinner-border spinner-border-sm me-2"
              role="status"
              aria-hidden="true"
            ></span>
            <i v-else class="fas fa-magic me-2"></i>
            <span v-if="!isSending">Generate Flashcards</span>
            <span v-else>Generating...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Document Upload View -->
    <div
      v-if="activeView === 'document'"
      class="main-content bg-gradient-dark text-white rounded-4 shadow-lg animate__animated animate__fadeIn p-4 p-md-5"
    >
      <div class="text-center mb-4">
        <i class="fas fa-file-pdf text-warning mb-3" style="font-size: 3rem;"></i>
        <h2 class="h3 fw-bold text-white mb-2">Upload Document</h2>
        <p class="text-light opacity-75">Upload a PDF document to extract flashcards</p>
      </div>

      <div class="row justify-content-center">
        <div class="col-12 col-lg-8">
          <div
            class="upload-area border border-2 border-dashed border-warning rounded-4 p-5 text-center cursor-pointer hover-glow"
            @click="fileInput.click()"
            @dragover.prevent
            @drop.prevent="onDrop"
            :class="{ 'border-success': currentFile, 'border-danger': fileError }"
          >
            <input
              type="file"
              ref="fileInput"
              class="d-none"
              accept="application/pdf"
              @change="onFileChange"
            />
            
            <div v-if="!currentFile" class="upload-placeholder">
              <i class="fas fa-cloud-upload-alt mb-4" style="font-size: 4rem; opacity: 0.7;"></i>
              <h5 class="fw-bold text-white mb-3">Drop your PDF here</h5>
              <p class="text-light mb-2">or <strong>click to browse</strong></p>
              <div class="upload-specs text-secondary small">
                <p class="mb-1"><i class="fas fa-file-pdf me-1"></i> PDF files only</p>
                <p class="mb-1"><i class="fas fa-weight-hanging me-1"></i> Maximum 5MB</p>
                <p class="mb-0"><i class="fas fa-info-circle me-1"></i> One file at a time</p>
              </div>
            </div>

            <div v-else class="selected-file">
              <i class="fas fa-file-pdf text-warning mb-3" style="font-size: 3rem;"></i>
              <h5 class="text-white fw-bold mb-2">{{ currentFile.name }}</h5>
              <p class="text-light mb-3">{{ (currentFile.size / 1024 / 1024).toFixed(2) }} MB</p>
              <button
                class="btn btn-outline-danger btn-sm"
                @click.stop="removeFile"
              >
                <i class="fas fa-times me-1"></i>Remove
              </button>
            </div>

            <div v-if="fileError" class="text-danger mt-3">
              <i class="fas fa-exclamation-triangle me-1"></i>
              {{ fileError }}
            </div>
          </div>

          <button
            class="btn w-100 btn-lg btn-gradient-success fw-bold shadow-sm mt-4"
            :disabled="!currentFile || fileError || isSending"
            @click="sendToBackend"
          >
            <span
              v-if="isSending"
              class="spinner-border spinner-border-sm me-2"
              role="status"
              aria-hidden="true"
            ></span>
            <i v-else class="fas fa-magic me-2"></i>
            <span v-if="!isSending">Generate Flashcards</span>
            <span v-else>Processing Document...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Image Upload View -->
    <div
      v-if="activeView === 'image'"
      class="main-content bg-gradient-dark text-white rounded-4 shadow-lg animate__animated animate__fadeIn p-4 p-md-5"
    >
      <div class="text-center mb-4">
        <i class="fas fa-image text-info mb-3" style="font-size: 3rem;"></i>
        <h2 class="h3 fw-bold text-white mb-2">Upload Picture</h2>
        <p class="text-light opacity-75">Upload an image containing text to extract flashcards</p>
      </div>

      <div class="row justify-content-center">
        <div class="col-12 col-lg-8">
          <div
            class="upload-area border border-2 border-dashed border-info rounded-4 p-5 text-center cursor-pointer hover-glow"
            @click="imageInput.click()"
            @dragover.prevent
            @drop.prevent="onImageDrop"
            :class="{ 'border-success': currentImage, 'border-danger': imageError }"
          >
            <input
              type="file"
              ref="imageInput"
              class="d-none"
              accept="image/jpeg, image/png, image/gif, image/bmp, image/webp"
              @change="onImageChange"
            />
            
            <div v-if="!currentImage" class="upload-placeholder">
              <i class="fas fa-images mb-4" style="font-size: 4rem; opacity: 0.7;"></i>
              <h5 class="fw-bold text-white mb-3">Drop your image here</h5>
              <p class="text-light mb-2">or <strong>click to browse</strong></p>
              <div class="upload-specs text-secondary small">
                <p class="mb-1"><i class="fas fa-image me-1"></i> JPEG, PNG, GIF, BMP, WebP</p>
                <p class="mb-1"><i class="fas fa-weight-hanging me-1"></i> Maximum 5MB</p>
                <p class="mb-0"><i class="fas fa-info-circle me-1"></i> One image at a time</p>
              </div>
            </div>

            <div v-else class="selected-file">
              <div class="image-preview mb-3">
                <img :src="imagePreview" alt="Preview" class="img-fluid rounded" style="max-height: 200px;" />
              </div>
              <h5 class="text-white fw-bold mb-2">{{ currentImage.name }}</h5>
              <p class="text-light mb-3">{{ (currentImage.size / 1024 / 1024).toFixed(2) }} MB</p>
              <button
                class="btn btn-outline-danger btn-sm"
                @click.stop="removeImage"
              >
                <i class="fas fa-times me-1"></i>Remove
              </button>
            </div>

            <div v-if="imageError" class="text-danger mt-3">
              <i class="fas fa-exclamation-triangle me-1"></i>
              {{ imageError }}
            </div>
          </div>

          <button
            class="btn w-100 btn-lg btn-gradient-success fw-bold shadow-sm mt-4"
            :disabled="!currentImage || imageError || isSending"
            @click="sendImageToBackend"
          >
            <span
              v-if="isSending"
              class="spinner-border spinner-border-sm me-2"
              role="status"
              aria-hidden="true"
            ></span>
            <i v-else class="fas fa-magic me-2"></i>
            <span v-if="!isSending">Generate Flashcards</span>
            <span v-else>Processing Image...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Video Link View -->
    <div
      v-if="activeView === 'video'"
      class="main-content bg-gradient-dark text-white rounded-4 shadow-lg animate__animated animate__fadeIn p-4 p-md-5"
    >
      <div class="text-center mb-4">
        <i class="fas fa-video text-danger mb-3" style="font-size: 3rem;"></i>
        <h2 class="h3 fw-bold text-white mb-2">Generate from Video</h2>
        <p class="text-light opacity-75">Paste a YouTube or video URL to extract learning content</p>
      </div>

      <div class="row justify-content-center">
        <div class="col-12 col-lg-8">
          <div class="mb-3">
            <label class="form-label text-light fw-semibold">Video URL</label>
            <div class="input-group">
              <span class="input-group-text bg-dark border-secondary text-light">
                <i class="fas fa-link"></i>
              </span>
              <input
                type="url"
                class="form-control bg-dark text-white border-secondary"
                placeholder="https://www.youtube.com/watch?v=... (Max 20 minutes)"
                v-model="videoLink"
                :class="{ 'border-success': isValidVideoUrl && videoLink, 'border-danger': videoLink && !isValidVideoUrl }"
              />
            </div>
            <div class="mt-2">
              <div v-if="videoLink && isValidVideoUrl" class="text-success small">
                <i class="fas fa-check-circle me-1"></i>
                Valid video URL detected
              </div>
              <div v-else-if="videoLink && !isValidVideoUrl" class="text-danger small">
                <i class="fas fa-exclamation-triangle me-1"></i>
                Please enter a valid YouTube or video URL
              </div>
              <div class="text-secondary small mt-1">
                <i class="fas fa-info-circle me-1"></i>
                Supported: YouTube, Vimeo, and direct video links (Max duration: 20 minutes)
              </div>
            </div>
          </div>

          <button
            class="btn w-100 btn-lg btn-gradient-success fw-bold shadow-sm"
            :disabled="!videoLink.trim() || !isValidVideoUrl || isSending"
            @click="sendVideoLinkToBackend"
          >
            <span
              v-if="isSending"
              class="spinner-border spinner-border-sm me-2"
              role="status"
              aria-hidden="true"
            ></span>
            <i v-else class="fas fa-magic me-2"></i>
            <span v-if="!isSending">Generate Flashcards</span>
            <span v-else>Processing Video...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Flashcard Viewing Component -->
    <div
      v-if="activeView === 'viewingFlashcards'"
      class="main-content bg-gradient-dark text-white rounded-4 shadow-lg animate__animated animate__fadeIn p-4 p-md-5"
    >
      <div v-if="!currentDeckId" class="text-center mb-4">
        <i class="fas fa-star text-warning mb-3" style="font-size: 3rem;"></i>
        <h2 class="h3 fw-bold text-white mb-2">Flashcards Generated! ✨</h2>
        <p class="lead text-light opacity-75">Save this deck to access it later</p>
        <div class="row justify-content-center mt-4">
          <div class="col-12 col-md-6">
            <div class="input-group">
              <input
                v-model="newDeckName"
                type="text"
                class="form-control bg-dark text-white border-secondary"
                placeholder="Enter deck name"
                @keyup.enter="saveFlashcards"
              />
              <button
                @click="saveFlashcards"
                :disabled="!newDeckName.trim()"
                class="btn btn-warning fw-bold"
              >
                <i class="fas fa-save me-1"></i>Save
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="flashcards.length > 0" class="flashcard-viewer">
        <div class="text-center mb-4">
          <h3 class="h4 fw-bold">
            <span v-if="!currentDeckId" class="text-primary">New Deck Preview</span>
            <span v-else class="text-warning">{{ currentDeckName }}</span>
          </h3>
          <p class="text-light opacity-75">
            Card {{ currentFlashcardIndex + 1 }} of {{ flashcards.length }}
          </p>
          <div class="progress mb-3" style="height: 6px;">
            <div 
              class="progress-bar bg-gradient-primary" 
              role="progressbar" 
              :style="{ width: ((currentFlashcardIndex + 1) / flashcards.length) * 100 + '%' }"
            ></div>
          </div>
        </div>

        <div class="flashcard-container mb-4">
          <div class="flashcard shadow-lg" :class="{ 'is-flipped': isFlipped }" @click="flipCard">
            <div class="flashcard-face flashcard-front">
              <div class="card-content">
                <div class="card-type-indicator">
                  <i class="fas fa-question-circle"></i>
                  <span>Question</span>
                </div>
                <h4 class="fw-bold mb-0">{{ flashcards[currentFlashcardIndex].question }}</h4>
              </div>
            </div>
            <div class="flashcard-face flashcard-back">
              <div class="card-content">
                <div class="card-type-indicator">
                  <i class="fas fa-lightbulb"></i>
                  <span>Answer</span>
                </div>
                <p class="lead mb-0">{{ flashcards[currentFlashcardIndex].answer }}</p>
              </div>
            </div>
          </div>
          <div class="text-center mt-3">
            <small class="text-light opacity-75">
              <i class="fas fa-hand-pointer me-1"></i>Click card to flip
            </small>
          </div>
        </div>

        <div class="card-navigation d-flex justify-content-between align-items-center mb-4">
          <button
            @click="prevCard"
            :disabled="currentFlashcardIndex === 0"
            class="btn btn-outline-light d-flex align-items-center"
          >
            <i class="fas fa-chevron-left me-2"></i>Previous
          </button>
          
          <div class="card-dots d-flex gap-2">
            <span 
              v-for="(card, index) in flashcards" 
              :key="index"
              class="dot"
              :class="{ active: index === currentFlashcardIndex }"
              @click="goToCard(index)"
            ></span>
          </div>

          <button
            @click="nextCard"
            :disabled="currentFlashcardIndex === flashcards.length - 1"
            class="btn btn-warning d-flex align-items-center"
          >
            Next<i class="fas fa-chevron-right ms-2"></i>
          </button>
        </div>

        <!-- Add New Card Section -->
        <div class="add-card-section border-top border-secondary pt-4">
          <h4 class="h5 fw-bold mb-3 text-center">
            <i class="fas fa-plus-circle me-2"></i>Add New Flashcard
          </h4>
          <form @submit.prevent="addNewCard" class="row g-3">
            <div class="col-12 col-md-6">
              <label class="form-label text-light fw-semibold">Question</label>
              <textarea
                v-model="newCard.question"
                class="form-control bg-dark text-white border-secondary"
                rows="3"
                placeholder="Enter your question..."
                required
              ></textarea>
            </div>
            <div class="col-12 col-md-6">
              <label class="form-label text-light fw-semibold">Answer</label>
              <textarea
                v-model="newCard.answer"
                class="form-control bg-dark text-white border-secondary"
                rows="3"
                placeholder="Enter the answer..."
                required
              ></textarea>
            </div>
            <div class="col-12 text-center">
              <button
                type="submit"
                :disabled="!newCard.question.trim() || !newCard.answer.trim()"
                class="btn btn-gradient-success fw-bold"
              >
                <i class="fas fa-plus me-2"></i>Add Card to Deck
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Rename Deck Modal -->
    <div
      v-if="activeView === 'renamingDeck'"
      class="modal-overlay"
      @click="cancelRename"
    >
      <div class="modal-content bg-gradient-dark text-white rounded-4 shadow-lg p-4" @click.stop>
        <div class="text-center mb-4">
          <i class="fas fa-edit text-warning mb-3" style="font-size: 2rem;"></i>
          <h3 class="h4 fw-bold">Rename Deck</h3>
          <p class="text-light opacity-75">{{ currentDeckName }}</p>
        </div>
        <div class="mb-4">
          <label class="form-label text-light fw-semibold">New Name</label>
          <input
            v-model="newDeckName"
            type="text"
            class="form-control bg-dark text-white border-secondary"
            placeholder="Enter new deck name"
            @keyup.enter="confirmRename"
            ref="renameInput"
          />
        </div>
        <div class="d-flex gap-3 justify-content-center">
          <button
            @click="confirmRename"
            :disabled="!newDeckName.trim()"
            class="btn btn-success px-4"
          >
            <i class="fas fa-check me-1"></i>Confirm
          </button>
          <button @click="cancelRename" class="btn btn-outline-secondary px-4">
            <i class="fas fa-times me-1"></i>Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Error/Success Messages -->
    <div v-if="uploadMessage" class="toast-message" :class="{ 'success': !uploadMessage.includes('error'), 'error': uploadMessage.includes('error') }">
      <div class="toast-content">
        <i :class="uploadMessage.includes('error') ? 'fas fa-exclamation-circle' : 'fas fa-check-circle'"></i>
        <span>{{ uploadMessage }}</span>
        <button @click="uploadMessage = ''" class="toast-close">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from "vue";

// --- STATE MANAGEMENT ---
const fileInput = ref(null);
const imageInput = ref(null);
const renameInput = ref(null);
const currentFile = ref(null);
const currentImage = ref(null);
const imagePreview = ref(null);
const fileError = ref("");
const imageError = ref("");
const isSending = ref(false);
const uploadMessage = ref("");
const flashcards = ref([]);
const currentFlashcardIndex = ref(0);
const isFlipped = ref(false);
const decks = ref([]);
const newDeckName = ref("");
const currentDeckId = ref(null);
const currentDeckName = ref("");
const newCard = ref({ question: "", answer: "" });
const storedUser = JSON.parse(localStorage.getItem("user"));
const token = localStorage.getItem("auth_token");
const userId = storedUser ? storedUser.id : null;

// View state - default to 'decks'
const activeView = ref("decks");

// Input states
const textInput = ref("");
const videoLink = ref("");

// --- COMPUTED PROPERTIES ---
const wordCount = computed(() => {
  return textInput.value.trim().split(/\s+/).filter(word => word.length > 0).length;
});

const isValidVideoUrl = computed(() => {
  if (!videoLink.value) return false;
  const urlPattern = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be|vimeo\.com|.*\.(mp4|webm|ogg|avi|mov|wmv|flv|mkv)).*$/i;
  return urlPattern.test(videoLink.value);
});

// --- WATCHERS ---
watch(uploadMessage, (newMessage) => {
  if (newMessage) {
    setTimeout(() => {
      uploadMessage.value = "";
    }, 5000);
  }
});

// --- LIFECYCLE HOOKS ---
onMounted(() => {
  fetchDecks();
});

// --- VIEW MANAGEMENT ---
const setActiveView = (view) => {
  activeView.value = view;
  resetErrors();
  if (view === 'decks') {
    fetchDecks();
  }
};

const resetErrors = () => {
  fileError.value = "";
  imageError.value = "";
  uploadMessage.value = "";
};

// --- API FUNCTIONS ---
const fetchDecks = async () => {
  try {
    const response = await fetch(`/api/decks/user/${userId}`, { 
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const result = await response.json();
    if (response.ok) {
      decks.value = result.decks;
    } else {
      console.error("Failed to fetch decks:", result.error);
    }
  } catch (error) {
    console.error("Failed to fetch decks:", error);
  }
};

const sendTextToBackend = async () => {
  if (!textInput.value.trim() || wordCount.value > 1000 || isSending.value || !userId) return;

  isSending.value = true;
  try {
    const response = await fetch(`/api/generate_from_text/${userId}`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ text: textInput.value }),
    });
    const result = await response.json();
    if (response.ok) {
      flashcards.value = result.flashcards;
      activeView.value = "viewingFlashcards";
      newDeckName.value = "Text Flashcards";
      uploadMessage.value = `Generated ${result.flashcards.length} flashcards from video!`;
    } else {
      uploadMessage.value = result.error || "Failed to generate flashcards from video.";
    }
  } catch (error) {
    uploadMessage.value = "Network error. Please check your connection.";
  } finally {
    isSending.value = false;
  }
};

const sendImageToBackend = async () => {
  if (!currentImage.value || imageError.value || isSending.value || !userId) return;
  
  isSending.value = true;
  const formData = new FormData();
  formData.append("file", currentImage.value);
  
  try {
    const response = await fetch(`/api/generate_from_image/${userId}`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`
      },
      body: formData,
    });
    const result = await response.json();
    if (response.ok) {
      if (result.flashcards && result.flashcards.length > 0) {
        flashcards.value = result.flashcards;
        currentDeckId.value = null;
        newDeckName.value = "Image Flashcards";
        activeView.value = "viewingFlashcards";
        uploadMessage.value = `Generated ${result.flashcards.length} flashcards from image!`;
      } else {
        uploadMessage.value = result.message || "No flashcards generated from image.";
      }
    } else {
      uploadMessage.value = result.error || "Failed to process image.";
    }
  } catch (error) {
    uploadMessage.value = "Network error. Please check your connection.";
  } finally {
    isSending.value = false;
  }
};

const sendToBackend = async () => {
  if (!currentFile.value || fileError.value || isSending.value) return;
  
  isSending.value = true;
  const formData = new FormData();
  formData.append("file", currentFile.value);

  try {
    const response = await fetch("/api/upload_notes", { 
      method: "POST", 
      body: formData,
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });
    const result = await response.json();
    if (response.ok) {
      if (result.flashcards && result.flashcards.length > 0) {
        flashcards.value = result.flashcards;
        currentDeckId.value = null;
        newDeckName.value = "Document Flashcards";
        activeView.value = "viewingFlashcards";
        uploadMessage.value = `Generated ${result.flashcards.length} flashcards from document!`;
      } else {
        uploadMessage.value = result.message || "No flashcards generated from document.";
      }
    } else {
      uploadMessage.value = result.error || "Failed to process document.";
    }
  } catch (error) {
    uploadMessage.value = "Network error. Please check your connection.";
  } finally {
    isSending.value = false;
  }
};

const sendVideoLinkToBackend = async () => {
  if (!videoLink.value.trim() || !isValidVideoUrl.value || isSending.value || !userId) {
    uploadMessage.value = "Please enter a valid video URL.";
    return;
  }

  isSending.value = true;
  try {
    const response = await fetch(`/api/generate_from_video/${userId}`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ url: videoLink.value }),
    });
    const result = await response.json();
    
    if (response.ok) {
      if (result.flashcards && result.flashcards.length > 0) {
        flashcards.value = result.flashcards;
        currentDeckId.value = null;
        newDeckName.value = "Video Flashcards";
        activeView.value = "viewingFlashcards";
        uploadMessage.value = result.message || `Generated ${result.flashcards.length} flashcards from video!`;
      } else {
        uploadMessage.value = result.message || "No flashcards generated from video.";
      }
    } else {
      uploadMessage.value = result.error || "Failed to generate flashcards from video.";
    }
  } catch (error) {
    console.error("Network or server error:", error);
    uploadMessage.value = "Network error. Please check your connection.";
  } finally {
    isSending.value = false;
  }
};

const saveFlashcards = async () => {
  if (!newDeckName.value.trim() || !flashcards.value.length) return;
  
  try {
    const response = await fetch("/api/decks", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({
        name: newDeckName.value,
        cards: flashcards.value,
      }),
    });
    if (response.ok) {
      await fetchDecks();
      resetState();
      uploadMessage.value = `Deck "${newDeckName.value}" saved successfully!`;
      activeView.value = "decks";
    } else {
      const err = await response.json();
      throw new Error(err.error || "Failed to save deck.");
    }
  } catch (error) {
    console.error(error);
    uploadMessage.value = error.message;
  }
};

const addNewCard = async () => {
  if (!flashcards.value || flashcards.value.length === 0) {
    uploadMessage.value = "You must have a deck to add cards to. Please generate or load one first.";
    return;
  }
  if (!newCard.value.question.trim() || !newCard.value.answer.trim()) {
    return;
  }
  
  const addedCard = { ...newCard.value };
  flashcards.value.push(addedCard);
  newCard.value = { question: "", answer: "" };

  if (currentDeckId.value) {
    try {
      const response = await fetch(`/api/decks/${currentDeckId.value}/cards`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(addedCard),
      });

      if (!response.ok) {
        flashcards.value.pop();
        const err = await response.json();
        throw new Error(err.error || "Failed to save new card to the backend.");
      }
      uploadMessage.value = "New card added successfully!";
    } catch (error) {
      console.error(error);
      uploadMessage.value = "Error saving new card.";
    }
  } else {
    uploadMessage.value = "New card added locally! Save the deck to persist this card.";
  }
};

// --- DECK MANAGEMENT ---
const viewDeck = async (deck) => {
  try {
    const response = await fetch(`/api/decks/${deck.id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const result = await response.json();
    if (response.ok) {
      flashcards.value = result.cards;
      currentDeckId.value = deck.id;
      currentDeckName.value = deck.name;
      currentFlashcardIndex.value = 0;
      isFlipped.value = false;
      activeView.value = "viewingFlashcards";
    }
  } catch (error) {
    console.error("Failed to fetch deck cards:", error);
    uploadMessage.value = "Failed to load deck cards.";
  }
};

const renameDeck = (deck) => {
  currentDeckId.value = deck.id;
  currentDeckName.value = deck.name;
  newDeckName.value = deck.name;
  activeView.value = "renamingDeck";
  nextTick(() => {
    renameInput.value?.focus();
  });
};

const confirmRename = async () => {
  if (!newDeckName.value.trim()) return;
  
  try {
    const response = await fetch(`/api/decks/${currentDeckId.value}`, {
      method: "PUT",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ name: newDeckName.value }),
    });
    if (response.ok) {
      await fetchDecks();
      uploadMessage.value = `Deck renamed to "${newDeckName.value}" successfully!`;
      resetState();
      activeView.value = "decks";
    } else {
      const err = await response.json();
      uploadMessage.value = err.error || "Failed to rename deck.";
    }
  } catch (error) {
    console.error("Failed to rename deck:", error);
    uploadMessage.value = "Network error while renaming deck.";
  }
};

const cancelRename = () => {
  resetState();
  activeView.value = "decks";
};

const deleteDeck = async (deck) => {
  if (confirm(`Are you sure you want to delete the deck "${deck.name}"? This action cannot be undone.`)) {
    try {
      const response = await fetch(`/api/decks/${deck.id}`, { 
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      if (response.ok) {
        await fetchDecks();
        uploadMessage.value = `Deck "${deck.name}" deleted successfully.`;
      } else {
        const err = await response.json();
        uploadMessage.value = err.error || "Failed to delete deck.";
      }
    } catch (error) {
      console.error("Failed to delete deck:", error);
      uploadMessage.value = "Network error while deleting deck.";
    }
  }
};

// --- FILE HANDLING ---
const onFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    validateAndSetFile(file);
  }
  e.target.value = '';
};

const onDrop = (e) => {
  const file = e.dataTransfer.files[0];
  if (file) {
    validateAndSetFile(file);
  }
};

const validateAndSetFile = (file) => {
  fileError.value = "";
  
  // Check file type
  if (file.type !== 'application/pdf') {
    fileError.value = "Only PDF files are supported.";
    return;
  }
  
  // Check file size (5MB limit)
  if (file.size > 5 * 1024 * 1024) {
    fileError.value = "File size must be less than 5MB.";
    return;
  }
  
  currentFile.value = file;
};

const removeFile = () => {
  currentFile.value = null;
  fileError.value = "";
};

// --- IMAGE HANDLING ---
const onImageChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    validateAndSetImage(file);
  }
  e.target.value = '';
};

const onImageDrop = (e) => {
  const file = e.dataTransfer.files[0];
  if (file) {
    validateAndSetImage(file);
  }
};

const validateAndSetImage = (file) => {
  imageError.value = "";
  
  // Check file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
  if (!allowedTypes.includes(file.type)) {
    imageError.value = "Only JPEG, PNG, GIF, BMP, and WebP images are supported.";
    return;
  }
  
  // Check file size (5MB limit)
  if (file.size > 5 * 1024 * 1024) {
    imageError.value = "Image size must be less than 5MB.";
    return;
  }
  
  currentImage.value = file;
  
  // Create preview
  const reader = new FileReader();
  reader.onload = (e) => {
    imagePreview.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

const removeImage = () => {
  currentImage.value = null;
  imagePreview.value = null;
  imageError.value = "";
};

// --- FLASHCARD NAVIGATION ---
const flipCard = () => {
  isFlipped.value = !isFlipped.value;
};

const nextCard = () => {
  if (currentFlashcardIndex.value < flashcards.value.length - 1) {
    currentFlashcardIndex.value++;
    isFlipped.value = false;
  }
};

const prevCard = () => {
  if (currentFlashcardIndex.value > 0) {
    currentFlashcardIndex.value--;
    isFlipped.value = false;
  }
};

const goToCard = (index) => {
  currentFlashcardIndex.value = index;
  isFlipped.value = false;
};

// --- UTILITY FUNCTIONS ---
const resetState = () => {
  currentFile.value = null;
  currentImage.value = null;
  imagePreview.value = null;
  fileError.value = "";
  imageError.value = "";
  isSending.value = false;
  flashcards.value = [];
  currentFlashcardIndex.value = 0;
  isFlipped.value = false;
  currentDeckId.value = null;
  currentDeckName.value = "";
  newDeckName.value = "";
  newCard.value = { question: "", answer: "" };
  textInput.value = "";
  videoLink.value = "";
};
</script>

<style scoped>
/* Import Font Awesome */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

/* CSS Custom Properties - Updated to match parent dashboard */
:root {
  --primary-color: #ff5722;
  --secondary-color: #bbb;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #dc3545;
  --info-color: #06b6d4;
  --dark-color: #181818;
  --darker-color: #0d0d0d;
  --sidebar-color: #1a1a1a;
}

/* Global Styles */
.container-fluid {
  max-width: 1400px;
  margin: 0 auto;
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Background Gradients */
.bg-gradient-dark {
  background: var(--dark-color);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.3);
}

.main-content {
  min-height: 500px;
  position: relative;
  color: #fff;
}

/* Toggle Navigation */
.toggle-group {
  position: relative;
  display: flex;
  background: var(--sidebar-color);
  border: 2px solid rgba(255, 255, 255, 0.1);
  padding: 6px;
  border-radius: 50px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
}

.toggle-group::before {
  content: '';
  position: absolute;
  top: 6px;
  bottom: 6px;
  background: linear-gradient(135deg, var(--primary-color) 0%, #e64a19 100%);
  border-radius: 50px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 15px rgba(255, 87, 34, 0.4);
  z-index: 0;
}

/* Toggle positioning for 5 buttons */
.toggle-group[data-active="decks"]::before {
  left: 6px;
  width: calc(20% - 2px);
  transform: translateX(0%);
}
.toggle-group[data-active="text"]::before {
  left: 6px;
  width: calc(20% - 2px);
  transform: translateX(100%);
}
.toggle-group[data-active="document"]::before {
  left: 6px;
  width: calc(20% - 2px);
  transform: translateX(200%);
}
.toggle-group[data-active="image"]::before {
  left: 6px;
  width: calc(20% - 2px);
  transform: translateX(300%);
}
.toggle-group[data-active="video"]::before {
  left: 6px;
  width: calc(20% - 2px);
  transform: translateX(400%);
}

.toggle-btn {
  background: transparent;
  color: #bbb;
  border: none;
  font-weight: 600;
  flex: 1;
  padding: 12px 16px;
  transition: all 0.3s ease;
  z-index: 1;
  position: relative;
  border-radius: 50px;
  font-size: 0.9rem;
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.toggle-btn:hover {
  color: #fff;
  transform: translateY(-1px);
}

.btn-active {
  color: #ffffff !important;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* Responsive toggle */
@media (max-width: 768px) {
  .toggle-btn {
    font-size: 0.8rem;
    padding: 10px 8px;
  }
  .toggle-btn i {
    display: block;
    margin-bottom: 2px;
  }
  .toggle-btn .me-2 {
    margin-right: 0 !important;
  }
}

/* Button Gradients */
.btn-gradient-success {
  background: linear-gradient(135deg, var(--success-color) 0%, #059669 100%);
  border: none;
  color: white;
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
  transition: all 0.3s ease;
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.btn-gradient-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
  color: white;
}

.btn-gradient-primary {
  background: linear-gradient(135deg, var(--primary-color) 0%, #e64a19 100%);
  font-weight: 500;
  border: none;
  color: white;
  transition: all 0.3s ease;
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.btn-gradient-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 25px rgba(255, 87, 34, 0.4);
  color: white;
}

/* Upload Areas */
.upload-area {
  transition: all 0.3s ease;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--darker-color);
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.upload-area:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}

.hover-glow:hover {
  box-shadow: 0 0 30px rgba(255, 87, 34, 0.3);
}

.upload-placeholder i {
  transition: all 0.3s ease;
  color: #bbb;
}

.upload-area:hover .upload-placeholder i {
  transform: scale(1.1);
  color: var(--primary-color);
}

/* Deck Cards */
.deck-card {
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: var(--sidebar-color);
  border-radius: 10px;
}

.hover-lift:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
}

/* Flashcard Styles */
.flashcard-container {
  perspective: 1000px;
  height: 400px;
  margin: 2rem auto;
  max-width: 600px;
}

.flashcard {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  transform-style: preserve-3d;
  cursor: pointer;
  border-radius: 10px;
}

.flashcard.is-flipped {
  transform: rotateY(180deg);
}

.flashcard-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
}

.flashcard-front {
  background: var(--sidebar-color);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.flashcard-back {
  background: var(--warning-color);
  color: white;
  transform: rotateY(180deg);
  border: 2px solid var(--warning-color);
}

.card-content {
  text-align: center;
  width: 100%;
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.card-type-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  opacity: 0.7;
  font-size: 0.9rem;
  font-weight: 600;
}

/* Card Navigation */
.card-dots {
  display: flex;
  gap: 8px;
  align-items: center;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
}

.dot.active {
  background: var(--primary-color);
  transform: scale(1.3);
  box-shadow: 0 0 10px rgba(255, 87, 34, 0.5);
}

.dot:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: scale(1.1);
}

/* Progress Bar */
.progress {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar {
  background: linear-gradient(90deg, var(--primary-color) 0%, #e64a19 100%);
  border-radius: 10px;
  transition: width 0.6s ease;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  min-width: 400px;
  max-width: 90vw;
  animation: slideInUp 0.3s ease;
  background: var(--dark-color);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Toast Messages */
.toast-message {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1100;
  animation: slideInRight 0.3s ease;
  max-width: 400px;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 10px;
  color: white;
  font-weight: 500;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.toast-message.success .toast-content {
  background: linear-gradient(135deg, var(--success-color) 0%, #059669 100%);
}

.toast-message.error .toast-content {
  background: linear-gradient(135deg, var(--danger-color) 0%, #dc2626 100%);
}

.toast-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0;
  margin-left: auto;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.toast-close:hover {
  opacity: 1;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Form Enhancements */
.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem rgba(255, 87, 34, 0.25);
}

.form-control.bg-dark {
  background-color: var(--darker-color) !important;
  border-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.form-control.bg-dark:focus {
  background-color: var(--darker-color) !important;
  border-color: var(--primary-color);
}

/* Responsive Design */
@media (max-width: 768px) {
  .flashcard-container {
    height: 300px;
    margin: 1rem auto;
  }
  
  .flashcard-face {
    padding: 1.5rem;
  }
  
  .main-content {
    margin: 0 10px;
  }
  
  .toggle-group {
    flex-wrap: nowrap;
    overflow-x: auto;
  }
  
  .modal-content {
    margin: 20px;
    min-width: auto;
  }
}

@media (max-width: 576px) {
  .card-dots {
    max-width: 200px;
    overflow-x: auto;
    justify-content: flex-start;
  }
  
  .flashcard-container {
    height: 250px;
  }
  
  .upload-area {
    min-height: 200px;
  }
}

/* Custom Scrollbars */
.card-dots::-webkit-scrollbar {
  height: 4px;
}

.card-dots::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.card-dots::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}

/* Loading States */
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .flashcard,
  .toggle-group::before,
  .hover-lift,
  .upload-area {
    transition: none;
  }
  
  .animate__animated {
    animation: none;
  }
}

/* Focus styles for better accessibility */
.btn:focus,
.form-control:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}
</style>