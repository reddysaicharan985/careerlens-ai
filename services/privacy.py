import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+?91[\s-]?)?"
    r"[6-9]\d{9}"
    r"(?!\d)"
)

URL_PATTERN = re.compile(
    r"\b(?:https?://|www\.)[^\s|]+"
    r"|\b(?:linkedin\.com|github\.com)/[^\s|]+",
    re.IGNORECASE,
)


def redact_personal_data(resume_text):
    """
    Remove direct contact details before AI processing.
    """

    safe_text, email_count = EMAIL_PATTERN.subn(
        "[EMAIL REDACTED]",
        resume_text,
    )

    safe_text, phone_count = PHONE_PATTERN.subn(
        "[PHONE REDACTED]",
        safe_text,
    )

    safe_text, url_count = URL_PATTERN.subn(
        "[URL REDACTED]",
        safe_text,
    )

    redaction_counts = {
        "emails": email_count,
        "phone_numbers": phone_count,
        "urls": url_count,
    }

    return safe_text, redaction_counts