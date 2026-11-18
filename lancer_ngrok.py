"""
Lance un tunnel ngrok sur le port 8000.
Affiche l'URL publique à partager avec le téléphone.
"""
from pyngrok import ngrok

print("=== Tunnel ngrok ===")
print("Démarrage du tunnel...")

# Ouvre un tunnel HTTP sur le port 8000
tunnel = ngrok.connect(8000)
url = tunnel.public_url

print(f"\nURL publique : {url}")
print(f"Dashboard    : {url}/dashboard")
print("\nPartage cette URL avec ton téléphone.")
print("Appuie sur Ctrl+C pour arrêter le tunnel.\n")

try:
    ngrok.get_ngrok_process().proc.wait()
except KeyboardInterrupt:
    print("\nTunnel ferme.")
    ngrok.kill()
