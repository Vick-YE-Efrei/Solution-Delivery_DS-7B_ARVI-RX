from __future__ import annotations

from typing import Any

ALLOWED_CLASSES = {"normal", "suspected_opacity", "uncertain"}
REQUIRED_KEYS = {"image_quality", "predicted_class", "confidence", "visual_evidence", "justification", "limitations", "warning"}
WARNING_TEXT = "Prototype pédagogique. Non destiné au diagnostic. Validation par un professionnel qualifié requise."


def validate_prediction(pred: dict[str, Any]):
    """Vérifie qu'une prédiction respecte le contrat JSON attendu.

    Renvoie (True, []) si tout est bon, sinon (False, liste des erreurs trouvées).
    On accumule les erreurs plutôt que de s'arrêter à la première, pour avoir un
    diagnostic complet d'un coup (utile dans les logs/CSV d'évaluation).
    """
    errors: list[str] = []

    # Toutes les clés du schéma doivent être présentes, même si leur valeur est vide.
    missing = REQUIRED_KEYS - set(pred)
    if missing:
        errors.append(f"missing keys: {sorted(missing)}")

    if pred.get("predicted_class") not in ALLOWED_CLASSES:
        errors.append("invalid predicted_class")

    try:
        conf = float(pred.get("confidence", -1))
        if not 0 <= conf <= 1:
            errors.append("confidence outside [0,1]")
    except Exception:
        # confidence n'est même pas convertible en float (mauvais type, None, etc.)
        errors.append("confidence is not numeric")

    if not pred.get("warning"):
        errors.append("warning missing")

    return not errors, errors


def apply_safety_guardrails(pred: dict[str, Any]):
    """Force une sortie sûre par défaut : en cas de doute, on répond "uncertain".

    Trois filets de sécurité successifs :
    1. si le JSON ne respecte pas le contrat, on bascule sur "uncertain" et on
       plafonne la confiance à 0.5 plutôt que de laisser passer une sortie invalide ;
    2. si la qualité d'image est limitée/mauvaise et que la confiance reste faible,
       on préfère l'incertitude à une classe qu'on ne peut pas vraiment justifier ;
    3. le warning "prototype pédagogique" est toujours réécrit, pour ne jamais
       l'oublier même si le modèle ne l'a pas renvoyé.
    """
    valid, errors = validate_prediction(pred)
    if not valid:
        pred["predicted_class"] = "uncertain"
        pred["confidence"] = min(float(pred.get("confidence", 0.0) or 0.0), 0.5)
        pred.setdefault("limitations", []).append("guardrail triggered: invalid output schema")
    if pred.get("image_quality") in {"limited", "poor"} and float(pred.get("confidence", 0)) < 0.6:
        pred["predicted_class"] = "uncertain"
    pred["warning"] = WARNING_TEXT
    pred["guardrail_errors"] = errors  # conservé pour tracer pourquoi le garde-fou s'est déclenché
    return pred
