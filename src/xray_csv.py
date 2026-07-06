from __future__ import annotations

import csv
import os
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

DATA_ROOT = ROOT / "data" / "chest_xray"
OUT_TRAIN_CSV = ROOT / "data" / "chest_xray_train.csv"
OUT_TEST_CSV = ROOT / "data" / "chest_xray_test.csv"

IMG_EXTS = {".jpeg", ".jpg", ".png"}

# Correspondance entre le dossier Kaggle et les labels du projet (avant reclassement par score de confiance)
LABEL_MAP = {
    "NORMAL": "normal",
    "PNEUMONIA": "suspected_opacity",
}

ALL_LABELS = ["normal", "suspected_opacity", "uncertain"]

# permet de reproduire les splits train/val à effectif fixe par classe, pour
# éviter que le shuffle aléatoire ne change la composition du dataset à chaque exécution.
SEED = 42

# Score de confiance qualité (contraste + netteté), relatif au dataset traité
QUALITY_SIZE = 64  # downscale pour accélérer le calcul sur de gros volumes
CONFIDENCE_PERCENTILE = 15  # les X% scores les plus bas sont classés "uncertain"

# Paramètres du split (à ajuster selon les ressources GPU disponibles)
N_PER_CLASS_TRAIN = 640
N_PER_CLASS_TEST = 160


# Étape 1 — indexation brute des images sur disque.
def index_raw_cases():
    """
    Parcourt train/, test/, val/ et indexe chaque image avec son label
    de dossier. case_id préfixé par le split Kaggle pour éviter les
    collisions entre fichiers de même nom dans des dossiers différents.
    """
    all_imgs = [p for p in DATA_ROOT.rglob("*") if p.suffix.lower() in IMG_EXTS]
    print(f"{len(all_imgs)} images trouvées sur disque")

    cases_raw: list[dict] = []
    for p in all_imgs:
        folder = p.parent.name.upper() # NORMAL / PNEUMONIA
        if folder not in LABEL_MAP:
            continue
        kaggle_split = p.parent.parent.name.lower()  # train / test / val
        case_id = f"{kaggle_split}_{p.stem}"
        cases_raw.append({
            "case_id": case_id,
            "label": LABEL_MAP[folder],
            "image_path": p,
        })

    print(f"{len(cases_raw)} cas valides indexés")
    print("Distribution :", Counter(c["label"] for c in cases_raw))
    return cases_raw


# Étape 2 — déduplication et filtrage des fichiers parasites.
def deduplicate(cases_raw: list[dict]):
    """
    Déduplique sur (case_id, label) et exclut __MACOSX / ._* / fichiers
    cachés, qui apparaissent fréquemment dans les archives zip Kaggle
    décompressées sur macOS.
    """
    seen = set()
    cases = []
    n_skipped_junk = 0
    for c in cases_raw:
        path_str = str(c["image_path"])
        basename = c["image_path"].name
        if "__MACOSX" in path_str or basename.startswith("._") or basename.startswith("."):
            n_skipped_junk += 1
            continue
        key = (c["case_id"], c["label"])
        if key in seen:
            continue
        seen.add(key)
        cases.append(c)

    print(f"Après déduplication : {len(cases)} cas (was {len(cases_raw)})")
    if n_skipped_junk:
        print(f"  dont {n_skipped_junk} fichiers parasites ignorés (__MACOSX / ._*)")
    print("Distribution (label dossier) :", Counter(c["label"] for c in cases))
    return cases


# Étape 3 — score de confiance qualité (contraste + netteté).
def quality_metrics(image_path: Path):
    """
    Retourne (contraste, netteté) bruts pour une image, sur une version
    réduite. Retourne None si le fichier n'est pas une image lisible.
    """
    try:
        img = Image.open(image_path).convert("L").resize((QUALITY_SIZE, QUALITY_SIZE))
    except Exception as e:
        print(f"  Image illisible ignorée : {image_path} ({e})")
        return None

    arr = np.asarray(img, dtype=np.float32)
    contrast = float(arr.std())

    edges = np.asarray(img.filter(ImageFilter.FIND_EDGES), dtype=np.float32)
    sharpness = float(edges.std())

    return contrast, sharpness


def min_max_norm(x: np.ndarray):
    """
    Normalisation min-max indépendante de chaque métrique.
    """
    low, high = x.min(), x.max()
    if high - low < 1e-8:
        # Si toutes les valeurs sont identiques, on retourne un tableau de 0.5
        # Cela évite la division par zéro et place toutes les images au milieu de l'échelle de confiance.
        return np.full_like(x, 0.5)
    return (x - low) / (high - low)


