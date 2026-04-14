from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import pickle
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from huggingface_hub import hf_hub_download

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Download model files from Hugging Face on startup ──
REPO_ID = "AniruddhaS30/scamshield-model"

print("Downloading model files from Hugging Face...")

model_path      = hf_hub_download(repo_id=REPO_ID, filename="scam_model.h5")
vectorizer_path = hf_hub_download(repo_id=REPO_ID, filename="vectorizer.pkl")
encoder_path    = hf_hub_download(repo_id=REPO_ID, filename="label_encoder.pkl")

print("Loading model...")
model = load_model(model_path)

with open(vectorizer_path, "rb") as f:
    vectorizer = pickle.load(f)

with open(encoder_path, "rb") as f:
    label_encoder = pickle.load(f)

print("Model ready!")

# ── Request schema ──
class TextInput(BaseModel):
    text: str

# ── Predict endpoint ──
@app.post("/predict")
def predict(input: TextInput):
    text = input.text.lower().strip()
    sequences = vectorizer.texts_to_sequences([text])
    padded = pad_sequences(sequences, maxlen=100)
    prediction = model.predict(padded)
    predicted_index = np.argmax(prediction, axis=1)[0]
    predicted_label = label_encoder.inverse_transform([predicted_index])[0]
    confidence = float(np.max(prediction))
    return {
        "label": predicted_label,
        "confidence": round(confidence * 100, 2)
    }

@app.get("/")
def root():
    return {"status": "ScamShield API is running"}