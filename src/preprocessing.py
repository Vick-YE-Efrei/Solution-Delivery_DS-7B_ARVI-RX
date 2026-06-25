from __future__ import annotations

from importlib.resources import path
from pathlib import Path

from PIL import Image
from pydicom import pixels # Librairie pour manipuler les images médicales au format DICOM, souvent utilisées pour les radiographies.

ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp"}

# Taille cible pour MedGemma (entrée attendue : 512×512 ou 896×896 selon la config)
DEFAULT_SIZE = (512, 512)

# Seuils de qualité (sur image en niveaux de gris, valeurs 0–255)
MIN_MEAN_BRIGHTNESS = 20       # image trop sombre → non diagnostique
MAX_MEAN_BRIGHTNESS = 235      # image surexposée / saturée
MIN_STD_DEV = 15               # image trop uniforme → blanc/noir pur, pas de contenu
MIN_EDGE_DENSITY = 0.01        # ratio de pixels de bord détectés (Laplacien)


def load_image(path: str | Path, size: tuple[int, int] = DEFAULT_SIZE) -> Image.Image:
    """Load an image safely for the educational prototype.

    This function intentionally keeps preprocessing minimal. For real CXR work,
    DICOM metadata, windowing, projection and acquisition details should be handled
    explicitly and documented.
    """
    path = Path(path)
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError(f"Unsupported image format: {path.suffix}")
    img = Image.open(path).convert("RGB")
    return img.resize(size)

def _compute_image_stats(img: Image.Image) -> dict[str, float]:
    """Calcule des statistiques simples sur l'image en niveaux de gris."""
    gray = img.convert("L")

    pixels = list(gray.getdata())
 
    mean_val = sum(pixels) / len(pixels)
    std_val  = (sum((p - mean_val) ** 2 for p in pixels) / len(pixels)) ** 0.5
 
    # Détection de bords par filtre Laplacien simplifié (variance du Laplacien)
    # On approxime avec la variance locale — suffisant pour un flag de qualité jouet.
    edge_density = _laplacian_variance(gray) / (255.0 ** 2)
 
    return {
        "mean_brightness": round(mean_val, 2),
        "std_dev": round(std_val, 2),
        "edge_density": round(edge_density, 4),
    }

def _laplacian_variance(gray: Image.Image) -> float:
    """Variance du Laplacien discret 3×3 — mesure de netteté/contenu."""
    import struct
 
    w, h = gray.size
    pixels = gray.load()
 
    laplacian_vals = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            lap = (
                -pixels[x - 1, y - 1] - pixels[x, y - 1] - pixels[x + 1, y - 1]
                - pixels[x - 1, y]    + 8 * pixels[x, y]  - pixels[x + 1, y]
                - pixels[x - 1, y + 1] - pixels[x, y + 1] - pixels[x + 1, y + 1]
            )
            laplacian_vals.append(lap)
 
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
    

def basic_quality_flag(path: str | Path) -> str:
    """Toy quality flag based on filename metadata.
    """
    try:
        img = load_image(path)
    except Exception:
        return "poor"
    
