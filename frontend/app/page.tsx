import Link from "next/link";
import { AdSlot, Footer, Header } from "./components";

const steps = [
  {
    number: "01",
    title: "Upload your resume",
    description:
      "Upload your current PDF resume. Personal details will be removed before AI analysis.",
    color: "bg-violet-100 text-violet-700",
  },
  {
    number: "02",
    title: "Add the target role",
    description:
      "Paste the complete job description so the analysis remains specific to the opportunity.",
    color: "bg-cyan-100 text-cyan-700",
  },
  {
    number: "03",
    title: "Improve your application",
    description:
      "Receive matched skills, missing keywords, improvements and a practical learning plan.",
    color: "bg-lime-100 text-lime-800",
  },
];

const guideCards = [
  {
    category: "Resume Format",
    number: "01",
    title: "AI Engineer Resume Format for Freshers",
    description:
      "Create a clear one-page resume that highlights your AI skills, projects and evidence.",
    href: "/guides/ai-engineer-resume-format",
    color: "bg-violet-100",
  },
  {
    category: "Projects",
    number: "02",
    title: "How to Write AI Projects in Your Resume",
    description:
      "Turn student projects into credible achievement bullets that recruiters understand.",
    href: "/guides/write-projects-in-resume",
    color: "bg-cyan-100",
  },
  {
    category: "ATS",
    number: "03",
    title: "ATS Resume Mistakes Freshers Should Avoid",
    description:
      "Fix formatting problems, weak evidence and unnecessary keyword stuffing.",
    href: "/guides/ats-mistakes-freshers",
    color: "bg-lime-100",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden bg-[#fbfcff] text-slate-950">
      <Header />

      {/* Hero section */}
      <section className="mx-auto grid min-h-[650px] w-[calc(100%-28px)] max-w-7xl items-center gap-14 py-14 md:w-[calc(100%-48px)] lg:grid-cols-[0.9fr_1.1fr] lg:gap-20 lg:py-20">
        <div>
          <p className="inline-flex items-center rounded-full border border-violet-200 bg-violet-50 px-4 py-2 text-[11px] font-extrabold uppercase tracking-wider text-violet-700">
            ✦ AI resume intelligence for students
          </p>

          <h1 className="mt-6 text-[52px] font-black leading-[0.96] tracking-[-0.06em] sm:text-6xl lg:text-7xl">
            See the gap.
            <br />
            <span className="relative text-violet-600">
              Land the role.
              <span className="absolute bottom-1 left-0 -z-10 h-3 w-full -rotate-1 bg-lime-300" />
            </span>
          </h1>

          <p className="mt-7 max-w-xl text-base leading-8 text-slate-600 sm:text-lg">
            Upload your resume, paste a job description, and get an honest
            match score with the exact skills and actions that can improve your
            application.
          </p>

          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
            <Link
              href="/tool"
              className="flex min-h-14 items-center justify-center rounded-xl bg-slate-950 px-6 text-sm font-bold text-white shadow-xl shadow-slate-300 transition hover:-translate-y-1 hover:bg-violet-600"
            >
              Analyze my resume →
            </Link>

            <Link
              href="/guides"
              className="text-center text-sm font-bold underline decoration-slate-300 underline-offset-8"
            >
              Explore free guides
            </Link>
          </div>

          <div className="mt-7 flex flex-col gap-3 text-xs font-semibold text-slate-500 sm:flex-row sm:gap-6">
            <span>✓ Privacy-first analysis</span>
            <span>✓ No registration required</span>
          </div>
        </div>

        {/* Example analysis card */}
        <div className="relative rounded-3xl border border-slate-200 bg-white p-5 shadow-[0_30px_80px_rgba(49,44,91,0.16)] sm:p-7">
          <div className="absolute -right-20 -top-20 -z-10 h-64 w-64 rounded-full bg-violet-200/50 blur-3xl" />
          <div className="absolute -bottom-20 -left-20 -z-10 h-56 w-56 rounded-full bg-cyan-200/40 blur-3xl" />

          <div className="flex items-center justify-between border-b border-slate-200 pb-5">
            <div className="flex items-center gap-3">
              <span className="grid h-11 w-11 place-items-center rounded-xl bg-violet-100 text-xl">
                ◎
              </span>

              <div>
                <h2 className="text-sm font-extrabold">Resume match</h2>
                <p className="text-xs text-slate-500">AI Engineer Intern</p>
              </div>
            </div>

            <span className="rounded-full bg-emerald-50 px-3 py-2 text-[10px] font-bold text-emerald-700">
              ● Analysis ready
            </span>
          </div>

          <div className="grid items-center gap-6 py-7 sm:grid-cols-[150px_1fr]">
            <div className="mx-auto grid h-32 w-32 place-items-center rounded-full bg-[conic-gradient(#6d4aff_0_78%,#ebe9f6_78%)]">
              <div className="grid h-24 w-24 place-items-center rounded-full bg-white text-center">
                <div>
                  <strong className="block text-4xl tracking-tight">78</strong>
                  <small className="text-slate-500">out of 100</small>
                </div>
              </div>
            </div>

            <div>
              <p className="text-xs font-extrabold uppercase tracking-widest text-violet-600">
                Strong match
              </p>

              <h3 className="mt-2 text-2xl font-black tracking-tight">
                You&apos;re closer than you think.
              </h3>

              <p className="mt-3 text-sm leading-6 text-slate-500">
                Your projects align well. Add three missing skills to move into
                the highest match group.
              </p>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl border border-slate-200 p-4">
              <p className="text-xs text-slate-500">Matched skills</p>
              <div className="mt-2 flex items-center justify-between gap-3">
                <strong className="text-xs">
                  Python · RAG · Firebase
                </strong>
                <b className="text-xl text-emerald-600">12</b>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 p-4">
              <p className="text-xs text-slate-500">Missing skills</p>
              <div className="mt-2 flex items-center justify-between gap-3">
                <strong className="text-xs">
                  Docker · FastAPI · AWS
                </strong>
                <b className="text-xl text-amber-600">3</b>
              </div>
            </div>
          </div>

          <div className="mt-3 flex items-center gap-3 rounded-xl bg-slate-50 p-4">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-white">
              ✦
            </span>

            <div className="min-w-0 flex-1">
              <p className="text-[10px] text-slate-500">Best next action</p>
              <strong className="block truncate text-xs">
                Add measurable impact to your RAG project
              </strong>
            </div>

            <Link
              href="/tool"
              className="hidden text-xs font-bold text-violet-600 sm:block"
            >
              View plan →
            </Link>
          </div>
        </div>
      </section>

      {/* Supported roles */}
      <section className="border-y border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-7 md:flex-row md:items-center md:justify-between md:px-8">
          <p className="text-sm text-slate-500">
            Created for students and freshers applying to
          </p>

          <div className="flex flex-wrap gap-3 text-xs font-extrabold uppercase tracking-wider text-slate-700 sm:gap-6">
            <span>AI/ML</span>
            <span>Python</span>
            <span>Data</span>
            <span>Software</span>
            <span>Internships</span>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-7xl px-5 py-24 md:px-8">
        <div className="max-w-2xl">
          <p className="text-xs font-extrabold uppercase tracking-widest text-violet-600">
            One focused workflow
          </p>

          <h2 className="mt-3 text-4xl font-black tracking-[-0.04em] sm:text-5xl">
            From job description to a sharper application.
          </h2>

          <p className="mt-5 text-base leading-7 text-slate-500">
            CareerLens turns a confusing role description into a clear,
            practical improvement plan.
          </p>
        </div>

        <div className="mt-12 grid gap-4 md:grid-cols-3">
          {steps.map((step) => (
            <article
              key={step.number}
              className="relative rounded-2xl border border-slate-200 bg-white p-7 transition hover:-translate-y-1 hover:shadow-xl"
            >
              <span className="absolute right-6 top-6 text-xs font-bold text-slate-300">
                {step.number}
              </span>

              <span
                className={`grid h-12 w-12 place-items-center rounded-xl text-xl font-black ${step.color}`}
              >
                {step.number}
              </span>

              <h3 className="mt-10 text-xl font-extrabold tracking-tight">
                {step.title}
              </h3>

              <p className="mt-3 text-sm leading-7 text-slate-500">
                {step.description}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* Safe advertisement position */}
      <div className="px-5 md:px-8">
        <AdSlot position="home-middle" />
      </div>

      {/* Guides */}
      <section className="mx-auto max-w-7xl px-5 py-24 md:px-8">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-extrabold uppercase tracking-widest text-violet-600">
              Free career resources
            </p>

            <h2 className="mt-3 text-4xl font-black tracking-tight">
              Learn before you apply.
            </h2>
          </div>

          <Link
            href="/guides"
            className="text-sm font-bold text-violet-600"
          >
            View all resume guides →
          </Link>
        </div>

        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {guideCards.map((guide) => (
            <article
              key={guide.title}
              className="overflow-hidden rounded-2xl border border-slate-200 bg-white"
            >
              <div
                className={`flex h-28 items-start justify-between p-5 ${guide.color}`}
              >
                <span className="rounded-md bg-white/80 px-2 py-1 text-[10px] font-bold uppercase">
                  {guide.category}
                </span>

                <strong className="text-5xl text-slate-900/20">
                  {guide.number}
                </strong>
              </div>

              <div className="flex min-h-64 flex-col p-6">
                <h3 className="text-xl font-extrabold leading-7 tracking-tight">
                  {guide.title}
                </h3>

                <p className="mt-4 text-sm leading-7 text-slate-500">
                  {guide.description}
                </p>

                <Link
                  href={guide.href}
                  className="mt-auto pt-7 text-sm font-bold text-violet-600"
                >
                  Read guide →
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="mx-auto mb-24 w-[calc(100%-28px)] max-w-7xl overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-[#242044] to-violet-700 px-7 py-14 text-white md:w-[calc(100%-48px)] md:px-14">
        <div className="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl">
            <p className="text-xs font-extrabold uppercase tracking-widest text-lime-300">
              Free CareerLens analysis
            </p>

            <h2 className="mt-4 text-4xl font-black tracking-tight md:text-5xl">
              Ready to see your real match?
            </h2>

            <p className="mt-4 leading-7 text-slate-300">
              Compare your resume with a target role and receive a focused
              improvement plan.
            </p>
          </div>

          <Link
            href="/tool"
            className="flex min-h-14 items-center justify-center rounded-xl bg-white px-7 text-sm font-extrabold text-slate-950"
          >
            Analyze my resume →
          </Link>
        </div>
      </section>

      <Footer />
    </main>
  );
}