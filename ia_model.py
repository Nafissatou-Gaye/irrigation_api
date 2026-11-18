import joblib
import numpy as np
import os

# ── Chargement du modèle ──────────────────────────────
MODEL_PATH = "irrigation_model.pkl"

model = None

def charger_modele():
    global model
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ Modèle introuvable : {MODEL_PATH}")
        return False
    model = joblib.load(MODEL_PATH)
    print("✅ Modèle IA chargé !")
    return True

def predire(humidity: float, temperature: float, water_level: float) -> dict:
    global model

    # Sécurité : réservoir vide → pas d'irrigation
    if water_level < 10:
        return {
            "irrigate": False,
            "confidence": 100.0,
            "reason": "Réservoir trop vide"
        }

    if model is None:
        # Fallback basé sur des seuils si le modèle n'est pas chargé
        irrigate = humidity < 25 or (humidity < 40 and temperature > 28)
        return {
            "irrigate": bool(irrigate),
            "confidence": 75.0,
            "reason": "Seuils fixes (modèle non chargé)"
        }

    # Prédiction IA
    X = np.array([[humidity, temperature, water_level]])
    prediction = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    confidence = round(max(proba) * 100, 1)

    return {
        "irrigate": bool(prediction == 1),
        "confidence": confidence,
        "reason": "Modèle IA (régression logistique)"
    }