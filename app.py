from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import logging
import re
import time
from collections import defaultdict, deque
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from urllib.parse import quote
import requests
import google.generativeai as genai
from PIL import Image
import io

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS: open by default for local development, restricted via ALLOWED_ORIGINS in
# any deployed environment (comma separated origin list).
_allowed_origins = [
    origin.strip()
    for origin in os.environ.get('ALLOWED_ORIGINS', '').split(',')
    if origin.strip()
]
if _allowed_origins:
    CORS(app, resources={r"/api/*": {"origins": _allowed_origins}})
    logger.info("CORS restricted to: %s", _allowed_origins)
else:
    CORS(app)

# --- Limits -----------------------------------------------------------------
MAX_UPLOAD_BYTES = 16 * 1024 * 1024
MAX_MESSAGE_CHARS = 2000
MAX_CONCERN_CHARS = 300
MAX_DESCRIPTION_CHARS = 500
MAX_IMAGE_PIXELS = 25_000_000
MAX_UPLOAD_DESCRIPTION_CHARS = 500
NEARBY_RESULT_LIMIT = 4
GEMINI_TIMEOUT = (5, 25)   # (connect, read) seconds
GEMINI_MAX_ATTEMPTS = 2

app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_BYTES
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32)

# Uploads are processed fully in memory; nothing needs to touch the disk, so the
# folder is no longer created and no file is ever written.
app.config['UPLOAD_FOLDER'] = None

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY, transport='rest')
else:
    logger.warning("GEMINI_API_KEY is not set: chat and nearby-care will return 503.")

GEMINI_REST_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
NEARBY_CARE_MODEL = "gemini-2.5-flash"

# Simple in-process rate limit for the two paid Gemini routes.
RATE_LIMIT = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '20'))
_rate_buckets = defaultdict(deque)


def rate_limited(view):
    """Reject calls from a client that exceeds RATE_LIMIT_PER_MINUTE requests."""
    def wrapper(*args, **kwargs):
        client = request.remote_addr or 'unknown'
        now = time.time()
        bucket = _rate_buckets[client]

        while bucket and now - bucket[0] > 60:
            bucket.popleft()

        if len(bucket) >= RATE_LIMIT:
            logger.warning("rate limit hit for %s", client)
            return jsonify({"error": "Too many requests, please slow down"}), 429

        bucket.append(now)
        return view(*args, **kwargs)

    wrapper.__name__ = view.__name__
    return wrapper


ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp',
    'wav', 'mp3', 'mp4', 'webm', 'ogg', 'aac', 'm4a', 'flac'
}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """Determine if file is image or audio based on extension"""
    if not filename or '.' not in filename:
        return 'unknown'
    extension = filename.rsplit('.', 1)[1].lower()
    image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    audio_extensions = {'wav', 'mp3', 'mp4', 'webm', 'ogg', 'aac', 'm4a', 'flac'}
    if extension in image_extensions:
        return 'image'
    elif extension in audio_extensions:
        return 'audio'
    return 'unknown'