def compute_confidence_and_reclassify(cases: list[dict]):
    """
    Calcule le score de confiance par image, puis reclasse en
    "uncertain" les CONFIDENCE_PERCENTILE % de scores les plus bas.

    Le seuil est calculé dynamiquement par percentile sur le lot traité
    (pas une valeur fixe) — évite qu'une distribution à longue queue 
    (ie. quelques images avec des scores très éloignés de la majorité)
    n'écrase la quasi-totalité du dataset en "uncertain" après
    normalisation min-max. La classe d'origine (avant reclassement) est
    conservée dans true_label, pour analyse d'erreurs ultérieure.
    """
    print(f"Calcul du score de confiance qualité sur {len(cases)} images "
          f"(peut prendre quelques minutes)...")

    raw_metrics_all = [quality_metrics(c["image_path"]) for c in cases]

    # Ne garder que les cas dont l'image a pu être lue, pour rester synchronisé
    paired = [(c, m) for c, m in zip(cases, raw_metrics_all) if m is not None]
    n_unreadable = len(cases) - len(paired)
    if n_unreadable:
        print(f"{n_unreadable} image(s) illisible(s) exclue(s) du dataset.")
    cases = [c for c, m in paired]
    raw_metrics = [m for c, m in paired]

    # si aucune image n'est lisible, on retourne une liste vide pour éviter des erreurs plus loin
    if not cases:
        return []

    contrasts = np.array([m[0] for m in raw_metrics])
    sharpnesses = np.array([m[1] for m in raw_metrics])

    confidence_scores = (min_max_norm(contrasts) + min_max_norm(sharpnesses)) / 2.0

    threshold = np.percentile(confidence_scores, CONFIDENCE_PERCENTILE)

    n_reclassified = 0
    for c, score in zip(cases, confidence_scores):
        c["confidence"] = round(float(score), 4)
        c["true_label"] = c["label"]
        if score < threshold:
            c["label"] = "uncertain"
            n_reclassified += 1

    print(f"Seuil de confiance calculé : {threshold:.4f} (percentile {CONFIDENCE_PERCENTILE})")
    print(f'{n_reclassified} cas reclassés "uncertain"')
    print("Distribution (3 classes) :", Counter(c["label"] for c in cases))
    return cases


# Étape 4 — split train/test à effectif fixe par classe.
def split_train_test(cases: list[dict], seed: int = SEED):
    """
    Split stratifié à effectif fixe par classe : exactement
    N_PER_CLASS_TRAIN et N_PER_CLASS_TEST cas pour chacune des 3 classes,
    dans la limite des effectifs disponibles. Garantit un dataset
    d'entraînement équilibré, indépendamment du ratio naturel du dataset
    source (qui est environ 3:1 PNEUMONIA:NORMAL sur Kaggle).
    """
    random.seed(seed)
    train_cases, test_cases = [], []
    for label in ALL_LABELS:
        subset = [c for c in cases if c["label"] == label]
        if len(subset) == 0:
            print(f'  Classe "{label}" absente du dataset.')
            continue
        random.shuffle(subset)
        n_train = min(N_PER_CLASS_TRAIN, max(0, len(subset) - N_PER_CLASS_TEST))
        n_test = min(N_PER_CLASS_TEST, len(subset) - n_train)
        train_cases.extend(subset[:n_train])
        test_cases.extend(subset[n_train:n_train + n_test])
        print(f"  {label:<20} -> train={n_train}, test={n_test}  (dispo={len(subset)})")

    random.seed(seed)
    random.shuffle(train_cases)
    random.shuffle(test_cases)

    print(f"\nTrain total : {len(train_cases)} | Test total : {len(test_cases)}")
    print("Train dist :", Counter(c["label"] for c in train_cases))
    print("Test dist   :", Counter(c["label"] for c in test_cases))
    return train_cases, test_cases


# Écriture CSV — format attendu par eval/run_evaluation.py.
def write_csv(path: Path, rows: list[dict], split_name: str):
    """Écrit un split (train ou test) au format case_id/image_path/label/true_label/confidence."""
    if not rows:
        print(f"Aucune ligne pour {split_name}, fichier non créé.")
        return
    fieldnames = ["case_id", "image_path", "label", "true_label", "confidence"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({
                "case_id": row["case_id"],
                "image_path": str(row["image_path"].relative_to(ROOT))
                    if isinstance(row["image_path"], Path) else row["image_path"],
                "label": row["label"],
                "true_label": row.get("true_label", row["label"]),
                "confidence": row.get("confidence", ""),
            })


def main():
    """Pipeline complet : indexation -> déduplication -> score qualité -> split -> écriture CSV."""
    cases_raw = index_raw_cases()
    cases = deduplicate(cases_raw)
    cases = compute_confidence_and_reclassify(cases)
    train_cases, test_cases = split_train_test(cases)

    write_csv(OUT_TRAIN_CSV, train_cases, split_name="train")
    write_csv(OUT_TEST_CSV, test_cases, split_name="test")

    print(f"\nFichiers écrits :\n  {OUT_TRAIN_CSV}\n  {OUT_TEST_CSV}")


if __name__ == "__main__":
    main()