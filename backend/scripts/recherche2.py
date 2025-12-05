import os, json, torch
from flask import Blueprint, request
from flask_cors import cross_origin
from sentence_transformers import SentenceTransformer, util
import numpy as np

from scripts.recherche1 import book_title

recherche_book = Blueprint('recherche_book', __name__)
#model = SentenceTransformer("sentence-transformers/bert-base-nli-mean-tokens")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "index_books_chunks.json")

with open(json_path, "r", encoding="utf-8") as f:
    index_raw = json.load(f)

# convertir en tensors numpy pour rapidité
index = {}
for book_name, data in index_raw.items():
    index[book_name] = {
        # Attention au nom de la clé : dans votre script d'indexation c'était "chunk_embeddings"
        # On convertit la liste de listes en un seul grand Tensor 2D
        "chunks_emb": torch.tensor(data["chunk_embeddings"], dtype=torch.float32),

        # On garde aussi les métadonnées (textes, etc)
        "chunks": data.get("chunks", []),

        # Le vecteur global (agg_embedding) s'il existe
        "agg": torch.tensor(data["agg_embedding"], dtype=torch.float32) if "agg_embedding" in data else None
    }

dossier_livres = os.path.join(current_dir, "../ressources")

@recherche_book.route('/api/recherche', methods=['POST','PUT'])
@cross_origin(origins=['http://localhost:8081'], supports_credentials=True)

def book_recherche():
    data = request.json
    query = data.get("query", "")
    top_k = int(data.get("top_k", 10))

    # Encoder la requête
    q_vec = model.encode(query, convert_to_tensor=True).float()

    candidates = []

    for book_filename, info in index.items():
        # --- 1. Calculer les scores de tous les chunks ---
        # info["chunks_emb"] est supposé être une liste de listes ou un tenseur
        # On calcule la similarité pour TOUS les chunks de ce livre d'un coup
        # Note: Si chunks_emb est une liste Python, convertissez-la en tenseur avant la boucle pour la vitesse
        book_chunk_embeddings = torch.tensor(info["chunks_emb"])  # ou utiliser info["chunks_emb"] si déjà tenseur

        # Cosine similarity entre la requête et tous les chunks du livre
        cos_scores = util.cos_sim(q_vec, book_chunk_embeddings)[0]  # Retourne [score_chunk1, score_chunk2...]

        # --- 2. Stratégie de Ranking ---

        # A. Le meilleur passage (Le "Pic")
        best_score_val, best_idx = torch.max(cos_scores, dim=0)
        best_chunk_score = best_score_val.item()

        # B. La densité de pertinence (Moyenne du Top 3 ou Top 5)
        # Si le livre a peu de chunks, on prend tout, sinon on prend les 3 meilleurs
        k_best = min(3, len(cos_scores))
        top_n_values, _ = torch.topk(cos_scores, k_best)
        density_score = torch.mean(top_n_values).item()

        # --- 3. Score Final Pondéré ---
        # On donne beaucoup de poids au meilleur passage (70%)
        # et un peu de poids au fait que le livre en parle plusieurs fois (30%)
        final_score = (0.7 * best_chunk_score) + (0.3 * density_score)

        # On garde tout (pas de seuil dur), on filtrera à la fin
        # Optionnel : un seuil très bas pour éliminer le bruit total (ex: 0.15)
        if final_score > 0.15:
            candidates.append({
                "book": book_filename,
                "final_score": final_score,
                "best_chunk_score": best_chunk_score,
                "best_chunk_idx": best_idx.item()
            })

    # --- 4. Tri et Récupération ---
    # On trie par le score final calculé
    candidates.sort(key=lambda x: x["final_score"], reverse=True)

    results = []
    # On ne traite que les Top K demandés pour ne pas charger 1000 JSONs
    for c in candidates[:top_k]:

        # Récupération du Titre propre
        title_clean = book_title(c["book"])
        if not title_clean: title_clean = c["book"]  # Fallback

        # Chargement Métadonnées
        meta_path = f"{dossier_livres}/MesLivresMetadata/{title_clean}.json"

        book_info = {}
        # On essaie de charger le JSON, sinon on crée un objet vide
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    book_info = json.load(f)
            except:
                pass  # Fichier corrompu ou erreur lecture

        # On injecte les infos de pertinence
        book_info["filename"] = c["book"]
        book_info["relevance"] = round(c["final_score"], 4)

        # Récupération du texte du meilleur passage (Snippet)
        try:
            # On va chercher dans l'index global l'aperçu du texte
            chunk_data = index[c["book"]]["chunks"][c["best_chunk_idx"]]

            # C'est ici qu'on affiche le texte qui a matché !
            # "text_preview" doit avoir été sauvegardé lors de l'indexation
            book_info["snippet"] = chunk_data.get("text_preview", "Aperçu non disponible")
            book_info["page_estimee"] = chunk_data.get("page_guess", "?")

        except IndexError:
            book_info["snippet"] = "Erreur index snippet"

        results.append(book_info)

    return results
'''def book_recherche():
    data = request.json
    query = data.get("query", "")
    top_k = int(data.get("top_k", 10))

    q_vec = model.encode(query, convert_to_tensor=True).float()

    candidates = []
    for book, info in index.items():
        # score agrégé (rapide)
        agg_score = util.cos_sim(q_vec, info["agg"]).item()

        # score best chunk : on calcule cosine avec chaque chunk (ou seulement un sous-ensemble si nombreux)
        # pour optimiser, on peut vectoriser, mais pour simplicité ici boucle
        best_chunk_score = -1.0
        best_chunk_idx = None
        for i, c_emb in enumerate(info["chunks_emb"]):
            s = util.cos_sim(q_vec, c_emb).item()
            if s > best_chunk_score:
                best_chunk_score = s
                best_chunk_idx = i

        # combiner : pondération (ajuste si besoin)
        combined_score = 0.5 * agg_score + 0.5 * best_chunk_score
        SEUIL = 0.5
        top_n = 5
        chunk_scores = [util.cos_sim(q_vec, c_emb).item() for c_emb in info["chunks_emb"]]
        best_n_scores = sorted(chunk_scores, reverse=True)[:top_n]
        mean_chunk_score = sum(best_n_scores) / len(best_n_scores)
        relevance_score = 0.3 * agg_score + 0.7 * mean_chunk_score
        print(book, relevance_score)
        if relevance_score > SEUIL:


            candidates.append({
                "book": book,
                "agg_score": float(agg_score),
                "best_chunk_score": float(best_chunk_score),
                "combined_score": float(combined_score),
                "best_chunk_idx": best_chunk_idx
            })

    # trier et prendre top_k
    candidates.sort(key=lambda x: x["combined_score"], reverse=True)
    results = []
    for c in candidates[:top_k]:
        # charger métadonnées si disponibles
        title = book_title(c["book"])
        #meta_path = os.path.join(dossier_livres, "MesLivresMetadata", f"{title.replace('.pdf','')}.json")
        meta_path = f"{dossier_livres}/MesLivresMetadata/{title}.json"
        meta = {}
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        # ajouter info chunk preview
        chunk_meta = index[c["book"]]["chunks_meta"][c["best_chunk_idx"]]
        meta["scores"] = {
            "agg_score": c["agg_score"],
            "best_chunk_score": c["best_chunk_score"],
            "combined_score": c["combined_score"]
        }
        meta["best_chunk_preview"] = chunk_meta.get("text_preview","")
        results.append(meta)

    return results
'''