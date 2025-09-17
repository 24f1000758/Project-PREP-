<template>
  <div class="chat-container">
    <div v-if="!chatActive" class="welcome-text">
      Welcome to PrepAI
    </div>

    <div v-else class="chat-area" ref="chatArea">
      <div
        v-for="(msg, i) in chatMessages"
        :key="i"
        :class="['chat-message', msg.sender]"
      >
        <div v-if="msg.sender === 'user'" class="message-text">
          {{ msg.text }}
        </div>

        <div v-else-if="msg.sender === 'ai'" class="ai-block">
          <div
            class="message-text"
            v-html="renderMarkdown(msg.text)"
          ></div>

          <div class="bot-actions">
            <i class="bi bi-volume-up action-icon" title="Speak" @click="speak(msg.text)"></i>
            <i class="bi bi-clipboard action-icon" title="Copy" @click="copyText(msg.text)"></i>
            <i class="bi bi-hand-thumbs-up action-icon" title="Like"></i>
            <i class="bi bi-hand-thumbs-down action-icon" title="Dislike"></i>
            <i v-if="speaking" class="bi bi-stop-circle action-icon stop-icon" title="Stop" @click="stopSpeaking"></i>
          </div>
        </div>
      </div>

      <div v-if="isTyping" class="chat-message ai typing">
        <span></span><span></span><span></span>
      </div>
    </div>

    <div class="input-area">
      <input
        v-model="command"
        @keyup.enter="submitCommand"
        type="text"
        placeholder="Message PrepAI..."
        class="command-input"
      />
      <button class="send-btn" @click="submitCommand">➤</button>
      <button class="clear-btn" @click="clearchat">🗑️</button>
    </div>
  </div>
</template>

<script>
import MarkdownIt from "markdown-it";

export default {
  data() {
    return {
      command: "",
      chatMessages: [],
      chatActive: false,
      isTyping: false,
      sessionId: localStorage.getItem("chat_session") || Date.now().toString(),
      // FIX: Configure MarkdownIt to handle lists and paragraphs correctly
      md: new MarkdownIt({
        html: true,
        breaks: true,
        linkify: true
      }),
      speaking: false,
      voices: [],
      selectedVoice: null,
    };
  },
  created() {
    const savedLogs = JSON.parse(localStorage.getItem("chat_logs") || "[]");
    if (savedLogs.length > 0) {
      this.chatMessages = savedLogs;
      this.chatActive = true;
      this.scrollToBottom();
    }
  },
  mounted() {
    this.loadVoices();
    window.speechSynthesis.onvoiceschanged = this.loadVoices;
  },
  methods: {
    renderMarkdown(text) {
      // Return the rendered markdown without extra p tags
      const renderedHtml = this.md.render(text || "");
      // FIX: Replace <p> tags with nothing, leaving the content
      return renderedHtml.replace(/<p>/g, '').replace(/<\/p>/g, '');
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const chatArea = this.$refs.chatArea;
        if (chatArea) chatArea.scrollTop = chatArea.scrollHeight;
      });
    },
    async submitCommand() {
      if (this.command.trim() === "") return;
      if (!this.chatActive) {
        this.chatActive = true;
        this.scrollToBottom();
      }

      const user = JSON.parse(localStorage.getItem("user") || "{}");
      const userInfo = {
        full_name: user.full_name || "there",
        email: user.email || null,
        phone: user.phone || null,
        id: user.id || null
      };

      const question = this.command;
      const userEntry = {
        sender: "user",
        text: question,
        username: user.full_name || "guest",
        user_id: user.id || null,
        timestamp: new Date().toISOString(),
        session_id: this.sessionId,
      };
      this.chatMessages.push(userEntry);
      this.saveToLocal();

      this.command = "";
      this.isTyping = true;
      this.scrollToBottom();

      const botEntry = {
        sender: "ai",
        text: "",
        timestamp: new Date().toISOString(),
        intent: "unknown",
        confidence: null,
        session_id: this.sessionId,
      };
      this.chatMessages.push(botEntry);

      try {
        const response = await fetch("/api/query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_input: question,
            user_info: userInfo, 
            conversation_history: this.chatMessages.slice(0, -2).map(msg => {
              const role = msg.sender === 'user' ? 'user' : 'assistant';
              return { role: role, content: msg.text };
            })
          }),
        });

        if (!response.body) throw new Error("Stream not available");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let currentChunk;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          currentChunk = decoder.decode(value, { stream: true });
          this.chatMessages[this.chatMessages.length - 1].text += currentChunk; 
          this.scrollToBottom();
        }
        
        const lastMessage = this.chatMessages[this.chatMessages.length - 1];
        lastMessage.text = lastMessage.text.replace('[[END]]', '').trim();
      } catch (error) {
        console.error("Error during streaming fetch:", error);
        const errEntry = {
          sender: "ai",
          text: "⚠️ Error connecting to API or streaming response.",
          timestamp: new Date().toISOString(),
          intent: "unknown",
          confidence: null,
          session_id: this.sessionId,
        };
        this.chatMessages.pop();
        this.chatMessages.push(errEntry);
      } finally {
        this.isTyping = false;
        this.saveToLocal();
        this.scrollToBottom();
      }
    },
    saveToLocal() {
      localStorage.setItem("chat_logs", JSON.stringify(this.chatMessages));
      localStorage.setItem("chat_session", this.sessionId);
    },
    clearchat() {
      this.chatMessages = [];
      localStorage.removeItem("chat_logs");
      this.chatActive = false;
    },
    loadVoices() {
      this.voices = window.speechSynthesis.getVoices();
      const ukMale = this.voices.find(v => v.name === "Google UK English Male");
      if (ukMale) {
        this.selectedVoice = ukMale.name;
      } else {
        const enVoice = this.voices.find(v => v.lang.startsWith("en"));
        this.selectedVoice = enVoice ? enVoice.name : (this.voices[0]?.name || null);
      }
    },
    speak(text) {
      if (!text) return;
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      const voice = this.voices.find(v => v.name === this.selectedVoice);
      if (voice) utterance.voice = voice;
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.onstart = () => { this.speaking = true; };
      utterance.onend = () => { this.speaking = false; };
      window.speechSynthesis.speak(utterance);
    },
    stopSpeaking() {
      window.speechSynthesis.cancel();
      this.speaking = false;
    },
    copyText(text) {
      navigator.clipboard.writeText(text)
        .then(() => console.log("Copied:", text))
        .catch(err => console.error("Copy failed:", err));
    }
  },
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #181818;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  box-shadow: 3px 0 15px rgba(0, 0, 0, 0.6);
}

