from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# ── Connexion SQLite ──────────────────────────────────
engine = create_engine(
    "sqlite:///./irrigation.db",
    connect_args={"check_same_thread": False}
)

Base = declarative_base()

# ── Modèle de la table mesures ────────────────────────
class Mesure(Base):
    __tablename__ = "mesures"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    humidity    = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    water_level = Column(Float, default=100.0)
    decision    = Column(Integer, default=None)
    date        = Column(DateTime, default=datetime.now)

# ── Création de la table ──────────────────────────────
Base.metadata.create_all(engine)

# ── Session factory ───────────────────────────────────
SessionLocal = sessionmaker(bind=engine)

# ── Fonctions CRUD ────────────────────────────────────
def inserer_mesure(humidity, temperature, water_level):
    session = SessionLocal()
    m = Mesure(
        humidity=humidity,
        temperature=temperature,
        water_level=water_level,
        date=datetime.now()
    )
    session.add(m)
    session.commit()
    session.refresh(m)
    session.close()
    return m.id

def get_derniere_mesure():
    session = SessionLocal()
    m = session.query(Mesure).order_by(Mesure.id.desc()).first()
    session.close()
    if m:
        return {
            "id": m.id,
            "humidity": m.humidity,
            "temperature": m.temperature,
            "water_level": m.water_level,
            "date": str(m.date)
        }
    return None

def get_historique(limit=50):
    session = SessionLocal()
    mesures = session.query(Mesure).order_by(
        Mesure.id.desc()
    ).limit(limit).all()
    session.close()
    return [
        {
            "id": m.id,
            "humidity": m.humidity,
            "temperature": m.temperature,
            "water_level": m.water_level,
            "decision": m.decision,
            "date": str(m.date)
        }
        for m in mesures
    ]

def update_decision(mesure_id, decision):
    session = SessionLocal()
    m = session.query(Mesure).filter(Mesure.id == mesure_id).first()
    if m:
        m.decision = decision
        session.commit()
    session.close()