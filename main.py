from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime
import database
import ia_model
# ── Initialisation ────────────────────────────────────
app = FastAPI(
    title="API Irrigation Intelligente",
    description="API REST pour la gestion automatique de l'irrigation",
    version="1.0.0"
)

# ── CORS (pour le dashboard web) ─────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Chargement du modèle IA au démarrage ──────────────
@app.on_event("startup")
def startup():
    ia_model.charger_modele()

# ── Schémas de données ────────────────────────────────
class DonneesCapteur(BaseModel):
    humidity:    float
    temperature: float
    water_level: float = 100.0

class CommandeManuelle(BaseModel):
    activate: bool

# ── État manuel de la pompe ───────────────────────────
etat_manuel = {"active": False, "override": False}

# ══════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════

@app.get("/")
def accueil(request: Request):
    # Redirige vers /mobile si accès depuis un navigateur (pas l'ESP32)
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return RedirectResponse(url="/mobile")
    return {
        "message": "API Irrigation Intelligente",
        "version": "1.0.0",
        "status": "online"
    }

# ── POST /data ────────────────────────────────────────
@app.post("/data")
def recevoir_donnees(data: DonneesCapteur):
    """Reçoit les mesures des capteurs ESP32"""

    # Validation des données
    if not (0 <= data.humidity <= 100):
        raise HTTPException(400, "Humidité invalide (0-100)")
    if not (0 <= data.temperature <= 60):
        raise HTTPException(400, "Température invalide (0-60)")
    if not (0 <= data.water_level <= 100):
        raise HTTPException(400, "Niveau eau invalide (0-100)")

    # Prédiction IA
    resultat = ia_model.predire(
        data.humidity,
        data.temperature,
        data.water_level
    )

    # Sauvegarde en BDD
    mesure_id = database.inserer_mesure(
        data.humidity,
        data.temperature,
        data.water_level
    )

    # Mise à jour de la décision en BDD
    database.update_decision(mesure_id, int(resultat["irrigate"]))

    return {
        "status": "ok",
        "mesure_id": mesure_id,
        "decision": resultat
    }

# ── GET /decision ─────────────────────────────────────
@app.get("/decision")
def obtenir_decision():
    """Retourne la décision d'irrigation basée sur la dernière mesure"""

    # Commande manuelle prioritaire
    if etat_manuel["override"]:
        return {
            "irrigate": etat_manuel["active"],
            "confidence": 100.0,
            "reason": "Commande manuelle"
        }

    # Dernière mesure en BDD
    derniere = database.get_derniere_mesure()
    if not derniere:
        return {
            "irrigate": False,
            "confidence": 0.0,
            "reason": "Aucune mesure disponible"
        }

    return ia_model.predire(
        derniere["humidity"],
        derniere["temperature"],
        derniere["water_level"]
    )

# ── GET /history ──────────────────────────────────────
@app.get("/history")
def obtenir_historique(limit: int = 50):
    """Retourne les dernières mesures"""
    return {"mesures": database.get_historique(limit)}

# ── POST /manual ──────────────────────────────────────
@app.post("/manual")
def commande_manuelle(cmd: CommandeManuelle):
    """Active ou désactive la pompe manuellement"""
    etat_manuel["active"]   = cmd.activate
    etat_manuel["override"] = True
    return {
        "status": "ok",
        "pompe": "ON" if cmd.activate else "OFF",
        "mode": "manuel"
    }

# ── DELETE /manual ────────────────────────────────────
@app.delete("/manual")
def annuler_manuel():
    """Repasse en mode automatique (IA)"""
    etat_manuel["override"] = False
    return {"status": "ok", "mode": "automatique"}

# ── GET /status ───────────────────────────────────────
@app.get("/status")
def statut_systeme():
    """État général du système"""
    derniere = database.get_derniere_mesure()
    decision = ia_model.predire(
        derniere["humidity"] if derniere else 50,
        derniere["temperature"] if derniere else 30,
        derniere["water_level"] if derniere else 100
    )
    return {
        "timestamp": str(datetime.now()),
        "mode": "manuel" if etat_manuel["override"] else "automatique",
        "pompe": etat_manuel["active"] if etat_manuel["override"] else decision["irrigate"],
        "derniere_mesure": derniere,
        "decision_ia": decision
    }
@app.get("/dashboard")
def dashboard():
    return FileResponse("dashboard.html")

@app.get("/mobile")
def mobile():
    return FileResponse("mobile.html")

@app.get("/manifest.json")
def manifest():
    return FileResponse("manifest.json", media_type="application/manifest+json")

@app.get("/sw.js")
def service_worker():
    return FileResponse("sw.js", media_type="application/javascript")

@app.get("/icon-192.png")
def icon192():
    return FileResponse("icon-192.png", media_type="image/png")

@app.get("/icon-512.png")
def icon512():
    return FileResponse("icon-512.png", media_type="image/png")