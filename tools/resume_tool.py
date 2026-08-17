from pypdf import PdfReader


def extract_resume_text(uploaded_file):
    """
    Extract text from an uploaded PDF resume.

    Returns:
        resume_text: Combined text from every page.
        page_count: Number of pages in the PDF.
    """

    if uploaded_file is None:
        raise ValueError("No resume file was provided.")

    uploaded_file.seek(0)
    reader = PdfReader(uploaded_file)

    if reader.is_encrypted:
        raise ValueError(
            "The uploaded resume is password-protected."
        )

    extracted_pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        page_text = page.extract_text() or ""

        if page_text.strip():
            extracted_pages.append(
                f"[Page {page_number}]\n"
                f"{page_text.strip()}"
            )

    resume_text = "\n\n".join(extracted_pages).strip()

    if not resume_text:
        raise ValueError(
            "No readable text was found in the resume. "
            "The PDF may contain only scanned images."
        )

    return resume_text, len(reader.pages)