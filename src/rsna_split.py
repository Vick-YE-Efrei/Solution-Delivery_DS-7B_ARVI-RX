"""rsna_split.py — ARVI-RX

Split le fichier rsna_samples.csv (généré par src/rsna.py) en deux CSV
train / test au MÊME format que chest_xray_train.csv / chest_xray_test.csv :
    case_id, image_path, label, true_label, confidence

Le dataset RSNA original n'a pas de split train/test exploitable côté labels
(le dossier Test/ de la compétition Kaggle n'a pas de labels publics), donc on
split rsna_samples.csv lui-même — qui contient les 30 227 cas labellisés du
Training via stage2_train_metadata.csv.

Pipeline :
  1. Chargement de rsna_samples.csv (déjà labellisé : normal /
     suspected_opacity / uncertain, dérivé de la colonne `class` RSNA).
  2. true_label = label d'origine (annotation RSNA). Comme rsna_samples.csv
     ne porte pas de score de confiance, confidence est laissé vide et
     label == true_label (pas de reclassement pixel ici, contrairement à
     chest_xray où la classe uncertain vient d'un score qualité). La classe
     uncertain de RSNA vient déjà de l'annotation "No Lung Opacity / Not
     Normal", pas du preprocessing — voir src/rsna.py.
  3. Split stratifié à effectif fixe par classe : N_PER_CLASS_TEST cas par
     classe pour le test (soit 3 * N_PER_CLASS_TEST images de test au
     total), le reste pour le train, dans la limite de N_PER_CLASS_TRAIN.
     Garantit un test équilibré entre les 3 classes.

Format de sortie identique à chest_xray_*.csv pour que eval/run_evaluation.py
et l'entraînement puissent consommer les deux datasets de la même façon.
"""

from __future__ import annotations

import csv
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

IN_CSV = ROOT / "data" / "rsna_samples.csv"
OUT_TRAIN_CSV = ROOT / "data" / "rsna_train.csv"
OUT_TEST_CSV = ROOT / "data" / "rsna_test.csv"

ALL_LABELS = ["normal", "suspected_opacity", "uncertain"]

SEED = 42

# ~3000 images de test = 1000 par classe (les 3 classes ont > 1000 cas dispo)
N_PER_CLASS_TEST = 1000
# Plafond train par classe (None = prendre tout le reste après le test)
N_PER_CLASS_TRAIN = None


def read_cases(path: Path) -> list[dict]:
    """Charge un CSV de cas (rsna_samples.csv) en liste de dicts, une entrée par ligne."""
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def split_train_test(cases: list[dict], seed: int = SEED) -> tuple[list[dict], list[dict]]:
    """Split stratifié à effectif fixe par classe. Prend d'abord
    N_PER_CLASS_TEST cas par classe pour le test, puis le reste pour le
    train (plafonné à N_PER_CLASS_TRAIN si défini).
    """
    random.seed(seed)
    train_cases, test_cases = [], []

    for label in ALL_LABELS:
        subset = [c for c in cases if c["label"] == label]
        if not subset:
            print(f'  Classe "{label}" absente du dataset.')
            continue
        random.shuffle(subset)

        n_test = min(N_PER_CLASS_TEST, len(subset))
        test_part = subset[:n_test]
        remaining = subset[n_test:]

        if N_PER_CLASS_TRAIN is not None:
            train_part = remaining[:N_PER_CLASS_TRAIN]
        else:
            train_part = remaining

        test_cases.extend(test_part)
        train_cases.extend(train_part)
        print(f"  {label:<20} -> train={len(train_part)}, test={len(test_part)}  (dispo={len(subset)})")

    random.seed(seed)
    random.shuffle(train_cases)
    random.shuffle(test_cases)
    return train_cases, test_cases


def write_csv(path: Path, rows: list[dict]) -> None:
    """Écrit au format chest_xray_*.csv : case_id, image_path, label,
    true_label, confidence.
    """
    if not rows:
        print(f"Aucune ligne à écrire dans {path}.")
        return
    fieldnames = ["case_id", "image_path", "label", "true_label", "confidence"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({
                "case_id": row["case_id"],
                "image_path": row["image_path"],
                "label": row["label"],
                # RSNA : pas de reclassement pixel, la classe vient de
                # l'annotation -> true_label == label
                "true_label": row.get("true_label", row["label"]),
                # rsna_samples.csv ne porte pas de score de confiance
                "confidence": row.get("confidence", ""),
            })


def print_distribution(rows: list[dict], title: str) -> None:
    """Affiche le nombre de cas par classe, pour vérifier à l'œil que le split reste équilibré."""
    counts = Counter(r["label"] for r in rows)
    print(f"\n{title} — {len(rows)} cas")
    for label in ALL_LABELS:
        print(f"  {label:<20}: {counts.get(label, 0)}")


def main() -> None:
    """Point d'entrée CLI : charge rsna_samples.csv, split, écrit les CSV train/test."""
    cases = read_cases(IN_CSV)
    print(f"{len(cases)} cas chargés depuis {IN_CSV.name}")
    print("Distribution :", dict(Counter(c["label"] for c in cases)))
    print()

    train_cases, test_cases = split_train_test(cases)

    write_csv(OUT_TRAIN_CSV, train_cases)
    write_csv(OUT_TEST_CSV, test_cases)

    print_distribution(train_cases, "CSV d'entraînement")
    print_distribution(test_cases, "CSV de test")

    print(f"\nFichiers écrits :\n  {OUT_TRAIN_CSV}\n  {OUT_TEST_CSV}")


if __name__ == "__main__":
    main()