.clear-btn {
  margin-left: 8px;
  background: #ff5722;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s ease, transform 0.2s ease;
  font-weight: 500;
}

.clear-btn:hover {
  background: #e64a19;
  transform: scale(1.05);
}

.welcome-text {
  margin: auto;
  font-size: 1.6rem;
  font-weight: 700;
  color: #bbb;
  text-align: center;
  padding: 20px;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  scroll-behavior: smooth;
}

.chat-message {
  display: flex;
  margin: 6px 0;
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.5;
  word-break: break-word;
  font-size: 0.95rem;
  transition: background-color 0.3s ease;
}

.chat-message.user {
  background: #ff5722;
  color: #fff;
  align-self: flex-end;
  border-bottom-right-radius: 4px;
  font-weight: 500;
}

.chat-message.ai {
  background: #1a1a1a;
  color: #fff;
  align-self: flex-start;
  border-bottom-left-radius: 4px;
  flex-direction: column;
  align-items: flex-start;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.bot-actions {
  margin-top: 6px;
  display: flex;
  gap: 10px;
  font-size: 1.1rem;
  color: #888;
}

.action-icon {
  cursor: pointer;
  transition: color 0.3s ease, transform 0.2s ease;
}

.action-icon:hover {
  color: #ff5722;
  transform: scale(1.1);
}

.stop-icon {
  color: #ff5722;
}

.stop-icon:hover {
  color: #e64a19;
}

.typing {
  background: #1a1a1a;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.typing span {
  height: 6px;
  width: 6px;
  margin: 0 2px;
  background: #888;
  display: inline-block;
  border-radius: 50%;
  animation: blink 1.2s infinite both;
}

.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0%, 80%, 100% { opacity: 0; }
  40% { opacity: 1; }
}

.input-area {
  padding: 10px;
  display: flex;
  align-items: center;
  background: #0d0d0d;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.command-input {
  flex: 1;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  background: #1a1a1a;
  color: #fff;
  font-size: 0.95rem;
  outline: none;
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  transition: border-color 0.3s ease, background-color 0.3s ease;
}

.command-input:focus {
  border-color: #ff5722;
  background: rgba(255, 255, 255, 0.05);
}

.command-input::placeholder {
  color: #888;
}

.send-btn {
  margin-left: 8px;
  background: #ff5722;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s ease, transform 0.2s ease;
  font-weight: 500;
}

.send-btn:hover {
  background: #e64a19;
  transform: scale(1.05);
}

/* Scrollbar */
.chat-area::-webkit-scrollbar {
  width: 8px;
}

.chat-area::-webkit-scrollbar-thumb {
  background: #1a1a1a;
  border-radius: 4px;
  transition: background 0.3s ease;
}

.chat-area::-webkit-scrollbar-thumb:hover {
  background: #ff5722;
}

.chat-area::-webkit-scrollbar-track {
  background: #0d0d0d;
}

@media (max-width: 768px) {
  .chat-area {
    padding: 10px;
  }
  
  .chat-message {
    max-width: 100%;
    font-size: 0.9rem;
    padding: 8px 12px;
  }
  
  .welcome-text {
    font-size: 1.25rem;
  }
  
  .command-input {
    font-size: 0.9rem;
    padding: 8px;
  }
  
  .send-btn, .clear-btn {
    padding: 6px 10px;
    font-size: 0.95rem;
  }
}
</style>