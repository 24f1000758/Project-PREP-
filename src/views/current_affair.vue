<template>
  <div class="news-container">
    <!-- Header -->
    <div class="text-center mb-5">
      <h1 class="fw-bold text-accent">📰 Current Affairs</h1>
      <p class="text-muted">Focused updates, exam-oriented only.</p>
    </div>

    <!-- Filters -->
    <div class="filters">
      <select v-model="selectedDomain" class="filter-select">
        <option v-for="domain in domains" :key="domain.value" :value="domain.value">
          {{ domain.icon }} {{ domain.text }}
        </option>
      </select>

      <select v-model="selectedTimePeriod" class="filter-select">
        <option v-for="period in timePeriods" :key="period.value" :value="period.value">
          {{ period.text }}
        </option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>Loading current affairs...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-box">
      <p><strong>Error:</strong> {{ error }}</p>
      <button class="retry-btn" @click="fetchCurrentAffairs">Retry</button>
    </div>

    <!-- No Data -->
    <div v-else-if="!hasCurrentAffairs" class="empty-box">
      No articles found.
    </div>

    <!-- Articles -->
    <div v-else class="articles">
      <div
        v-for="article in currentAffairs"
        :key="article.id"
        class="news-card"
        :class="{ 'read-card': article.read }"
      >
        <h5 class="news-title">{{ article.headline }}</h5>
        <p class="news-snippet">{{ article.explain.slice(0, 100) }}...</p>
        <div class="news-meta">
          <span>{{ article.domain }}</span>
          <span>{{ article.date }}</span>
        </div>
        <div class="button-row">
          <button class="read-btn" @click="openModal(article)">
            Read More →
          </button>
          <button
            class="mark-btn"
            @click="markAsRead(article)"
            :disabled="article.read"
          >
            {{ article.read ? "✔ Read" : "Mark as Read" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-backdrop">
      <div class="modal-box">
        <h4>{{ selectedArticle.headline }}</h4>
        <p class="mt-3">{{ selectedArticle.explain }}</p>
        <p class="small text-muted">
          📅 {{ selectedArticle.date }} | 🏷 {{ selectedArticle.domain }}
        </p>
        <button class="close-btn" @click="closeModal">Close</button>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, computed, watch, onMounted } from "vue";

const selectedDomain = ref("");
const selectedTimePeriod = ref("");
const currentAffairs = ref([]);
const isLoading = ref(true);
const error = ref(null);
const showModal = ref(false);
const selectedArticle = ref(null);

// --- store read articles in localStorage ---
const readArticles = ref(new Set());

const loadReadArticles = () => {
  const saved = localStorage.getItem("readArticles");
  if (saved) {
    try {
      readArticles.value = new Set(JSON.parse(saved));
    } catch (e) {
      readArticles.value = new Set();
    }
  }
};

const saveReadArticles = () => {
  localStorage.setItem(
    "readArticles",
    JSON.stringify(Array.from(readArticles.value))
  );
};

// --- All domains (from your JSON) ---
const domains = [
  { "value": "", "text": "All", "icon": "🌍" },
  { "value": "economy", "text": "Economy & Policy", "icon": "💼" },
  { "value": "governance", "text": "Polity & Governance", "icon": "🏛️" },
  { "value": "international", "text": "International Relations", "icon": "🌐" },
  { "value": "defence", "text": "Defence & Security", "icon": "🪖" },
  { "value": "environment", "text": "Environment & Ecology", "icon": "🌿" },
  { "value": "science", "text": "Science & Technology", "icon": "🔬" },
  { "value": "reports", "text": "Reports, Indices & Rankings", "icon": "📈" },
  { "value": "awards", "text": "Awards & Personalities", "icon": "🏆" },
  { "value": "schemes", "text": "Government Schemes & Initiatives", "icon": "✅" },
  { "value": "society", "text": "Society & Education", "icon": "🤝" },
  { "value": "health", "text": "Health & Demographics", "icon": "🏥" },
  { "value": "disaster", "text": "Environment & Disaster Management", "icon": "🌊" },
  { "value": "agriculture", "text": "Agriculture & Rural Development", "icon": "🌾" },
  { "value": "politics", "text": "Politics & Governance", "icon": "🗳️" },
  { "value": "sports", "text": "Sports", "icon": "🏅" },
  { "value": "culture", "text": "Culture & Heritage", "icon": "🎨" },
  { "value": "law", "text": "Law & Governance", "icon": "⚖️" },
  { "value": "exams", "text": "Exams & Recruitment", "icon": "✍️" }
];

// --- Time Filters ---
const timePeriods = [
  { value: "", text: "All" },
  { value: "today", text: "Today" },
  { value: "this-week", text: "This Week" },
  { value: "this-month", text: "This Month" },
];

const hasCurrentAffairs = computed(() => currentAffairs.value.length > 0);

const fetchCurrentAffairs = async () => {
  isLoading.value = true;
  error.value = null;

  try {
    const response = await fetch(`/api/current_affairs`);
    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const data = await response.json();
    let articles = data.current_affairs || [];

    // --- Filtering by domain ---
    if (selectedDomain.value) {
      articles = articles.filter((a) =>
        a.domain.toLowerCase().includes(selectedDomain.value.toLowerCase())
      );
    }

    // --- Filtering by date ---
    const today = new Date();
    articles = articles.filter((a) => {
      const articleDate = new Date(a.date);

      if (selectedTimePeriod.value === "today") {
        return (
          articleDate.toDateString() === today.toDateString()
        );
      }

      if (selectedTimePeriod.value === "this-week") {
        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() - today.getDay()); // Sunday
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6); // Saturday
        return articleDate >= weekStart && articleDate <= weekEnd;
      }

      if (selectedTimePeriod.value === "this-month") {
        return (
          articleDate.getMonth() === today.getMonth() &&
          articleDate.getFullYear() === today.getFullYear()
        );
      }

      return true; // no filter
    });

    currentAffairs.value = articles.map((article, index) => ({
      ...article,
      id: article.id ?? index,
      read: readArticles.value.has(article.id ?? index),
    }));
  } catch (e) {
    error.value = e.message || "Error fetching news";
    currentAffairs.value = [];
  } finally {
    isLoading.value = false;
  }
};

