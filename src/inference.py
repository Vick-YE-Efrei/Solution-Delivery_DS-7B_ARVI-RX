from __future__ import annotations

import re
from pathlib import Path
import time
from typing import Any
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText, BitsAndBytesConfig
from peft import PeftModel

from .preprocessing import basic_quality_flag

WARNING = "Prototype pédagogique. Non destiné au diagnostic. Validation par un professionnel qualifié requise."

_ROOT = Path(__file__).resolve().parents[1]

# Les modèles/processeurs HuggingFace sont lourds à charger (plusieurs secondes à
# quelques minutes) : on les garde en mémoire une fois chargés plutôt que de les
# recharger à chaque appel de vlm_predict_medgemma.
_processor_cache: dict[str, Any] = {}
_model_cache: dict[str, Any] = {}

# Classification par mots-clés, même logique que dans le notebook d'inférence.
_OPACITY_KW = [
    "opacity", "opacities", "opacified", "opacification",
    "consolidation", "consolidations", "pneumonia", "infiltrate",
    "infiltration", "airspace", "air space", "effusion", "effusions",
    "haziness", "hazy", "nodule", "nodules", "mass", "masses",
    "atelectasis", "density", "densities", "reticular",
]
_NORMAL_KW = [
    "normal", "clear", "unremarkable", "no acute", "no focal",
    "within normal limits", "no abnormal", "no significant",
]
_CLEAR_KW = ["clear"]
_HEDGE_KW = [
    "possible", "possibly", "may represent", "cannot exclude",
    "cannot be excluded", "difficult to assess", "questionable",
    "equivocal", "suboptimal", "underpenetrated", "poorly",
    "low lung volumes", "suspicious", "concerning for",
]
_NEG_TERMS = ["no", "without", "free of", "negative for", "absence of"]


def _positive_hit(text: str, keywords: list[str]) :
    """Cherche le premier mot-clé présent dans text qui n'est pas nié juste avant.

    Renvoie le mot-clé trouvé (utile pour la justification), ou None si aucun
    des keywords n'apparaît "positivement". On regarde les 150 caractères qui
    précèdent chaque occurrence pour repérer une négation même un peu éloignée
    dans la phrase (ex: "without focal consolidation, pleural effusion").
    """
    t = text.lower()
    for k in keywords:
        for m in re.finditer(re.escape(k), t):
            # Fenêtre élargie à 150 chars pour capturer les négations distantes
            # ex: "without focal consolidation, pleural effusion" (~38 chars)
            ctx = t[max(0, m.start() - 150):m.start()]
            if any(re.search(rf"\b{re.escape(n)}\b", ctx) for n in _NEG_TERMS):
                continue  # le mot-clé est nié dans son contexte, on ne le compte pas
            return k
    return None


def _classify_from_text(text: str) :
    """Transforme la description en texte libre générée par le VLM en une classe du projet.

    Logique de décision, dans l'ordre :
    - un terme d'opacité ET "clear" en même temps → contradictoire, on reste prudent (uncertain) ;
    - un terme d'opacité seul → suspected_opacity ;
    - un langage de type "possible/questionable/suboptimal" → le modèle hésite, on suit (uncertain) ;
    - un terme "normal/clear/unremarkable" → normal ;
    - rien de tout ça → on ne force pas une classe qu'on ne peut pas justifier (uncertain).
    Les confidences (0.50/0.70) sont des heuristiques fixes, pas des probabilités calibrées.
    """
    op    = _positive_hit(text, _OPACITY_KW)
    clear = _positive_hit(text, _CLEAR_KW)
    hedge = _positive_hit(text, _HEDGE_KW)

    if op and clear:
        return "uncertain", 0.50, [f"ambigu : '{op}' + 'clear'"]
    if op:
        return "suspected_opacity", 0.70, [f"terme détecté : '{op}'"]
    if hedge:
        return "uncertain", 0.50, [f"langage d'incertitude : '{hedge}'"]
    norm = _positive_hit(text, _NORMAL_KW)
    if norm:
        return "normal", 0.70, [f"terme détecté : '{norm}'"]
    return "uncertain", 0.50, ["aucun terme discriminant clair"]


