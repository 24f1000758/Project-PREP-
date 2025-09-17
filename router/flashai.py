import os
import json
import re
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import fitz # PyMuPDF
from dotenv import load_dotenv
from models.schema import Deck, Flashcard
from extension import db
import pytesseract
from PIL import Image
import subprocess
import whisper
import logging
# Import client libraries for the different APIs
import google.generativeai as genai 
from flask_jwt_extended import jwt_required, get_jwt_identity 

# =====================================================
# 🔹 SETUP AND CONFIG
# =====================================================
# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define and configure a Blueprint for API routes
flashai_bp = Blueprint('flashai_bp', __name__, url_prefix='/api')

# API Key and Client Setup
api_clients = {}

# 1. Gemini API Setup
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        api_clients['gemini'] = genai.GenerativeModel('gemini-2.5-flash')
        logging.info("✅ Gemini API client initialized.")
    except Exception as e:
        logging.error(f"❌ Error initializing Gemini API: {e}")

# =====================================================
# 🔹 CORE HELPER FUNCTIONS
# =====================================================
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text")
        return text
    except Exception as e:
        logging.error(f"❌ PDF text extraction failed: {e}")
        return ""

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def extract_text_from_image(image_path: str) -> str:
    """Extracts text from an image file using OCR."""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except pytesseract.TesseractNotFoundError:
        logging.error("❌ Tesseract is not installed or not in your PATH.")
        return ""
    except Exception as e:
        logging.error(f"❌ Image text extraction failed: {e}")
        return ""

# --- Corrected and updated video function ---
def generate_flashcards_from_video_url(video_url: str, api_name: str, client) -> list:
    """
    Handles transcription and flashcard generation from any video URL.
    """
    temp_dir = 'temp_downloads'
    os.makedirs(temp_dir, exist_ok=True)
    
    # Initialize audio_path to None to prevent UnboundLocalError in the finally block
    audio_path = None
    
    # Define the output template for yt-dlp
    output_template = os.path.join(temp_dir, '%(id)s.%(ext)s')

    # Define the full path to BOTH executables to bypass PATH issues
    # !!! YOU MUST REPLACE THESE PATHS WITH THE EXACT ONES ON YOUR SYSTEM !!!
    yt_dlp_location = r"C:\Users\kumar\Documents\PREP\backend\venv\Scripts\yt-dlp.exe"
    ffmpeg_location = r"C:\Users\kumar\Documents\PREP\backend\youtube-module\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\bin\ffmpeg.exe"

    try:
        logging.info(f"🔄 Starting audio download for video: {video_url}")
        
        # We'll use yt-dlp to get the final filename as well
        info_command = [
            yt_dlp_location, # Use the full path here
            '--print-json', # Print video info as a JSON string
            '--no-playlist', # Don't get info for entire playlist
            '--audio-format', 'mp3', # Specify audio format
            '--ffmpeg-location', ffmpeg_location, # Explicitly tell yt-dlp where to find ffmpeg
            video_url
        ]
        
        info_result = subprocess.run(info_command, check=True, capture_output=True, text=True)
        video_info = json.loads(info_result.stdout)
        
        # Construct the final path of the downloaded file
        audio_path = os.path.join(temp_dir, f"{video_info['id']}.mp3")

        # Now, run the actual download command
        download_command = [
            yt_dlp_location, # Use the full path here as well
            '-x', # Extract audio only
            '--audio-format', 'mp3',
            '--ffmpeg-location', ffmpeg_location,
            '-o', output_template,
            video_url
        ]

        subprocess.run(download_command, check=True, capture_output=True, text=True)
        logging.info(f"✅ Audio downloaded to: {audio_path}")

        logging.info("🔄 Transcribing with Whisper...")
        
        # Load the Whisper model and transcribe the actual downloaded audio file
        model = whisper.load_model("tiny")
        transcription_result = model.transcribe(audio_path)
        transcribed_text = transcription_result['text']
        
        if not transcribed_text:
            logging.warning("Transcription returned empty text.")
            return []

        logging.info("✅ Transcription complete. Generating flashcards with LLM...")
        
        # Pass the transcribed text to your existing function
        flashcards = generate_flashcards_with_api(transcribed_text, api_name, client)
        
        return flashcards

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ yt-dlp failed with error: {e.stderr}")
        return []
    except Exception as e:
        logging.error(f"❌ An error occurred during video processing: {e}")
        return []
    finally:
        # This cleanup block is now safe from UnboundLocalError
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            logging.info(f"🗑️ Cleaned up temporary audio file: {audio_path}")

