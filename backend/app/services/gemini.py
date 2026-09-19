"""
Plain-language summary of an AnalysisResult via Gemini.

The prompt hard-codes the PLAN.md section 4 honesty rule so the model can never
claim we detect migraine. If GEMINI_API_KEY is unset, returns a deterministic
template summary so the app still works.
"""

import logging

from backend.app.config import settings
from backend.app.schemas import AnalysisResult

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are writing a short findings note for a radiologist or neurologist reviewing a FLAIR MRI slice.
You are given structured output from a lesion detector plus a rule-based pattern layer.

Rules you must follow:
- 3 to 5 sentences, plain clinical language, no bullet points.
- Report lesion count, how many are MS-typical vs atypical/nonspecific, and the burden percentage.
- Describe WHY lesions were flagged using the provided reasons (location, shape, orientation).
- State that the pattern flags encode established radiological criteria for distinguishing MS-typical
  from nonspecific white-matter lesions. NEVER say the system was trained to detect migraine or that it
  distinguishes MS from migraine.
- End with one sentence making clear this is decision support for the clinician's review, not a diagnosis.
"""


def _template_summary(result: AnalysisResult) -> str:
    b = result.burden
    return (
        f"{b.lesion_count} white-matter lesions were detected in this slice: {b.ms_typical_count} with an "
        f"MS-typical pattern and {b.atypical_count} with an atypical or nonspecific pattern. Total lesion burden "
        f"is {b.total_area_pct}% of the slice. Pattern flags encode established radiological criteria for "
        f"distinguishing MS-typical from nonspecific lesions. This output is decision support for clinician "
        f"review and is not a diagnosis."
    )


def _lesion_lines(result: AnalysisResult) -> str:
    return "\n".join(
        f"- lesion {l.id}: {l.pattern}, {l.features.location}, elongation {l.features.elongation:.1f}, "
        f"ovoid {l.features.ovoid_score:.2f}, confidence {l.confidence:.2f}; reasons: {', '.join(l.reasons)}"
        for l in result.lesions
    )


def summarize(result: AnalysisResult) -> str:
    if not settings.gemini_api_key:
        return _template_summary(result)

    try:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        b = result.burden
        user = (
            f"Lesion count: {b.lesion_count}. MS-typical: {b.ms_typical_count}. Atypical: {b.atypical_count}. "
            f"Burden: {b.total_area_pct}% of slice.\nLesions:\n{_lesion_lines(result)}"
        )
        resp = client.models.generate_content(
            model=settings.gemini_model,
            contents=user,
            config={"system_instruction": SYSTEM_PROMPT, "temperature": 0.3},
        )
        return (resp.text or "").strip() or _template_summary(result)
    except Exception as exc:  # noqa: BLE001
        log.warning("Gemini failed (%s); using template summary", exc)
        return _template_summary(result)
