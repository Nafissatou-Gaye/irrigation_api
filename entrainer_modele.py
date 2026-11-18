import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# ── Chargement du dataset ─────────────────────────────
print("📂 Chargement du dataset...")
df = pd.read_csv("dataset.csv")
print(f"Dataset : {len(df)} lignes, {df.shape[1]} colonnes")

# ── Préparation des données ───────────────────────────
X = df[["humidity", "temperature", "water_level"]]
y = df["decision"]

# ── Séparation train / test (80% / 20%) ──────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\nEntraînement : {len(X_train)} exemples")
print(f"Test         : {len(X_test)} exemples")

# ── Entraînement ──────────────────────────────────────
print("\n🤖 Entraînement du modèle...")
model = LogisticRegression(max_iter=1000, class_weight="balanced")
model.fit(X_train, y_train)
print("✅ Modèle entraîné !")

# ── Évaluation ────────────────────────────────────────
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n📊 Résultats :")
print(f"  Accuracy : {accuracy*100:.1f}%")
print(f"\nRapport complet :")
print(classification_report(y_test, y_pred,
      target_names=["Pas irrigation", "Irrigation"]))

# ── Matrice de confusion ──────────────────────────────
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Greens",
            xticklabels=["Pas irrigation", "Irrigation"],
            yticklabels=["Pas irrigation", "Irrigation"])
plt.title("Matrice de confusion")
plt.ylabel("Réel")
plt.xlabel("Prédit")
plt.tight_layout()
plt.savefig("matrice_confusion.png")
plt.show()
print("📈 Matrice de confusion sauvegardée !")

# ── Test manuel ───────────────────────────────────────
print("\n🧪 Tests manuels :")
tests = [
    {"humidity": 20, "temperature": 35, "water_level": 80},  # sol sec + chaud → irriguer
    {"humidity": 80, "temperature": 22, "water_level": 90},  # sol humide + frais → pas irrigation
    {"humidity": 30, "temperature": 30, "water_level": 50},  # cas limite
]
for t in tests:
    pred = model.predict([[t["humidity"], t["temperature"], t["water_level"]]])[0]
    proba = model.predict_proba([[t["humidity"], t["temperature"], t["water_level"]]])[0]
    decision = "💧 IRRIGUER" if pred == 1 else "✅ PAS D'IRRIGATION"
    print(f"  Hum={t['humidity']}% Temp={t['temperature']}°C Eau={t['water_level']}%"
          f" → {decision} (confiance: {max(proba)*100:.1f}%)")

# ── Sauvegarde du modèle ──────────────────────────────
joblib.dump(model, "irrigation_model.pkl")
print("\n💾 Modèle sauvegardé : irrigation_model.pkl")