from pathlib import Path
import csv
import numpy as np
from PIL import Image

RSNA_ROOT = Path('data/RSNA/Training')
IMAGES_DIR = RSNA_ROOT / 'Images'
MASKS_DIR = RSNA_ROOT / 'Masks'
OUT_CSV = Path('data/rsna_samples.csv')

rows = []
for mask_path in sorted(MASKS_DIR.glob('*.png')): 
# glob sélectionne tous les fichiers PNG dans le répertoire Masks.
    image_path = IMAGES_DIR / mask_path.name
    # le mask et l'image correspondant partagent le même nom de fichier.

    if not image_path.exists(): # si l'image n'existe pas, on ignore ce mask.
        continue

    # convertit le mask en niveaux de gris (0 ou 255).
    mask_arr = np.array(Image.open(mask_path).convert('L'))

    # Les masques RSNA sont binaires : 0 pour le fond, 255 pour les zones d'opacité.
    label = 'suspected_opacity' if np.any(mask_arr > 0) else 'normal'
    rows.append(
        {
            'case_id': mask_path.stem,  # nom du fichier sans extension.
            'image_path': str(image_path.relative_to(Path('.'))),  # chemin relatif.
            'label': label,
            'quality' : '',
            'split' : 'RSNA'
        }
    )

f = OUT_CSV.open('w', newline='', encoding='utf-8')
try:
    # Écriture du CSV avec les en-têtes et les lignes collectées.
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    # Écriture de l'en-tête et des lignes dans le fichier CSV.
    w.writeheader()
    # Écriture de toutes les lignes collectées dans le fichier CSV.
    w.writerows(rows)
finally:
    # Fermeture du fichier pour s'assurer que les données sont bien sauvegardées.
    f.close()

print(f'{len(rows)} cas écrits dans {OUT_CSV}')
n_opacity = sum(1 for r in rows if r['label'] == 'suspected_opacity')
print(f'  suspected_opacity : {n_opacity}')
print(f'  normal            : {len(rows) - n_opacity}')  