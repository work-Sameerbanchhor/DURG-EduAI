"""
DURG-EduAI — Early Warning System Engine
Author: Sameer Banchhor
DOI: https://doi.org/10.5281/zenodo.18826162
"""


def generate_warnings(
    failed_subjects: int,
    near_fail_subjects: int,
    percentage: float,
    sgpa_pred: float | None,
    dropout_risk: int,
) -> list[str]:
    """
    Generate a prioritized list of early warning alerts.

    Parameters
    ----------
    failed_subjects    : number of subjects below minimum passing marks
    near_fail_subjects : number of subjects within 30% above minimum
    percentage         : overall marks percentage
    sgpa_pred          : predicted SGPA (None for UG)
    dropout_risk       : 0=Low, 1=Medium, 2=High

    Returns
    -------
    list of warning strings, ordered by severity
    """
    warnings = []

    # ── Severity: CRITICAL ───────────────────────────────────
    if failed_subjects >= 1:
        warnings.append(
            f"🚨 CRITICAL: Failed {failed_subjects} subject(s) — "
            f"immediate academic support required"
        )
    if dropout_risk == 2:
        warnings.append(
            "🚨 CRITICAL: HIGH dropout risk detected — "
            "urgent counselling and intervention recommended"
        )

    # ── Severity: WARNING ────────────────────────────────────
    if near_fail_subjects >= 2:
        warnings.append(
            f"⚠️  WARNING: {near_fail_subjects} subjects are near the "
            f"minimum passing threshold"
        )
    if percentage is not None and percentage < 45:
        warnings.append(
            f"⚠️  WARNING: Overall percentage critically low ({percentage:.1f}%) — "
            f"below the 45% safety threshold"
        )
    if sgpa_pred is not None and sgpa_pred < 5.0:
        warnings.append(
            f"⚠️  WARNING: Predicted SGPA is very low ({sgpa_pred:.2f}) — "
            f"academic performance is at risk"
        )
    if dropout_risk == 1:
        warnings.append(
            "⚠️  WARNING: Medium dropout risk — "
            "monitor this student closely this semester"
        )

    # ── All clear ────────────────────────────────────────────
    if not warnings:
        warnings.append("✅  No major academic concerns detected")

    return warnings