# Chargement du modèle réel (VLM), utilisé par vlm_predict_medgemma.

def toy_predict(image_path: str | Path, mode: str = "baseline"):
    """Prédicteur jouet, déterministe : il lit la classe attendue dans le nom du fichier.

    Ça n'a rien d'un vrai modèle — c'est fait exprès, pour valider tout le reste du
    pipeline (garde-fous, métriques, format JSON, base SQLite...) sans dépendre d'un
    modèle réel. En mode "improved" la confiance est légèrement plus basse : on
    simule un système un peu plus prudent que la baseline.
    """
    start   = time.perf_counter()
    name    = Path(image_path).name.lower()
    quality = basic_quality_flag(image_path)

    if "suspected_opacity" in name:
        pred          = "suspected_opacity"
        conf          = 0.78 if mode == "baseline" else 0.72
        evidence      = ["synthetic opacity-like area visible in the lung field"]
        justification = "The synthetic image contains a localized brighter region compatible with the toy opacity class."
    elif "normal" in name:
        pred          = "normal"
        conf          = 0.72 if mode == "baseline" else 0.68
        evidence      = ["no synthetic opacity marker detected"]
        justification = "The synthetic image does not contain the opacity marker used by the toy generator."
    else:
        pred          = "uncertain"
        conf          = 0.52
        evidence      = ["limited synthetic image quality"]
        justification = "The image is treated as limited quality in the toy catalog."

    return {
        "image_quality":   quality,
        "predicted_class": pred,
        "confidence":      round(float(conf), 3),
        "visual_evidence": evidence,
        "justification":   justification,
        "limitations":     ["synthetic toy image", "no clinical context", "not a validated medical model"],
        "warning":         WARNING,
        "model_name":      f"toy-rule-{mode}",
        "prompt_version":  f"{mode}_v1",
        "latency_ms":      int((time.perf_counter() - start) * 1000),
    }


def _load_model(model_id: str, lora_path: str | None):
    """Charge (ou récupère depuis le cache) le processor et le modèle pour model_id.

    Sur GPU, le modèle est chargé en 4-bit (NF4 + double quantization via
    bitsandbytes) pour tenir dans peu de VRAM — c'est ce qui permet de faire tourner
    un modèle de plusieurs milliards de paramètres sur une carte grand public.
    Sans GPU, on retombe sur du float32 CPU : ça marche mais c'est nettement plus lent.
    Si un chemin d'adaptateurs LoRA est fourni et existe, on le greffe par-dessus le
    modèle de base (fine-tuning léger) ; sinon on garde le modèle pré-entraîné tel quel.
    """
    cache_key = f"{model_id}:{lora_path}"
    if cache_key not in _model_cache:
        processor = AutoProcessor.from_pretrained(model_id)

        has_gpu = torch.cuda.is_available()
        if has_gpu:
            vram_gb   = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"[INFO] GPU détecté ({vram_gb:.1f} Go VRAM)")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",           # quantization NF4 : bon compromis précision/mémoire pour des poids ~gaussiens
                bnb_4bit_use_double_quant=True,       # quantifie aussi les constantes de quantization, gagne un peu plus de mémoire
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            base = AutoModelForImageTextToText.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                dtype=torch.bfloat16,
                device_map={"": 0},   # force tout le modèle sur le GPU 0 (pas de split multi-GPU ici)
                low_cpu_mem_usage=True,
            )
        else:
            print("[INFO] Pas de GPU — chargement CPU (lent)")
            base = AutoModelForImageTextToText.from_pretrained(
                model_id,
                dtype=torch.float32,
                low_cpu_mem_usage=True,
            )

        if lora_path and Path(lora_path).exists():
            print(f"[INFO] Chargement adaptateurs LoRA : {lora_path}")
            base = PeftModel.from_pretrained(base, lora_path)
        else:
            print("[INFO] Aucun adaptateur LoRA — modèle de base utilisé")

        base.eval()  # mode inférence : désactive dropout etc., on ne fait pas de training ici
        _processor_cache[cache_key] = processor
        _model_cache[cache_key]     = base

    return _processor_cache[cache_key], _model_cache[cache_key]


