from pydantic import BaseModel, Field


class SkillEvidence(BaseModel):
    """A skill supported by evidence from the resume."""

    skill: str = Field(
        description="The matched or transferable skill."
    )

    evidence: str = Field(
        description=(
            "A short quotation or factual reference "
            "from the resume supporting the skill."
        )
    )


class ResumeMatchAnalysis(BaseModel):
    """Validated comparison between a resume and job requirements."""

    matched_required_skills: list[SkillEvidence] = Field(
        default_factory=list,
        description="Required skills supported by resume evidence.",
    )

    missing_required_skills: list[str] = Field(
        default_factory=list,
        description="Required skills not supported by the resume.",
    )

    matched_preferred_skills: list[SkillEvidence] = Field(
        default_factory=list,
        description="Preferred skills supported by resume evidence.",
    )

    transferable_skills: list[SkillEvidence] = Field(
        default_factory=list,
        description=(
            "Related candidate skills that may transfer to the role."
        ),
    )

    education_match: bool = Field(
        default=False,
        description="Whether the resume meets the education requirement.",
    )

    education_evidence: str = Field(
        default="Not specified",
        description="Evidence supporting the education decision.",
    )

    experience_match: bool = Field(
        default=False,
        description="Whether the resume meets the experience requirement.",
    )

    experience_evidence: str = Field(
        default="Not specified",
        description="Evidence supporting the experience decision.",
    )

    strengths: list[str] = Field(
        default_factory=list,
        description="Strong points relevant to this job.",
    )

    improvement_areas: list[str] = Field(
        default_factory=list,
        description="Honest areas the candidate should improve.",
    )

    summary: str = Field(
        description="A concise and evidence-based match summary.",
    )