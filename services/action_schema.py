from pydantic import BaseModel, Field


class ApplicationMaterials(BaseModel):
    """Application content generated for a matched role."""

    email_subject: str = Field(
        description="A concise and professional email subject."
    )

    email_body: str = Field(
        description=(
            "A short application email using only verified "
            "resume evidence."
        )
    )

    cover_letter: str = Field(
        description=(
            "A role-specific cover letter without invented claims."
        )
    )

    interview_focus: list[str] = Field(
        default_factory=list,
        description=(
            "Topics the candidate should prepare for the interview."
        ),
    )


class LearningStep(BaseModel):
    """One prioritized skill-development step."""

    skill: str = Field(
        description="The missing or weak skill to develop."
    )

    reason: str = Field(
        description="Why this skill matters for the target role."
    )

    actions: list[str] = Field(
        default_factory=list,
        description="Practical learning and implementation actions.",
    )

    proof_project: str = Field(
        description=(
            "A small project that can demonstrate this skill."
        )
    )


class LearningPlan(BaseModel):
    """Targeted preparation plan for a low-match role."""

    priority_steps: list[LearningStep] = Field(
        default_factory=list,
        description="Ordered learning steps for the candidate.",
    )

    suggested_project: str = Field(
        description=(
            "One portfolio project combining the priority skills."
        )
    )

    readiness_note: str = Field(
        description=(
            "An honest explanation of when the candidate "
            "should reconsider applying."
        )
    )