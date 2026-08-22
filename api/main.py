from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from agent import careerlens_agent
from services.privacy import redact_personal_data
from tools.resume_tool import extract_resume_text


MAX_FILE_SIZE = 5 * 1024 * 1024
MIN_JOB_DESCRIPTION_LENGTH = 80

app = FastAPI(
    title="CareerLens AI API",
    description="Resume and job-description analysis API.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "CareerLens AI API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    filename = resume.filename or "resume.pdf"
    extension = Path(filename).suffix.lower()

    if extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are currently supported.",
        )

    cleaned_job_description = job_description.strip()

    if len(cleaned_job_description) < MIN_JOB_DESCRIPTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                "The job description must contain at least "
                f"{MIN_JOB_DESCRIPTION_LENGTH} characters."
            ),
        )

    file_bytes = await resume.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded resume is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The resume must be smaller than 5 MB.",
        )

    try:
        resume_stream = BytesIO(file_bytes)

        resume_text, page_count = extract_resume_text(
            resume_stream,
        )

        safe_resume_text, redaction_counts = (
            redact_personal_data(resume_text)
        )

        agent_result = careerlens_agent.invoke(
            {
                "safe_resume_text": safe_resume_text,
                "job_description": cleaned_job_description,
            }
        )

        public_analysis = {
            "job_requirements": agent_result["job_requirements"],
            "match_analysis": agent_result["match_analysis"],
            "match_score": agent_result["match_score"],
        }

        if "application_materials" in agent_result:
            public_analysis["route"] = "prepare_application"
            public_analysis["application_materials"] = (
                agent_result["application_materials"]
            )

        elif "learning_plan" in agent_result:
            public_analysis["route"] = "create_learning_plan"
            public_analysis["learning_plan"] = (
                agent_result["learning_plan"]
            )

        return jsonable_encoder(
            {
                "success": True,
                "resume": {
                    "filename": filename,
                    "page_count": page_count,
                    "character_count": len(resume_text),
                    "private_details_removed": sum(
                        redaction_counts.values()
                    ),
                    "redaction_counts": redaction_counts,
                },
                "analysis": public_analysis,
            }
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        error_text = str(error).lower()

        if "429" in error_text or "resource_exhausted" in error_text:
            message = (
                "The AI request limit has been reached. "
                "Please wait and try again later."
            )
            status_code = 429

        elif "503" in error_text or "unavailable" in error_text:
            message = (
                "The AI service is temporarily unavailable. "
                "Please try again shortly."
            )
            status_code = 503

        else:
            message = (
                "CareerLens could not complete the analysis. "
                "Please check the resume and job description."
            )
            status_code = 500

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error

    finally:
        await resume.close()