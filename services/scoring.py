from dataclasses import dataclass

from services.job_schema import JobRequirements
from services.match_schema import ResumeMatchAnalysis


@dataclass(frozen=True)
class MatchScore:
    """Transparent CareerLens match score."""

    overall_score: int
    recommendation: str
    required_skill_score: int | None
    preferred_skill_score: int | None
    education_score: int | None
    experience_score: int | None


def percentage(matched_count, total_count):
    """Calculate a percentage without exceeding 100."""

    if total_count == 0:
        return None

    safe_matched_count = min(matched_count, total_count)

    return round((safe_matched_count / total_count) * 100)


def calculate_match_score(
    job_requirements,
    match_analysis,
):
    """Calculate a deterministic resume-to-job score."""

    if not isinstance(job_requirements, JobRequirements):
        raise TypeError(
            "job_requirements must be a JobRequirements object."
        )

    if not isinstance(match_analysis, ResumeMatchAnalysis):
        raise TypeError(
            "match_analysis must be a ResumeMatchAnalysis object."
        )

    components = []

    required_score = percentage(
        len(match_analysis.matched_required_skills),
        len(job_requirements.required_skills),
    )

    if required_score is not None:
        components.append((required_score, 70))

    preferred_score = percentage(
        len(match_analysis.matched_preferred_skills),
        len(job_requirements.preferred_skills),
    )

    if preferred_score is not None:
        components.append((preferred_score, 10))

    education_score = None

    if job_requirements.education:
        education_score = (
            100 if match_analysis.education_match else 0
        )
        components.append((education_score, 10))

    experience_score = None

    if (
        job_requirements.experience_level.strip().lower()
        != "not specified"
    ):
        experience_score = (
            100 if match_analysis.experience_match else 0
        )
        components.append((experience_score, 10))

    if not components:
        overall_score = 0
    else:
        weighted_total = sum(
            score * weight for score, weight in components
        )
        active_weight = sum(
            weight for _, weight in components
        )
        overall_score = round(weighted_total / active_weight)

    if overall_score >= 75:
        recommendation = "Strong match — apply"

    elif overall_score >= 50:
        recommendation = (
            "Moderate match — apply and address the gaps"
        )

    else:
        recommendation = (
            "Develop the missing skills before prioritizing this role"
        )

    return MatchScore(
        overall_score=overall_score,
        recommendation=recommendation,
        required_skill_score=required_score,
        preferred_skill_score=preferred_score,
        education_score=education_score,
        experience_score=experience_score,
    )