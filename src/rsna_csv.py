"""Génération des CSV de split train/test pour la dataset RSNA.

Ce script reproduit le split physique de Kaggle (dossiers Training/ vs Test/)
et produit deux fichiers CSV :
    - data/RSNA/train.csv : images d'entraînement avec label
    - data/RSNA/test.csv  : images de test SANS label (inférence seule)

Sources de labels :
    - Le split provient de l'arborescence des dossiers, PAS d'une colonne.
    - Les labels train proviennent de stage2_train_metadata.csv.
    - Le test RSNA n'a pas de labels publics -> colonne 'label' laissée vide.

Mapping des 3 classes RSNA vers le schéma du projet (3 classes) :
    Normal                        -> normal
    Lung Opacity (Target == 1)    -> suspected_opacity
    No Lung Opacity / Not Normal  -> uncertain

Colonnes de sortie (alignées sur run_evaluation.py) :
    case_id, image_path, label

Exécution locale (JupyterLab / terminal) :
    python rsna_csv.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


DATA_ROOT = Path("data/RSNA")
TRAIN_IMAGES_DIR = DATA_ROOT / "Training" / "Images"
TEST_IMAGES_DIR = DATA_ROOT / "Test"

# Métadonnées Kaggle brutes
TRAIN_META = DATA_ROOT / "stage2_train_metadata.csv"
TEST_META = DATA_ROOT / "stage2_test_metadata.csv"

# Sorties
TRAIN_CSV_OUT = DATA_ROOT / "rsna_train.csv"
TEST_CSV_OUT = DATA_ROOT / "rsna_test.csv"

IMG_SUFFIX = ".png"

# --- Mapping des classes ---------------------------------------------------

# La colonne 'class' de RSNA porte 3 valeurs distinctes.
CLASS_MAP = {
    "Normal": "normal",
    "Lung Opacity": "suspected_opacity",
    "No Lung Opacity / Not Normal": "uncertain",
}


def build_train_csv() -> pd.DataFrame:
    """Construit le CSV d'entraînement à partir des métadonnées + images présentes."""
    meta = pd.read_csv(TRAIN_META)

    # RSNA contient une ligne PAR bbox : un patient "Lung Opacity" avec plusieurs
    # opacités apparaît plusieurs fois. On déduplique au niveau patientId.
    # La classe est identique sur toutes les lignes d'un même patient.
    meta = meta.drop_duplicates(subset="patientId", keep="first")

    # Mapping des 3 classes RSNA vers le schéma du projet.
    meta["label"] = meta["class"].map(CLASS_MAP)

    # Garde-fou : toute classe non mappée doit être signalée, pas ignorée.
    unmapped = meta["label"].isna()
    if unmapped.any():
        bad = meta.loc[unmapped, "class"].unique().tolist()
        raise ValueError(f"Classe(s) RSNA non mappée(s) : {bad}")

    # Ne conserver que les images réellement présentes sur le disque.
    # (Le sous-ensemble téléchargé peut être plus petit que les métadonnées.)
    present = {p.stem for p in TRAIN_IMAGES_DIR.glob(f"*{IMG_SUFFIX}")}
    if not present:
        raise FileNotFoundError(
            f"Aucune image {IMG_SUFFIX} trouvée dans {TRAIN_IMAGES_DIR}"
        )
    meta = meta[meta["patientId"].isin(present)].copy()

    # Chemin relatif de l'image, exploitable directement par la pipeline.
    meta["image_path"] = meta["patientId"].apply(
        lambda pid: str(TRAIN_IMAGES_DIR / f"{pid}{IMG_SUFFIX}")
    )

    # run_evaluation.py lit case["case_id"] : on renomme patientId en case_id.
    meta = meta.rename(columns={"patientId": "case_id"})

    df = meta[["case_id", "image_path", "label"]].reset_index(drop=True)
    return df.sort_values("case_id").reset_index(drop=True)


def build_test_csv() -> pd.DataFrame:
    """Construit le CSV de test : images sans label (labels RSNA non publics)."""
    meta = pd.read_csv(TEST_META)
    meta = meta.drop_duplicates(subset="patientId", keep="first")

    present = {p.stem for p in TEST_IMAGES_DIR.glob(f"*{IMG_SUFFIX}")}
    if not present:
        raise FileNotFoundError(
            f"Aucune image {IMG_SUFFIX} trouvée dans {TEST_IMAGES_DIR}"
        )
    meta = meta[meta["patientId"].isin(present)].copy()

    meta["image_path"] = meta["patientId"].apply(
        lambda pid: str(TEST_IMAGES_DIR / f"{pid}{IMG_SUFFIX}")
    )

    # Colonne 'label' vide : le test sert à l'inférence, pas à l'évaluation supervisée.
    meta["label"] = ""

    # run_evaluation.py lit case["case_id"] : on renomme patientId en case_id.
    meta = meta.rename(columns={"patientId": "case_id"})

    df = meta[["case_id", "image_path", "label"]].reset_index(drop=True)
    return df.sort_values("case_id").reset_index(drop=True)


def main() -> None:
    train_df = build_train_csv()
    test_df = build_test_csv()

    TRAIN_CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(TRAIN_CSV_OUT, index=False)
    test_df.to_csv(TEST_CSV_OUT, index=False)

    # Récapitulatif de contrôle.
    print(f"[train] {len(train_df)} images -> {TRAIN_CSV_OUT}")
    print(train_df["label"].value_counts().to_string())
    print(f"\n[test]  {len(test_df)} images (sans label) -> {TEST_CSV_OUT}")


if __name__ == "__main__":
    main()
