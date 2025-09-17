import os
import sys
import threading
import time
from flask import Blueprint, request, jsonify, Response, stream_with_context
from llama_cpp import Llama
import json
from rapidfuzz import fuzz, process
from datetime import datetime
import random
from dotenv import load_dotenv
import requests
import re
import uuid
import psutil  # For system monitoring

print("🔄 Loading environment variables...")
load_dotenv()
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if WEATHER_API_KEY:
    print("✅ Weather API key loaded successfully!")
else:
    print("⚠️ Warning: Weather API key not found in .env")

# --- Create the Blueprint instance ---
bot_bp = Blueprint('bot_bp', __name__)
print("✅ Flask Blueprint created!")

# --- Global constants and file paths ---
CHAT_LOG_FILE = "chat_logs.json"

# --- System Performance Monitoring ---
def get_system_info():
    """Get current system performance metrics"""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    return {
        "cpu_usage": cpu_percent,
        "memory_usage": memory.percent,
        "available_memory": memory.available // (1024**3),  # GB
    }

def optimize_for_hardware():
    """Auto-detect optimal settings based on hardware"""
    system = get_system_info()
    cpu_count = psutil.cpu_count()
    
    print(f"🖥️ System Info: CPU Usage: {system['cpu_usage']}%, Memory: {system['memory_usage']}%, Available RAM: {system['available_memory']}GB")
    
    # Optimize based on available resources
    if system['available_memory'] >= 8:  # 8GB+ RAM
        return {
            "n_threads": min(cpu_count, 8),
            "n_batch": 512,
            "n_gpu_layers": 0,  # Increase if you have GPU
            "use_mlock": True,
            "use_mmap": True,
        }
    elif system['available_memory'] >= 4:  # 4-8GB RAM
        return {
            "n_threads": min(cpu_count, 6),
            "n_batch": 256,
            "n_gpu_layers": 0,
            "use_mlock": False,
            "use_mmap": True,
        }
    else:  # Less than 4GB RAM
        return {
            "n_threads": min(cpu_count, 4),
            "n_batch": 128,
            "n_gpu_layers": 0,
            "use_mlock": False,
            "use_mmap": False,
        }

# --- Opening and reading the JSON files ---
try:
    with open("chats_dataset.json", "r", encoding="utf-8") as f:
        intents = json.load(f)["intents"]
    print("✅ chats_dataset.json loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load chats_dataset.json: {e}")
    intents = []

def find_intent(user_input, threshold=70):
    print(f"🔎 Running intent detection for: {user_input}")
    all_patterns = []
    for intent in intents:
        for p in intent["patterns"]:
            all_patterns.append((p, intent))

    if not all_patterns:
        print("⚠️ No patterns found in intents.json")
        return None, 0.0

    match, score, _ = process.extractOne(
        user_input,
        [p[0] for p in all_patterns],
        scorer=fuzz.token_sort_ratio
    )
    print(f"🔍 Best match: {match} (score={score})")

    if score >= threshold:
        for p, intent in all_patterns:
            if p == match:
                print(f"✅ Intent detected: {intent['tag']}")
                return intent, score
    print("❌ No matching intent found.")
    return None, 0.0

def get_time_of_day():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

def extract_city(user_input: str) -> str:
    print(f"🌍 Extracting city from input: {user_input}")
    match = re.search(r"(?:in|at|of)\s+([A-Za-z\s]+)", user_input, re.IGNORECASE)
    if match:
        city = match.group(1).strip()
        for bad in ["today", "yesterday", "now", "currently", "weather"]:
            city = city.replace(bad, "").strip()
        print(f"✅ City extracted: {city}")
        return city
    print("⚠️ No city found, defaulting to 'your location'")
    return "your location"

