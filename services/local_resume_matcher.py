import re

from services.job_schema import JobRequirements
from services.local_job_parser import SKILL_ALIASES
from services.match_schema import (
    ResumeMatchAnalysis,
    SkillEvidence,
)
from services.privacy import redact_personal_data


TRANSFERABLE_SKILLS = {
    "FastAPI": [
        "Flask",
        "Django",
        "Python",
        "REST APIs",
    ],
    "Docker": [
        "CI/CD",
        "AWS",
        "Google Cloud",
        "Microsoft Azure",
    ],
    "Kubernetes": [
        "Docker",
        "CI/CD",
    ],
    "Machine Learning": [
        "Deep Learning",
        "Generative AI",
        "Retrieval-Augmented Generation",
    ],
    "Deep Learning": [
        "Machine Learning",
        "TensorFlow",
        "PyTorch",
    ],
    "SQL": [
        "PostgreSQL",
        "MySQL",
        "MongoDB",
    ],
    "AWS": [
        "Google Cloud",
        "Microsoft Azure",
        "Firebase",
    ],
    "Google Cloud": [
        "AWS",
        "Microsoft Azure",
        "Firebase",
    ],
    "Microsoft Azure": [
        "AWS",
        "Google Cloud",
    ],
    "React": [
        "JavaScript",
        "TypeScript",
        "Next.js",
    ],
    "Next.js": [
        "React",
        "JavaScript",
        "TypeScript",
    ],
    "LangGraph": [
        "LangChain",
        "Retrieval-Augmented Generation",
    ],
}


def _contains_phrase(text, phrase):
    """Match a phrase without matching inside another word."""

    escaped = re.escape(phrase.lower())
    pattern = rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"

    return re.search(pattern, text.lower()) is not None


def _skill_aliases(skill):
    """Return known aliases or the skill name itself."""

    return SKILL_ALIASES.get(skill, [skill])


def _find_skill_evidence(resume_text, skill):
    """Find a short resume line supporting one skill."""

    aliases = _skill_aliases(skill)

    for raw_line in resume_text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()

        if not line or line.startswith("[Page "):
            continue

        if any(
            _contains_phrase(line, alias)
            for alias in aliases
        ):
            return line[:350]

    sentences = re.split(
        r"(?<=[.!?])\s+",
        resume_text,
    )

    for sentence in sentences:
        cleaned = re.sub(r"\s+", " ", sentence).strip()

        if any(
            _contains_phrase(cleaned, alias)
            for alias in aliases
        ):
            return cleaned[:350]

    return None


def _match_skills(resume_text, skills):
    """Separate matched skills from unsupported skills."""

    matched = []
    missing = []

    for skill in skills:
        evidence = _find_skill_evidence(
            resume_text,
            skill,
        )

        if evidence:
            matched.append(
                SkillEvidence(
                    skill=skill,
                    evidence=evidence,
                )
            )
        else:
            missing.append(skill)

    return matched, missing


def _find_transferable_skills(
    resume_text,
    missing_required_skills,
):
    """Find related evidence without calling it a direct match."""

    transferable = []
    added = set()

    for missing_skill in missing_required_skills:
        related_skills = TRANSFERABLE_SKILLS.get(
            missing_skill,
            [],
        )

        for related_skill in related_skills:
            if related_skill in added:
                continue

            evidence = _find_skill_evidence(
                resume_text,
                related_skill,
            )

            if evidence:
                transferable.append(
                    SkillEvidence(
                        skill=related_skill,
                        evidence=(
                            f"Related to {missing_skill}: "
                            f"{evidence}"
                        ),
                    )
                )
                added.add(related_skill)

    return transferable[:8]


def _evaluate_education(
    resume_text,
    job_requirements,
):
    """Evaluate education using explicit degree evidence."""

    if not job_requirements.education:
        return (
            True,
            "The job description does not specify an education requirement.",
        )

    degree_markers = (
        "b.tech",
        "btech",
        "bachelor",
        "b.e.",
        "master",
        "m.tech",
        "degree",
        "computer science",
        "engineering",
    )

    for raw_line in resume_text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        lowered = line.lower()

        if any(
            marker in lowered
            for marker in degree_markers
        ):
            return True, line[:350]

    return (
        False,
        "No clear degree evidence was found in the resume.",
    )


