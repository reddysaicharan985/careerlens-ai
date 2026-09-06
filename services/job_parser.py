from services.ai_router import generate_structured
from services.job_schema import JobRequirements


def parse_job_description(job_description):
    """Extract validated requirements from a job description."""

    cleaned_description = job_description.strip()

    if len(cleaned_description) < 100:
        raise ValueError(
            "The job description must contain at least "
            "100 characters."
        )

    system_prompt = """
You are the job-description analysis component of CareerLens AI.

Extract only information explicitly stated in the job description.

Rules:
1. Do not invent company names, skills or requirements.
2. Use "Not specified" when a text field is unavailable.
3. Use an empty list when a list field is unavailable.
4. Separate required skills from preferred skills.
5. Include useful technical and ATS keywords.
6. Keep each responsibility clear and concise.
""".strip()

    user_prompt = f"""
JOB DESCRIPTION:

{cleaned_description}
""".strip()

    extracted_data = generate_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        schema=JobRequirements.model_json_schema(),
        max_tokens=2000,
    )

    return JobRequirements.model_validate(extracted_data)