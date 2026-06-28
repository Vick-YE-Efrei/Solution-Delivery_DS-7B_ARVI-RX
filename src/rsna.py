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
            'quality'   : '',
            'split'     : 'RSNA',
        })
        continue

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

# with OUT_CSV.open('w', newline='', encoding='utf-8') as f:
#     w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
#     w.writeheader()
#     w.writerows(rows)

print(f'{len(rows)} cas écrits dans {OUT_CSV}')
n_opacity = sum(1 for r in rows if r['label'] == 'suspected_opacity')
n_normal = sum(1 for r in rows if r['label'] == 'normal')
n_limited = sum(1 for r in rows if r['label'] == 'uncertain')

print(f'  suspected_opacity : {n_opacity}')
print(f'  normal            : {n_normal}')
print(f'  limited           : {n_limited}')  