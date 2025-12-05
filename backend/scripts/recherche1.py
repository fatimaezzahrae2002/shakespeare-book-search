import json
from re import search

import requests
import torch
from flask import Blueprint, request
from flask_cors import cross_origin
import re
import os

from sentence_transformers import SentenceTransformer, util
recherche_book = Blueprint('recherche_book',__name__ )

# Charger le modèle
model = SentenceTransformer("sentence-transformers/bert-base-nli-mean-tokens")
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "index_bert_books.json")
# Charger l'index JSON
with open(json_path, "r", encoding="utf-8") as f:
    index_vecteurs_raw = json.load(f)

# Convertir en Tensors une seule fois pour gagner du temps
index_vecteurs = {}
for doc, vec in index_vecteurs_raw.items():
    index_vecteurs[doc] = torch.tensor(vec, dtype=torch.float32)
dossier_livres =os.path.join(current_dir, "../ressources")
print(f"✅ Initialisation terminée : {len(index_vecteurs)} documents chargés.")
def book_title(filename):
    try:
        # 1. Enlever l'extension .pdf
        clean_name = filename.replace(".pdf", "")

        # 2. Séparer le Titre de l'Auteur
        # On coupe la phrase au moment où on voit " author "
        if " author " in clean_name:
            # part[0] sera le début (21 The Two...), part[1] sera l'auteur
            title_part = clean_name.split(" author ")[0]
        else:
            # Si "author" n'est pas écrit, on prend tout
            title_part = clean_name

        # 3. Nettoyer le numéro au début (21)
        words = title_part.split()

        # Si le premier mot est un nombre (ex: "21"), on l'enlève
        if words and words[0].isdigit():
            words = words[1:]  # On garde tout sauf le 1er élément

        # 4. Reconstituer le titre
        return " ".join(words)

    except Exception as e:
        return None
'''def book_recherche(top_k = 20) :
    data=request.json
    query=data["query"]
    q_vec = model.encode(query, convert_to_tensor=True).float()

    results = []
    for doc, vec_t in index_vecteurs.items():
        titre_courant = book_title(doc)

        # Si book_title renvoie None (erreur), on passe au suivant
        if not titre_courant:
            continue

        score = util.cos_sim(q_vec, vec_t).item()

        # --- LOGIQUE DE COMPARAISON ---
        trouve = False

        # On parcourt les résultats existants avec 'enumerate' pour avoir l'index 'i'
        for i, (existing_title, existing_score) in enumerate(results):
            if existing_title == titre_courant:
                trouve = True
                # C'est ici qu'on compare : Si le nouveau score est plus grand
                if score > existing_score:
                    # On met à jour l'entrée existante avec le nouveau score
                    results[i] = (titre_courant, score)
                break  # On a trouvé le livre, inutile de continuer la boucle interne

        if not trouve:
            if score >= 0.5 :
                results.append((titre_courant, score))
    results.sort(key=lambda x: x[1], reverse=True)
    for doc, score in results:
        print(f"{doc} — {score:.4f}")
    results_search = []
    print()
    for title,score in results:
        with open(f"{dossier_livres}/MesLivresMetadata/{title}.json", "r", encoding="utf-8") as f:
                info_book = json.load(f)
                results_search.append(info_book)


    #return results[:top_k]
    return results_search[:10]
'''
@recherche_book.route('/api/recherche', methods=['POST', 'PUT'])
@cross_origin(origins=['http://localhost:8081'], supports_credentials=True)
def book_recherche(top_k=10):
    data = request.json
    query = data["query"]

    # Embedding de la requête
    q_vec = model.encode(query, convert_to_tensor=True).float()

    results = []

    # Comparaison directe avec un embedding par livre
    for doc, vec_t in index_vecteurs.items():
        titre_courant = book_title(doc)
        if not titre_courant:
            continue

        score = util.cos_sim(q_vec, vec_t).item()

        if score >= 0.0:
            results.append((titre_courant, score))

    # Trier les résultats par score décroissant
    results.sort(key=lambda x: x[1], reverse=True)
    for doc, score in results[:top_k]:
        print(doc, score)

    # Charger les métadonnées
    results_search = []
    for title, score in results:
        metadata_path = f"{dossier_livres}/MesLivresMetadata/{title}.json"
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                info_book = json.load(f)
                info_book["similarity"] = score
                results_search.append(info_book)

    return results_search
if __name__ == "__main__":
    query = input("Enter your query: ")
    results = book_recherche(query)

    print("\nTop results:")

