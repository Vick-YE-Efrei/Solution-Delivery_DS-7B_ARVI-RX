from __future__ import annotations

from pathlib import Path
from PIL import Image

import numpy as np

# Liste des extensions de fichiers autorisées.
ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp"}

# Taille cible pour MedGemma (entrée attendue : 512×512 ou 896×896 selon la config)
DEFAULT_SIZE = (512, 512)

# Seuils de qualité (sur image en niveaux de gris, valeurs 0–255)
MIN_MEAN_BRIGHTNESS = 20       # image trop sombre / rien n'est visible
MAX_MEAN_BRIGHTNESS = 235      # image surexposée / saturée
MIN_STD_DEV = 5                # image trop uniforme / blanc/noir pur, sans de contenu
MIN_EDGE_DENSITY = 0.001       # ratio de pixels de bord détectés (Laplacien) — si trop faible, l'image est probablement floue ou vide.


def load_image(path: str | Path, size: tuple[int, int] = DEFAULT_SIZE):
    """Load an image safely for the educational prototype.

    This function intentionally keeps preprocessing minimal. For real CXR work,
    DICOM metadata, windowing, projection and acquisition details should be handled
    explicitly and documented.
    """
    path = Path(path)
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError(f"Unsupported image format: {path.suffix}")
    img = Image.open(path).convert("RGB")
    return img.resize(size, resample=Image.LANCZOS) #Filtre de référence pour les images 

def _compute_image_stats(img: Image.Image):
    """
    Calcule des statistiques simples sur l'image en niveaux de gris.
    """
    gray = img.convert("L") # Convertit l'image RGB en niveaux de gris.
    pixels_arr = np.array(gray)

    mean_val = float(pixels_arr.mean())
    std_val  = float(pixels_arr.std())

    # Détection de bords par un filtre Laplacien simplifié (variance du Laplacien)
    # On approxime avec la variance locale pour ramener à une échelle comparable avec l'image.
    edge_density = _laplacian_variance(gray) / (255.0 ** 2)
 
    return {
        "mean_brightness": round(mean_val, 2),
        "std_dev": round(std_val, 2),
        "edge_density": round(edge_density, 4),
    }

def _laplacian_variance(gray: Image.Image):
    """Variance du Laplacien discret 3×3 — mesure de netteté/contenu."""
    arr = np.array(gray, dtype=np.float32)
    lap = (
        - arr[:-2, :-2] - arr[:-2, 1:-1] - arr[:-2, 2:]
        - arr[1:-1, :-2] + 8 * arr[1:-1, 1:-1] - arr[1:-1, 2:]
        - arr[2:, :-2]  - arr[2:, 1:-1]  - arr[2:, 2:]
    )

    # On vérifie que le Laplacien n'est pas vide (image trop petite ou uniforme).
    if lap.size == 0:
        return 0.0
    
    return float(lap.var())

# def basic_quality_flag(path: str | Path) -> str:
#     """Toy quality flag based on filename metadata.

#     Replace this with real image-quality checks in a serious implementation.
#     """
#     name = Path(path).name.lower()
#     if "uncertain" in name or "limited" in name:
#         return "limited"
#     return "good"
    

def basic_quality_flag(path: str | Path):
    """
    Toy quality flag based on filename metadata.
    """
    path = Path(path)
    if not path.exists():
        # Si le fichier n'existe pas, 
        # on retourne "poor" pour signaler un problème.
        return "poor"

    try:
        img = load_image(path)
    except Exception:
        return "poor"
    
    img_stats = _compute_image_stats(img)
    img_mean_bright = img_stats["mean_brightness"]
    img_std_dev  = img_stats["std_dev"]
    img_edge_density = img_stats["edge_density"]

    # Ici, on considère l'écart-type 
    # = [0;15] comme une image trop uniforme (mauvaise qualité).
    # = [15;30] comme une image de qualité limitée (à interpréter avec prudence).
    # >= 30 comme une image de bonne qualité (exploitable par le VLM).

    # On filtre les images de mauvaise qualité selon les seuils définis.
    if img_mean_bright < MIN_MEAN_BRIGHTNESS or img_mean_bright > MAX_MEAN_BRIGHTNESS:
        return "poor"
    if img_std_dev < MIN_STD_DEV:
        return "poor"
    
    # On identifie les images de qualité limitée mais encore utilisables.
    if img_edge_density < MIN_EDGE_DENSITY:
        return "limited"
    if img_std_dev < MIN_STD_DEV * 2:
        return "limited"
    
    return "good"
