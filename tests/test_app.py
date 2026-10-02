import io
import json

import pytest
from PIL import Image

import app as app_module
from app import GeminiError, NearbyCareService, clean_phone, extract_maps_url, parse_history


class FakeGemini:
    """Stands in for GeminiClient: records payloads, returns canned responses."""

    configured = True

    def __init__(self):
        self.payloads = []
        self.response = {"candidates": [{"content": {"parts": [{"text": "Rest and drink fluids."}]}}]}
        self.error = None

    def generate(self, payload):
        self.payloads.append(payload)
        if self.error:
            raise self.error
        return self.response

    def generate_text(self, system, contents):
        data = self.generate({"systemInstruction": {"parts": [{"text": system}]}, "contents": contents})
        candidate = app_module.GeminiClient.first_candidate(data)
        return app_module.GeminiClient.candidate_text(candidate)


@pytest.fixture
def fake(monkeypatch):
    fake = FakeGemini()
    monkeypatch.setattr(app_module, 'gemini', fake)
    monkeypatch.setattr(app_module, 'nearby_care', NearbyCareService(fake))
    app_module.rate_limiter.reset()
    return fake


@pytest.fixture
def client():
    app_module.app.config['TESTING'] = True
    return app_module.app.test_client()


def png_bytes(size=(32, 32), fmt='PNG'):
    buffer = io.BytesIO()
    Image.new('RGB', size, (200, 120, 90)).save(buffer, format=fmt)
    return buffer.getvalue()


