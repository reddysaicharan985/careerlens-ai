"use client";

import {
  ChangeEvent,
  FormEvent,
  useState,
} from "react";

import {
  Footer,
  Header,
} from "../components";

const MAX_FILE_SIZE = 5 * 1024 * 1024;
type AnalysisResponse = {
  success: boolean;
  resume: {
    filename: string;
    page_count: number;
    character_count: number;
    private_details_removed: number;
  };
  analysis: {
    job_requirements: {
      job_title: string;
      company_name: string;
      location: string;
      required_skills: string[];
      preferred_skills: string[];
    };
    match_analysis: {
      summary: string;
      matched_required_skills: {
        skill: string;
        evidence: string;
      }[];
      missing_required_skills: string[];
    };
    match_score: {
      overall_score: number;
      recommendation: string;
      required_skill_score: number | null;
      preferred_skill_score: number | null;
      education_score: number | null;
      experience_score: number | null;
    };
    route: string;
  };
};

function formatFileSize(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} bytes`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ResumeAnalyzerPage() {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [error, setError] = useState("");
  const [inputsReady, setInputsReady] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] =
    useState<AnalysisResponse | null>(null);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0];

    setError("");
    setInputsReady(false);

    if (!selectedFile) {
      setResumeFile(null);
      return;
    }

    const allowedExtensions = [".pdf"];
    const lowercaseName = selectedFile.name.toLowerCase();

    const isAllowed = allowedExtensions.some((extension) =>
      lowercaseName.endsWith(extension),
    );

    if (!isAllowed) {
      setResumeFile(null);
      setError("Please upload a PDF resume.");
      event.target.value = "";
      return;
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      setResumeFile(null);
      setError("The resume must be smaller than 5 MB.");
      event.target.value = "";
      return;
    }

    setResumeFile(selectedFile);
  }

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setInputsReady(false);
    setAnalysisResult(null);

    if (!resumeFile) {
      setError("Upload your resume before starting the analysis.");
      return;
    }

    if (jobDescription.trim().length < 80) {
      setError(
        "Paste a complete job description containing at least 80 characters.",
      );
      return;
    }

    const formData = new FormData();
    formData.append("resume", resumeFile);
    formData.append("job_description", jobDescription.trim());

    setIsAnalyzing(true);

    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

      const response = await fetch(`${apiUrl}/analyze`, {
        method: "POST",
        body: formData,
      });

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(
          responseData.detail ||
            "CareerLens could not complete the analysis.",
        );
      }

           setAnalysisResult(responseData as AnalysisResponse);
      setInputsReady(true);

      setTimeout(() => {
        document
          .getElementById("connection-status")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "center",
          });
      }, 100);
    } catch (requestError) {
      const message =
        requestError instanceof Error
          ? requestError.message
          : "Unable to connect to the CareerLens API.";

      setError(message);
    } finally {
      setIsAnalyzing(false);
    }
    }

  function clearForm() {
    setResumeFile(null);
    setJobDescription("");
    setInputsReady(false);
    setAnalysisResult(null);
    setError("");

    const fileInput = document.getElementById(
      "resume-upload",
    ) as HTMLInputElement | null;

    if (fileInput) {
      fileInput.value = "";
    }
  }

  return (
    <main className="min-h-screen bg-[#fbfcff] text-slate-950">
      <Header />

      <section className="mx-auto w-[calc(100%-28px)] max-w-6xl py-14 md:w-[calc(100%-48px)] md:py-20">
        {/* Heading */}
        <header className="mx-auto max-w-3xl text-center">
          <p className="inline-flex rounded-full border border-violet-200 bg-violet-50 px-4 py-2 text-[11px] font-extrabold uppercase tracking-wider text-violet-700">
            ✦ CareerLens Resume Analyzer
          </p>

          <h1 className="mt-5 text-4xl font-black tracking-[-0.05em] sm:text-5xl md:text-6xl">
            Match your resume
            <br />
            to the role.
          </h1>

          <p className="mx-auto mt-5 max-w-2xl text-sm leading-7 text-slate-500 sm:text-base">
            Upload your resume and paste the complete job description.
            CareerLens will compare your real evidence with the employer&apos;s
            requirements.
          </p>
        </header>

        {/* Progress */}
        <div className="mx-auto my-10 flex max-w-2xl items-center">
          <div className="flex items-center gap-2 text-violet-700">
            <span className="grid h-8 w-8 place-items-center rounded-full bg-violet-600 text-xs font-bold text-white">
              1
            </span>
            <span className="hidden text-xs font-bold sm:block">
              Resume
            </span>
          </div>

          <span className="mx-3 h-px flex-1 bg-slate-200" />

          <div
            className={`flex items-center gap-2 ${
              jobDescription
                ? "text-violet-700"
                : "text-slate-400"
            }`}
          >
            <span
              className={`grid h-8 w-8 place-items-center rounded-full border text-xs font-bold ${
                jobDescription
                  ? "border-violet-600 bg-violet-600 text-white"
                  : "border-slate-300 bg-white"
              }`}
            >
              2
            </span>

            <span className="hidden text-xs font-bold sm:block">
              Job description
            </span>
          </div>

          <span className="mx-3 h-px flex-1 bg-slate-200" />

          <div
            className={`flex items-center gap-2 ${
              inputsReady
                ? "text-violet-700"
                : "text-slate-400"
            }`}
          >
            <span
              className={`grid h-8 w-8 place-items-center rounded-full border text-xs font-bold ${
                inputsReady
                  ? "border-violet-600 bg-violet-600 text-white"
                  : "border-slate-300 bg-white"
              }`}
            >
              3
            </span>

            <span className="hidden text-xs font-bold sm:block">
              Results
            </span>
          </div>
        </div>

        <div className="grid items-start gap-6 lg:grid-cols-[1fr_310px]">
          {/* Main input form */}
          <form
            onSubmit={handleSubmit}
            className="rounded-3xl border border-slate-200 bg-white p-5 shadow-[0_25px_70px_rgba(49,44,91,0.08)] sm:p-8"
          >
            {/* Resume */}
            <section>
              <div className="flex items-center gap-3">
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-slate-950 text-xs font-bold text-white">
                  01
                </span>

                <div>
                  <h2 className="text-lg font-extrabold">
                    Add your resume
                  </h2>

                  <p className="text-xs text-slate-500">
                    PDF only · maximum 5 MB
                  </p>
                </div>
              </div>

              <label
                htmlFor="resume-upload"
                className={`mt-6 flex min-h-48 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-5 text-center transition ${
                  resumeFile
                    ? "border-emerald-300 bg-emerald-50"
                    : "border-slate-300 bg-slate-50 hover:border-violet-400 hover:bg-violet-50"
                }`}
              >
                <input
                  id="resume-upload"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="sr-only"
                />

                <span
                  className={`grid h-12 w-12 place-items-center rounded-xl text-2xl ${
                    resumeFile
                      ? "bg-emerald-100 text-emerald-700"
                      : "bg-violet-100 text-violet-700"
                  }`}
                >
                  {resumeFile ? "✓" : "↑"}
                </span>

                <strong className="mt-4 max-w-full break-all text-sm">
                  {resumeFile
                    ? resumeFile.name
                    : "Drop your resume here"}
                </strong>

                <span className="mt-2 text-xs text-slate-500">
                  {resumeFile
                    ? `${formatFileSize(resumeFile.size)} · ready to process`
                    : "or click to choose a file"}
                </span>

                {!resumeFile && (
                  <span className="mt-4 rounded-lg border border-violet-200 bg-white px-4 py-2 text-xs font-bold text-violet-700">
                    Choose resume
                  </span>
                )}
              </label>
            </section>

            <div className="my-8 h-px bg-slate-200" />

            {/* Job description */}
            <section>
              <div className="flex items-center gap-3">
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-slate-950 text-xs font-bold text-white">
                  02
                </span>

                <div>
                  <h2 className="text-lg font-extrabold">
                    Paste the job description
                  </h2>

                  <p className="text-xs text-slate-500">
                    Include requirements, responsibilities and preferred skills.
                  </p>
                </div>
              </div>

              <label
                htmlFor="job-description"
                className="mt-6 block text-xs font-bold text-slate-700"
              >
                Complete job description
              </label>

              <textarea
                id="job-description"
                value={jobDescription}
                onChange={(event) => {
                  setJobDescription(event.target.value);
                  setInputsReady(false);
                  setError("");
                }}
                placeholder="Paste the complete AI Engineer or internship job description here..."
                className="mt-2 min-h-64 w-full resize-y rounded-2xl border border-slate-300 bg-slate-50 p-4 text-sm leading-7 outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:bg-white focus:ring-4 focus:ring-violet-100"
              />

              <div className="mt-2 flex items-center justify-between gap-4 text-[11px] text-slate-400">
                <span>
                  Minimum 80 characters
                </span>

                <span>
                  {jobDescription.length.toLocaleString()} characters
                </span>
              </div>
            </section>

            {error && (
              <div
                role="alert"
                className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700"
              >
                {error}
              </div>
            )}

            <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row">
              <button
                type="button"
                onClick={clearForm}
                className="min-h-13 rounded-xl border border-slate-300 px-5 text-sm font-bold text-slate-600"
              >
                Clear
              </button>

                            <button
                type="submit"
                disabled={isAnalyzing}
                className="flex min-h-13 flex-1 items-center justify-center rounded-xl bg-slate-950 px-6 text-sm font-bold text-white shadow-lg transition hover:-translate-y-0.5 hover:bg-violet-600 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isAnalyzing
                  ? "Analyzing your resume..."
                  : "Analyze resume match →"}
              </button>
            </div>

            <p className="mt-4 text-center text-[11px] leading-5 text-slate-400">
              🔒 Personal information will be redacted before protected resume
              text is sent to the configured AI provider.
            </p>
          </form>

          {/* Right information column */}
          <aside className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
            <section className="rounded-2xl border border-lime-200 bg-lime-50 p-6">
              <span className="grid h-11 w-11 place-items-center rounded-xl bg-white text-xl">
                💡
              </span>

              <h2 className="mt-5 text-base font-extrabold">
                Get a better result
              </h2>

              <p className="mt-3 text-sm leading-6 text-slate-600">
                Use the original job description from the employer. Short
                summaries can hide important responsibilities and keywords.
              </p>
            </section>

            <section className="rounded-2xl border border-slate-200 bg-white p-6">
              <h2 className="text-base font-extrabold">
                What you&apos;ll receive
              </h2>

              <ul className="mt-5 space-y-4 text-sm text-slate-600">
                <li className="flex gap-3">
                  <span className="text-emerald-600">✓</span>
                  Role-specific match score
                </li>

                <li className="flex gap-3">
                  <span className="text-emerald-600">✓</span>
                  Matched and missing skills
                </li>

                <li className="flex gap-3">
                  <span className="text-emerald-600">✓</span>
                  Resume improvement plan
                </li>

                <li className="flex gap-3">
                  <span className="text-emerald-600">✓</span>
                  Recruiter application email
                </li>

                <li className="flex gap-3">
                  <span className="text-emerald-600">✓</span>
                  Cover-letter guidance
                </li>
              </ul>
            </section>

            <section className="rounded-2xl border border-violet-200 bg-violet-50 p-6 sm:col-span-2 lg:col-span-1">
              <div className="flex gap-3">
                <span className="text-2xl">
                  🛡
                </span>

                <div>
                  <h2 className="text-base font-extrabold">
                    Your privacy matters
                  </h2>

                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    Resume files must not be permanently stored. Sensitive
                    details are removed before AI analysis.
                  </p>
                </div>
              </div>
            </section>
          </aside>
        </div>

                {/* Real CareerLens analysis results */}
        {inputsReady && analysisResult && (
          <section
            id="connection-status"
            className="mt-10 rounded-3xl border border-emerald-200 bg-white p-5 shadow-[0_25px_70px_rgba(49,44,91,0.08)] sm:p-8"
          >
            <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
              <div className="grid h-28 w-28 shrink-0 place-items-center rounded-full border-[12px] border-violet-600 bg-violet-50">
                <div className="text-center">
                  <strong className="block text-3xl font-black">
                    {analysisResult.analysis.match_score.overall_score}
                  </strong>
                  <span className="text-[10px] text-slate-500">
                    out of 100
                  </span>
                </div>
              </div>

              <div className="flex-1">
                <p className="text-xs font-extrabold uppercase tracking-wider text-emerald-700">
                  Analysis completed
                </p>

                <h2 className="mt-2 text-2xl font-black tracking-tight sm:text-3xl">
                  {analysisResult.analysis.job_requirements.job_title}
                </h2>

                <p className="mt-2 text-sm font-semibold text-violet-700">
                  {analysisResult.analysis.match_score.recommendation}
                </p>

                <p className="mt-3 text-sm leading-7 text-slate-600">
                  {analysisResult.analysis.match_analysis.summary}
                </p>
              </div>
            </div>

            <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Resume pages</p>
                <strong className="mt-2 block text-xl">
                  {analysisResult.resume.page_count}
                </strong>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Required skills</p>
                <strong className="mt-2 block text-xl">
                  {analysisResult.analysis.match_score
                    .required_skill_score ?? "N/A"}
                  %
                </strong>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Education match</p>
                <strong className="mt-2 block text-xl">
                  {analysisResult.analysis.match_score.education_score ??
                    "N/A"}
                  %
                </strong>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-xs text-slate-500">
                  Private details removed
                </p>
                <strong className="mt-2 block text-xl">
                  {analysisResult.resume.private_details_removed}
                </strong>
              </div>
            </div>

            <div className="mt-8 grid gap-5 md:grid-cols-2">
              <section className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
                <h3 className="font-extrabold text-emerald-900">
                  Matched required skills
                </h3>

                <div className="mt-4 space-y-4">
                  {analysisResult.analysis.match_analysis
                    .matched_required_skills.length > 0 ? (
                    analysisResult.analysis.match_analysis.matched_required_skills.map(
                      (item) => (
                        <div key={item.skill}>
                          <p className="text-sm font-bold text-emerald-900">
                            ✓ {item.skill}
                          </p>
                          <p className="mt-1 text-xs leading-5 text-slate-600">
                            {item.evidence}
                          </p>
                        </div>
                      ),
                    )
                  ) : (
                    <p className="text-sm text-slate-600">
                      No required skills were confirmed.
                    </p>
                  )}
                </div>
              </section>

              <section className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
                <h3 className="font-extrabold text-amber-900">
                  Missing required skills
                </h3>

                <ul className="mt-4 space-y-3">
                  {analysisResult.analysis.match_analysis
                    .missing_required_skills.length > 0 ? (
                    analysisResult.analysis.match_analysis.missing_required_skills.map(
                      (skill) => (
                        <li
                          key={skill}
                          className="text-sm text-amber-900"
                        >
                          • {skill}
                        </li>
                      ),
                    )
                  ) : (
                    <li className="text-sm text-slate-600">
                      No required skill gaps were identified.
                    </li>
                  )}
                </ul>
              </section>
            </div>
          </section>
        )}
        <section className="mt-10 rounded-2xl border border-amber-200 bg-amber-50 p-5">
          <h2 className="font-extrabold text-amber-900">
             Important notice
          </h2>

          <p className="mt-2 text-sm leading-6 text-amber-800">
                        CareerLens provides evidence-based decision support, not a hiring
            guarantee. Always review the score, identified skills and generated
            application materials before applying..
          </p>
        </section>
      </section>

      <Footer />
    </main>
  );
}