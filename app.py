from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import base64
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
import requests
import google.generativeai as genai
from PIL import Image
import io

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'aarogyalink-secret')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY, transport='rest')

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp',
    'wav', 'mp3', 'mp4', 'webm', 'ogg', 'aac', 'm4a', 'flac'
}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """Determine if file is image or audio based on extension"""
    if '.' not in filename:
        return 'unknown'
    extension = filename.rsplit('.', 1)[1].lower()
    image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    audio_extensions = {'wav', 'mp3', 'mp4', 'webm', 'ogg', 'aac', 'm4a', 'flac'}
    if extension in image_extensions:
        return 'image'
    elif extension in audio_extensions:
        return 'audio'
    return 'unknown'


class HealthCompanionAPI:
    def __init__(self):
        try:
            if GEMINI_API_KEY:
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            else:
                self.gemini_model = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.gemini_model = None

    def call_gemini_api(self, prompt, image_data=None):
        """Call Gemini API"""
        try:
            if not self.gemini_model:
                return None
            if image_data:
                image = Image.open(io.BytesIO(image_data))
                response = self.gemini_model.generate_content([prompt, image])
            else:
                response = self.gemini_model.generate_content(prompt)
            return {
                "text": response.text,
                "usage": getattr(response, 'usage_metadata', {}),
                "safety_ratings": getattr(response, 'safety_ratings', [])
            }
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return None

    def process_health_query(self, query_type, content, file_data=None, predictions=None, language='en'):
        """Process health-related queries using Gemini with multilingual support"""

        # Language-specific medical analysis templates
        health_contexts = {
            'en': """
            You are Dr. AarogyaLink, a friendly AI health companion. Provide conversational, concise medical guidance in 2-4 sentences maximum.
            
            Tone: Friendly and reassuring, like texting a doctor friend
            Length: Maximum 2-4 sentences
            
            Analyze the symptoms and provide:
            1. A brief assessment of the condition
            2. Simple treatment suggestions 
            3. When to see a doctor if needed
            
            Keep responses short, conversational, and friendly. No lengthy medical analysis or complex formatting.
            """,

            'hi': """
            आप डॉ. आरोग्यलिंक हैं, एक मित्रवत AI स्वास्थ्य साथी। बातचीत के स्वर में, अधिकतम 2-4 वाक्यों में संक्षिप्त चिकित्सा मार्गदर्शन प्रदान करें।
            
            स्वर: मित्रवत और आश्वस्त करने वाला
            लंबाई: अधिकतम 2-4 वाक्य
            
            लक्षणों का विश्लेषण करें और प्रदान करें:
            1. स्थिति का संक्षिप्त आकलन
            2. सरल उपचार सुझाव
            3. यदि आवश्यक हो तो डॉक्टर से कब मिलना चाहिए
            
            सभी उत्तर हिंदी में दें।
            """,

            'pa': """
            ਤੁਸੀਂ ਡਾ. ਆਰੋਗਿਆਲਿੰਕ ਹੋ, ਇੱਕ ਦੋਸਤਾਨਾ AI ਸਿਹਤ ਸਾਥੀ। ਗੱਲਬਾਤ ਵਾਲੇ ਸੁਰ ਵਿੱਚ, ਵੱਧ ਤੋਂ ਵੱਧ 2-4 ਵਾਕਾਂ ਵਿੱਚ ਸੰਖੇਪ ਮੈਡੀਕਲ ਮਾਰਗਦਰਸ਼ਨ ਪ੍ਰਦਾਨ ਕਰੋ।
            
            ਸਾਰੇ ਜਵਾਬ ਪੰਜਾਬੀ ਵਿੱਚ ਦਿਓ।
            """
        }

        health_context = health_contexts.get(language, health_contexts['en'])

        if query_type == "text":
            full_prompt = f"""{health_context}
 
User Symptoms/Query: {content}
 
Provide a comprehensive medical analysis. Be thorough, professional, and educational while maintaining medical accuracy."""

            gemini_response = self.call_gemini_api(full_prompt)

            return {
                "primary_response": gemini_response.get("text") if gemini_response else None,
                "source": "gemini" if gemini_response else "none",
                "analysis_type": "comprehensive",
                "timestamp": datetime.now().isoformat()
            }

        elif query_type == "image":
            image_prompt = f"""{health_context}
 
Image Analysis Request: {content}
 
Analyze this medical image comprehensively. If AI predictions are available: {predictions}
 
Provide detailed medical analysis focusing on visual findings and their clinical significance."""

            gemini_response = self.call_gemini_api(image_prompt, file_data)

            return {
                "primary_response": gemini_response.get("text") if gemini_response else "Unable to analyze image",
                "source": "gemini",
                "analysis_type": "image_analysis",
                "ai_predictions": predictions,
                "safety_ratings": gemini_response.get("safety_ratings") if gemini_response else [],
                "timestamp": datetime.now().isoformat()
            }

        elif query_type == "audio":
            text_content = content
            return self.process_health_query("text", text_content)


