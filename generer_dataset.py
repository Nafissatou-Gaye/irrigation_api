import pandas as pd
import numpy as np

# Fixe le générateur aléatoire pour avoir des résultats reproductibles
np.random.seed(42)

N = 600  # nombre de mesures à générer

# ── Génération des données ────────────────────────────
humidite_sol  = np.random.uniform(0, 100, N)    # 0% à 100%
temperature   = np.random.uniform(18, 42, N)    # 18°C à 42°C
water_level   = np.random.uniform(10, 100, N)   # 10% à 100%

# ── Règle de décision (logique agronomique) ───────────
# On irrigue si :
#   - humidité sol < 40% (sol trop sec)
#   - ET température > 28°C (évaporation forte)
# OU :
#   - humidité sol < 25% (sol très sec, peu importe la temp)

decision = []
for i in range(N):
    h = humidite_sol[i]
    t = temperature[i]
    w = water_level[i]

    if w < 10:
        # Réservoir vide → pas d'irrigation possible
        irriguer = 0
    elif h < 25:
        # Sol très sec → irriguer dans tous les cas
        irriguer = 1
    elif h < 40 and t > 28:
        # Sol modérément sec + forte chaleur → irriguer
        irriguer = 1
    else:
        # Sol suffisamment humide → pas d'irrigation
        irriguer = 0

    decision.append(irriguer)

# ── Création du DataFrame ─────────────────────────────
df = pd.DataFrame({
    "humidity":    humidite_sol.round(1),
    "temperature": temperature.round(1),
    "water_level": water_level.round(1),
    "decision":    decision
})

# ── Sauvegarde en CSV ─────────────────────────────────
df.to_csv("dataset.csv", index=False)

# ── Résumé ────────────────────────────────────────────
print("✅ Dataset généré : 600 mesures")
print(f"\nDistribution des décisions :")
print(f"  Irriguer (1) : {sum(decision)} mesures ({sum(decision)/N*100:.1f}%)")
print(f"  Ne pas irriguer (0) : {N-sum(decision)} mesures ({(N-sum(decision))/N*100:.1f}%)")
print(f"\nAperçu des 5 premières lignes :")
print(df.head())
print(f"\nStatistiques :")
print(df.describe())