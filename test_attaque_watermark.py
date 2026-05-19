#!/usr/bin/env python3
"""
Test des attaques sur images tatouees LSB.

Usage:
  python test_attaque_watermark.py                    # dernier log dans logs/
  python test_attaque_watermark.py logs/mon_log.png   # fichier precis
"""
import os
import sys
import glob

from watermark.attacks import tester_toutes_attaques, lister_attaques
from watermark.log_manager import verifier_log


def _dernier_log() -> str | None:
    fichiers = glob.glob(os.path.join("logs", "log_*.png"))
    fichiers = [f for f in fichiers if "attaque" not in f and "_temp" not in f]
    if not fichiers:
        return None
    return max(fichiers, key=os.path.getmtime)


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else _dernier_log()
    if not chemin or not os.path.exists(chemin):
        print("Aucun log trouve. Lancez une reconnaissance ou passez un chemin PNG.")
        sys.exit(1)

    print("=" * 70)
    print(f"Image source : {chemin}")
    print("=" * 70)

    original = verifier_log(chemin)
    print("\n[ORIGINAL]")
    if original:
        print(f"  Watermark OK : {original}")
    else:
        print("  Watermark ABSENT (image non tatouee ou corrompue)")
        sys.exit(1)

    print("\n[ATTAQUES DISPONIBLES]")
    for cle, lib in lister_attaques():
        print(f"  - {cle}: {lib}")

    print("\n[RESULTATS]")
    resultats = tester_toutes_attaques(chemin)
    for r in resultats:
        statut = "OK" if r.get("watermark_ok") else "ECHEC"
        print(f"\n  {r['libelle']} ({r['attaque']})")
        print(f"    Fichier : {r.get('fichier', '—')}")
        print(f"    Watermark apres attaque : {statut}")
        if r.get("infos"):
            print(f"    Donnees extraites : {r['infos']}")
        if r.get("erreur"):
            print(f"    Erreur : {r['erreur']}")

    ok = sum(1 for r in resultats if r.get("watermark_ok"))
    print("\n" + "=" * 70)
    print(f"Resume : {ok}/{len(resultats)} attaques — watermark encore lisible")
    print("Images attaquees dans : logs/attacks/")
    print("=" * 70)


if __name__ == "__main__":
    main()
