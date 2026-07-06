"""Démo Streamlit du pipeline jouet : upload d'une image, prédiction, affichage.

Lancer avec `streamlit run app/streamlit_app.py` depuis la racine du projet.
Utilise toy_predict (pas de vrai modèle) : ça sert à visualiser le format de
sortie et les garde-fous, pas à évaluer une vraie performance médicale.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
import streamlit as st
from PIL import Image

from src.inference import toy_predict
from src.guardrails import apply_safety_guardrails

st.set_page_config(page_title="Assistant radiologue virtuel", layout="wide")
st.title("Assistant radiologue virtuel — prototype pédagogique")
st.warning("Prototype pédagogique. Non destiné au diagnostic. Validation par un professionnel qualifié requise.")

uploaded = st.file_uploader("Déposer une radiographie thoracique frontale", type=["png", "jpg", "jpeg"])
mode = st.selectbox("Mode", ["baseline", "improved"])

if uploaded:
    # toy_predict attend un chemin de fichier, pas un objet en mémoire : on
    # réécrit donc l'upload sur disque dans un fichier temporaire avant de l'utiliser.
    suffix = Path(uploaded.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.read())
        tmp_path = Path(tmp.name)

    # Image à gauche, résultat de la prédiction à droite.
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(Image.open(tmp_path), caption="Image uploadée", use_container_width=True)
    with col2:
        pred = apply_safety_guardrails(toy_predict(tmp_path, mode=mode))
        st.metric("Classe", pred["predicted_class"])
        st.metric("Confiance", pred["confidence"])
        st.write("**Observations**", pred["visual_evidence"])
        st.write("**Justification**", pred["justification"])
        st.write("**Limites**", pred["limitations"])
        st.json(pred)
else:
    st.info("Utiliser les images synthétiques dans data/sample_images pour tester le flux.")