const openModal = (article) => {
  selectedArticle.value = article;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  selectedArticle.value = null;
};

// mark an article as read
const markAsRead = (article) => {
  article.read = true;
  readArticles.value.add(article.id);
  saveReadArticles();
};

watch([selectedDomain, selectedTimePeriod], fetchCurrentAffairs);

onMounted(() => {
  loadReadArticles();
  fetchCurrentAffairs();
});
</script>



<style scoped>
/* General dark theme */
.news-container {
  color: #f0f0f0;
  padding: 20px;
  background: #181818;
  min-height: 100vh;
  overflow-x: hidden;
}

/* Hide scrollbars but allow scroll */
.news-container::-webkit-scrollbar {
  display: none;
}
.news-container {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Header */
.text-accent {
  color: #ff7043;
}

/* Filters */
.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.filter-select {
  background: #222;
  border: 1px solid #444;
  color: #eee;
  padding: 8px 12px;
  border-radius: 6px;
  outline: none;
}

.filter-select:focus {
  border-color: #ff7043;
}

/* Loading Spinner */
.loading {
  text-align: center;
  margin-top: 50px;
}
.spinner {
  border: 4px solid #333;
  border-top: 4px solid #ff7043;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  animation: spin 1s linear infinite;
  margin: auto;
}
@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}

/* Error and Empty states */
.error-box,
.empty-box {
  text-align: center;
  padding: 20px;
  background: #2a2a2a;
  border-radius: 8px;
  margin: 20px auto;
}
.retry-btn {
  background: #ff7043;
  color: #fff;
  border: none;
  padding: 6px 14px;
  margin-top: 10px;
  border-radius: 5px;
  cursor: pointer;
}
.retry-btn:hover {
  background: #e64a19;
}

/* News Cards */
.articles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.news-card {
  background: #222;
  border: 1px solid #333;
  border-radius: 10px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.news-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(255, 112, 67, 0.3);
}
.news-card.read-card {
  opacity: 0.6;
  background: #2b2b2b;
  border-color: #444;
}

.news-title {
  font-size: 1.1rem;
  color: #fff;
  font-weight: 600;
}
.news-snippet {
  font-size: 0.9rem;
  color: #bbb;
  margin: 8px 0;
}
.news-meta {
  font-size: 0.8rem;
  color: #888;
  display: flex;
  justify-content: space-between;
}
.button-row {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
.read-btn,
.mark-btn {
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  border: none;
  font-size: 0.85rem;
}
.read-btn {
  background: #ff7043;
  color: #fff;
}
.read-btn:hover {
  background: #e64a19;
}
.mark-btn {
  background: #555;
  color: #fff;
}
.mark-btn:disabled {
  background: #2e7d32;
  cursor: not-allowed;
}
.mark-btn:not(:disabled):hover {
  background: #666;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(20, 20, 20, 0.9);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}
.modal-box {
  background: #222;
  padding: 2rem;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  box-shadow: 0 6px 20px rgba(255, 112, 67, 0.4);
  animation: fadeIn 0.3s ease-in-out;
}
.close-btn {
  background: #555;
  color: #fff;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
}
.close-btn:hover {
  background: #ff7043;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