# Initialize the API handler
health_api = HealthCompanionAPI()


@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')


@app.route('/debug')
def debug():
    """Serve the debug page"""
    return render_template('debug.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle text-based health queries with language support"""
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400

        message = data['message']
        language = data.get('language', 'en')

        response = health_api.process_health_query("text", message, language=language)

        if response['primary_response']:
            return jsonify({
                "success": True,
                "response": response['primary_response'],
                "source": response['source'],
                "timestamp": response['timestamp'],
                "language": language
            })
        else:
            return jsonify({"error": "Unable to process your query at the moment"}), 500

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads (images/audio)"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        query_type = request.form.get('type', 'auto')
        description = request.form.get('description', '')
        language = request.form.get('language', 'en')
        ai_predictions = request.form.get('ai_predictions')

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_data = file.read()

            if query_type == 'auto':
                query_type = get_file_type(filename)

            if len(file_data) == 0:
                return jsonify({"error": "File is empty"}), 400

            if len(file_data) > app.config['MAX_CONTENT_LENGTH']:
                return jsonify({"error": "File too large. Maximum size is 16MB."}), 413

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                with open(file_path, 'wb') as f:
                    f.write(file_data)
            except Exception as e:
                logger.error(f"Error saving file: {e}")
                return jsonify({"error": "Failed to save file"}), 500

            try:
                if query_type == 'image':
                    try:
                        img = Image.open(io.BytesIO(file_data))
                        img.verify()
                    except Exception as e:
                        return jsonify({"error": "Invalid image file"}), 400

                    predictions_data = None
                    if ai_predictions:
                        try:
                            predictions_data = json.loads(ai_predictions)
                        except json.JSONDecodeError:
                            pass

                    enhanced_description = description
                    if predictions_data:
                        enhanced_description += f"\n\nAI Model Predictions: {predictions_data}"

                    response = health_api.process_health_query("image", enhanced_description, file_data, predictions_data, language=language)

                elif query_type == 'audio':
                    audio_description = f"Audio file received: {filename} ({len(file_data)} bytes). "
                    if description:
                        audio_description += f"Description: {description}"
                    else:
                        audio_description += "Please describe your symptoms or health concerns from the audio recording."
                    response = health_api.process_health_query("text", audio_description, language=language)

                else:
                    return jsonify({"error": f"Unsupported file type: {query_type}"}), 400

            except Exception as e:
                logger.error(f"Error processing {query_type} file: {e}")
                return jsonify({"error": f"Failed to process {query_type} file"}), 500

            # Clean up temporary file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass

            if response and response.get('primary_response'):
                return jsonify({
                    "success": True,
                    "response": response['primary_response'],
                    "source": response['source'],
                    "analysis_type": response.get('analysis_type', 'basic'),
                    "ai_predictions": response.get('ai_predictions'),
                    "timestamp": response['timestamp'],
                    "file_info": {
                        "filename": filename,
                        "type": query_type,
                        "size": len(file_data)
                    }
                })
            else:
                return jsonify({"error": "Unable to process file at the moment"}), 500
        else:
            allowed_exts = ', '.join(sorted(ALLOWED_EXTENSIONS))
            return jsonify({"error": f"File type not allowed. Supported formats: {allowed_exts}"}), 400

    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()

        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        logger.info(f"Contact form submission from {data['email']}")

        return jsonify({
            "success": True,
            "message": "Thank you for your message. We'll get back to you soon!"
        })

    except Exception as e:
        logger.error(f"Error in contact endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large"}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)