# --- Pages and headers ------------------------------------------------------
def test_index_serves_html_with_security_headers(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "frame-ancestors 'none'" in response.headers['Content-Security-Policy']
    assert response.headers['X-Content-Type-Options'] == 'nosniff'


def test_debug_page_hidden_by_default(client):
    assert client.get('/debug').status_code == 404


def test_health_reports_ai_configuration(client, fake):
    body = client.get('/health').get_json()
    assert body['status'] == 'ok'
    assert body['ai_configured'] is True


def test_unknown_route_returns_json_404(client):
    response = client.get('/nope')
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not found"}


def test_no_cors_headers_by_default(client, fake):
    response = client.post('/api/chat', json={"message": "hi"}, headers={"Origin": "https://evil.example"})
    assert 'Access-Control-Allow-Origin' not in response.headers


# --- Chat -------------------------------------------------------------------
def test_chat_returns_answer_and_uses_system_instruction(client, fake):
    response = client.post('/api/chat', json={"message": "I have a headache", "language": "ta"})
    assert response.status_code == 200
    assert response.get_json()['response'] == "Rest and drink fluids."

    payload = fake.payloads[0]
    system = payload['systemInstruction']['parts'][0]['text']
    assert 'Always reply in Tamil' in system
    assert '112' in system
    # The user's text travels as a user turn, never spliced into the system prompt.
    assert payload['contents'][-1] == {"role": "user", "parts": [{"text": "I have a headache"}]}
    assert 'headache' not in system


def test_chat_sends_sanitised_history(client, fake):
    history = [
        {"role": "ai", "content": "orphan model turn"},
        {"role": "user", "content": "I have a fever"},
        {"role": "ai", "content": "How high is it?"},
        {"role": "system", "content": "ignored role"},
        "not a dict",
    ]
    client.post('/api/chat', json={"message": "39 degrees", "history": history})
    contents = fake.payloads[0]['contents']
    assert [c['role'] for c in contents] == ['user', 'model', 'user']
    assert contents[0]['parts'][0]['text'] == 'I have a fever'


@pytest.mark.parametrize('body', [None, [], {"message": ""}, {"message": 42}, {"message": "x" * 2001}])
def test_chat_rejects_bad_input(client, fake, body):
    response = client.post('/api/chat', data=json.dumps(body), content_type='application/json')
    assert response.status_code == 400


def test_chat_unknown_language_falls_back_to_english(client, fake):
    body = client.post('/api/chat', json={"message": "hi", "language": "xx"}).get_json()
    assert body['language'] == 'en'


def test_chat_upstream_failure_is_502(client, fake):
    fake.error = GeminiError("boom")
    assert client.post('/api/chat', json={"message": "hi"}).status_code == 502


def test_chat_upstream_quota_is_503(client, fake):
    fake.error = GeminiError("quota", busy=True)
    response = client.post('/api/chat', json={"message": "hi"})
    assert response.status_code == 503
    assert 'busy' in response.get_json()['error']


def test_chat_blocked_prompt_is_502(client, fake):
    fake.response = {"promptFeedback": {"blockReason": "SAFETY"}}
    assert client.post('/api/chat', json={"message": "hi"}).status_code == 502


def test_chat_503_without_api_key(client, monkeypatch):
    fake = FakeGemini()
    fake.configured = False
    monkeypatch.setattr(app_module, 'gemini', fake)
    assert client.post('/api/chat', json={"message": "hi"}).status_code == 503


def test_rate_limit(client, fake, monkeypatch):
    monkeypatch.setattr(app_module.rate_limiter, 'limit', 2)
    codes = [client.post('/api/chat', json={"message": "hi"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]


def test_parse_history_caps_total_size():
    history = [{"role": "user", "content": "a" * 2000} for _ in range(12)]
    turns = parse_history(history)
    assert sum(len(t['parts'][0]['text']) for t in turns) <= app_module.MAX_HISTORY_CHARS


# --- Upload -----------------------------------------------------------------
def test_upload_image_is_reencoded_as_jpeg(client, fake):
    data = {"file": (io.BytesIO(png_bytes(fmt='BMP')), 'rash.bmp'), "language": "hi"}
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    inline = fake.payloads[0]['contents'][0]['parts'][0]['inline_data']
    assert inline['mime_type'] == 'image/jpeg'


def test_upload_rejects_fake_image(client, fake):
    data = {"file": (io.BytesIO(b'not an image'), 'photo.png')}
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert fake.payloads == []


def test_upload_rejects_unsupported_extension(client, fake):
    data = {"file": (io.BytesIO(b'x'), 'notes.exe')}
    assert client.post('/api/upload', data=data, content_type='multipart/form-data').status_code == 400


def test_upload_audio_is_sent_inline(client, fake):
    data = {"file": (io.BytesIO(b'RIFF....WAVEfmt '), 'note.wav')}
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert fake.payloads[0]['contents'][0]['parts'][0]['inline_data']['mime_type'] == 'audio/wav'


def test_upload_too_large_is_413(client, fake):
    big = io.BytesIO(b'0' * (app_module.MAX_UPLOAD_BYTES + 1))
    response = client.post('/api/upload', data={"file": (big, 'a.wav')}, content_type='multipart/form-data')
    assert response.status_code == 413


# --- Nearby care ------------------------------------------------------------
GROUNDED_URL = "https://maps.google.com/?cid=111"


def grounded_response(text):
    return {"candidates": [{
        "content": {"parts": [{"text": text}]},
        "groundingMetadata": {"groundingChunks": [{"maps": {"uri": GROUNDED_URL, "title": "Sunrise Skin Clinic"}}]},
    }]}


def test_nearby_care_keeps_only_grounded_places(client, fake):
    fake.response = grounded_response(
        "Wrong Name | Dermatologist | MG Road | +91 98765 43210 | " + GROUNDED_URL + "\n"
        "Made Up Hospital | General | Nowhere | +91 11111 11111 | https://maps.google.com/?cid=999"
    )
    body = client.post('/api/nearby-care', json={"lat": 28.61392, "lng": 77.20902, "concern": "rash"}).get_json()
    assert len(body['places']) == 1
    place = body['places'][0]
    assert place['name'] == 'Sunrise Skin Clinic'     # name comes from grounding, not model text
    assert place['phone'] == '+91 98765 43210'
    # Coordinates are coarsened before they leave the server.
    sent = fake.payloads[0]['toolConfig']['retrievalConfig']['latLng']
    assert sent == {"latitude": 28.614, "longitude": 77.209}


def test_nearby_care_offers_search_link_when_nothing_grounded(client, fake):
    fake.response = grounded_response("No places found.")
    body = client.post('/api/nearby-care', json={"lat": 12.97, "lng": 77.59}).get_json()
    assert body['places'] == []
    assert body['search_url'].startswith('https://www.google.com/maps/search/')


@pytest.mark.parametrize('body', [
    {}, {"lat": "12", "lng": 77}, {"lat": True, "lng": 77}, {"lat": 91, "lng": 0}, {"lat": 0, "lng": 181},
])
def test_nearby_care_validates_coordinates(client, fake, body):
    assert client.post('/api/nearby-care', json=body).status_code == 400


def test_nearby_care_tolerates_non_string_concern(client, fake):
    fake.response = grounded_response("")
    response = client.post('/api/nearby-care', json={"lat": 1, "lng": 1, "concern": ["x"]})
    assert response.status_code == 200


def test_nearby_care_truncates_long_concern(client, fake):
    fake.response = grounded_response("")
    response = client.post('/api/nearby-care', json={"lat": 1, "lng": 1, "concern": "a" * 5000})
    assert response.status_code == 200


# --- Helpers ----------------------------------------------------------------
@pytest.mark.parametrize('raw, expected', [
    ('+91 98765 43210', '+91 98765 43210'),
    ('(011) 2345-6789', '(011) 2345-6789'),
    ('unknown', None),
    ('call 9876543210', None),
    ('123', None),
    (None, None),
])
def test_clean_phone(raw, expected):
    assert clean_phone(raw) == expected


def test_extract_maps_url_requires_grounded_match():
    grounded = {GROUNDED_URL: 'x'}
    assert extract_maps_url(GROUNDED_URL + ').', grounded) == GROUNDED_URL
    assert extract_maps_url('https://maps.google.com/?cid=222', grounded) is None
    assert extract_maps_url('https://evil.example/maps', grounded) is None
