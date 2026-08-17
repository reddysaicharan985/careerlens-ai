from services.privacy import redact_personal_data


def test_redacts_contact_information():
    resume_text = """
    Mukkara Sai Charan Reddy
    Email: student@example.com
    Phone: +91 9876543210
    LinkedIn: https://www.linkedin.com/in/example-user
    GitHub: github.com/example-user
    Skills: Python, RAG and LangChain
    """

    safe_text, counts = redact_personal_data(resume_text)

    assert "student@example.com" not in safe_text
    assert "9876543210" not in safe_text
    assert "linkedin.com/in/example-user" not in safe_text
    assert "github.com/example-user" not in safe_text

    assert "[EMAIL REDACTED]" in safe_text
    assert "[PHONE REDACTED]" in safe_text
    assert safe_text.count("[URL REDACTED]") == 2

    assert counts["emails"] == 1
    assert counts["phone_numbers"] == 1
    assert counts["urls"] == 2

    assert "Python, RAG and LangChain" in safe_text


def test_text_without_private_data_is_preserved():
    resume_text = "Skills: Python, LangChain, RAG and Firebase"

    safe_text, counts = redact_personal_data(resume_text)

    assert safe_text == resume_text
    assert counts["emails"] == 0
    assert counts["phone_numbers"] == 0
    assert counts["urls"] == 0