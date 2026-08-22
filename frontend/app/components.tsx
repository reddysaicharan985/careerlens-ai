"use client";

import Link from "next/link";
import { useState } from "react";

const navigation = [
  { name: "Home", href: "/" },
  { name: "Analyzer", href: "/tool" },
  { name: "Resume Guides", href: "/guides" },
  { name: "AI Internships", href: "/internships" },
  { name: "JD Keywords", href: "/keywords" },
];

export function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2">
      <span className="relative block h-8 w-8 rounded-full border-2 border-slate-950">
        <span className="absolute inset-[7px] rounded-full bg-violet-600" />
        <span className="absolute -bottom-1 -right-1 h-2 w-2 rotate-45 border-b-2 border-slate-950" />
      </span>

      <span className="text-xl font-extrabold tracking-tight text-slate-950">
        CareerLens
        <span className="ml-1 text-violet-600">AI</span>
      </span>
    </Link>
  );
}

export function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      <header className="mx-auto flex h-[72px] w-[calc(100%-28px)] max-w-7xl items-center border-b border-slate-200 md:w-[calc(100%-48px)]">
        <Logo />

        <nav className="ml-auto hidden items-center gap-7 lg:flex">
          {navigation.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm font-semibold text-slate-500 transition hover:text-violet-600"
            >
              {item.name}
            </Link>
          ))}
        </nav>

        <Link
          href="/tool"
          className="ml-auto hidden rounded-xl bg-slate-950 px-5 py-3 text-sm font-bold text-white transition hover:bg-violet-600 sm:block lg:ml-8"
        >
          Analyze resume →
        </Link>

        <button
          type="button"
          aria-label="Open navigation"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen(true)}
          className="ml-auto grid h-11 w-11 place-items-center rounded-xl border border-slate-200 bg-white text-2xl lg:hidden"
        >
          ☰
        </button>
      </header>

      {menuOpen && (
        <div className="fixed inset-0 z-50 bg-white px-5 py-5 lg:hidden">
          <div className="flex items-center justify-between">
            <Logo />

            <button
              type="button"
              aria-label="Close navigation"
              onClick={() => setMenuOpen(false)}
              className="grid h-11 w-11 place-items-center rounded-xl border border-slate-200 text-3xl"
            >
              ×
            </button>
          </div>

          <nav className="mt-12 flex flex-col">
            {navigation.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMenuOpen(false)}
                className="flex items-center justify-between border-b border-slate-200 py-5 text-xl font-bold text-slate-700"
              >
                {item.name}
                <span>→</span>
              </Link>
            ))}
          </nav>

          <Link
            href="/tool"
            onClick={() => setMenuOpen(false)}
            className="mt-8 flex h-14 items-center justify-center rounded-xl bg-slate-950 font-bold text-white"
          >
            Analyze my resume →
          </Link>
        </div>
      )}
    </>
  );
}

export function AdSlot({
  position,
}: {
  position: "home-middle" | "article-middle" | "results-bottom";
}) {
  return (
    <aside
      aria-label="Advertisement"
      data-ad-position={position}
      className="mx-auto my-10 w-full max-w-5xl"
    >
      <p className="mb-2 text-center text-[10px] font-semibold uppercase tracking-widest text-slate-400">
        Advertisement
      </p>

      <div className="flex min-h-24 items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 text-center text-xs text-slate-400 sm:min-h-28">
        Responsive advertisement area
      </div>
    </aside>
  );
}

export function Footer() {
  return (
    <footer className="bg-slate-950 text-white">
      <div className="mx-auto grid max-w-7xl gap-12 px-5 py-16 md:grid-cols-2 md:px-8 lg:grid-cols-[1.4fr_1fr_1fr]">
        <div>
          <Logo />

          <p className="mt-6 max-w-md text-sm leading-7 text-slate-400">
            Practical resume intelligence for students and freshers building
            careers in AI, software and data.
          </p>

          <p className="mt-5 text-xs font-bold text-lime-300">
            ✓ Privacy-first by design
          </p>
        </div>

        <div className="flex flex-col gap-3 text-sm text-slate-400">
          <strong className="mb-2 text-xs uppercase tracking-widest text-white">
            Product
          </strong>
          <Link href="/tool">Resume Analyzer</Link>
          <Link href="/keywords">JD Keywords</Link>
          <Link href="/guides">Resume Guides</Link>
          <Link href="/internships">Internship Guides</Link>
        </div>

        <div className="flex flex-col gap-3 text-sm text-slate-400">
          <strong className="mb-2 text-xs uppercase tracking-widest text-white">
            CareerLens
          </strong>
          <Link href="/about">About</Link>
          <Link href="/contact">Contact</Link>
          <Link href="/privacy">Privacy Policy</Link>
          <Link href="/terms">Terms and Conditions</Link>
          <Link href="/cookies">Cookie Policy</Link>
        </div>
      </div>

      <div className="mx-auto flex max-w-7xl flex-col gap-2 border-t border-slate-800 px-5 py-6 text-xs text-slate-500 md:flex-row md:justify-between md:px-8">
        <span>© 2026 CareerLens AI</span>
        <span>Created by Mukkara Sai Charan Reddy · Hyderabad, India</span>
      </div>
    </footer>
  );
}