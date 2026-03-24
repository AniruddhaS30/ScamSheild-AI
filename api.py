from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tensorflow as tf
import pickle
import numpy as np
import re
import uvicorn

app = FastAPI()

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load LSTM model ───────────────────────────────────────────
model = tf.keras.models.load_model('model/scam_model.h5')

# ── Load vectorizer ───────────────────────────────────────────
with open('model/vectorizer.pkl', 'rb') as f:
    saved_data = pickle.load(f)

vectorizer = tf.keras.layers.TextVectorization(
    max_tokens=10000,
    output_mode='int',
    output_sequence_length=100
)
vectorizer.set_vocabulary(saved_data['vocabulary'])

# ── Load label encoder ────────────────────────────────────────
with open('model/label_encoder.pkl', 'rb') as f:
    le = pickle.load(f)

print("Vocab size:", len(saved_data['vocabulary']))
print("Classes:", le.classes_)

# ── Hinglish support ──────────────────────────────────────────
from utils.hinglish_map import HINGLISH_TO_ENGLISH, normalize_hinglish

def preprocess(text: str) -> str:
    text = normalize_hinglish(text)
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    return text.lower().strip()

# ── Input model ───────────────────────────────────────────────
class Message(BaseModel):
    text: str

# ── Routes ────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ScamShield AI API is running!"}

@app.post("/predict")
def predict(message: Message):
    try:
        clean = preprocess(message.text)
        vec = vectorizer([clean])
        pred = model.predict(vec, verbose=0)
        idx = int(np.argmax(pred))
        label = le.inverse_transform([idx])[0]
        confidence = round(float(pred[0][idx]) * 100, 2)
        is_scam = label in ['spam', 'smishing']
        return {
            "prediction": label,
            "is_scam": is_scam,
            "confidence": confidence,
            "message": "⚠️ Scam Detected!" if is_scam else "✅ Looks Safe"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)