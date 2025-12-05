import os
import json
import fitz
import re
from sentence_transformers import SentenceTransformer

# ===== Encodage MiniLM =====
model = SentenceTransformer("all-MiniLM-L6-v2")

# ===== Dossiers et fichiers =====
dossier_articles = "../ressources"
nom_fichier_index = "index_minilm_pages.json"
index_vecteurs = {}

# ===== Nettoyage texte =====
def nettoyer_texte(texte):
    texte = texte.lower()
    texte = re.sub(r'[^a-zA-Z0-9\s]', ' ', texte)
    texte = re.sub(r'\s+', ' ', texte)
    return texte.strip()

# ===== Charger index si existe =====
if os.path.exists(nom_fichier_index):
    print("Loading existing MiniLM index...")
    with open(nom_fichier_index, "r", encoding="utf-8") as f:
        index_vecteurs = json.load(f)
else:
    print("Creating MiniLM index for English documents...")

    fichiers = [f for f in os.listdir(dossier_articles) if f.endswith(".pdf")]

    for fichier in fichiers:
        chemin = os.path.join(dossier_articles, fichier)

        try:
            pdf = fitz.open(chemin)
        except Exception as e:
            print(f"Error reading {fichier}: {e}")
            continue

        print(f"Indexing {fichier} ({pdf.page_count} pages)...")

        for page_num, page in enumerate(pdf, start=1):
            texte_page = page.get_text()
            texte_nettoye = nettoyer_texte(texte_page)

            if texte_nettoye.strip() == "":
                continue  # sauter les pages vides

            # Embedding MiniLM
            vecteur = model.encode(texte_nettoye).tolist()

            # Stocker avec clé "fichier_page"
            key = f"{fichier}_page_{page_num}"
            index_vecteurs[key] = vecteur

            print(f"Indexed: {key}")

        pdf.close()

    # Sauvegarder index
    with open(nom_fichier_index, "w", encoding="utf-8") as f:
        json.dump(index_vecteurs, f, indent=2, ensure_ascii=False)

print(f"MiniLM index ready! {len(index_vecteurs)} page vectors embedded.")