# ==========================================
# LANGUAGE PROMPTS (module level: built once, not per request)
# ==========================================
HEALTH_CONTEXTS = {
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
        """,

        'ta': """
        நீங்கள் டாக்டர் ஆரோக்யலிங்க், ஒரு நண்பன் AI சுகாதார துணை. பேசும் முறையில்,
        அதிகபட்சம் 2-4 சொற்களில் சுருக்கமான மருத்துவ வழிகாட்டுதல் வழங்குங்கள்.

        பொதுவான காரணங்கள், எளிய சிகிச்சை முறைகள், மருத்துவரை நாடும்
        தேவை இருக்கும்போது ஆலோசிப்பதை மட்டும் சுருக்கமாகக் கூறவும்.

        அனைத்து பதில்களையும் தமிழில் வழங்குங்கள்.
        """,

        'bn': """
        আপনি ডা. আরোগ্যলিঙ্ক, এক বন্ধুর মতো AI স্বাস্থ্য সঙ্গী। কথোপকথনের ভঙ্গিতে,
        সর্বোচ্চ ২-৪ বাক্যে সংক্ষিপ্ত চিকিৎসা পরামর্শ দিন।

        সম্ভাব্য কারণ, সহজ চিকিৎসা ব্যবস্থা এবং প্রয়োজনে চিকিৎসকের
        পরামর্শ নেওয়ার পরিস্থিতি সংক্ষেপে জানান।

        সব উত্তর বাংলায় দিন।
        """,

        'te': """
        మీరు డాక్టర్ ఆరోగ్యలింక్, ఒక మిత్రుడిలాంటి AI ఆరోగ్య సహాయకుడు. సంభాషణ భాషలో,
        గరిష్టంగా 2-4 వాక్యాల్లో సంక్షిప్త వైద్య సూచనలు ఇవ్వండి.

        సంభావ్య కారణాలు, సులభ వైద్య చర్యలు, వైద్యుడిని సంప్రదించాల్సిన
        పరిస్థితులను సంక్షిప్తంగా చెప్పండి.

        అన్ని సమాధానాలు తెలుగులో ఇవ్వండి.
        """,

        'mr': """
        तुम्ही डॉ. आरोग्यलिंक, एक मित्रासारखे AI आरोग्य सोबती. संवादाच्या शैलीत,
        अधिकतम 2-4 वाक्यांत सविस्तर वैद्यकीय मार्गदर्शन द्या.

        संभाव्य कारणे, सोपी उपचारपद्धती आणि गरज असल्यास डॉक्टरांचा
        सल्ला घ्यावा याबाबत सांगा.

        सर्व उत्तरे मराठीत द्या.
        """,

        'kn': """
        ನೀವು ಡಾ. ಆರೋಗ್ಯಲಿಂಕ್, ಒಬ್ಬ ಸ್ನೇಹಿತನಂತೆ AI ಆರೋಗ್ಯ ಸಂಗಾತಿ. ಸಂಭಾಷಣೆಯ ಶೈಲಿಯಲ್ಲಿ,
        ಗರಿಷ್ಠ 2-4 ವಾಕ್ಯಗಳಲ್ಲಿ ಸಂಕ್ಷಿಪ್ತ ವೈದ್ಯಕೀಯ ಮಾರ್ಗದರ್ಶನ ನೀಡಿ.

        ಸಂಭವನೀಯ ಕಾರಣಗಳು, ಸರಳ ಚಿಕಿತ್ಸಾ ಕ್ರಮಗಳು ಮತ್ತು ವೈದ್ಯರ
        ಸಲಹೆ ಅಗತ್ಯವಿದ್ದಲ್ಲಿ ತಿಳಿಸಿ.

        ಎಲ್ಲಾ ಉತ್ತರಗಳನ್ನೂ ಕನ್ನಡದಲ್ಲಿ ನೀಡಿ.
        """,

        'gu': """
        તમે ડા. આરોગ્યલિંક, એક મિત્રની જેમ AI આરોગ્ય સહાયક. વાતચીતની શૈળીમાં,
        વધુમાં વધુ 2-4 વાક્યમાં સંક્ષિપ્ત તબીબી માર્ગદર્શન આપો.

સંભવિત કારણો, સરળ સારવાર પદ્ધતિઓ અને જરૂર હોય ત્યારે ડૉક્ટરની
સલાહ લેવાની જરૂરિયાત સંક્ષેપમાં જણાવો.

બધા જવાબો ગુજરાતીમાં આપો.
        """,

        'ml': """
        നിങ്ങൾ ഡോ. ആരോഗ്യലിങ്ക്, ഒരു സുഹൃതനെപ്പോലെ AI ആരോഗ്യ സഹായി. സംഭാഷണ
        രീതിയിൽ, പരമാവധി 2-4 വാക്കുകളിൽ ചുരുക്കിയ വൈദ്യ മാർഗനിർദേശം നൽകൂ.

        സാധ്യമായ കാരണങ്ങൾ, എളുപ്പമാಯ ചികിത്സാ മാർഗങ്ങൾ, ഡോക്ടറെ
        കാണാൻ വേണ്ട സാഹചര്യങ്ങൾ എന്നിവ ചുരുക്കിയിട്ട് പറയൂ.

        എല്ലാ പ്രതികരണങ്ങളും മലയാളത്തിൽ നൽകൂ.
        """
    
}


class HealthCompanionAPI:
    def __init__(self):
        try:
            if GEMINI_API_KEY:
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            else:
                self.gemini_model = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.gemini_model = None

    @property
    def available(self):
        return self.gemini_model is not None

    def call_gemini_api(self, prompt, image_data=None):
        """Call Gemini API, returning a dict or None on failure."""
        if not self.gemini_model:
            return None
        try:
            if image_data:
                with Image.open(io.BytesIO(image_data)) as image:
                    response = self.gemini_model.generate_content([prompt, image])
            else:
                response = self.gemini_model.generate_content(prompt)
            text = getattr(response, 'text', None)
            if not text:
                logger.warning("Gemini returned an empty response.")
                return None
            return {
                "text": text,
                "usage": getattr(response, 'usage_metadata', {}),
                "safety_ratings": getattr(response, 'safety_ratings', [])
            }
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return None

    def process_health_query(self, query_type, content, file_data=None, predictions=None, language='en'):
        """Process health-related queries using Gemini with multilingual support"""
        health_context = HEALTH_CONTEXTS.get(language) or HEALTH_CONTEXTS['en']

        if query_type == "text":
            # The health_context already fixes the tone and the 2-4 sentence
            # length; do not contradict it with a "be comprehensive" instruction.
            full_prompt = (
                f"{health_context}\n\n"
                f"User Symptoms/Query: {content}\n\n"
                "Answer in the language requested above, and remind the user that "
                "this is guidance rather than a diagnosis."
            )

            gemini_response = self.call_gemini_api(full_prompt)

            return {
                "primary_response": gemini_response.get("text") if gemini_response else None,
                "source": "gemini" if gemini_response else "none",
                "analysis_type": "text",
                "timestamp": datetime.now().isoformat()
            }

        elif query_type == "image":
            predictions_note = f"\n\nOn-device model predictions: {predictions}" if predictions else ""
            image_prompt = (
                f"{health_context}\n\n"
                f"Image Analysis Request: {content}{predictions_note}\n\n"
                "Describe only what is visible in the image, keep it to 2-4 sentences, "
                "and state clearly that a clinician should confirm anything clinical."
            )

            gemini_response = self.call_gemini_api(image_prompt, file_data)

            return {
                "primary_response": gemini_response.get("text") if gemini_response else None,
                "source": "gemini" if gemini_response else "none",
                "analysis_type": "image_analysis",
                "ai_predictions": predictions,
                "safety_ratings": gemini_response.get("safety_ratings", []) if gemini_response else [],
                "timestamp": datetime.now().isoformat()
            }

        elif query_type == "audio":
            return self.process_health_query("text", content, language=language)

        raise ValueError(f"Unsupported query type: {query_type}")


# ==========================================
# NEARBY CARE (Google Maps grounded lookup)
# ==========================================
NEARBY_CARE_PROMPTS = {
    'en': (
        "Decide which kind of doctor or clinic fits the user's concern: a relevant "
        "specialist practice, or a nearby multi-speciality clinic or hospital."
    ),
    'hi': "उपयोगकर्ता की समस्या के अनुसार उपयुक्त विशेषज्ञ डॉक्टर या क्लिनिक तय करें।",
    'pa': "ਉਪਭੋਗਤਾ ਦੀ ਸਮੱਸਿਆ ਅਨੁਸਾਰ ਢੁਕਵਾਂ ਮਾਹਰ ਡਾਕਟਰ ਜਾਂ ਕਲਿਨਿਕ ਚੁਣੋ।",
}


def clean_phone(value):
    """Keep a phone number only when it is well formed.

    Grounded output often carries broken fragments, so anything that is not a
    plausible dialable number is discarded rather than shown to the user.
    Leading '(' is allowed because parenthesised area codes are common.
    """
    if not value:
        return None

    text = ' '.join(str(value).split())
    if not text or text.lower() in {'unknown', 'n/a', 'na', 'none', 'not available', '-'}:
        return None

    if not re.fullmatch(r"[+(]?[\d(][\d\s()+-]{6,19}", text):
        return None

    digits = re.sub(r"\D", "", text)
    if not 8 <= len(digits) <= 15:
        return None

    return text


def digits_only(value):
    """Reduce a phone-ish string to its digits, for grounded comparison."""
    return re.sub(r"\D", "", value or "")


def is_valid_maps_url(url, grounded_urls):
    """Accept only map links that actually came back from grounding."""
    if not url:
        return None

    match = re.search(r"https://(?:www\.)?(?:maps\.google\.com|google\.com/maps)/\S+", str(url))
    if not match:
        return None

    candidate = match.group(0).rstrip('.,;)\'"')
    return candidate if candidate in grounded_urls else None


class NearbyCareService:
    """Looks up real clinics and specialists near the user's own coordinates.

    Every field returned here comes from Google Maps grounding: the model may
    only report places that grounding returned, and a map link or phone number
    is dropped unless it appears verbatim in the grounded data.
    """

    def __init__(self, model_name=NEARBY_CARE_MODEL):
        self.model_name = model_name

    def build_prompt(self, concern, language):
        guidance = NEARBY_CARE_PROMPTS.get(language) or NEARBY_CARE_PROMPTS['en']
        return (
            f"{guidance}\n\n"
            f"User concern: {concern}\n\n"
            f"Find up to {NEARBY_RESULT_LIMIT} real providers near the user's location: "
            "relevant specialist practices first, then nearby multi-speciality "
            "clinics or hospitals.\n\n"
            "Hard rules:\n"
            "- Only list places returned by Google Maps grounding.\n"
            f"- Return exactly {NEARBY_RESULT_LIMIT} places, nearest first.\n"
            "- One place per line, exactly five pipe-separated fields:\n"
            "  NAME | SPECIALTY | ADDRESS | PHONE | MAPS_URL\n"
            "- Example: Apollo Clinic | Dermatologist | "
            "Baner Road, Pune, Maharashtra | +91 98765 43210 | "
            "https://maps.google.com/maps?cid=1234567890\n"
            "- Prefer MBBS/allopathic providers, named specialist practices and "
            "multi-speciality hospitals with a working reception desk.\n"
            "- NAME, ADDRESS, PHONE and MAPS_URL must be copied exactly from the "
            "grounding data. Never invent a phone number.\n"
            "- Use 'unknown' for PHONE when grounding has no number.\n"
            "- Every line must end with the exact https://maps.google.com/... link "
            "from grounding for that place.\n"
            "- Write SPECIALTY in the user's language if it is not English.\n"
            "- Output nothing else: no preamble, no bullets, no blank lines."
        )

    def post_to_gemini(self, payload):
        """POST to Gemini with a bounded timeout and one retry on 429/5xx."""
        url = f"{GEMINI_REST_BASE}/{self.model_name}:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}

        last_error = None
        for attempt in range(GEMINI_MAX_ATTEMPTS):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=GEMINI_TIMEOUT)
            except requests.RequestException as err:
                last_error = err
            else:
                if response.status_code in (429, 500, 502, 503, 504):
                    last_error = requests.HTTPError(
                        f"Gemini returned {response.status_code}", response=response
                    )
                else:
                    response.raise_for_status()
                    return response.json()

            if attempt + 1 < GEMINI_MAX_ATTEMPTS:
                backoff = 1.5 * (attempt + 1)
                logger.warning("Gemini call failed (%s); retrying in %ss", last_error, backoff)
                time.sleep(backoff)

        raise last_error if last_error else ValueError("Gemini request failed")

    def find(self, lat, lng, concern, language='en'):
        payload = {
            "contents": [{"parts": [{"text": self.build_prompt(concern, language)}]}],
            "tools": [{"googleMaps": {}}],
            "toolConfig": {
                "retrievalConfig": {
                    "latLng": {"latitude": lat, "longitude": lng}
                }
            },
        }

        data = self.post_to_gemini(payload)

        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError("No candidates returned")

        candidate = candidates[0]
        parts = (candidate.get("content") or {}).get("parts") or []
        text = "".join(part.get("text", "") for part in parts)

        grounded_urls = set()
        grounding = candidate.get("groundingMetadata") or {}
        for chunk in grounding.get("groundingChunks") or []:
            uri = (chunk.get("maps") or chunk.get("web") or {}).get("uri")
            if uri and uri.startswith(("https://maps.google.com", "https://www.google.com/maps")):
                grounded_urls.add(uri.split()[0])

        if not grounded_urls:
            logger.warning("Google Maps grounding returned no map links; falling back to search.")

        places = self.parse_places(text, grounded_urls)

        if not places:
            search_url = (
                "https://www.google.com/maps/search/?api=1&query="
                f"{quote(concern[:120])}&center={lat},{lng}"
            )
            return {
                "places": [],
                "search_url": search_url,
                "latitude": lat,
                "longitude": lng,
                "source": "google_maps"
            }

        return {
            "places": places,
            "latitude": lat,
            "longitude": lng,
            "source": "google_maps"
        }

    def parse_places(self, text, grounded_urls):
        """Parse the pipe-delimited reply, keeping only grounded, well-formed rows.

        A row survives only if its map link is present verbatim in the grounding
        metadata. A phone number additionally has to appear in the grounded
        response text, so a number the model made up can never be shown.
        """
        places = []
        grounded_digits = digits_only(text)

        for raw_line in text.splitlines():
            line = raw_line.strip().lstrip('-* ').strip()
            if '|' not in line:
                continue

            fields = [field.strip() for field in line.split('|')]
            if len(fields) < 3:
                continue

            name = fields[0]
            specialty = fields[1] if len(fields) > 1 else ''
            address = fields[2] if len(fields) > 2 else ''
            raw_phone = clean_phone(fields[3]) if len(fields) > 3 else None
            maps_url = is_valid_maps_url(
                fields[4] if len(fields) > 4 else None, grounded_urls
            )

            # A row without a verified grounded map link cannot be shown safely.
            if not name or len(name) < 3 or not maps_url:
                continue

            # Only surface a phone number that the grounded text also contains.
            phone = None
            if raw_phone:
                candidate_digits = digits_only(raw_phone)
                if len(candidate_digits) >= 8 and candidate_digits in grounded_digits:
                    phone = raw_phone
                else:
                    logger.info("Dropped ungrounded phone number for %r", name)

            places.append({
                "name": name,
                "specialty": specialty or None,
                "address": address or None,
                "phone": phone,
                "maps_url": maps_url
            })

            if len(places) == NEARBY_RESULT_LIMIT:
                break

        return places


# Initialize the API handler
health_api = HealthCompanionAPI()
nearby_care = NearbyCareService()


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
@rate_limited
def chat():
    """Handle text-based health queries with language support"""
    try:
        if not health_api.available:
            return jsonify({"error": "Chat service is not configured"}), 503

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "A JSON object body is required"}), 400

        message = data.get('message')
        if not isinstance(message, str) or not message.strip():
            return jsonify({"error": "Message is required"}), 400

        message = message.strip()
        if len(message) > MAX_MESSAGE_CHARS:
            return jsonify({
                "error": f"Message is too long (max {MAX_MESSAGE_CHARS} characters)"
            }), 400

        language = data.get('language')
        if not isinstance(language, str) or language not in HEALTH_CONTEXTS:
            language = 'en'

        response = health_api.process_health_query("text", message, language=language)

        if response.get('primary_response'):
            return jsonify({
                "success": True,
                "response": response['primary_response'],
                "source": response['source'],
                "timestamp": response['timestamp'],
                "language": language
            })

        logger.warning("Chat request produced no response (language=%s)", language)
        return jsonify({"error": "Unable to process your query at the moment"}), 502

    except RequestEntityTooLarge:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/upload', methods=['POST'])
@rate_limited
def upload_file():
    """Handle image and audio uploads.

    Files are processed entirely in memory: nothing is written to disk, so there
    is no temporary file to leak on an error path.
    """
    try:
        if not health_api.available:
            return jsonify({"error": "Upload service is not configured"}), 503

        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if not file or not file.filename:
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            allowed_exts = ', '.join(sorted(ALLOWED_EXTENSIONS))
            return jsonify({
                "error": f"File type not allowed. Supported formats: {allowed_exts}"
            }), 400

        filename = secure_filename(file.filename) or 'upload'
        query_type = request.form.get('type', 'auto')
        description = (request.form.get('description') or '')[:MAX_DESCRIPTION_CHARS]
        language = request.form.get('language', 'en')
        if language not in HEALTH_CONTEXTS:
            language = 'en'
        ai_predictions = request.form.get('ai_predictions')

        file_data = file.read()
        if not file_data:
            return jsonify({"error": "File is empty"}), 400

        if len(file_data) > MAX_UPLOAD_BYTES:
            return jsonify({
                "error": f"File too large. Maximum size is {MAX_UPLOAD_BYTES // (1024 * 1024)}MB."
            }), 413

        if query_type == 'auto':
            query_type = get_file_type(filename)

        if query_type == 'image':
            try:
                with Image.open(io.BytesIO(file_data)) as img:
                    img.verify()
                with Image.open(io.BytesIO(file_data)) as img:
                    width, height = img.size
            except Exception:
                return jsonify({"error": "Invalid image file"}), 400

            # Guard against decompression bombs: verify() only reads the header.
            if width * height > MAX_IMAGE_PIXELS:
                return jsonify({"error": "Image dimensions are too large"}), 400

            predictions_data = None
            if ai_predictions:
                try:
                    predictions_data = json.loads(ai_predictions)
                except json.JSONDecodeError:
                    logger.warning("Ignoring unparseable ai_predictions field")

            response = health_api.process_health_query(
                "image", description or "Please analyse this skin photo.",
                file_data, predictions_data, language=language
            )

        elif query_type == 'audio':
            audio_description = f"Audio note received ({len(file_data)} bytes). "
            audio_description += description or (
                "Please describe the symptoms or health concerns from the audio recording."
            )
            response = health_api.process_health_query(
                "text", audio_description, language=language
            )

        else:
            return jsonify({"error": f"Unsupported file type: {query_type}"}), 400

        if response.get('primary_response'):
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

        logger.warning("Upload produced no response (type=%s)", query_type)
        return jsonify({"error": "Unable to process file at the moment"}), 502

    except RequestEntityTooLarge:
        raise
    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/nearby-care', methods=['POST'])
@rate_limited
def nearby_care_lookup():
    """Find real clinics and specialists near the coordinates sent by the browser.

    Location is always the user's own fetched position. Nothing is returned when
    coordinates are missing, so the client never shows invented providers.
    """
    try:
        if not GEMINI_API_KEY:
            return jsonify({"error": "Nearby care lookup is not configured"}), 503

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "A JSON object body is required"}), 400

        lat_raw = data.get('lat')
        lng_raw = data.get('lng')
        if lat_raw is None or lng_raw is None:
            return jsonify({"error": "Valid latitude and longitude are required"}), 400

        try:
            lat = float(lat_raw)
            lng = float(lng_raw)
        except (TypeError, ValueError):
            return jsonify({"error": "Valid latitude and longitude are required"}), 400

        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return jsonify({"error": "Coordinates out of range"}), 400

        concern = (data.get('concern') or '').strip()
        if not isinstance(concern, str) or not concern:
            concern = 'general physician and multi-speciality clinic'
        if len(concern) > MAX_CONCERN_CHARS:
            return jsonify({
                "error": f"Concern is too long (max {MAX_CONCERN_CHARS} characters)"
            }), 400

        language = data.get('language')
        if not isinstance(language, str) or language not in HEALTH_CONTEXTS:
            language = 'en'

        result = nearby_care.find(lat, lng, concern, language=language)

        return jsonify({
            "success": True,
            **result,
            "timestamp": datetime.now().isoformat()
        })

    except requests.RequestException as e:
        logger.error(f"Nearby care request failed: {e}")
        return jsonify({"error": "Nearby care lookup is temporarily unavailable"}), 502
    except ValueError as e:
        logger.error(f"Nearby care response invalid: {e}")
        return jsonify({"error": "Nearby care lookup is temporarily unavailable"}), 502
    except Exception as e:
        logger.error(f"Error in nearby care endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/contact', methods=['POST'])
def contact():
    """Validate a contact submission.

    No delivery channel is wired up yet (no mail transport, no datastore), so
    this endpoint reports 501 rather than pretending the message was received.
    Swap the body for a real send once a transport exists.
    """
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "A JSON object body is required"}), 400

        missing = [
            field for field in ('name', 'email', 'message')
            if not isinstance(data.get(field), str) or not data[field].strip()
        ]
        if missing:
            return jsonify({"error": f"{', '.join(missing)} required"}), 400

        logger.info("Contact form submission received (delivery not yet configured)")

        return jsonify({
            "success": False,
            "error": "Contact delivery is not configured on this deployment."
        }), 501

    except RequestEntityTooLarge:
        raise
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
    logger.error("Unhandled server error", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Never expose the Werkzeug debugger on a network interface by default.
    debug_enabled = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    host = os.environ.get('HOST', '127.0.0.1')
    if debug_enabled:
        logger.warning("FLASK_DEBUG is enabled: interactive debugger available on %s", host)
    app.run(debug=debug_enabled, host=host, port=port)