def generate_flashcards_with_api(summary: str, api_name: str, client) -> list:
    """
    Generates flashcards using a specified API client with robust JSON parsing.
    """
    prompt = f"""
    You are an expert educator and flashcard creator. Your task is to generate a comprehensive set of flashcards from the provided notes summary. Each flashcard should test a key concept, fact, or definition.

    **Instructions:**
    1.  Generate at least **15** unique flashcards.
    2.  Each flashcard must be a JSON object with two keys: "question" and "answer".
    3.  The questions should be thought-provoking, not just simple recall. Include "Why," "How," or "Explain" questions.
    4.  The answers should be concise but complete, providing the core information needed.
    5.  Ensure the flashcards cover a wide range of topics from the summary, hitting all major themes.
    6.  The final output must be **ONLY a single JSON array** containing all the flashcard objects.

    **Example format:**
    ```json
    [
    {{"question": "What is the primary function of the mitochondria?", "answer": "To generate most of the chemical energy needed to power the cell's biochemical reactions."}},
    {{"question": "Why is the invention of the printing press considered a turning point in history?", "answer": "Because it enabled the rapid and widespread dissemination of information and ideas, leading to the Renaissance and Reformation."}}
    ]
    ```

    **Summary of notes:**
    ---
    {summary}
    ---
    Generated Flashcards:
    """
    raw_text = None
    try:
        # Step 1: Get the raw text from the API
        if api_name == 'gemini':
            response = client.generate_content(prompt)
            raw_text = response.text.strip()
        elif api_name == 'mistral':
            response = client.chat(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            raw_text = response.choices[0].message.content.strip()
        elif api_name == 'huggingface':
            raw_text = client.text_generation(prompt, max_new_tokens=2048)
            if hasattr(raw_text, 'text'):
                raw_text = raw_text.text
            raw_text = str(raw_text).strip()
        
        # Step 2: Implement robust JSON extraction and parsing
        if raw_text:
            # 2a. Aggressively find and extract all potential JSON objects
            # This regex finds all key-value pair blocks
            json_objects = re.findall(r'\{[^}]*\"answer\"[^}]*\}', raw_text, re.DOTALL)
            
            if json_objects:
                # 2b. Reconstruct the JSON array from the found objects
                reconstructed_json = '[' + ',\n'.join(json_objects) + ']'
                
                try:
                    flashcards = json.loads(reconstructed_json)
                    if isinstance(flashcards, list) and all("question" in d and "answer" in d for d in flashcards):
                        logging.info(f"✅ Successfully generated flashcards using {api_name} API after aggressive reconstruction.")
                        return flashcards
                except json.JSONDecodeError as jde:
                    logging.error(f"❌ JSON parsing failed for {api_name} even after aggressive reconstruction: {jde}")
                    logging.debug(f"Reconstructed JSON was: {reconstructed_json}")

            # 2c. Fallback to the previous, less aggressive method if the above fails
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', raw_text, re.DOTALL)
            if not json_match:
                json_match = re.search(r'(\[.*?\])', raw_text, re.DOTALL)
            
            if json_match:
                json_string = json_match.group(1).strip()
                cleaned_json_string = re.sub(r',\s*([\]}])', r'\1', json_string)
                
                try:
                    flashcards = json.loads(cleaned_json_string)
                    if isinstance(flashcards, list) and all("question" in d and "answer" in d for d in flashcards):
                        logging.info(f"✅ Successfully generated flashcards using {api_name} API after cleaning.")
                        return flashcards
                except json.JSONDecodeError as jde:
                    logging.error(f"❌ JSON parsing failed for {api_name} even after advanced cleaning: {jde}")
                    logging.debug(f"Raw text was: {raw_text}")
            else:
                logging.warning(f"❌ Could not find a JSON array in the response from {api_name}.")
                logging.debug(f"Raw text was: {raw_text}")
    
    except Exception as e:
        logging.error(f"❌ Flashcard generation failed for {api_name} API: {e}")

    return None

# =====================================================
# 🔹 API ROUTE
# =====================================================
@flashai_bp.route("/upload_notes", methods=["POST"])
@jwt_required()
def upload_notes():
    """Handles PDF upload, extracts text, and generates flashcards using Gemini."""
    current_user_id = get_jwt_identity()
    if 'gemini' not in api_clients:
        return jsonify({"error": "Gemini API key is not configured. Please check your .env file."}), 503

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        temp_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(temp_dir, exist_ok=True)
        filepath = os.path.join(temp_dir, filename)

        try:
            logging.info(f"🔄 Starting flashcard generation from PDF: {filename}")
            file.save(filepath)
            extracted_text = extract_text_from_pdf(filepath)
            if not extracted_text:
                return jsonify({"error": "Failed to extract text from PDF."}), 500

            flashcards = generate_flashcards_with_api(extracted_text, 'gemini', api_clients['gemini'])
            if flashcards:
                logging.info(f"✅ Flashcards generated successfully from {filename}.")
                return jsonify({
                    "message": "Flashcards generated successfully!",
                    "flashcards": flashcards,
                })
            else:
                return jsonify({"error": "Gemini API failed to generate flashcards."}), 500

        except Exception as e:
            logging.error(f"❌ An error occurred during PDF-based flashcard generation: {str(e)}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
                logging.info(f"🗑️ Cleaned up temporary PDF file: {filepath}")
    else:
        return jsonify({"error": "Invalid file type. Please upload a PDF."}), 400

# ---
# New API routes to handle deck and flashcard management

@flashai_bp.route("/decks", methods=["POST"])
@jwt_required()
def save_deck():
    """Saves a new deck and its flashcards to the database."""
    try:
        data = request.get_json()
        user_id = get_jwt_identity() 
        deck_name = data.get('name')
        cards_data = data.get('cards',[])
        
        if not all([user_id, deck_name, cards_data]):
            return jsonify({"error": "Missing deck data"}), 400
        
        new_deck = Deck(user_id=user_id, deck_name=deck_name)
        db.session.add(new_deck)
        db.session.flush() 

        flashcards = [
            Flashcard(question=card['question'], answer=card['answer'], deck_id=new_deck.id)
            for card in cards_data
        ]
        db.session.bulk_save_objects(flashcards)
        db.session.commit()
        logging.info(f"✅ Deck '{deck_name}' saved successfully for user {user_id}.")
        return jsonify({"message": "Deck saved successfully", "deck_id": new_deck.id}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error saving deck: {e}")
        return jsonify({"error": "Failed to save deck"}), 500

@flashai_bp.route("/decks/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_decks(user_id):
    """Retrieves all decks for a specific user."""
    try:
        current_user_id = get_jwt_identity()
        if int(current_user_id) != user_id:
            return jsonify({"error": "Unauthorized access"}), 403
            
        decks = Deck.query.filter_by(user_id=user_id).all()
        decks_list = [{
            "id": deck.id,
            "name": deck.deck_name,
            "card_count": len(deck.cards)
        } for deck in decks]
        logging.info(f"✅ Retrieved {len(decks_list)} decks for user {user_id}.")
        return jsonify({"decks": decks_list}), 200
    except Exception as e:
        logging.error(f"❌ Error fetching user decks: {e}")
        return jsonify({"error": "Failed to retrieve decks"}), 500

@flashai_bp.route("/decks/<int:deck_id>", methods=["GET"])
@jwt_required()
def get_deck_cards(deck_id):
    """Retrieves all flashcards for a specific deck."""
    try:
        current_user_id = get_jwt_identity() 
        deck = Deck.query.get(deck_id)
        if not deck:
            return jsonify({"error": "Deck not found"}), 404
        
        if int(deck.user_id) != int(current_user_id):
            return jsonify({"error": "Unauthorized access to this deck"}), 403

        cards = [{"question": card.question, "answer": card.answer} for card in deck.cards]
        logging.info(f"✅ Retrieved {len(cards)} cards for deck {deck_id}.")
        return jsonify({"name": deck.deck_name, "cards": cards}), 200
    except Exception as e:
        logging.error(f"❌ Error fetching deck cards: {e}")
        return jsonify({"error": "Failed to retrieve cards"}), 500

@flashai_bp.route("/decks/<int:deck_id>", methods=["PUT"])
@jwt_required()
def rename_deck(deck_id):
    """Updates the name of a deck."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        new_name = data.get('name')
        if not new_name:
            return jsonify({"error": "New deck name is required"}), 400

        deck = Deck.query.get(deck_id)
        if not deck:
            return jsonify({"error": "Deck not found"}), 404
        
        if int(deck.user_id) != int(user_id):
            return jsonify({"error": "Unauthorized access to this deck"}), 403
        
        deck.deck_name = new_name
        db.session.commit()
        logging.info(f"✅ Deck {deck_id} renamed to '{new_name}'.")
        return jsonify({"message": "Deck renamed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error renaming deck: {e}")
        return jsonify({"error": "Failed to rename deck"}), 500

@flashai_bp.route("/decks/<int:deck_id>", methods=["DELETE"])
@jwt_required()
def delete_deck(deck_id):
    """Deletes a deck and all its associated flashcards."""
    try:
        user_id = get_jwt_identity()
        deck = Deck.query.get(deck_id)
        if not deck:
            return jsonify({"error": "Deck not found"}), 404
        
        if int(deck.user_id) != int(user_id):
            return jsonify({"error": "Unauthorized access to this deck"}), 403

        db.session.delete(deck)
        db.session.commit()
        logging.info(f"✅ Deck {deck_id} deleted successfully.")
        return jsonify({"message": "Deck deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error deleting deck: {e}")
        return jsonify({"error": "Failed to delete deck"}), 500

@flashai_bp.route("/decks/<int:deck_id>/cards", methods=["POST"])
@jwt_required()
def add_card_to_deck(deck_id):
    """Adds a new flashcard to an existing deck."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        question = data.get('question')
        answer = data.get('answer')
        
        if not all([question, answer]):
            return jsonify({"error": "Question and answer are required"}), 400

        deck = Deck.query.get(deck_id)
        if not deck:
            return jsonify({"error": "Deck not found"}), 404

        if int(deck.user_id) != int(user_id):
            return jsonify({"error": "Unauthorized access to this deck"}), 403

        new_card = Flashcard(question=question, answer=answer, deck_id=deck.id)
        db.session.add(new_card)
        db.session.commit()
        logging.info(f"✅ New flashcard added to deck {deck_id}.")
        return jsonify({"message": "Flashcard added successfully!", "card_id": new_card.id}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error adding new card: {e}")
        return jsonify({"error": "Failed to add new flashcard"}), 500

# =====================================================
@flashai_bp.route("/generate_from_text/<int:user_id>", methods=["POST"])
@jwt_required()
def generate_from_text(user_id):
    """
    Handles text input from the frontend, generates flashcards using Gemini,
    and returns the result.
    """
    current_user_id = get_jwt_identity()
    if int(current_user_id) != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    if 'gemini' not in api_clients:
        return jsonify({"error": "Gemini API key is not configured. Please check your .env file."}), 503

    try:
        data = request.get_json()
        text_input = data.get('text')
        
        if not text_input:
            return jsonify({"error": "No text provided in the request body"}), 400
        
        logging.info("🔄 Starting flashcard generation from text.")
        flashcards = generate_flashcards_with_api(text_input, 'gemini', api_clients['gemini'])
        if flashcards:
            logging.info("✅ Flashcards generated successfully from text.")
            return jsonify({
                "message": "Flashcards generated successfully!",
                "flashcards": flashcards,
            })
        else:
            return jsonify({"error": "Gemini API failed to generate flashcards."}), 500

    except Exception as e:
        logging.error(f"❌ An error occurred during text-based flashcard generation: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500

@flashai_bp.route("/generate_from_image/<int:user_id>", methods=["POST"])
@jwt_required()
def upload_image(user_id):
    """
    Handles image upload, extracts text via OCR, and generates flashcards
    using Gemini.
    """
    current_user_id = get_jwt_identity()
    if int(current_user_id) != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    if 'gemini' not in api_clients:
        return jsonify({"error": "Gemini API key is not configured. Please check your .env file."}), 503

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({"error": "Invalid file type. Please upload an image (PNG, JPG, JPEG, GIF, BMP)."}), 400

    filename = secure_filename(file.filename)
    temp_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(temp_dir, exist_ok=True)
    filepath = os.path.join(temp_dir, filename)

    try:
        logging.info(f"🔄 Starting flashcard generation from image: {filename}")
        file.save(filepath)
        extracted_text = extract_text_from_image(filepath)
        if not extracted_text:
            return jsonify({"error": "Failed to extract text from the image."}), 500

        flashcards = generate_flashcards_with_api(extracted_text, 'gemini', api_clients['gemini'])
        if flashcards:
            logging.info(f"✅ Flashcards generated successfully from {filename}.")
            return jsonify({
                "message": "Flashcards generated successfully!",
                "flashcards": flashcards,
            })
        else:
            return jsonify({"error": "Gemini API failed to generate flashcards."}), 500

    except Exception as e:
        logging.error(f"❌ An error occurred during image-based flashcard generation: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            logging.info(f"🗑️ Cleaned up temporary image file: {filepath}")

@flashai_bp.route("/generate_from_video/<int:user_id>", methods=["POST"])
@jwt_required()
def generate_from_video_route(user_id):
    """
    API endpoint to generate flashcards from a video URL using Gemini.
    """
    current_user_id = get_jwt_identity()
    if int(current_user_id) != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    if 'gemini' not in api_clients:
        return jsonify({"error": "Gemini API key is not configured."}), 503

    try:
        data = request.get_json()
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({"error": "No video URL provided"}), 400

        logging.info(f"🔄 Starting flashcard generation from video URL: {video_url}")
        # Correctly call the helper function with the required 'api_name' argument
        flashcards = generate_flashcards_from_video_url(video_url, 'gemini', api_clients['gemini'])
        if flashcards:
            logging.info(f"✅ Flashcards generated successfully from video.")
            return jsonify({
                "message": "Flashcards generated successfully from video!",
                "flashcards": flashcards,
                "source_url": video_url
            })
        else:
            return jsonify({"error": "Gemini API failed to generate flashcards."}), 500

    except Exception as e:
        logging.error(f"❌ An unexpected error occurred in video route: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500