def vlm_predict_medgemma(
    image_path: str | Path,
    model_key: str = "medgemma_4b_pt",
    lora_path: str | None = None,
):
    """Inférence réelle avec un VLM (Gemma/MedGemma) : décrit l'image puis classe le texte.

    Contrairement à toy_predict, ici on charge un vrai modèle et on lui fait générer
    une description en langage naturel de la radio, qu'on reclasse ensuite avec
    _classify_from_text (mots-clés). C'est expérimental : la confiance vient de
    règles heuristiques, pas d'une probabilité calibrée par le modèle.
    """
    MODEL_IDS = {
        "gemma_4_E4B":    "google/gemma-4-E4B",
        "medgemma_4b_pt": "google/medgemma-4b-pt",
    }
    model_id = MODEL_IDS.get(model_key, "google/medgemma-4b-pt")

    # Chemin LoRA par défaut si non spécifié
    if lora_path is None:
        default_paths = {
            "medgemma_4b_pt": _ROOT / "finetuning" / "lora_adapters" / "medgemma_4b_pt" / "medgemma_4b_pt",
            "gemma_4_E4B":    _ROOT / "finetuning" / "lora_adapters" / "gemma_4_E4B" / "gemma_4_E4B" / "gemma4_chestxray_lora_adapters",
        }
        candidate = default_paths.get(model_key)
        lora_path = str(candidate) if candidate and candidate.exists() else None

    processor, model = _load_model(model_id, lora_path)
    start = time.perf_counter()

    image = Image.open(image_path).convert("RGB")

    # Prompt description libre — adapté au modèle -pt (non instruction-tuned).
    # boi_token = "beginning of image", le token spécial qui indique au modèle où
    # insérer les embeddings visuels dans la séquence de texte.
    boi    = processor.tokenizer.boi_token
    prompt = (
        f"{boi}\n"
        "You are reading a frontal chest X-ray.\n"
        "Describe the lung fields and state whether there is any opacity, "
        "consolidation, or whether the lungs are clear.\n"
        "Findings:"
    )

    inputs = processor(images=image, text=prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():  # pas d'entraînement ici, inutile de calculer les gradients
        outputs = model.generate(**inputs, max_new_tokens=120, do_sample=False)  # greedy, déterministe

    # generate() renvoie prompt + réponse concaténés : on retire la partie prompt
    # pour ne décoder que ce que le modèle a réellement généré.
    generated = outputs[0][inputs["input_ids"].shape[1]:]
    raw_text  = processor.decode(generated, skip_special_tokens=True)

    pred, conf, evidence = _classify_from_text(raw_text)
    evidence.append(raw_text.strip()[:300])

    lora_used = lora_path and Path(lora_path).exists()
    return {
        "image_quality":   basic_quality_flag(image_path),
        "predicted_class": pred,
        "confidence":      round(float(conf), 3),
        "visual_evidence": evidence,
        "justification":   (
            "Classe déduite par mots-clés depuis la description libre générée "
            f"par {model_key}{'+ LoRA' if lora_used else ' (base)'}. "
            "Résultat expérimental, non clinique."
        ),
        "limitations":     [
            "modèle de base (pt) non instruction-tuned" if not lora_used else "adaptateurs LoRA expérimentaux",
            "classification par mots-clés, non calibrée",
            "confiance heuristique, non probabiliste",
            "pas de contexte clinique",
        ],
        "warning":         WARNING,
        "model_name":      model_key + ("+lora" if lora_used else "-base"),
        "prompt_version":  "findings_v2",
        "latency_ms":      int((time.perf_counter() - start) * 1000),
    }
