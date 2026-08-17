from pydantic import BaseModel, Field


class JobRequirements(BaseModel):
    """Validated information extracted from a job description."""

    job_title: str = Field(
        default="Not specified",
        description="The advertised job title.",
    )

    company_name: str = Field(
        default="Not specified",
        description="The hiring company name.",
    )

    location: str = Field(
        default="Not specified",
        description="Job location or remote-work information.",
    )

    employment_type: str = Field(
        default="Not specified",
        description="Internship, full-time, part-time or contract.",
    )

    experience_level: str = Field(
        default="Not specified",
        description="Requested experience or candidate level.",
    )

    required_skills: list[str] = Field(
        default_factory=list,
        description="Skills explicitly required by the employer.",
    )

    preferred_skills: list[str] = Field(
        default_factory=list,
        description="Optional or preferred skills.",
    )

    responsibilities: list[str] = Field(
        default_factory=list,
        description="Main work responsibilities.",
    )

    education: list[str] = Field(
        default_factory=list,
        description="Education and graduation requirements.",
    )

    important_keywords: list[str] = Field(
        default_factory=list,
        description="Important ATS and technical keywords.",
    )