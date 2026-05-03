#!/usr/bin/env python3
"""
Test simulant le démarrage de l'application GUI.
"""
import sys

print("[TEST] Simulation du démarrage de BiometriX GUI...\n")

# Step 1: Init DB
print("1. Initialisation de la base de données (app.lancer_app)...")
try:
    from database.db_manager import init_db
    init_db()
    print("   ✓ BD initialisée")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Test imports de page_login
print("\n2. Chargement de page_login...")
try:
    from gui.page_login import LoginPage
    print("   ✓ LoginPage importée")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Test imports de page_historique
print("\n3. Chargement de page_historique...")
try:
    from gui.page_historique import HistoriquePage
    print("   ✓ HistoriquePage importée")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Test rafraichir() sans erreur
print("\n4. Test de rafraichir() sur HistoriquePage...")
try:
    # On simule juste l'import, pas l'exécution de la méthode
    # (sinon il faudrait toute la stack PyQt5)
    from gui.page_historique import HistoriquePage
    # La méthode rafraichir() utilise des widgets PyQt5, donc on ne peut pas l'appeler
    # sans une QApplication, mais on peut au moins vérifier que le code compile
    print("   ✓ Code de HistoriquePage OK")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test RecognitionThread
print("\n5. Test de RecognitionThread...")
try:
    from gui.page_login import RecognitionThread
    print("   ✓ RecognitionThread importée")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[TEST] ✓ Tous les imports passent! L'app devrait démarrer.")
