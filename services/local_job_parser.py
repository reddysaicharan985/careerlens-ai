import re

from services.job_schema import JobRequirements


SKILL_ALIASES = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript"],
    "SQL": ["sql"],
    "HTML": ["html"],
    "CSS": ["css"],
    "React": ["react", "react.js", "reactjs"],
    "Next.js": ["next.js", "nextjs"],
    "Node.js": ["node.js", "nodejs"],
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],
    "Django": ["django"],
    "REST APIs": ["rest api", "restful api", "rest apis"],
    "Machine Learning": ["machine learning", "ml fundamentals"],
    "Deep Learning": ["deep learning"],
    "Generative AI": ["generative ai", "genai"],
    "Large Language Models": [
        "large language model",
        "large language models",
        "llm",
        "llms",
    ],
    "Retrieval-Augmented Generation": [
        "retrieval-augmented generation",
        "retrieval augmented generation",
        "rag",
    ],
    "LangChain": ["langchain"],
    "LangGraph": ["langgraph"],
    "Prompt Engineering": ["prompt engineering"],
    "Natural Language Processing": [
        "natural language processing",
        "nlp",
    ],
    "Computer Vision": ["computer vision"],
    "Data Structures": ["data structures", "dsa"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "ChromaDB": ["chromadb", "chroma"],
    "Pinecone": ["pinecone"],
    "FAISS": ["faiss"],
    "Vector Databases": [
        "vector database",
        "vector databases",
        "vector store",
    ],
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "CI/CD": ["ci/cd", "continuous integration"],
    "AWS": ["aws", "amazon web services"],
    "Google Cloud": ["google cloud", "gcp"],
    "Microsoft Azure": ["microsoft azure", "azure"],
    "Firebase": ["firebase", "firestore"],
    "MongoDB": ["mongodb"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
    "Streamlit": ["streamlit"],
    "Pytest": ["pytest"],
    "Linux": ["linux"],
    "Agile": ["agile", "scrum"],
}

PREFERRED_MARKERS = (
    "preferred",
    "nice to have",
    "good to have",
    "bonus",
    "optional",
    "plus",
)

REQUIRED_MARKERS = (
    "required",
    "requirements",
    "must have",
    "must-have",
    "mandatory",
    "qualifications",
)

SECTION_HEADINGS = (
    "responsibilities",
    "requirements",
    "required skills",
    "preferred skills",
    "qualifications",
    "education",
    "experience",
    "about the role",
    "job description",
)


def _clean_line(value):
    """Remove bullets and repeated whitespace from one line."""

    without_bullet = re.sub(
        r"^\s*[-•*✓✔\d.)]+\s*",
        "",
        value,
    )

    return re.sub(r"\s+", " ", without_bullet).strip()


def _contains_phrase(text, phrase):
    """Match a skill phrase without matching inside another word."""

    escaped = re.escape(phrase.lower())
    pattern = rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"

    return re.search(pattern, text.lower()) is not None


def _extract_label_value(text, labels):
    """Extract values such as 'Company: Example Technologies'."""

    label_pattern = "|".join(
        re.escape(label)
        for label in labels
    )

    match = re.search(
        rf"(?im)^\s*(?:{label_pattern})\s*[:\-]\s*(.+?)\s*$",
        text,
    )

    if match:
        return _clean_line(match.group(1))

    return "Not specified"


def _extract_job_title(text):
    title = _extract_label_value(
        text,
        (
            "job title",
            "position",
            "role",
        ),
    )

    if title != "Not specified":
        return title

    role_pattern = re.compile(
        r"\b(?:engineer|developer|analyst|scientist|"
        r"consultant|specialist|intern)\b",
        re.IGNORECASE,
    )

    for raw_line in text.splitlines():
        line = _clean_line(raw_line)

        if (
            line
            and len(line) <= 100
            and role_pattern.search(line)
        ):
            return line

    return "Not specified"


def _extract_employment_type(text):
    lowered = text.lower()

    employment_types = (
        ("Internship", ("internship", "intern role")),
        ("Full-time", ("full-time", "full time")),
        ("Part-time", ("part-time", "part time")),
        ("Contract", ("contract", "contractual")),
        ("Temporary", ("temporary",)),
    )

    for name, markers in employment_types:
        if any(marker in lowered for marker in markers):
            return name

    return "Not specified"


def _extract_experience_level(text):
    patterns = (
        r"\b\d+\s*(?:-\s*\d+)?\+?\s*years?"
        r"(?:\s+of)?\s+experience\b",
        r"\b(?:fresher|freshers|entry[- ]level)\b",
        r"\b(?:student|students)\b",
    )

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return _clean_line(match.group(0))

    return "Not specified"


def _find_skills(text):
    found = []

    for canonical_name, aliases in SKILL_ALIASES.items():
        if any(
            _contains_phrase(text, alias)
            for alias in aliases
        ):
            found.append(canonical_name)

    return found


def _classify_skills(text):
    """
    Separate preferred skills from required skills using nearby text.

    Skills without an explicit preferred marker are treated as required
    because ATS descriptions commonly list core skills without repeating
    the word "required" on every bullet.
    """

    lowered = text.lower()
    required = []
    preferred = []

    for canonical_name, aliases in SKILL_ALIASES.items():
        locations = []

        for alias in aliases:
            escaped = re.escape(alias.lower())
            pattern = rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"

            locations.extend(
                match.start()
                for match in re.finditer(pattern, lowered)
            )

        if not locations:
            continue

        is_preferred = False

        for location in locations:
            context_start = max(0, location - 180)
            context = lowered[context_start:location]

            last_preferred = max(
                (
                    context.rfind(marker)
                    for marker in PREFERRED_MARKERS
                ),
                default=-1,
            )

            last_required = max(
                (
                    context.rfind(marker)
                    for marker in REQUIRED_MARKERS
                ),
                default=-1,
            )

            if last_preferred > last_required:
                is_preferred = True
                break

        if is_preferred:
            preferred.append(canonical_name)
        else:
            required.append(canonical_name)

    return required, preferred


def _extract_responsibilities(text):
    lines = text.splitlines()
    responsibilities = []
    collecting = False

    for raw_line in lines:
        cleaned = _clean_line(raw_line)
        lowered = cleaned.lower().rstrip(":")

        if lowered in (
            "responsibilities",
            "key responsibilities",
            "roles and responsibilities",
            "what you will do",
            "what you'll do",
        ):
            collecting = True
            continue

        if collecting and lowered in SECTION_HEADINGS:
            break

        if collecting and cleaned:
            responsibilities.append(cleaned)

        if len(responsibilities) >= 10:
            break

    return responsibilities


def _extract_education(text):
    education = []

    education_markers = (
        "b.tech",
        "btech",
        "bachelor",
        "master",
        "degree",
        "computer science",
        "artificial intelligence",
        "machine learning",
        "engineering",
    )

    for raw_line in text.splitlines():
        cleaned = _clean_line(raw_line)
        lowered = cleaned.lower()

        if (
            cleaned
            and any(
                marker in lowered
                for marker in education_markers
            )
        ):
            education.append(cleaned)

        if len(education) >= 5:
            break

    return education


def parse_job_description_local(job_description):
    """Parse a job description without calling an AI API."""

    cleaned_description = job_description.strip()

    if len(cleaned_description) < 80:
        raise ValueError(
            "The job description must contain at least "
            "80 characters."
        )

    required_skills, preferred_skills = _classify_skills(
        cleaned_description
    )

    all_skills = _find_skills(cleaned_description)

    important_keywords = list(
        dict.fromkeys(
            required_skills
            + preferred_skills
            + all_skills
        )
    )

    return JobRequirements(
        job_title=_extract_job_title(cleaned_description),
        company_name=_extract_label_value(
            cleaned_description,
            (
                "company",
                "company name",
                "organization",
                "organisation",
            ),
        ),
        location=_extract_label_value(
            cleaned_description,
            (
                "location",
                "job location",
                "work location",
            ),
        ),
        employment_type=_extract_employment_type(
            cleaned_description
        ),
        experience_level=_extract_experience_level(
            cleaned_description
        ),
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        responsibilities=_extract_responsibilities(
            cleaned_description
        ),
        education=_extract_education(cleaned_description),
        important_keywords=important_keywords,
    )