import os, json, torch
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Import de votre fonction de nettoyage de titre
from scripts.recherche1 import book_title

recherche_book = Blueprint('recherche_book', __name__)

# Modèle plus rapide et performant
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# --- INITIALISATION (Chargement unique) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "index_books_chunks.json")
dossier_livres = os.path.join(current_dir, "../ressources")  # Ajustez si besoin

print("Chargement de l'index en mémoire...")
with open(json_path, "r", encoding="utf-8") as f:
    index_raw = json.load(f)

# Conversion en Tensors UNE SEULE FOIS au démarrage
index = {}
for book_name, data in index_raw.items():
    # Sécurité : vérifier que chunk_embeddings n'est pas vide
    if "chunk_embeddings" in data and len(data["chunk_embeddings"]) > 0:
        index[book_name] = {
            # On crée le Tensor ici. dtype=float32 est crucial pour la vitesse.
            "chunks_emb": torch.tensor(data["chunk_embeddings"], dtype=torch.float32),
            "chunks": data.get("chunks", [])
        }
print(f"✅ Index chargé : {len(index)} livres prêts.")


@recherche_book.route('/api/recherche', methods=['POST'])  # POST est standard pour envoyer des données
@cross_origin(origins=['http://localhost:8081'], supports_credentials=True)
def api_recherche():
    try:
        data = request.json
        query = data.get("query", "")
        top_k = int(data.get("top_k", 10))

        if not query:
            return jsonify([])

        # Encoder la requête
        q_vec = model.encode(query, convert_to_tensor=True).float()

        candidates = []

        # --- 1. RECHERCHE ET SCORING ---
        for book_filename, info in index.items():
            # CORRECTION BUG : On utilise le Tensor déjà créé, on ne refait pas torch.tensor()
            book_chunk_embeddings = info["chunks_emb"]

            # Calcul Vectoriel (Rapide)
            # Similarité entre la requête et TOUS les chunks du livre
            cos_scores = util.cos_sim(q_vec, book_chunk_embeddings)[0]

            # A. Le Meilleur Chunk (Peak) - 70% du poids
            best_score_val, best_idx = torch.max(cos_scores, dim=0)
            best_chunk_score = best_score_val.item()

            # B. La Densité (Moyenne du Top 3) - 30% du poids
            # Cela favorise les livres qui parlent beaucoup du sujet
            k_density = min(3, len(cos_scores))
            if k_density > 0:
                top_n_values, _ = torch.topk(cos_scores, k_density)
                density_score = torch.mean(top_n_values).item()
            else:
                density_score = best_chunk_score

            # Score Pondéré
            final_score = (0.7 * best_chunk_score) + (0.3 * density_score)

            # --- SEUIL 1 : FILTRE ABSOLU (NETTOYAGE DU BRUIT) ---
            # Si le score est inférieur à 0.25, c'est probablement hors sujet.
            if final_score > 0.25:
                candidates.append({
                    "book": book_filename,
                    "final_score": final_score,
                    "best_chunk_idx": best_idx.item(),
                    "pdf_url": f"{book_filename}"
                })

        # Trier les résultats par pertinence
        candidates.sort(key=lambda x: x["final_score"], reverse=True)

        # --- SEUIL 2 : FILTRE RELATIF (LOGIQUE GOOGLE) ---
        # Si on a des résultats, on regarde le meilleur score.
        # On élimine ceux qui sont trop loin du "champion".
        final_results = []

        if candidates:
            best_score_overall = candidates[0]["final_score"]

            # On ne garde que les résultats qui ont au moins 70% de la pertinence du premier
            # Ex: Si le 1er a 0.80, on rejette tout ce qui est sous 0.56
            cutoff_ratio = 0.7

            for c in candidates:
                if c["final_score"] >= (best_score_overall * cutoff_ratio):
                    print("finl scor",c["final_score"])
                    final_results.append(c)
                else:
                    # Dès qu'on tombe sous le seuil relatif, on arrête (car la liste est triée)
                    break

        # Limiter au Top K demandé
        final_results = final_results[:top_k]

        # --- 2. RÉCUPÉRATION DES MÉTADONNÉES ---
        results_json = []
        for c in final_results:

            # Nettoyage Titre
            title_clean = book_title(c["book"])
            if not title_clean: title_clean = c["book"].replace(".pdf", "")

            # Charger JSON Metadata
            # Attention au chemin : dossier_livres/MesLivresMetadata/Titre.json
            meta_path = os.path.join(dossier_livres, "MesLivresMetadata", f"{title_clean}.json")

            book_info = {}
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        book_info = json.load(f)
                except:
                    print(f"Erreur lecture JSON pour {title_clean}")

            # Ajout des infos de recherche
            book_info["filename"] = c["book"]
            book_info["relevance_score"] = round(c["final_score"], 4)  # Score lisible
            book_info["pdfUrl"]=c["pdf_url"]

            # Récupération du Snippet (Extrait de texte)
            try:
                chunk_data = index[c["book"]]["chunks"][c["best_chunk_idx"]]
                book_info["snippet"] = chunk_data.get("text_preview", "...")
                book_info["page_match"] = chunk_data.get("page_guess", "?")
            except:
                book_info["snippet"] = "Aperçu non disponible"

            results_json.append(book_info)

        return jsonify(results_json)

    except Exception as e:
        print(f"ERREUR API : {e}")
        return jsonify({"error": str(e)}), 500