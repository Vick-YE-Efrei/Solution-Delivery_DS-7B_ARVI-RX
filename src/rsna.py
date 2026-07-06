"""Construit data/rsna_samples.csv à partir des métadonnées RSNA officielles.

Script à lancer une fois, après avoir placé le dataset RSNA (téléchargé sur Kaggle)
dans data/RSNA/. Il relit stage2_train_metadata.csv, ne garde que les patients dont
l'image existe réellement en local, et remappe les 3 classes RSNA vers les labels
du projet (normal / suspected_opacity / uncertain).
"""
from pathlib import Path
import csv

METADATA_CSV = Path('data/RSNA/stage2_train_metadata.csv')
IMAGES_DIR = Path('data/RSNA/Training/Images')
OUT_CSV = Path('data/rsna_samples.csv')

CLASSES = {
    'Normal' : 'normal',
    'Lung Opacity' : 'suspected_opacity',
    # Anomalie autre que la pneumonie (ex. cardiomégalie, fracture, etc.)
    'No Lung Opacity / Not Normal' : 'uncertain'
}

# On ne garde que les patients pour lesquels l'image PNG est réellement présente
# en local : le CSV de métadonnées RSNA référence plus de cas que ce qu'on a téléchargé.
rows = []
with METADATA_CSV.open(encoding='utf-8') as f:
    for row in csv.DictReader(f):
        patient_id = row['patientId']
        image_path = IMAGES_DIR / f'{patient_id}.png'
        if not image_path.exists():
            continue
        label = CLASSES.get(row['class'], 'uncertain')
        rows.append({
            'case_id'   : patient_id,
            'image_path': str(image_path.relative_to(Path('.'))),
            'label'     : label,
            'quality'   : ''
        })
        continue

    # Ancienne approche par masques de segmentation, non utilisée pour ce dataset
    # (RSNA fournit des labels directs par classe, pas de masque à convertir) :
    # # convertit le mask en niveaux de gris (0 ou 255).
    # mask_arr = np.array(Image.open(mask_path).convert('L'))

    # # Les masques RSNA sont binaires : 0 pour le fond, 255 pour les zones d'opacité.
    # label = 'suspected_opacity' if np.any(mask_arr > 0) else 'normal'
    # rows.append(
    #     {
    #         'case_id': mask_path.stem,  # nom du fichier sans extension.
    #         'image_path': str(image_path.relative_to(Path('.'))),  # chemin relatif.
    #         'label': label,
    #         'quality' : '',
    #         'split' : 'RSNA'
    #     }
    # )

# NB : l'écriture du CSV est désactivée ci-dessous (data/rsna_samples.csv est déjà
# généré et versionné) — décommenter pour le régénérer depuis un nouvel export RSNA.
# with OUT_CSV.open('w', newline='', encoding='utf-8') as f:
#     w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
#     w.writeheader()
#     w.writerows(rows)

print(f'{len(rows)} cas trouvés (image + métadonnées) pour {OUT_CSV}')
n_opacity = sum(1 for r in rows if r['label'] == 'suspected_opacity')
n_normal = sum(1 for r in rows if r['label'] == 'normal')
n_limited = sum(1 for r in rows if r['label'] == 'uncertain')

print(f'  suspected_opacity : {n_opacity}')
print(f'  normal            : {n_normal}')
print(f'  limited           : {n_limited}')  