def _requested_years(experience_level):
    """Extract the minimum requested years of experience."""

    match = re.search(
        r"\b(\d+)\s*(?:-\s*\d+)?\+?\s*years?",
        experience_level,
        re.IGNORECASE,
    )

    return int(match.group(1)) if match else None


def _resume_years(resume_text):
    """Extract the largest explicitly claimed year count."""

    matches = re.findall(
        r"\b(\d+)\+?\s*years?(?:\s+of)?\s+experience\b",
        resume_text,
        re.IGNORECASE,
    )

    if not matches:
        return None

    return max(int(value) for value in matches)


def _evaluate_experience(
    resume_text,
    job_requirements,
):
    """Evaluate only explicit experience requirements."""

    experience_level = (
        job_requirements.experience_level.strip().lower()
    )

    if experience_level == "not specified":
        return (
            True,
            "The job description does not specify experience.",
        )

    if any(
        marker in experience_level
        for marker in (
            "fresher",
            "student",
            "entry-level",
            "entry level",
        )
    ):
        return (
            True,
            "The role is open to students, freshers or entry-level candidates.",
        )

    required_years = _requested_years(experience_level)

    if required_years is None:
        return (
            False,
            "The experience requirement could not be verified.",
        )

    candidate_years = _resume_years(resume_text)

    if (
        candidate_years is not None
        and candidate_years >= required_years
    ):
        return (
            True,
            f"The resume explicitly states {candidate_years} "
            "years of experience.",
        )

    return (
        False,
        f"The resume does not verify the requested "
        f"{required_years}+ years of experience.",
    )


def match_resume_to_job_local(
    safe_resume_text,
    job_requirements,
):
    """Match a resume to a job without an AI API."""

    if not isinstance(job_requirements, JobRequirements):
        raise TypeError(
            "job_requirements must be a JobRequirements object."
        )

    protected_text, _ = redact_personal_data(
        safe_resume_text
    )

    if len(protected_text.strip()) < 100:
        raise ValueError(
            "The protected resume does not contain enough text."
        )

    matched_required, missing_required = _match_skills(
        protected_text,
        job_requirements.required_skills,
    )

    matched_preferred, _ = _match_skills(
        protected_text,
        job_requirements.preferred_skills,
    )

    transferable = _find_transferable_skills(
        protected_text,
        missing_required,
    )

    education_match, education_evidence = (
        _evaluate_education(
            protected_text,
            job_requirements,
        )
    )

    experience_match, experience_evidence = (
        _evaluate_experience(
            protected_text,
            job_requirements,
        )
    )

    matched_names = [
        item.skill
        for item in matched_required
    ]

    strengths = matched_names.copy()

    if education_match and job_requirements.education:
        strengths.append(
            "Education requirement supported by the resume"
        )

    improvement_areas = [
        f"Build verifiable evidence for {skill}"
        for skill in missing_required
    ]

    if matched_required:
        summary = (
            f"The resume provides evidence for "
            f"{len(matched_required)} of "
            f"{len(job_requirements.required_skills)} "
            "identified required skills."
        )
    elif job_requirements.required_skills:
        summary = (
            "The resume does not provide direct evidence for "
            "the identified required skills."
        )
    else:
        summary = (
            "No recognized required technical skills were "
            "identified in the job description."
        )

    if missing_required:
        summary += (
            " Missing evidence: "
            + ", ".join(missing_required)
            + "."
        )

    return ResumeMatchAnalysis(
        matched_required_skills=matched_required,
        missing_required_skills=missing_required,
        matched_preferred_skills=matched_preferred,
        transferable_skills=transferable,
        education_match=education_match,
        education_evidence=education_evidence,
        experience_match=experience_match,
        experience_evidence=experience_evidence,
        strengths=strengths,
        improvement_areas=improvement_areas,
        summary=summary,
    )