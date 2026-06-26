from __future__ import annotations

from pathlib import Path
from PIL import Image

# Librairie pour manipuler les images médicales au format DICOM,
# souvent utilisées pour les radiographies avec du windowing.
from pydicom import pixels 

import numpy as np

# Liste des extensions de fichiers autorisées.
ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp"}

# Taille cible pour MedGemma (entrée attendue : 512×512 ou 896×896 selon la config)
DEFAULT_SIZE = (512, 512)

# Seuils de qualité (sur image en niveaux de gris, valeurs 0–255)
MIN_MEAN_BRIGHTNESS = 20       # image trop sombre / rien n'est visible
MAX_MEAN_BRIGHTNESS = 235      # image surexposée / saturée
MIN_STD_DEV = 15               # image trop uniforme / blanc/noir pur, sans de contenu
MIN_EDGE_DENSITY = 0.01        # ratio de pixels de bord détectés (Laplacien) — si trop faible, l'image est probablement floue ou vide.


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
    pixels = list(gray.getdata()) # Récupère les valeurs de pixels en niveaux de gris (0-255).
 
    pixels_arr = np.array(pixels)
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
    """
    Variance du Laplacien discret 3×3 — mesure de netteté/contenu.
    """
 
    w, h = gray.size
    pixels = gray.load()
 
    laplacian_vals = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            # lap = -voisins + 8 * pixel_central
            lap = (
                - pixels[x - 1, y - 1] - pixels[x, y - 1] - pixels[x + 1, y - 1]
                - pixels[x - 1, y]    + 8 * pixels[x, y]  - pixels[x + 1, y]
                - pixels[x - 1, y + 1] - pixels[x, y + 1] - pixels[x + 1, y + 1]
            )
            laplacian_vals.append(lap)
 
    # Si aucun pixel n'a été traité (image trop petite),
    # on retourne 0.0 pour éviter une division par zéro.
    if not laplacian_vals:
        return 0.0
    mean_lap = sum(laplacian_vals) / len(laplacian_vals)
    variance = sum((v - mean_lap) ** 2 for v in laplacian_vals) / len(laplacian_vals)
    
    return variance

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