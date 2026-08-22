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

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0];

    setError("");
    setInputsReady(false);

    if (!selectedFile) {
      setResumeFile(null);
      return;
    }

    const allowedExtensions = [".pdf", ".doc", ".docx", ".txt"];
    const lowercaseName = selectedFile.name.toLowerCase();

    const isAllowed = allowedExtensions.some((extension) =>
      lowercaseName.endsWith(extension),
    );

    if (!isAllowed) {
      setResumeFile(null);
      setError("Please upload a PDF, DOC, DOCX or TXT resume.");
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

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setInputsReady(false);

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

    setInputsReady(true);

    setTimeout(() => {
      document
        .getElementById("connection-status")
        ?.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
    }, 100);
  }

  function clearForm() {
    setResumeFile(null);
    setJobDescription("");
    setInputsReady(false);
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
                    PDF, DOCX or TXT · maximum 5 MB
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
                  accept=".pdf,.doc,.docx,.txt"
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
                className="flex min-h-13 flex-1 items-center justify-center rounded-xl bg-slate-950 px-6 text-sm font-bold text-white shadow-lg transition hover:-translate-y-0.5 hover:bg-violet-600"
              >
                Analyze resume match →
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

        {/* Honest integration status */}
        {inputsReady && (
          <section
            id="connection-status"
            className="mt-10 rounded-3xl border border-emerald-200 bg-emerald-50 p-6 sm:p-8"
          >
            <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
              <span className="grid h-14 w-14 shrink-0 place-items-center rounded-2xl bg-emerald-100 text-2xl text-emerald-700">
                ✓
              </span>

              <div className="flex-1">
                <p className="text-xs font-extrabold uppercase tracking-wider text-emerald-700">
                  Frontend inputs ready
                </p>

                <h2 className="mt-2 text-2xl font-black tracking-tight">
                  Resume and job description validated.
                </h2>

                <p className="mt-3 text-sm leading-7 text-slate-600">
                  The interface is working correctly. The next development
                  stage will connect this form to your existing CareerLens
                  Python agents through a secure FastAPI endpoint.
                </p>
              </div>
            </div>
          </section>
        )}

        <section className="mt-10 rounded-2xl border border-amber-200 bg-amber-50 p-5">
          <h2 className="font-extrabold text-amber-900">
            Development notice
          </h2>

          <p className="mt-2 text-sm leading-6 text-amber-800">
            This page currently validates the inputs only. It does not yet send
            the resume to Gemini or display a fake match score. We will connect
            your real resume extraction, privacy redaction, job parser, scoring
            and agent-routing services in the backend stage.
          </p>
        </section>
      </section>

      <Footer />
    </main>
  );
}