import re

from pydantic import BaseModel, Field

from services.job_schema import JobRequirements


class ATSReadinessResult(BaseModel):
    """Transparent, deterministic ATS-readiness assessment."""

    overall_score: int = Field(ge=0, le=100)
    parseability_score: int = Field(ge=0, le=20)
    section_score: int = Field(ge=0, le=25)
    keyword_score: int = Field(ge=0, le=35)
    impact_score: int = Field(ge=0, le=20)

    found_sections: list[str] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


SECTION_ALIASES = {
    "Professional summary": [
        "professional summary",
        "career summary",
        "profile summary",
        "objective",
    ],
    "Skills": [
        "technical skills",
        "core skills",
        "skills",
        "technologies",
    ],
    "Experience": [
        "work experience",
        "professional experience",
        "experience",
        "internship",
    ],
    "Education": [
        "education",
        "academic background",
        "qualifications",
    ],
    "Projects": [
        "projects",
        "academic projects",
        "personal projects",
    ],
}

ACTION_VERBS = {
    "built",
    "created",
    "developed",
    "designed",
    "deployed",
    "implemented",
    "improved",
    "integrated",
    "optimized",
    "reduced",
    "increased",
    "automated",
    "evaluated",
    "tested",
    "managed",
    "led",
}


def _normalize_text(value: str) -> str:
    """Normalize text for consistent keyword comparisons."""

    lowered = value.lower()
    without_symbols = re.sub(r"[^a-z0-9+#.\s-]", " ", lowered)
    return re.sub(r"\s+", " ", without_symbols).strip()


def _unique_keywords(job_requirements: JobRequirements) -> list[str]:
    """Build a deduplicated employer-keyword list."""

    combined = (
        job_requirements.required_skills
        + job_requirements.important_keywords
    )

    unique = []
    seen = set()

    for keyword in combined:
        cleaned = keyword.strip()

        if not cleaned:
            continue

        normalized = _normalize_text(cleaned)

        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(cleaned)

    return unique


def analyze_ats_readiness(
    resume_text: str,
    page_count: int,
    job_requirements: JobRequirements,
) -> ATSReadinessResult:
    """
    Calculate an explainable ATS-readiness estimate.

    This is separate from the CareerLens job-match score and does
    not claim to reproduce a specific employer's private ATS.
    """

    normalized_resume = _normalize_text(resume_text)
    recommendations = []

    parseability_score = 0

    if len(resume_text.strip()) >= 300:
        parseability_score += 10
    else:
        recommendations.append(
            "Add more readable resume content; very little text "
            "was extracted from the PDF."
        )

    if 1 <= page_count <= 3:
        parseability_score += 5
    else:
        recommendations.append(
            "Keep the resume between one and three pages."
        )

    average_characters = (
        len(resume_text.strip()) // page_count
        if page_count > 0
        else 0
    )

    if average_characters >= 300:
        parseability_score += 5
    else:
        recommendations.append(
            "Use selectable text instead of scanned images."
        )

    found_sections = []
    missing_sections = []

    for section_name, aliases in SECTION_ALIASES.items():
        if any(
            _normalize_text(alias) in normalized_resume
            for alias in aliases
        ):
            found_sections.append(section_name)
        else:
            missing_sections.append(section_name)

    section_score = len(found_sections) * 5

    if missing_sections:
        recommendations.append(
            "Add standard ATS headings for: "
            + ", ".join(missing_sections)
            + "."
        )

    keywords = _unique_keywords(job_requirements)
    matched_keywords = []
    missing_keywords = []

    for keyword in keywords:
        normalized_keyword = _normalize_text(keyword)

        if normalized_keyword in normalized_resume:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    if keywords:
        keyword_score = round(
            len(matched_keywords) / len(keywords) * 35
        )
    else:
        keyword_score = 0
        recommendations.append(
            "Use a complete job description so CareerLens can "
            "measure ATS keyword coverage."
        )

    if missing_keywords:
        recommendations.append(
            "Add missing keywords only when they truthfully match "
            "your experience or projects."
        )

    words = set(normalized_resume.split())
    action_verb_count = len(words.intersection(ACTION_VERBS))
    action_verb_score = min(action_verb_count * 2, 10)

    quantified_patterns = re.findall(
        r"\b(?:\d+(?:\.\d+)?%?|\d+\+)\b",
        resume_text,
    )
    quantified_score = min(len(quantified_patterns) * 2, 10)

    impact_score = action_verb_score + quantified_score

    if action_verb_score < 6:
        recommendations.append(
            "Begin more project and experience bullets with strong "
            "action verbs."
        )

    if quantified_score < 6:
        recommendations.append(
            "Add truthful numbers, percentages, scale or performance "
            "results to demonstrate impact."
        )

    overall_score = (
        parseability_score
        + section_score
        + keyword_score
        + impact_score
    )

    return ATSReadinessResult(
        overall_score=overall_score,
        parseability_score=parseability_score,
        section_score=section_score,
        keyword_score=keyword_score,
        impact_score=impact_score,
        found_sections=found_sections,
        missing_sections=missing_sections,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        recommendations=recommendations,
    )