def get_weather(city: str):
    print(f"🌦 Fetching weather for city: {city}")
    if not WEATHER_API_KEY:
        return "Weather API key is missing. Please set it in your .env file."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        r = requests.get(url, timeout=5).json()
        if r.get("main"):
            temp = r["main"]["temp"]
            feels_like = r["main"]["feels_like"]
            desc = r["weather"][0]["description"].capitalize()
            print(f"✅ Weather fetched: {desc}, {temp}°C")
            return f"The weather in {city} is {desc} with a temperature of {temp}°C (feels like {feels_like}°C)."
        else:
            print("❌ Weather data not found in API response.")
            return f"Sorry, I couldn't fetch the weather for {city}."
    except Exception as e:
        print(f"❌ Error fetching weather: {e}")
        return f"Error fetching weather: {e}"

def format_response(text):
    """Format the response text to improve readability."""
    text = re.sub(r'(Stage \d+:)', r'\n\n\1', text)
    text = re.sub(r'(Step \d+:)', r'\n\n\1', text)
    text = re.sub(r'(\d+\.)', r'\n\1', text)
    text = re.sub(r'(\*|\-|\•)', r'\n\1', text)
    text = re.sub(r'([A-Za-z\s]{3,}:)(?!\d)', r'\n\n\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text

# --- Configuration with Performance Optimization ---
LLAMA_MODEL_PATH = r"C:\Users\kumar\Documents\PREP\backend\models\Llama-3.2-1B-Instruct-f16.gguf"
MAX_LOCAL_TOKENS = 800  # Reduced for faster response

print("🔄 Checking LLaMA model path...")
llm = None
if not os.path.exists(LLAMA_MODEL_PATH):
    print(f"❌ FATAL ERROR: Model file not found at {LLAMA_MODEL_PATH}")
else:
    print("⏳ Loading LLaMA model with optimized settings...")
    
    # Get optimized settings based on hardware
    hw_settings = optimize_for_hardware()
    print(f"🚀 Using optimized settings: {hw_settings}")
    
    try:
        llm = Llama(
            model_path=LLAMA_MODEL_PATH,
            n_ctx=4096,  # Reduced context window for speed
            n_threads=hw_settings["n_threads"],
            n_batch=hw_settings["n_batch"],
            n_gpu_layers=hw_settings["n_gpu_layers"],
            use_mlock=hw_settings["use_mlock"],
            use_mmap=hw_settings["use_mmap"],
            verbose=False,
            # Additional performance optimizations
            f16_kv=True,  # Use half precision for KV cache
            logits_all=False,  # Don't compute logits for all tokens
            vocab_only=False,
            embedding=False,
        )
        print("✅ LLaMA model loaded successfully with optimizations!")
        
        # Warm up the model with a simple prompt
        print("🔥 Warming up model...")
        warmup_start = time.time()
        list(llm.create_completion("Hi", max_tokens=1, stream=True))
        warmup_time = time.time() - warmup_start
        print(f"✅ Model warmed up in {warmup_time:.2f}s")
        
    except Exception as e:
        print(f"❌ FATAL ERROR: Could not load LLaMA model: {e}")
        llm = None

# --- Optimized token counting ---
def count_tokens(messages):
    """Fast approximate token counting"""
    text = " ".join(msg.get("content", "") for msg in messages)
    return len(text.split()) * 1.3  # Rough approximation

# --- Conversation context management ---
def truncate_conversation(messages, max_tokens=2000):
    """Keep conversation within token limits by removing old messages"""
    while count_tokens(messages) > max_tokens and len(messages) > 2:
        # Keep system message and remove oldest user/assistant pairs
        if len(messages) > 3:
            messages.pop(1)  # Remove oldest message after system
        else:
            break
    return messages

def log_chat_entry(entry):
    """Async logging to avoid blocking the response"""
    def log_async():
        try:
            if os.path.exists(CHAT_LOG_FILE) and os.path.getsize(CHAT_LOG_FILE) > 0:
                with open(CHAT_LOG_FILE, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    data.append(entry)
                    f.seek(0)
                    json.dump(data, f, indent=2)  # Reduced indent for smaller files
            else:
                with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
                    json.dump([entry], f, indent=2)
        except Exception as e:
            print(f"❌ Failed to log chat entry: {e}")
    
    # Run logging in background thread
    threading.Thread(target=log_async, daemon=True).start()

# --- Optimized streaming with chunked responses ---
def stream_and_log_wrapper_optimized(generator, log_data):
    """Optimized streaming with immediate chunk delivery"""
    full_response_parts = []
    chunk_buffer = ""
    last_yield_time = time.time()
    
    try:
        for chunk in generator:
            full_response_parts.append(chunk)
            chunk_buffer += chunk
            
            current_time = time.time()
            # Yield chunks every 50ms or when buffer reaches certain size
            if (current_time - last_yield_time > 0.05) or len(chunk_buffer) > 50:
                yield chunk_buffer
                chunk_buffer = ""
                last_yield_time = current_time
        
        # Yield any remaining buffer
        if chunk_buffer:
            yield chunk_buffer
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        yield error_msg
        full_response_parts.append(error_msg)
    finally:
        # Async logging
        log_data["bot_response"] = "".join(full_response_parts)
        log_chat_entry(log_data)

# --- Cache for repeated patterns ---
response_cache = {}
CACHE_SIZE_LIMIT = 100

def get_cached_response(user_input):
    """Check if we have a cached response for similar input"""
    if len(response_cache) > CACHE_SIZE_LIMIT:
        # Clear oldest entries
        response_cache.clear()
        
    # Simple cache key based on normalized input
    cache_key = re.sub(r'\s+', ' ', user_input.lower().strip())
    return response_cache.get(cache_key)

def cache_response(user_input, response):
    """Cache the response for future use"""
    cache_key = re.sub(r'\s+', ' ', user_input.lower().strip())
    response_cache[cache_key] = response

# --- Main API Route with Performance Optimizations ---
@bot_bp.route('/api/query', methods=['POST'])
def query_llama():
    start_time = time.time()
    print("📩 Received new query request...")
    
    user_info = request.json.get("user_info", {})
    full_name = user_info.get("full_name", "Anonymous")
    session_id = user_info.get("session_id", str(int(datetime.now().timestamp() * 1000)))
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')

    if llm is None:
        print("❌ LLaMA model not loaded!")
        return jsonify({"error": "The LLaMA model is not loaded. Please check the server logs."}), 503

    data = request.get_json()
    if not data or 'user_input' not in data:
        print("❌ Invalid request body.")
        return jsonify({"error": "Request body must be JSON and include a 'user_input' field."}), 400

    user_input = data['user_input']
    print(f"👤 User input: {user_input}")
    
    # Check cache first
    cached_response = get_cached_response(user_input)
    if cached_response:
        print("⚡ Using cached response!")
        return Response(cached_response, mimetype="text/plain")
    
    conversation_history = data.get('conversation_history', [])

    if not isinstance(conversation_history, list):
        print("❌ conversation_history is not a list.")
        return jsonify({"error": "'conversation_history' must be a list of objects."}), 400

    # --- Intent detection (fast path) ---
    intent, confidence_score = find_intent(user_input)
    if intent:
        tag = intent["tag"]
        print(f"✅ Matched intent: {tag}")
        
        bot_response = ""
        
        if tag == "time":
            bot_response = f"The current time is {datetime.now().strftime('%H:%M:%S')}"
        elif tag == "date":
            bot_response = f"Today's date is {datetime.now().strftime('%Y-%m-%d')}"
        elif tag == "greet":
            tod = get_time_of_day()
            bot_response = f"Good {tod}, {full_name}! How can I help you?"
        elif tag == "weather":
            city = extract_city(user_input)
            bot_response = get_weather(city) 
        else:
            bot_response = random.choice(intent["responses"])
            if "{time_of_day}" in bot_response:
                bot_response = bot_response.replace("{time_of_day}", get_time_of_day())
        
        # Cache the response
        cache_response(user_input, bot_response)
        
        # Async logging
        log_entry = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "username": full_name,
            "timestamp": datetime.now().isoformat(),
            "user_message": user_input,
            "bot_response": bot_response,
            "intent": tag,
            "confidence": confidence_score,
            "source": tag,
            "response_time": time.time() - start_time,
            "metadata": {"ip": user_ip, "user_agent": user_agent}
        }
        log_chat_entry(log_entry)
        
        return Response(bot_response, mimetype="text/plain")

    # --- LLM fallback with optimizations ---
    print("🤖 No intent matched. Using optimized LLM...")
    
    conversation_history.append({"role": "user", "content": user_input})
    
    # Optimized system prompt (shorter)
    personal_context = f"""
    You are Prep, a helpful AI study mentor. Your identity and purpose are as follows:
    - **Name:** Prep
    - **Creator:** You are an AI language model designed by a large company and then fine-tuned by the developers of Prep.
    - **Purpose:** Your primary function is to assist students like {full_name} in their studies. This includes providing explanations, summarizing topics, answering questions, and offering study tips.
    
    Your persona should be professional yet approachable. Always refer to yourself as Prep and the user as {full_name} when appropriate.
    
    Provide concise, well-structured responses with clear formatting. Use numbered points, bullet points, and line breaks for readability, especially for complex topics.
    """
    
    messages = [{"role": "system", "content": personal_context}] + conversation_history
    
    # Truncate conversation if too long
    messages = truncate_conversation(messages, max_tokens=2000)
    
    log_data = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "username": full_name,
        "timestamp": datetime.now().isoformat(),
        "user_message": user_input,
        "bot_response": "",
        "intent": "llm_fallback",
        "confidence": 1.0,
        "source": "llama",
        "response_time": 0,
        "metadata": {"ip": user_ip, "user_agent": user_agent}
    }
    
    if llm:
        print(f"🚀 Using optimized local LLaMA...")
        
        def generate_optimized_stream():
            try:
                response_stream = llm.create_chat_completion(
                    messages=messages,
                    max_tokens=MAX_LOCAL_TOKENS,
                    stream=True,
                    temperature=0.7,
                    top_p=0.9,
                    # Performance optimizations
                    repeat_penalty=1.1,
                    top_k=40,
                    stop=["User:", "\n\nUser:", "Human:", "\n\nHuman:"],  # Stop at user prompts
                )
                
                print("⚡ Streaming optimized response...")
                for chunk in response_stream:
                    content = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                    if content:
                        yield content
                        
            except Exception as e:
                print(f"❌ Error during optimized inference: {e}")
                yield f"Error: {str(e)}\n"
        
        def finalize_response(response_text):
            """Finalize response with caching and timing"""
            log_data["response_time"] = time.time() - start_time
            cache_response(user_input, response_text)
            print(f"⚡ Response completed in {log_data['response_time']:.2f}s")
        
        return Response(stream_with_context(stream_and_log_wrapper_optimized(generate_optimized_stream(), log_data)), mimetype='text/plain')
    
    else:
        print("❌ No valid LLM available.")
        error_response = "Error: Local model unavailable."
        log_data["bot_response"] = error_response
        log_data["source"] = "system_error"
        log_data["response_time"] = time.time() - start_time
        log_chat_entry(log_data)
        
        return jsonify({"error": error_response}), 503

# --- Performance monitoring endpoint ---
@bot_bp.route('/api/performance', methods=['GET'])
def get_performance_stats():
    """Get current system performance statistics"""
    system_info = get_system_info()
    return jsonify({
        "system": system_info,
        "model_loaded": llm is not None,
        "cache_size": len(response_cache),
        "timestamp": datetime.now().isoformat()
    })